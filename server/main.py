from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exceptions_middleware
from routes.ask_question import router as ask_router
from routes.groq_stream import router as groq_stream_router
from config import settings

app=FastAPI(
    title="Clinic FAQ Chatbot API",
    description="AI-powered chatbot for aesthetic clinic patient questions",
    version="1.0.0"
)

# CORS Setup with configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# middleware exception handlers
app.middleware("http")(catch_exceptions_middleware)

# routers

# 1. FAQ question answering (RAG-based)
app.include_router(ask_router)
# 2. Streaming chat (conversational)
app.include_router(groq_stream_router)