from fastapi import APIRouter, Form, HTTPException
from modules.llm import get_llm_agent
from modules.query_handlers import query_agent
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from typing import List, Optional
from logger import logger
from services.vectorstore_service import get_vectorstore_service

router=APIRouter()

@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        logger.info(f"user query: {question}")

        # Use VectorStore service for querying
        vectorstore = get_vectorstore_service()
        docs = vectorstore.query(question, top_k=3)

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

    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error processing question")
        raise HTTPException(status_code=500, detail="Internal server error")