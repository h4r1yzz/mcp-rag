import os
import time
from pathlib import Path
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

UPLOAD_DIR = "./uploaded.docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_ENV,
)
existing_index = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_index:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=spec,
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)
    print(f"Index {PINECONE_INDEX_NAME} is ready")
else:
    print(f"Using existing index: {PINECONE_INDEX_NAME}")

index = pc.Index(PINECONE_INDEX_NAME)

# load, split, embed and upsert pdf docs content

def load_vectorstore(uploaded_files):
    embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    file_paths = []

    # 1. upload
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    # 2. split
    for path in file_paths:
        loader = PyPDFLoader(path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        text = [chunk.page_content for chunk in chunks]
        # Add text content to metadata so it can be retrieved later
        metadatas = []
        for chunk in chunks:
            metadata = chunk.metadata.copy()
            metadata["text"] = chunk.page_content  # Store the text content in metadata
            metadata["source"] = str(path)  # Ensure source is stored
            metadatas.append(metadata)
        ids = [f"{Path(path).stem}-{i}" for i in range(len(chunks))]

        # 3. embed
        print("Embedding chunks")
        embeddings = embed_model.embed_documents(text)

        # 4. upsert
        print("📤 Uploading to Pinecone...")
        with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
            # Format: list of tuples (id, vector, metadata)
            vectors_to_upsert = [
                (id_val, embedding, metadata)
                for id_val, embedding, metadata in zip(ids, embeddings, metadatas)
            ]
            index.upsert(vectors=vectors_to_upsert)
            progress.update(len(embeddings))

        print(f"✅ Upload complete for {path}")