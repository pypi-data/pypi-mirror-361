#!/usr/bin/env python

import sys, os, logging,datetime, docx, pandas as pd
logger = logging.getLogger( "genai_utils" )
from langchain_core.documents import Document
from genai_utils import pdf_parser

# ------------------------------------------------------------------------------------------
# Following functions extract chunks
# ------------------------------------------------------------------------------------------
def extractDocx(file):
    document = docx.Document(file)

    # STEP 1: extract tables 
    tables=[]
    for table in document.tables:
        data = []
        keys = None
        for i, row in enumerate(table.rows):
            text = (cell.text for cell in row.cells)

            if i == 0:
                keys = tuple(text)
                continue
            row_data = dict(zip(keys, text))
            data.append(row_data)

        df = pd.DataFrame(data)
        
        t = tables.append(Document(metadata={"head": "table", 'source': file}, 
                                       page_content= str(df)))
        tables.append(t)

    # STEP 2: extract text 
    paras = []
    paraTexts = []
    secHeader = ""

    for para in document.paragraphs:
        if (not para.text.strip()):
            continue;
        
        if para.style.name != "Normal" and "Paragraph" not in para.style.name:
            #print("==>", para.style.name)
            if ( len(paraTexts) > 0):
                paras.append(Document(metadata={"head": secHeader, 'source': file}, 
                                       page_content="\n".join(paraTexts)))
                paraTexts = []

            secHeader = para.text 
            continue;
        
        paraTexts.append(para.text)

    docs =  tables + paras
    return docs
# ---------------------------------------------------------------------------------------
'''
OLD FUNCTION

def getChunks(file, chunk_size=8000, overlap=256 ):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    txt= extractText( file= file)

    split = RecursiveCharacterTextSplitter(
        chunk_size= chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        add_start_index=True,
    )
    docs = []
    for txt in split.split_text(txt):
        d = Document(page_content= txt,  metadata=dict(source= file))
        docs.append(d)

    return docs
'''
# ---------------------------------------------------------------------------------------
def getchunksFromTxt(filename, chunk_overlap_ratio=0.2, chunk_size=8000):
    with open(filename, "r", encoding="utf-8", errors='ignore') as f:
        text = f.read()
        
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap= int(chunk_overlap_ratio * chunk_size),
        add_start_index=True,
    )
    texts = text_splitter.split_text(text)
    docs = []
    for t in texts:
        docs.append(Document( page_content=t,  metadata={"source": filename}))
    return docs
#-----------------------------------------------------------------------------------------    
def extractDocs(request=None, file=None, **kwargs):
    ret = f"Unknown file type {file}"

    if ( request and not file):
        for f in request.FILES.getlist('file'):
            content = f.read()
            #fileIO = io.BytesIO(content)
            file = f"/tmp/{str(f)}"
            with open(file, "wb") as f:
                f.write(content)


    if (file.endswith("doc") or file.endswith("docx") ):
        ret =  extractDocx(file)
    elif (file.endswith("txt") or file.endswith("md") ):
        ret =  getchunksFromTxt(file)
    elif (file.endswith("pdf") ):
        ret = pdf_parser.getDocsFromPDF(file)
    elif (file.endswith("xlsx") or file.endswith("xls")):
        df = pd.read_excel(file)
        ret = df.to_html()
        d = Document(page_content= ret,  metadata=dict(source= file))
        ret=[d]
    elif file.endswith("csv") :
        df = pd.read_csv(file)
        ret = df.to_html()
        d = Document(page_content= ret,  metadata=dict(source= file))
        ret=[d]
    elif file:
        with open(file, "r", encoding="utf-8", errors='ignore') as f:
            ret = f.read()
        d = Document(page_content= ret,  metadata=dict(source= file))
        ret=[d]
    else:
        ret = []
    
    return ret

