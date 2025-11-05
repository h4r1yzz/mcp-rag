from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.llm import get_llm_agent
from modules.query_handlers import query_agent
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
import os

router=APIRouter()

@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        logger.info(f"user query: {question}")

        # Embed model + Pinecone setup
        pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        index = pc.Index(os.environ["PINECONE_INDEX_NAME"])
        embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        embedded_query = embed_model.embed_query(question)
        res = index.query(vector=embedded_query, top_k=3, include_metadata=True)

        # Debug: Log what we retrieved
        logger.debug(f"Retrieved {len(res['matches'])} matches from Pinecone")
        
        docs = []
        for match in res["matches"]:
            text_content = match["metadata"].get("text", "")
            score = match.get("score", 0.0)
            logger.debug(f"Match score: {score:.4f}, Text length: {len(text_content)}")
            
            if text_content:  # Only add documents with content
                docs.append(
                    Document(
                        page_content=text_content,
                        metadata=match["metadata"]
                    )
                )
        
        logger.debug(f"Created {len(docs)} documents with content")

        class SimpleRetriever(BaseRetriever):
            tags: Optional[List[str]] = Field(default_factory=list)
            metadata: Optional[dict] = Field(default_factory=dict)

            def __init__(self, documents: List[Document]):
                super().__init__()
                self._docs = documents

            def _get_relevant_documents(self, query: str) -> List[Document]:
                return self._docs

        retriever = SimpleRetriever(docs)
        agent = get_llm_agent(retriever)
        result = query_agent(agent, question)

        logger.info("query successful")
        return result

    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(status_code=500, content={"error": str(e)})