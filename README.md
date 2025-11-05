# MCP RAG Server

## Environment Variables
Create a `.env` file in the project root with the following keys:

```env
GOOGLE_API_KEY=your-google-genai-key
GROQ_API_KEY=your-groq-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENV=us-east-1
PINECONE_INDEX_NAME=yourindexname
```

The server validates these at startup. You can also export them in your shell instead of using `.env`.

to test the api 
uvicorn main:app --reload