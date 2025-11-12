"""
Flask application for MCP RAG Chatbot.
Serves both UI and API endpoints in a single unified application.
"""

from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from logger import logger
from config import settings
from modules.llm import get_llm_agent
from modules.query_handlers import query_agent
from services.vectorstore_service import get_vectorstore_service
from services.llm_service import get_llm_service
from prompts import CLINICBOT_CHAT_PROMPT
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import Field
from typing import List, Optional, Dict
from threading import Lock
import time
import traceback

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Conversation memory for streaming chat
conversation_memory: Dict[str, List] = {}
memory_lock = Lock()
STREAM_DELAY = 0.05  # 50ms delay between chunks


@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "MCP RAG Chatbot"}), 200


@app.route('/ask', methods=['POST'])
def ask_question():
    """
    RAG-based question answering endpoint.
    Retrieves relevant documents and generates a response.
    """
    try:
        # Get question from form data or JSON
        if request.is_json:
            question = request.json.get('question')
        else:
            question = request.form.get('question')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        logger.info(f"User query: {question}")
        
        # Use VectorStore service for querying
        vectorstore = get_vectorstore_service()
        docs = vectorstore.query(question, top_k=3)
        
        # Create a simple retriever
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
        
        logger.info("Query successful")
        return jsonify(result), 200
        
    except Exception as e:
        logger.exception("Error in ask_question endpoint")
        return jsonify({
            "error": str(e),
            "response": "I apologize, but I encountered an error processing your question. Please try again.",
            "sources": []
        }), 500


@app.route('/groq_stream', methods=['POST'])
def groq_stream():
    """
    Streaming chat endpoint using Server-Sent Events.
    Maintains conversation history per thread_id.
    """
    try:
        # Get question and thread_id from form data or JSON
        if request.is_json:
            question = request.json.get('question')
            thread_id = request.json.get('thread_id', 'default')
        else:
            question = request.form.get('question')
            thread_id = request.form.get('thread_id', 'default')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        logger.info(f"Groq stream request - thread_id: {thread_id}, question: {question}")
        
        def generate():
            try:
                # Use LLM service for chat
                llm_service = get_llm_service()
                llm = llm_service.get_chat_llm()
                
                # Get conversation history for this thread_id
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
                
                # Add both user message and AI response to memory
                with memory_lock:
                    conversation_memory[thread_id].append(HumanMessage(content=question))
                    conversation_memory[thread_id].append(AIMessage(content=full_response))
                
            except Exception as e:
                logger.exception("Error in groq_stream generator")
                error_msg = f"Error: {str(e)}"
                yield error_msg
        
        return Response(stream_with_context(generate()), mimetype='text/plain')
        
    except Exception as e:
        logger.exception("Error in groq_stream endpoint")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Run on port 3000 for local development (8080 in production via gunicorn)
    app.run(host='0.0.0.0', port=3000, debug=True)

