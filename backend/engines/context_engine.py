#Context Engine - RAG-based question answering

import os
from pathlib import Path
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from engines.mood_engine import MoodEngine

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"


class ContextEngine:
    """
    RAG Engine: Query → Embed → Search ChromaDB → Build prompt → GPT → Response
    """

    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.chroma_client.get_collection(
            name="profile",
            embedding_function=self.embedding_fn
        )
        self.mood_engine = MoodEngine()

    def retrieve(self, query: str, n_results: int = 3) -> list[dict]:
        #Use Vector Search to find relevant documents in ChromaDB based on query
        results = self.collection.query(query_texts=[query], n_results=n_results)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            retrieved.append({
                "content": doc,
                "source": meta.get("source", "unknown"),
                "score": dist  #Lower = better match
            })
        return retrieved

    def generate_response(self, query: str, context_docs: list[dict], history: list[dict] = None) -> dict:
        #Generate response using GPT API with retrieved context and calendar status
        mood_status = self.mood_engine.get_status()

        #Build calendar context
        calendar_context = f"""[CURRENT STATUS - LIVE FROM GOOGLE CALENDAR]
- Currently in a meeting: {"YES" if mood_status.get("in_meeting") else "NO"}
- Availability: {mood_status.get("availability", "unknown")}
- Meetings remaining today: {mood_status.get("meetings_remaining", 0)}
- Total meetings today: {mood_status.get("meeting_count", 0)}
- Energy level: {mood_status.get("energy_estimate", "unknown")}
- Best time to reach: {mood_status.get("suggested_wait_time", "unknown")}
- Summary: {mood_status.get("context_summary", "")}"""

        #Document context
        context_parts = [f"[Source: {doc['source']}]\n{doc['content']}" for doc in context_docs]
        context_string = calendar_context + "\n\n---\n\n" + "\n\n---\n\n".join(context_parts)

        system_prompt = """You are Aaran's digital twin - an AI that represents Aaran in professional contexts.

Your role is to:
1. Answer questions about Aaran's background, experience, projects, and interests
2. Answer questions about Aaran's current availability using the LIVE calendar data provided
3. Speak in FIRST PERSON as if you ARE Aaran (use "I", "my", "me")
4. Be conversational, friendly, and authentic
5. Use the provided context - don't make things up

You have access to:
- Aaran's profile documents (resume, bio, projects, interests, work style)
- LIVE Google Calendar data (current meeting status, today's schedule)

PRIVACY RULES (strictly enforced):
- Only share PROFESSIONAL/WORK information (9 AM - 5 PM weekdays)
- NEVER share personal plans: weekends, evenings, vacations, personal appointments
- If asked about personal time (weekends, after-hours, personal plans), respond:
  "I'm only able to share professional availability and work-related information. For personal matters, please reach out to Aaran directly."
- This protects Aaran's privacy while still being helpful for professional contexts

When asked about availability or meetings, use the calendar data to give accurate, real-time answers.
Keep responses concise but informative (2-4 sentences for simple questions, more for complex ones)."""

        user_prompt = f"""Here is context about Aaran:

{context_string}

---

Question: {query}

Answer as Aaran (first person):"""

        #Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        #Conversation history
        if history:
            for msg in history:
                role = "assistant" if msg["role"] == "twin" else "user"
                messages.append({"role": role, "content": msg["content"]})

        messages.append({"role": "user", "content": user_prompt})

        #Call GPT
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return {
            "response": response.choices[0].message.content,
            "sources": [doc["source"] for doc in context_docs]
        }

    def ask(self, query: str, history: list[dict] = None) -> dict:
        """Main entry point: ask a question, get an answer."""
        if history is None:
            history = []

        context_docs = self.retrieve(query, n_results=3)
        return self.generate_response(query, context_docs, history)
