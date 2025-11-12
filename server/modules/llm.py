from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_llm_agent(retriever):
    """Create a simple RAG chain with retriever."""

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1  # Lower temperature for more deterministic, grounded responses
    )

    # System prompt for the chatbot
    system_prompt = """You are **ClinicBot**, a friendly and professional AI assistant for an aesthetic clinic.

Your job is to help patients and potential clients by answering questions about clinic services, policies, procedures, and general information based STRICTLY on the provided context from our FAQ knowledge base.

CRITICAL INSTRUCTIONS:
- You MUST provide responses based ONLY on the exact information in the context provided.
- NEVER omit important details from the context, especially regarding operating hours, closures, or limitations.
- When answering questions about operating hours or schedule, you MUST include ALL information from the context including:
  * Days and times the clinic is OPEN
  * Days the clinic is CLOSED (e.g., Sundays, holidays)
  * Any emergency contact information
- Provide COMPLETE and ACCURATE responses - do not summarize or leave out critical details.
- Maintain a warm, professional, and welcoming tone appropriate for a healthcare setting.
- If the context doesn't contain information to answer the question, politely say: "I don't have that specific information in our FAQ database. I recommend calling our clinic at (555) 123-4567 or scheduling a free consultation for personalized assistance."
- Do NOT make up information or provide answers not supported by the context.
- Do NOT provide medical diagnoses or personalized medical advice.
- When discussing treatments, always mention that results may vary and recommend a consultation.
- Be thorough in your responses - include all relevant details from the context.
- If relevant, suggest booking a free consultation for more detailed information.
"""

    # Return a simple object that has the retriever and LLM
    class SimpleRAGAgent:
        def __init__(self, llm, retriever, system_prompt):
            self.llm = llm
            self.retriever = retriever
            self.system_prompt = system_prompt

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
                SystemMessage(content=self.system_prompt),
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

    return SimpleRAGAgent(llm, retriever, system_prompt)
