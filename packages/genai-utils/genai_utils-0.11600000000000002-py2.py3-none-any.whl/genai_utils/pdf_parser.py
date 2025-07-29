
import re, pdfplumber, os
from collections import Counter
from functools import partial
from pathlib import Path

from pdfplumber.page import Page
from pdfplumber.pdf import PDF
from pdfplumber.table import Table
from pdfplumber.utils import intersects_bbox


NUM_TO_DOC: dict = {0: "Document Name", 1: "Chapter", 2: "Section", 3: "SubSection", 4: "SubSubSection"}
WHITESPACE_HEADER: dict = {72: "Paragraph", 101: "Chapter", 105: "Section", 116: "SubSection", 126: "SubSubSection"}
DOC_TO_NUM: dict = {"Document Name": 0, "Chapter": 1, "Section": 2, "SubSection": 3, "SubSubSection": 4}
TABLE_SETTINGS: dict = {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 2}
PARAGRAPH_KEY = min(WHITESPACE_HEADER.keys())


def parsePDF(file: str) -> list[dict]:
    pdf_file = Path(file)
    if not pdf_file.exists():
        raise FileExistsError("File does not exist")

    records = []

    with pdfplumber.open(pdf_file) as doc:
        for page in doc.pages:
            tables = page.find_tables(table_settings=TABLE_SETTINGS)
            nontable_page = page.filter(partial(outside_tables, tables=tables))
            char_stat_dict = character_statistics(nontable_page)
            filtered = filter_page_by_chars(nontable_page, char_stat_dict)
            records.extend(text_line_tagger(filtered))

    return sorted(records, key=lambda x: x["doctop"])


#    Character characteristics  like font name and font size.
def character_statistics(document: Page) -> dict:
    bold_counter = Counter()
    char_counter = Counter()
    size_counter = Counter()
    italic_counter = Counter()

    for char in document.chars:
        if "Bold" in char["fontname"]:
            bold_counter[char["fontname"]] += 1

        elif "Italic" in char["fontname"]:

            italic_counter[char["fontname"]] += 1
        else:
            char_counter[char["fontname"]] += 1

        size_counter[round(char["size"])] += 1

    counter_list = [bold_counter, char_counter, size_counter, italic_counter]
    final_dict = {}
    for counter in counter_list:
        if counter:
            k, v = counter.most_common()[0]
            final_dict[k] = v

    return final_dict


# PDF: returns a filtered page that does not contain table data.
def outside_tables(obj: PDF, tables: list[Table]) -> PDF:
    return not any(intersects_bbox([obj], t.bbox) for t in tables)


def filter_page_by_chars(page: Page, char_stat_dict: dict) -> Page:
    return page.filter(
        lambda x: x["object_type"] == "char" and x["fontname"] in 
                    char_stat_dict and round(x["size"]) in char_stat_dict,
    )


# Tag each line in the page appropriately
# list[dict]: records  for each text line.
def text_line_tagger(page: Page) -> list[dict]:
    page_lines = page.extract_text_lines()
    records = []

    horizontal_white_space = Counter(round(x["x0"]) for x in page_lines)

    for text in page_lines:

        if horizontal_white_space[round(text["x0"])] == 1:
            continue

        header = "Paragraph"

        if check_header(text):
            header = header_type(text)

        records.append(
            {
                "header_type": header,
                "text": text["text"],
                "doctop": text["chars"][0]["doctop"],
                "page_number": text["chars"][0]["page_number"],
            },
        )

    return records


#  Check for bold letters. => bool: return True for all bold letters.
def check_header(text: dict) -> bool:
    return all("Bold" in char["fontname"] for char in text["chars"])


"""
Assigns new header type if the text has :
1) leading number
2) white space position
3) has table or figure within its text.

These 2 criteria are mutually exclusive and are used for different cases.

Args:
    text (dict): text line dictionary
    horizontal_white_space (Counter): white space dictionary

Returns:
    str:  new header string
"""
def header_type(text: dict) -> str:

    non_headers = ["Table", "Figure"]

    if any(text["text"].startswith(non) for non in non_headers):
        return "Paragraph"

    if round(text["x0"]) == PARAGRAPH_KEY:

        return number_to_header(text["text"])

    return whitespace_to_header(text["x0"])


def number_to_header(text: str) -> str:
    """
    Assigns header type to number.

    Args:
        text (str): header and value

    Returns:
        str: header type in the form of string
    """
    nums = text.split()[0]
    total = len(re.findall(r"[0-9]+", nums))
    if total == 0:
        return "Paragraph"
    return NUM_TO_DOC.get(total, "SubSubSection")


def whitespace_to_header(x0_position: int) -> str:
    """
    Handle edge case where the tool cannot extract leading numbers.
    Assigns header type based on whitespace position.

    Args:
        x0_position (int): _description_

    Returns:
        str: _description_
    """
    min_val = float("inf")
    header = None

    for k, v in WHITESPACE_HEADER.items():
        x0_diff = abs(k - x0_position)
        if x0_diff < min_val:
            min_val = x0_diff
            header = v

    return header

# ---------------------------------------------------------------------------------------
def getDocsFromPDF(filename):
    from genai_utils.dataframe_tools import merge_records,metadata_chunks,chunk_dict_to_list, chunks_to_doc_obj
    from genai_utils import pdf_parser

    filename = os.path.expanduser(filename)
    
    record = pdf_parser.parsePDF(filename)
    # Seems like there is not data excepts figures and tables in the pdf
    if ( not record ):
        print("Hmmmm not records found in PDF file!")
        return [] 

    merged = merge_records(record)

    docName = os.path.basename(filename)
    chunk_dict = metadata_chunks(merged,docName)
    chunks = chunk_dict_to_list(chunk_dict)
    docs = chunks_to_doc_obj(chunks, docName )
    return docs
