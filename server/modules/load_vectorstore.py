import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings
from services.vectorstore_service import get_vectorstore_service
from logger import logger

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def load_vectorstore(uploaded_files):
    """
    Load PDF files into vector store.

    Args:
        uploaded_files: List of uploaded files

    Returns:
        Number of chunks added to vectorstore
    """
    file_paths = []

    # 1. Save uploaded files
    for file in uploaded_files:
        save_path = Path(settings.UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))
        logger.info(f"Saved file: {file.filename}")

    # 2. Process and split PDFs
    all_chunks = []
    for path in file_paths:
        logger.info(f"Processing {path}...")
        loader = PyPDFLoader(path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        chunks = splitter.split_documents(documents)

        # Add source to metadata
        for chunk in chunks:
            chunk.metadata["source"] = str(path)

        all_chunks.extend(chunks)
        logger.info(f"Split into {len(chunks)} chunks")

    logger.info(f"Total chunks to embed: {len(all_chunks)}")

    # 3. Use VectorStore service to embed and upsert
    vectorstore = get_vectorstore_service()
    count = vectorstore.upsert_documents(all_chunks, id_prefix="pdf")

    logger.info(f"✅ Successfully uploaded {count} chunks to vectorstore")
    return count