#!/usr/bin/env python 

import pdfplumber, os, base64, glob, tqdm, json
from io import BytesIO
import io, base64
from PIL import Image
from IPython.display import HTML
from genai_utils.describe_image import describe_image
from genai_utils import db_elastic

def _extractImagesFromPDF(file=None, **kwargs):
    assert file.endswith("pdf"), "Called with non PDF File!!"

    ret = {}
    txt = []
    with pdfplumber.open(file) as doc:
        for pageNumber, page in enumerate(doc.pages):
            images = page.images
            for image_index, img in enumerate(images):
                try:
                    bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                    image = page.within_bbox(bbox).to_image()
                    pil_image = image.original
                    imageRGB = pil_image.convert("RGB")
                    b = BytesIO()
                    imageRGB.save(b, format='PNG')
                    b.seek(0)
                    br= b.read()
                    b64Image = base64.b64encode(br).decode("utf-8")
                    url = "data:image/jpg;base64, " + b64Image
                    txt.append(page.extract_text())
                    #img = f"<img src='{url}' >"
                    #display (HTML(img))
                    ret[url] = 1
                except:
                    pass
    ret = [r for r in ret.keys()]
    return dict(images=ret, texts=txt)

def indexImagesFromPDF(file, savedir="/tmp/genai_utils/", verbose =0):
    ret = _extractImagesFromPDF(file)
        
    if ( savedir is None or not savedir):
        return ret, None
    files = []
    for i, img in enumerate(ret['images']):
        img1=img[img.index(",")+1:].strip()
        imgd = Image.open(io.BytesIO(base64.decodebytes(img1.encode()) ))
        
        bname = os.path.basename(file)
        sfile = f"{savedir}/{bname}__{i}.png"
        os.makedirs(savedir, exist_ok=True)
        imgd.save(sfile)
        files.append(sfile)
        print(f"Saved {sfile}")
        if ( verbose):
            display(HTML(f"<img src='{img}'> "))
            print(ret['texts'][i][0:128])
    return ret, files
    
def index_directory(directory, outf= {}, savedir="/tmp/genai_utils/", recurse=0, count=10000):
    pngs = glob.glob(os.path.join(directory, '**/*.png') , recursive=recurse)
    jpgs = glob.glob(os.path.join(directory, '**/*.jpg') , recursive=recurse)
    jpes = glob.glob(os.path.join(directory, '**/*.jpeg'), recursive=recurse)
    pdfs = glob.glob(os.path.join(directory, '**/*.pdf') , recursive=recurse)

    images= []
    for pdfFile in tqdm.tqdm(pdfs):
        print(f"Getting images from {pdfFile}")
        ret, files = indexImagesFromPDF(pdfFile)
        images.extend(files)
    
    image_paths = [*pngs, *jpgs, *jpes, *images]
    n = 0
    for image_path in tqdm.tqdm(image_paths):
        if ( n >= count):
            break;
        if image_path in outf:
            continue
        with open(image_path, 'rb') as f:
            image_data = f.read()
        try:
            description = ""
            description = describe_image(image_data)
            print(f"Indexed {image_path}: {description}")
            outf[image_path] = description
            n += 1
        except Exception as e:
            print(f"Failed to index {image_path}: {e}")
            pass
        
    return outf

def getDocs(outf):
    from langchain_core.documents import Document

    docs = []
    for k,v in outf.items():
        print(k, v[0:32])
        d = Document(page_content=v, metadata=dict(source=k) )
        docs.append(d)
    return docs

def save(outf, file="/tmp/genai_utils/images_dir.json"):
    with open(file, "wt") as f:
        f.write(json.dumps(outf))
    
def load(file="/tmp/genai_utils/images_dir.json"):
    outf = {}
    if ( os.path.exists(file)):
        with open(file, "rt") as f:
            outf = json.loads( f.read() )
    return outf

outf=load()
