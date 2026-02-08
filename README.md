# Aaran's Digital Twin MVP

A personal AI assistant that answers questions as me. My twin is powered by RAG and real-time Google Calendar integration.

**Live Demo:** https://digital-twin-indol-ten.vercel.app

---

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python, Pydantic
- **Vector DB:** ChromaDB with OpenAI Embeddings
- **LLM:** GPT-4o-mini
- **Auth:** Google OAuth 2.0
- **Deployment:** Vercel (frontend) + Render (backend)

---

## Quick Start (Local Development)

### 1. Clone & Setup Backend

```bash
cd digital-twin/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements.txt
pip install -r requirements.txt
```

### 2. Create `.env` file in `backend/`

```env
OPENAI_API_KEY=openai-key

# For Google Calendar integration
GOOGLE_CLIENT_ID=google-client-id
GOOGLE_CLIENT_SECRET=google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 3. Run Backend

```bash
cd digital-twin/backend
python main.py
```
Backend runs at http://localhost:8000

### 4. Setup & Start Frontend

```bash
cd digital-twin/frontend
npm install
npm run dev
```
Frontend runs at http://localhost:3000

---

## Data Ingestion

To update the knowledge base (if slides/data is edited):

```bash
cd digital-twin
source venv/bin/activate
python scripts/ingest_data.py --slides
```

---

## Features

- **RAG Pipeline**: Answers grounded in personal documents + slides
- **Real-Time Calendar**: Live data integration from Google Calendar
- **Source Attribution**: Shows which documents informed each response
- **Privacy Controls**: Hides events after 5 PM, declines personal questions
- **Conversation History**: Context retention per session

---

## Design Doc

See [DESIGN_DOC.md](./DESIGN_DOC.md) for design decisions and tradeoffs.