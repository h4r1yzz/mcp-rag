
from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from logger import logger
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, List
from threading import Lock

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

router = APIRouter()

STREAM_DELAY = 0.05  # 50ms delay between chunks

conversation_memory: Dict[str, List] = {}
memory_lock = Lock()

# LLM instance - will be initialized once
_llm = None

def get_llm():
    """Get or create the LLM instance."""
    global _llm
    if _llm is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        _llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.5,
            streaming=True,  # Enable streaming
        )
    
    return _llm


@router.post("/groq_stream/")
async def groq_stream(
    question: str = Form(...),
    thread_id: Optional[str] = Form(None)
):
    logger.info(f"groq_stream request received - thread_id: {thread_id}")
    
    # Use default thread_id if not provided
    if not thread_id:
        thread_id = "default"
    
    def token_generator():
        try:
            llm = get_llm()
            
            # Get conversation history for this thread_id (short-term memory)
            with memory_lock:
                if thread_id not in conversation_memory:
                    # Initialize with system message
                    conversation_memory[thread_id] = [
                        SystemMessage(content="You are ClinicBot, a friendly and professional AI assistant for an aesthetic clinic. Help patients with questions about services, policies, and general clinic information in a warm and welcoming manner.")
                    ]

                messages = list(conversation_memory[thread_id])
            
            # Add the new user message
            messages.append(HumanMessage(content=question))
            
            # Stream the response token by token
            full_response = ""
            for chunk in llm.stream(messages):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    full_response += content
                    yield content
                    time.sleep(STREAM_DELAY)
            
            # Add both user message and AI response
            with memory_lock:
                conversation_memory[thread_id].append(HumanMessage(content=question))
                conversation_memory[thread_id].append(AIMessage(content=full_response))
            
        except Exception as e:
            logger.exception("Error in groq_stream")
            error_msg = f"Error: {str(e)}"
            yield error_msg

    return StreamingResponse(token_generator(), media_type="text/plain")


