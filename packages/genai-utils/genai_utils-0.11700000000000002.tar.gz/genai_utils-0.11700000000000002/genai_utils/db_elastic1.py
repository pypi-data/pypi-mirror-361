#!/usr/bin/env python

import os,glob
from mangorest.mango import webapi
from ray import logger
from langchain_core.documents import Document

BASE = "~/data/gpt/"
from langchain_ollama import OllamaEmbeddings
from langchain_elasticsearch import (
    BM25Strategy,
    DenseVectorStrategy,
    ElasticsearchStore,
)
# ---------------------------------------------------------------------------------------
# Elastic search parameters
#
ES_URL, ES_USER, ES_PW  = "http://localhost:9200", "elastic", "elastic"
ES_CNX   = dict(es_url= ES_URL, es_user= ES_USER, es_password=ES_PW)
_ES_STARTEGIES = {
    "hnsw":     DenseVectorStrategy(), 
    "bm25":     BM25Strategy(),
    "hybrid":   DenseVectorStrategy(hybrid=True, rrf=False),
    "sparse":   None,
    "exact":    None,
}
# ---------------------------------------------------------------------------------------
# Embeddings - lets use local emebddings
#
def getEmbedding(model="all-minilm:L6-v2",base_url = "http://127.0.0.1:11434/"):
    e = OllamaEmbeddings( model = model, base_url =base_url )
    return e

class Elastic:
    def __init__(self, es_cnx=ES_CNX, index="sageai", strategy="hnsw", embed="all-minilm:L6-v2"):
        self.es_cnx, self.index, self. strategy, self.embed  = es_cnx, index, strategy, embed
        if type(self.embed) == str:
            self.embed = getEmbedding(embed)
            
        self.strategy = _ES_STARTEGIES[self.strategy]
    # ---------------------------------------------------------------------------------------
    def _getChunks(self, file=f"{BASE}HS4_SGS1_V1S2.pdf", chunk_overlap_ratio=0.2, chunk_size=8000):
        from rag_basic.process_files import multi_process_pdf,process_pdf_to_chunks
        if ( file.endswith(".pdf")):
            chunks = process_pdf_to_chunks(file)        
        elif( file.endswith(".txt")):
            with open(file, "r", encoding="utf-8", errors='ignore') as f:
                text = f.read()
                
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap= int(chunk_overlap_ratio * chunk_size),
                add_start_index=True,
            )
            texts = text_splitter.split_text(text)
            chunks = []
            for t in texts:
                chunks.append(Document( page_content=t,  metadata={"source": file}))
        else:
            assert 0, "Unknown file type"
        return chunks
    # ---------------------------------------------------------------------------------------
    def indexdoc(self, file=f"{BASE}HS4_SGS1_V1S2.pdf", embed=None, strategy="hnsw"):
        file = os.path.expanduser(file)
        chunks = self._getChunks(file)

        for i in range(0, len(chunks), 20000):
            vectorstore = ElasticsearchStore.from_documents(
                documents= chunks[i : min(i + 20000, len(chunks))],
                embedding=self.embed,
                **self.es_cnx,
                index_name=self.index,
                bulk_kwargs={
                    "chunk_size": 100,
                },
                strategy=self.strategy,
            )
        
        print(f"Indexed {len(chunks)} chunks from {file}")
    # ---------------------------------------------------------------------------------------
    def es_retriever( self, k= 10 ):
        v = ElasticsearchStore( **self.es_cnx, embedding=self.embed, index_name=self.index, strategy=self.strategy)
        return v.as_retriever(search_kwargs={"k": k})

    # ---------------------------------------------------------------------------------------
    def search(self,query, k=10, rerank=1, **kwargs):
        docs = self.es_retriever().invoke(query)

        h = {r.page_content: r for r in docs}
        if len(h) != len(docs):
            docs = [v for v in h.values()]
        
        ret = []
        for d in docs:
            ret.append(dict(page_content=d.page_content, metadata=d.metadata))
        return ret

def indexFolder(folder=".", recursive=1):
    folder = os.path.expanduser((folder))
    logger.info(f"Indexing {folder}")
    se = Elastic()
    files = [f for f in glob.glob(folder, recursive=recursive) if os.path.isfile(f)]
    for f in files:
        print(f"{os.path.getsize(f)} : {f} ")
        se.indexdoc(f)
        
from colabexts import utils as colabexts_utils
if __name__ == '__main__' and not colabexts_utils.inJupyter():
    folder = "." if len(sys.args) <= 1 else sys.args[1]
    logger.info(f"Indexing  {folder}")
    indexFolder(folder)


def test():
    se = Elastic()
    docs = se.search("tell me about Ka-band - where do they play")
    return docs
    
