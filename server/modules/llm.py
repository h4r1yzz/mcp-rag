from langchain_core.messages import SystemMessage, HumanMessage
from typing import List
from services.llm_service import get_llm_service
from prompts import CLINICBOT_RAG_PROMPT


def get_llm_agent(retriever):
    """Create a simple RAG chain with retriever."""

    # Use LLM service
    llm_service = get_llm_service()
    llm = llm_service.get_rag_llm()

    # Return a simple object that has the retriever and LLM
    class SimpleRAGAgent:
        def __init__(self, llm, retriever):
            self.llm = llm
            self.retriever = retriever

        def invoke(self, inputs):
            # Extract the user question
            messages = inputs.get("messages", [])
            if not messages:
                return {"messages": []}

            user_message = messages[-1]
            user_question = user_message.content if hasattr(user_message, 'content') else str(user_message)

            # Retrieve relevant documents
            retrieved_docs = self.retriever.invoke(user_question)

            # Format context from retrieved documents
            context = "\n\n".join([
                f"FAQ Category: {doc.metadata.get('category', 'General')}\n{doc.page_content}"
                for doc in retrieved_docs
            ])

            # Create the prompt with context
            prompt_messages = [
                SystemMessage(content=CLINICBOT_RAG_PROMPT),
                HumanMessage(content=f"""Context from FAQ knowledge base:

{context}

User Question: {user_question}

IMPORTANT: Answer the question using ONLY the information provided in the context above. Include ALL relevant details from the context - do not omit any important information. If the context mentions what days the clinic is closed, you MUST include that in your response.""")
            ]

            # Get response from LLM
            response = self.llm.invoke(prompt_messages)

            # Return in the expected format with sources
            return {
                "messages": messages + [response],
                "retrieved_docs": retrieved_docs
            }

    return SimpleRAGAgent(llm, retriever)
