#!/usr/bin/env python 

'''
RUN as 'python -m genai_utils.db_elastic -p "
'''

import os, sys, logging, argparse, glob, hashlib

from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_elasticsearch import (
    BM25Strategy,
    DenseVectorStrategy,
    ElasticsearchStore,
)

from elasticsearch import Elasticsearch
from mangorest.mango import webapi
from genai_utils import pdf_parser
from genai_utils import extract_docs

logger = logging.getLogger( "gpt" )

ES_URL, ES_USER, ES_PW  = "http://localhost:9200", "elastic", "elastic"

from genai_utils import config

ES_CNX= dict(es_url= ES_URL, es_user= ES_USER, es_password=ES_PW)


_ES_STARTEGIES = {
    "hnsw":     DenseVectorStrategy(), 
    "bm25":     BM25Strategy(),
    "hybrid":   DenseVectorStrategy(hybrid=True, rrf=False),
    "sparse":   None,
    "exact":    None,
}
# ---------------------------------------------------------------------------------------
def esDeleteIndex(index="test", es_url=ES_URL, es_user=ES_USER, es_pass= ES_PW, **kwargs):
    esclient = Elasticsearch(es_url, basic_auth = (es_user, es_pass))
    esclient.info()
    try:
        esclient.indices.delete(index=index)
    except:
        pass
# ---------------------------------------------------------------------------------------
def esCreateIndex(index="test", es_url=ES_URL, es_user=ES_USER, es_pass= ES_PW, **kwargs):
    esclient = Elasticsearch(es_url, basic_auth = (es_user, es_pass))
    esclient.indices.create(index=index)
# ---------------------------------------------------------------------------------------
def esCountIndex(index="test", es_url=ES_URL, es_user=ES_USER, es_pass= ES_PW, **kwargs):
    doc_count = 0
    try:
        esclient = Elasticsearch(es_url, basic_auth = (es_user, es_pass))
        doc_count = esclient.count(index=index)
    except:
        pass
    print(f"Total documents in index '{index}': {doc_count}")
    return doc_count
# ---------------------------------------------------------------------------------------
def getEmbedding(model="all-minilm:L6-v2", base_url = "http://127.0.0.1:11434/"):
    e = OllamaEmbeddings( model = model, base_url =base_url )
    return e
# ---------------------------------------------------------------------------------------
def getbyID( index="test",id="", es_url=ES_URL, es_user=ES_USER, es_pass= ES_PW, **kwargs):
    es_cnx = dict(es_url= es_url, es_user=es_user, es_password=es_pass)
    doc = ElasticsearchStore.get_by_ids(ids=[id]
            **es_cnx,
            index_name=index)
    return doc
# ---------------------------------------------------------------------------------------
def add_to_es( docs: list[Document], es_cnx: dict, index: str, embed, strategy= "hnsw" ):
    strat = _ES_STARTEGIES[strategy]
    vectorstore = None
    for i in range(0, len(docs), 20000):
        docsWithID = docs[i : min(i + 20000, len(docs))]
        for d in docsWithID:
            h = hashlib.md5(d.page_content.encode())
            d.id = h.hexdigest()
        
        vectorstore = ElasticsearchStore.from_documents(
            documents=docsWithID,
            embedding=embed,
            **es_cnx,
            index_name=index,
            bulk_kwargs={
                "chunk_size": 100,
            },
            strategy=strat,
        )
    return vectorstore

# ---------------------------------------------------------------------------------------
def es_retriever( es_cnx: dict, index: str, embed, strategy="hnsw", k= 10 ):
    strat = _ES_STARTEGIES[strategy]

    v = ElasticsearchStore( **es_cnx, embedding=embed, index_name=index, strategy=strat)
    return v.as_retriever(search_kwargs={"k": k})

def esVectorSearch( retreiver, q, k=10):
        ret = retreiver.as_retriever(search_kwargs={"k": k}).invoke(q)
        
        h = {r.page_content:r for r in ret}
        if len(h) != len(ret):
            ret = [v for v in h.values()]
            
        return ret

@webapi("/gpt/esSearchIndex/")
def esSearchIndex(request, index, query, model="all-minilm:L6-v2", user="", es_url=ES_URL, 
                    es_user=ES_URL, es_pass=ES_PW, k=10, rank=1, **kwargs):

    #print(f"\n{locals()}\n")
        
    if (not es_url):
        es = dict(es_url= ES_URL, es_user=ES_USER, es_password=ES_PW)
    else:
        es = dict(es_url= es_url, es_user=es_user, es_password=es_pass)

    #model = "llama3.2" #lets force the embedding for now
    embed = getEmbedding(model=model) 

    
    #if not os.path.exists(os.path.expanduser("~/.cache/RERANKER/")):
    #    print(f"**** Ranker cache does not exist ****")
    #    return ret
    if ( rank):
        v = es_retriever(es, index=index, embed=embed, k=k*2)
        docs = v.invoke(query)
        if (len(docs)):
            ranked = rerank( query, docs)
            docs = [Document(page_content=r['text'], metadata=r['metadata']) for r in ranked[0:k]]
    else:
        v = es_retriever(es, index=index, embed=embed, k=k)
        docs = v.invoke(query)

    h = {r.page_content: r for r in docs}
    if len(h) != len(docs):
        docs = [v for v in h.values()]
    
    ret = []
    for d in docs:
        ret.append(dict(page_content=d.page_content, metadata=d.metadata))
    return ret

# ---------------------------------------------------------------------------------------
def format(d, show=1):
    from IPython.display import HTML
    m=d['metadata']
    page = m['page'] if "page" in m  else "?"
    html=f'''
<h3>Document, {page} : {m['source']} </h3> 

{d['page_content'].replace("\n", "<br>")}
<hr/>
'''
    if(show):
        display(HTML(html))
    return html

# ---------------------------------------------------------------------------------------
@webapi("/gpt/esTextSearch/")
def esTextSearch(query, k=10, index="test", es_url = ES_URL, es_user=ES_USER, es_pass= ES_PW):
    esclient = Elasticsearch(es_url, basic_auth = (es_user, es_pass))
    res = esclient.search(index=index,  q=query, size=k)

    ret = []
    for i,r in enumerate(res['hits']['hits']):
        pc = r['_source']['text']
        mt = r['_source']['metadata']
        ret.append(dict(page_content = pc, metadata=mt))
        #print(i, " ==>", )
    return ret
# ---------------------------------------------------------------------------------------
def rerank(q, ret):
    from flashrank import (Ranker, RerankRequest,)
    
    ranker = Ranker("ms-marco-MiniLM-L-12-v2", os.path.expanduser("~/.cache/RERANKER/"))
    rerankrequest = RerankRequest(
        query=q, passages=[{"text": d.page_content, "metadata": d.metadata} for d in ret]
    )
    reranked = ranker.rerank(rerankrequest)
    return reranked
# ---------------------------------------------------------------------------------------
# This is standing by itself - should be called by indexFromFolder
# can be multi tasked 
def loadES( model="all-minilm:L6-v2", index="", filename = "/Users/e346104/Desktop/data/LLM/sample.pdf",
           es_url=ES_URL , es_user=ES_USER, es_pass=ES_PW, docs=[] ):
    
    if(not docs and filename):
        docs = extract_docs.extractDocs(file=filename)
        
    if (not docs):
        return docs
    embed= getEmbedding(model)
    es = dict(es_url=es_url , es_user=es_user, es_password=es_pass)
    v = add_to_es(docs, es, index=index, embed=embed)

    return docs

# ---------------------------------------------------------------------------------------
MARKER_BASE=f"/tmp/gpt/"
def indexFromFolder(folder="", force=0, index="test", recurse=0, just_show=0,
                        es_url=ES_URL, es_user=ES_USER, es_pass= ES_PW, model="all-minilm:L6-v2"):
    folder = os.path.expanduser(folder) + "/**"
    files = [f for f in glob.glob(folder, recursive=recurse) if os.path.isfile(f)]

    logger.info(f"URL: {es_url} Folder: {folder}: found {len(files)} files.")

    iFiles = []
    for f in files:
        bn = os.path.basename(f)
        dn = os.path.dirname(f)
        marker = f"{MARKER_BASE}/{index}/{dn}/.{bn}.indexed"

        if f.startswith(".") or f.endswith(".indexed") or (os.path.exists(marker) and not force):
            print(f"Already in cache '{f}' ... ")
            continue;

        try:
            if ( not just_show):
                pass
                logger.info(f"Indexing '{f}' {es_url}")        
                loadES(model, index, f, es_url, es_user, es_pass)
                os.makedirs(os.path.dirname(marker, mode=0o777), exist_ok=True)
                open(marker, "w", mode=0o777).write("")
                iFiles.append(f)
            else:
                print(f"Not indexing '{f}'\n======================")
        except Exception as e:
            logger.error(f"{f} failed to index {e}\n================")
            pass

    esCountIndex(index=index, es_url=es_url, user=es_user, pw= es_pass)
    return iFiles
#-----------------------------------------------------------------------------------
sysargs=None
def addargs(argv=sys.argv):
    global sysargs
    p = argparse.ArgumentParser(f"{os.path.basename(argv[0])}:")
    p.add_argument('-p', '--path',   required=False, type=str, default='.', help="path to look for files")
    p.add_argument('-i', '--index',  type=str, required=True, help="Elastic Search index")
    p.add_argument('-m', '--model',  type=str, required=False, default="all-minilm:L6-v2", 
                    help="embedding model; defaults to local ollama model 'all-minilm:L6-v2' ")
    p.add_argument('-e', '--es_url', type=str, required=False, default=ES_URL,  help=f"elastic URL default: {ES_URL}")
    p.add_argument('-u', '--es_user',type=str, required=False, default=ES_USER, help=f"elastic user. default: {ES_URL}")
    p.add_argument('-w', '--es_pass',type=str, required=False, default=ES_PW,   help=f"elastic password. default: {ES_PW}")
    p.add_argument('-f', '--force',  required=False, default=False, action='store_true', 
                   help="force and reindex - the files indexed will be ignored otherwise")
    p.add_argument('-j', '--just' ,  required=False, default=False, action='store_true', help="Just show - do not index")
    p.add_argument('-r', '--recurse',required=False, default=False, action='store_true', help="Recurse through the folder")
    p.add_argument('-q', '--query',required=False, type=str, default="", 
                   help="Search for context - instead of indexing - this will search the index")
    p.add_argument('-d', '--delete',required=False, default=False, action='store_true', help="Delete Index")

    sysargs=p.parse_args(argv[1:])
    return sysargs

from colabexts import utils as colabexts_utils
if __name__ == '__main__' and not colabexts_utils.inJupyter():
    a = addargs()
    logger.info(f"Indexing  {sysargs}")

    if ( a.delete):
        print(f"Deleting the index: {a.index}")
        esDeleteIndex(index=a.index, es_url=a.es_url, es_user=a.es_user, es_pass=a.es_pass )
        marker = f"{MARKER_BASE}/{a.index}/"
        os.rmdir(marker)
    elif ( a.query):
        print(f"Searching for context: {a.query}")
        res0 = esSearchIndex(None, index=a.index, es_url=a.es_url, es_user=a.es_user, es_pass=a.es_pass,  query=a.query)
        res1 = esTextSearch(query=a.query, index=a.index, es_url=a.es_url, es_user=a.es_user, k=5 )

        for d in res0:
            s = f"src: {d['metadata']['source']}\n{d['page_content']}\n{'-'*80}\n"
            print(s)
        for d in res1:
            s = f"src: {d['metadata']['source']}\n{d['page_content']}\n{'-'*80}\n"
            print(s)
    else:
        indexFromFolder(folder=a.path, force=a.force, index=a.index, es_url=a.es_url, recurse=a.recurse,
                        es_user=a.es_user, es_pass= a.es_pass, model=a.model)

#    indexFromFolder(sys.argv[1])
# index, model = "test2", "all-minilm:L6-v2"
# index, model = "test3", "llama3.2:latest"

# esDeleteIndex(index)
# esCreateIndex(index)

# loadES(model, index);
