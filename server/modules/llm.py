from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def create_retrieval_tool(retriever):
    """Create a retrieval tool for the agent to use."""
    
    # Create a closure that captures the retriever
    def retrieve_documents(query: str):
        """Retrieve documents using the retriever."""
        return retriever.invoke(query)
    
    @tool(response_format="content_and_artifact")
    def retrieve_context(query: str):
        """Retrieve information from medical documents to help answer a query.
        
        Use this tool when you need to search for information in the medical documents.
        The tool will return relevant context from the documents.
        """
        # Retrieve documents using the retriever
        retrieved_docs = retrieve_documents(query)
        
        # Serialize the documents for the model
        serialized = "\n\n".join(
            (f"Source: {doc.metadata.get('source', doc.metadata.get('sources', 'Unknown'))}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        
        return serialized, retrieved_docs
    
    return retrieve_context


def get_llm_agent(retriever):
    """Create an agent with retrieval capabilities using createAgent."""
    
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )

    # Create the retrieval tool
    retrieval_tool = create_retrieval_tool(retriever)
    
    # System prompt for the agent
    system_prompt = """You are **MediBot**, an AI-powered assistant trained to help users understand medical documents and health-related questions.

Your job is to provide clear, accurate, and helpful responses based **only on the retrieved context**.

Instructions:
- Use the retrieve_context tool to search for information when answering questions.
- Respond in a calm, factual, and respectful tone.
- Use simple explanations when needed.
- If the retrieved context does not contain the answer, say: "I'm sorry, but I couldn't find relevant information in the provided documents."
- Do NOT make up facts.
- Do NOT give medical advice or diagnoses.
- Always cite your sources when providing information.
"""

    # Create the agent with the retrieval tool
    agent = create_agent(
        model=llm,
        tools=[retrieval_tool],
        system_prompt=system_prompt
    )

    return agent
