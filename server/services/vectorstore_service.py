"""
Centralized VectorStore Service for Pinecone operations.
Provides singleton access to Pinecone client, index, and embedding model.
"""

from functools import lru_cache
from typing import List, Dict, Any
from pathlib import Path
import time

from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from config import settings
from logger import logger


class VectorStoreService:
    """Centralized service for Pinecone vector store operations."""
    
    def __init__(self):
        self._pc = None
        self._index = None
        self._embed_model = None
    
    @property
    def client(self) -> Pinecone:
        """Lazy-loaded Pinecone client (singleton)."""
        if self._pc is None:
            logger.info("Initializing Pinecone client")
            self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        return self._pc
    
    @property
    def index(self):
        """Lazy-loaded Pinecone index (singleton)."""
        if self._index is None:
            logger.info(f"Connecting to Pinecone index: {settings.PINECONE_INDEX_NAME}")
            self._index = self.client.Index(settings.PINECONE_INDEX_NAME)
        return self._index
    
    @property
    def embed_model(self) -> GoogleGenerativeAIEmbeddings:
        """Lazy-loaded embedding model (singleton)."""
        if self._embed_model is None:
            logger.info(f"Initializing embedding model: {settings.EMBEDDING_MODEL}")
            self._embed_model = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY
            )
        return self._embed_model
    
    def query(self, text: str, top_k: int = 3) -> List[Document]:
        """
        Query vector store and return documents.
        
        Args:
            text: Query text to search for
            top_k: Number of top results to return
            
        Returns:
            List of LangChain Document objects with relevant content
        """
        logger.debug(f"Querying vector store for: {text[:50]}...")
        
        # Embed the query
        embedded_query = self.embed_model.embed_query(text)
        
        # Query Pinecone
        res = self.index.query(
            vector=embedded_query,
            top_k=top_k,
            include_metadata=True
        )
        
        # Convert to LangChain documents
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
        
        logger.debug(f"Retrieved {len(docs)} documents with content")
        return docs
    
    def upsert_documents(
        self, 
        documents: List[Document], 
        id_prefix: str = "doc"
    ) -> int:
        """
        Upsert documents to vector store.
        
        Args:
            documents: List of LangChain Document objects to upsert
            id_prefix: Prefix for document IDs
            
        Returns:
            Number of documents upserted
        """
        if not documents:
            logger.warning("No documents to upsert")
            return 0
        
        logger.info(f"Upserting {len(documents)} documents to vector store")
        
        # Extract text and metadata
        texts = [doc.page_content for doc in documents]
        metadatas = []
        for doc in documents:
            metadata = doc.metadata.copy()
            # Ensure text is in metadata for retrieval
            metadata["text"] = doc.page_content
            metadatas.append(metadata)
        
        ids = [f"{id_prefix}-{i}" for i in range(len(documents))]
        
        # Generate embeddings
        logger.debug("Generating embeddings...")
        embeddings = self.embed_model.embed_documents(texts)
        
        # Prepare vectors for upsert
        vectors = [
            (id_val, embedding, metadata)
            for id_val, embedding, metadata in zip(ids, embeddings, metadatas)
        ]
        
        # Upsert to Pinecone
        logger.debug("Upserting to Pinecone...")
        self.index.upsert(vectors=vectors)
        
        logger.info(f"✅ Successfully upserted {len(vectors)} documents")
        return len(vectors)
    
    def ensure_index_exists(self):
        """
        Ensure Pinecone index exists, create if not.
        This is typically called during initialization scripts.
        """
        logger.info("Checking if Pinecone index exists...")
        
        existing_indexes = [i["name"] for i in self.client.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {settings.PINECONE_INDEX_NAME}")
            
            spec = ServerlessSpec(
                cloud="aws",
                region=settings.PINECONE_ENV,
            )
            
            self.client.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=spec,
            )
            
            # Wait for index to be ready
            logger.info("Waiting for index to be ready...")
            while not self.client.describe_index(settings.PINECONE_INDEX_NAME).status["ready"]:
                time.sleep(1)
            
            logger.info(f"Index {settings.PINECONE_INDEX_NAME} created and ready")
        else:
            logger.info(f"Using existing index: {settings.PINECONE_INDEX_NAME}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index."""
        return self.index.describe_index_stats()


@lru_cache()
def get_vectorstore_service() -> VectorStoreService:
    """Get singleton VectorStore service instance."""
    return VectorStoreService()

