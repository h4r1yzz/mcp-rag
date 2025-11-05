from logger import logger
from langchain_core.messages import HumanMessage
from typing import List, Dict, Any

def query_agent(agent, user_input: str):
    """Query the agent and extract response with source documents."""
    try:
        logger.debug(f"Running agent for input: {user_input}")
        
        # Invoke the agent with a human message
        result = agent.invoke({
            "messages": [HumanMessage(content=user_input)]
        })
        
        # Extract the final response from the agent
        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None
        
        # Extract the response content
        response_content = final_message.content if final_message else "No response generated"
        
        # Extract source documents from tool messages
        source_documents = []
        
        # Look through messages for ToolMessages that contain artifacts (source documents)
        for msg in messages:
            if hasattr(msg, 'artifact') and msg.artifact:
                # If the artifact is a list of documents, extract them
                if isinstance(msg.artifact, list):
                    source_documents.extend(msg.artifact)
                elif isinstance(msg.artifact, dict) and 'documents' in msg.artifact:
                    source_documents.extend(msg.artifact['documents'])
        
        # Extract source information from documents
        sources = []
        for doc in source_documents:
            if hasattr(doc, 'metadata'):
                source = doc.metadata.get("source") or doc.metadata.get("sources") or ""
                if source and source not in sources:
                    sources.append(source)
        
        # If no sources found, try to extract from document metadata directly
        if not sources and source_documents:
            for doc in source_documents:
                if hasattr(doc, 'metadata'):
                    # Try various metadata keys
                    for key in ['source', 'sources', 'file', 'filename']:
                        if key in doc.metadata and doc.metadata[key]:
                            source = str(doc.metadata[key])
                            if source not in sources:
                                sources.append(source)
                                break
        
        response = {
            "response": response_content,
            "sources": sources
        }
        
        logger.debug(f"Agent response: {response}")
        return response
    except Exception as e:
        logger.exception("Error on query agent")
        raise