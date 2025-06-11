import os
from langchain_community.document_loaders.parsers import RapidOCRBlobParser
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_core.runnables import chain
from typing import List
from rank_bm25 import BM25Okapi
from langchain_community.retrievers import BM25Retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import numpy as np
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain import hub
from docx import Document as DocxDocument
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from logger_config import logger
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["ASTRA_DB_API_ENDPOINT"] = os.getenv("ASTRA_DB_API_ENDPOINT")
os.environ["ASTRA_DB_APPLICATION_TOKEN"] = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
os.environ["LANGCHAIN_API_KEY"]=os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"]=os.getenv('LANGCHAIN_PROJECT')
os.environ["LANGCHAIN_TRACING_V2"]=os.getenv('LANGCHAIN_TRACING_V2')
os.environ["LANGSMITH_ENDPOINT"]=os.getenv('LANGSMITH_ENDPOINT')


ASTRA_DB_API_ENDPOINT=os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_APPLICATION_TOKEN=os.environ["ASTRA_DB_APPLICATION_TOKEN"]


def create_vectorstore():
    return AstraDBVectorStore(
        collection_name="astra_vectorize_langchain",
        embedding=embeddings_model,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_APPLICATION_TOKEN,
        namespace="default",
    )

def chunking_data(docs):
    try:
        logger.info("entered the ingestion function")
        logger.info(type(docs))
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        pages = text_splitter.split_documents(docs)
        logger.info("data was chunked successfully")
        data={"status":"success","response":str(pages[0].page_content)}
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"error:{e}")
        data={"status":"failed","response":str(e)}
        return JSONResponse(content=data)

class HybridRetriever:
    def __init__(self, vectorstore, top_k_vector=20, top_k_final=5):
        self.vectorstore = vectorstore
        self.top_k_vector = top_k_vector
        self.top_k_final = top_k_final

    def get_relevant_documents(self, query: str):
        candidate_docs, scores = zip(*self.vectorstore.similarity_search_with_score(query,k=self.top_k_vector))
        for doc, score in zip(candidate_docs, scores):
          doc.metadata["score"] = score
        lis=list(np.argsort(np.array([info.metadata["score"] for info in candidate_docs]))[::-1])
        ranked_documents = [(candidate_docs[i].page_content, candidate_docs[i].metadata["score"]) for i in lis]
        # Step 2: BM25 reranking
        top_ranked_documents = [doc[0] for doc in ranked_documents]
        split_docs=[item.split() for item in top_ranked_documents]
        tokenized_query=query.split()
        bm25=BM25Okapi(split_docs)
        bm25_scores = bm25.get_scores(tokenized_query)
        reranked_indices = np.argsort(bm25_scores)[::-1]
        reranked_documents = [(top_ranked_documents[i], bm25_scores[i]) for i in reranked_indices]
        # Step 3: Rank and return top-K
        top_docs=[rr_doc for rr_doc in reranked_documents[:self.top_k_final]]

        return top_docs


def format_docs(docs):
    return "\n\n".join(doc[0] for doc in docs)

def retrieve_generation(pages,user_query):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = AstraDBVectorStore(collection_name="astra_vectorize_langchain",embedding=embeddings_model,api_endpoint=ASTRA_DB_API_ENDPOINT,token=ASTRA_DB_APPLICATION_TOKEN,namespace="default",)
    uuids = vectorstore.add_documents(documents=pages)
    retriever = HybridRetriever(vectorstore=vectorstore)
    prompt = hub.pull("rlm/rag-prompt")
    model = ChatOpenAI(temperature=0, model="gpt-4")
    retriever_runnable = RunnableLambda(lambda query: retriever.get_relevant_documents(query))
    format_docs_runnable = RunnableLambda(format_docs)
    rag_chain = ({"context": retriever_runnable | format_docs_runnable,"question": RunnablePassthrough()}| prompt | model | StrOutputParser())
    output=rag_chain.invoke(user_query)
    return JSONResponse({"status":"success","response":output})




