from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from logger import logger
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import time
from typing import Optional, Dict, List
from threading import Lock
from services.llm_service import get_llm_service
from prompts import CLINICBOT_CHAT_PROMPT

router = APIRouter()

STREAM_DELAY = 0.05  # 50ms delay between chunks

conversation_memory: Dict[str, List] = {}
memory_lock = Lock()


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
            # Use LLM service for chat
            llm_service = get_llm_service()
            llm = llm_service.get_chat_llm()

            # Get conversation history for this thread_id (short-term memory)
            with memory_lock:
                if thread_id not in conversation_memory:
                    # Initialize with system message
                    conversation_memory[thread_id] = [
                        SystemMessage(content=CLINICBOT_CHAT_PROMPT)
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


