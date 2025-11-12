"""
FAQ Vector Store Initialization Script

This script loads the clinic FAQs from JSON and populates the Pinecone vector store.
Run this script once during initial setup or whenever the FAQ knowledge base is updated.

Usage:
    python server/scripts/initialize_faq_vectorstore.py
"""

import sys
from pathlib import Path
from tqdm.auto import tqdm

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.faq_loader import load_faqs_from_json
from server.logger import logger
from server.config import settings
from server.services.vectorstore_service import get_vectorstore_service


def initialize_pinecone_index():
    """Initialize or connect to Pinecone index using VectorStore service."""
    logger.info("Initializing Pinecone connection...")

    vectorstore = get_vectorstore_service()
    vectorstore.ensure_index_exists()

    return vectorstore.index


def clear_existing_faqs(index):
    """
    Clear existing FAQ entries from the index.
    This ensures we don't have duplicate or outdated FAQs.
    """
    logger.info("Checking for existing FAQ entries...")
    
    try:
        # Get index stats
        stats = index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors > 0:
            logger.warning(f"Found {total_vectors} existing vectors in index")
            response = input("Do you want to clear existing vectors? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                logger.info("Deleting all vectors from index...")
                index.delete(delete_all=True)
                logger.info("✅ Index cleared")
            else:
                logger.info("Keeping existing vectors. New FAQs will be added.")
        else:
            logger.info("Index is empty, ready for FAQ insertion")
            
    except Exception as e:
        logger.warning(f"Could not check index stats: {e}")


def load_and_embed_faqs(index):
    """Load FAQs and create embeddings, then upsert to Pinecone using VectorStore service."""

    # Load FAQs from JSON
    logger.info("Loading FAQs from knowledge base...")
    faq_documents = load_faqs_from_json()

    logger.info(f"Loaded {len(faq_documents)} FAQ documents")

    # Use VectorStore service to embed and upsert
    vectorstore = get_vectorstore_service()

    # Prepare documents with proper IDs in metadata
    for i, doc in enumerate(faq_documents):
        if 'id' not in doc.metadata:
            doc.metadata['id'] = i

    # Upsert using service
    logger.info("Uploading FAQ embeddings to Pinecone...")
    count = vectorstore.upsert_documents(faq_documents, id_prefix="faq")

    logger.info("✅ FAQ embeddings uploaded successfully")

    return count


def verify_upload(index, expected_count):
    """Verify that FAQs were uploaded correctly."""
    import time

    logger.info("Verifying upload...")

    time.sleep(2)  # Give Pinecone a moment to update stats

    stats = index.describe_index_stats()
    total_vectors = stats.get('total_vector_count', 0)

    logger.info(f"Index now contains {total_vectors} vectors")

    if total_vectors >= expected_count:
        logger.info("✅ Verification successful!")
        return True
    else:
        logger.warning(f"⚠️  Expected at least {expected_count} vectors, found {total_vectors}")
        return False


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("  CLINIC FAQ VECTOR STORE INITIALIZATION")
    print("="*80 + "\n")
    
    try:
        # Step 1: Initialize Pinecone
        index = initialize_pinecone_index()
        
        # Step 2: Clear existing FAQs (optional)
        clear_existing_faqs(index)
        
        # Step 3: Load and embed FAQs
        faq_count = load_and_embed_faqs(index)
        
        # Step 4: Verify upload
        verify_upload(index, faq_count)
        
        print("\n" + "="*80)
        print("  ✅ FAQ INITIALIZATION COMPLETE!")
        print("="*80)
        print(f"\n  {faq_count} FAQs have been loaded into the vector store.")
        print("  Your clinic chatbot is ready to answer questions!\n")
        
    except Exception as e:
        logger.exception("❌ Error during FAQ initialization")
        print(f"\n❌ Initialization failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

