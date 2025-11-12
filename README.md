# AI Medical Clinic Assistant - RAG Chatbot

A full-stack AI-powered chatbot application for medical clinic FAQs, built with **Retrieval-Augmented Generation (RAG)** using LangChain, Pinecone, and Groq LLM. Features a modern Next.js frontend with real-time streaming responses and conversation management.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Knowledge Base](#-knowledge-base)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### Backend (FastAPI + RAG)
- 🤖 **Retrieval-Augmented Generation (RAG)** - Accurate answers from clinic FAQ knowledge base
- 🔍 **Semantic Search** - Pinecone vector database with Google Generative AI embeddings
- 💬 **Streaming Responses** - Real-time LLM responses using Groq's Llama 3.3 70B
- 🛡️ **Robust Error Handling** - Comprehensive exception handling and logging
- ⚡ **Optimized Performance** - Singleton services, connection pooling, and caching

### Frontend (Next.js + React)
- 💬 **Multi-Conversation Management** - Create, switch, and manage multiple chat conversations
- 📌 **Pin Important Chats** - Pin frequently used conversations for quick access
- 🔄 **Auto-Save Conversations** - Automatic persistence to localStorage
- 🎨 **Modern UI/UX** - Clean, responsive design with dark/light theme support
- ⚡ **Real-time Streaming** - Live streaming of AI responses with typing indicators
- 🔐 **Authentication** - Clerk integration for user authentication
- 🔍 **Search Functionality** - Search through conversation history

---

## 🎥 Demo

### Chat Interface
- Auto-created chat on first load
- Real-time streaming responses
- Conversation history in sidebar
- Pin/unpin conversations
- Dark/light theme toggle

### Key Capabilities
- Answer clinic-specific questions (hours, pricing, services)
- Provide accurate information from FAQ knowledge base
- Handle follow-up questions with context
- Stream responses in real-time

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js UI    │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/SSE
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌─────┐  ┌──────┐  ┌──────┐
│Pinecone│ │Groq │  │Google│  │ FAQ  │
│Vector  │ │ LLM │  │Embed │  │ JSON │
│  DB    │ │     │  │      │  │      │
└────────┘ └─────┘  └──────┘  └──────┘
```

**RAG Pipeline:**
1. User query → Embedded using Google Generative AI
2. Semantic search in Pinecone vector database
3. Top-K relevant FAQ chunks retrieved
4. Context + Query sent to Groq LLM (Llama 3.3 70B)
5. Streaming response back to frontend

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **LLM:** Groq (Llama 3.3 70B Versatile)
- **Embeddings:** Google Generative AI (models/embedding-001, 768 dimensions)
- **Vector Database:** Pinecone (serverless)
- **RAG Framework:** LangChain
- **Configuration:** Pydantic Settings
- **Logging:** Loguru

### Frontend
- **Framework:** Next.js 15.2 (React 19)
- **Language:** TypeScript
- **Styling:** Tailwind CSS 4
- **Animations:** Framer Motion
- **Authentication:** Clerk
- **Icons:** Lucide React
- **HTTP Client:** Fetch API with SSE support

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python:** 3.11 or higher ([Download](https://www.python.org/downloads/))
- **Node.js:** 18.0 or higher ([Download](https://nodejs.org/))
- **npm/pnpm:** Latest version (pnpm recommended)
- **Git:** For cloning the repository

### Required API Keys
You'll need to sign up for the following services (all have free tiers):

1. **Google AI Studio** (for embeddings)
   - Sign up: https://makersuite.google.com/app/apikey
   - Get your API key from the dashboard

2. **Groq** (for LLM)
   - Sign up: https://console.groq.com/
   - Create an API key in the dashboard

3. **Pinecone** (for vector database)
   - Sign up: https://www.pinecone.io/
   - Note your API key and environment

4. **Clerk** (optional, for authentication)
   - Sign up: https://clerk.com/
   - Create a new application
   - Get your publishable and secret keys

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mcp-rag-chatbot.git
cd mcp-rag-chatbot
```

### 2. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# using uv:
uv pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd client/mcp_rag

# Install dependencies using pnpm
pnpm install

```

---

## ⚙️ Configuration

### 1. Backend Environment Variables

Create a `.env` file in the `server/` directory:

```bash
cd server
cp .env.example .env
```

Edit `server/.env` with your API keys:

```env
# Required API Keys
GOOGLE_API_KEY=your_google_ai_studio_api_key_here
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Pinecone Configuration
PINECONE_INDEX_NAME=clinic-faqs
PINECONE_ENV=us-east-1

# Optional: Model Configuration (defaults shown)
# EMBEDDING_MODEL=models/embedding-001
# EMBEDDING_DIMENSION=768
# LLM_MODEL=llama-3.3-70b-versatile
# CHUNK_SIZE=500
# CHUNK_OVERLAP=100
```

### 2. Frontend Environment Variables (Optional)

If using Clerk authentication, create `client/mcp_rag/.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

---

## 🏃 Running the Application

### Development Mode

You'll need **two terminal windows** - one for backend, one for frontend.

#### Terminal 1: Start Backend Server

```bash
cd server

# Activate virtual environment if not already activated
source venv/bin/activate  # macOS/Linux

# Start FastAPI server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Backend will be available at: **http://localhost:8000**

#### Terminal 2: Start Frontend Server

```bash
cd client/mcp_rag

# Start Next.js development server
pnpm dev
```

**Expected output:**
```
  ▲ Next.js 15.2.4
  - Local:        http://localhost:3000
  - Turbopack:    enabled

 ✓ Ready in 2.5s
```

Frontend will be available at: **http://localhost:3000**



---

## 📁 Project Structure

```
mcp-rag-chatbot/
├── server/                          # Backend (FastAPI)
│   ├── config.py                    # Centralized configuration (Pydantic)
│   ├── main.py                      # FastAPI application entry point
│   ├── logger.py                    # Logging configuration
│   ├── prompts.py                   # LLM prompt templates
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment variables template
│   │
│   ├── data/
│   │   └── clinic_faqs.json         # FAQ knowledge base
│   │
│   ├── services/
│   │   ├── vectorstore_service.py   # Pinecone vector store
│   │   └── llm_service.py           # LLM service factory
│   │
│   ├── routes/
│   │   ├── ask_question.py          # POST /ask/ - RAG query endpoint
│   │   └── groq_stream.py           # POST /groq_stream/ - Streaming endpoint
│   │
│   ├── modules/
│   │   ├── faq_loader.py            # Load FAQs from JSON
│   │   ├── query_handlers.py        # Query processing logic
│   │   └── load_vectorstore.py      # Vector store initialization
│   │
│   ├── middlewares/
│   │   └── exception_handlers.py    # Global exception handling
│   │
│   └── tests/
│       ├── test_rag_retrieval.py    # RAG system tests
│       └── test_results.json        # Test results
│
├── client/mcp_rag/                  # Frontend (Next.js)
│   ├── app/
│   │   ├── layout.tsx               # Root layout with Clerk provider
│   │   ├── page.tsx                 # Home page
│   │   └── globals.css              # Global styles
│   │
│   ├── components/
│   │   ├── AIAssistantUI.jsx        # Main chat interface
│   │   ├── Sidebar.jsx              # Conversation sidebar
│   │   ├── ChatPane.jsx             # Chat message display
│   │   ├── Composer.jsx             # Message input component
│   │   ├── Message.jsx              # Individual message component
│   │   ├── ConversationRow.jsx      # Sidebar conversation item
│   │   ├── Header.jsx               # Chat header
│   │   ├── SearchModal.jsx          # Search conversations
│   │   ├── SettingsPopover.jsx      # Settings menu
│   │   └── ThemeToggle.jsx          # Dark/light theme toggle
│   │
│   ├── lib/
│   │   └── api.ts                   # API client functions
│   │
│   ├── package.json                 # Node.js dependencies
│   └── next.config.ts               # Next.js configuration
│
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

---

## 📚 Knowledge Base

### FAQ Structure

The knowledge base is stored in `server/data/clinic_faqs.json` with the following structure:

```json
{
  "faqs": [
    {
      "id": "faq_001",
      "question": "What are your operating hours?",
      "answer": "Our clinic is open Monday through Friday...",
      "category": "General Information",
      "tags": ["hours", "schedule", "availability"]
    }
  ]
}
```


### Current FAQ Categories

- **General Information** - Hours, location, contact
- **Appointments** - Booking, walk-ins, scheduling
- **Billing & Payment** - Payment methods, financing
- **Facilities** - Parking, accessibility
- **Treatments** - Laser hair removal, Botox, etc.
- **Safety & Credentials** - Certifications, safety
- **Consultations** - Free consultations, assessments
- **First Visit** - Preparation, what to bring
- **Policies** - Cancellation, rescheduling

### Embedding Strategy

Each FAQ is embedded as a complete unit:
```
Question: {question}
Answer: {answer}
Category: {category}
```

This ensures:
- Complete context in each chunk
- High retrieval accuracy
- Relevant answers to user queries

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Problem:** Python dependencies not installed

**Solution:**
```bash
cd server
pip install -r requirements.txt
```

#### 2. "GOOGLE_API_KEY not found"

**Problem:** Environment variables not set

**Solution:**
```bash
# Check if .env file exists
ls server/.env

# If not, create it from template
cp server/.env.example server/.env

# Edit with your API keys
nano server/.env
```



#### 4. Frontend can't connect to backend

**Problem:** CORS or backend not running

**Solution:**
```bash
# Check backend is running on port 8000
curl http://localhost:8000

# Check CORS settings in server/config.py
# Ensure http://localhost:3000 is in CORS_ORIGINS
```

#### 5. "Rate limit exceeded" errors

**Problem:** API rate limits hit

**Solution:**
- Wait a few minutes before retrying
- Check your API quotas in respective dashboards
- Consider upgrading to paid tiers for higher limits

#### 6. Conversations not persisting

**Problem:** localStorage not working

**Solution:**
- Check browser console for errors
- Clear browser cache and reload
- Ensure localStorage is enabled in browser settings

---
