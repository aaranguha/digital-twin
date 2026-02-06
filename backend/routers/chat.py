"""
Chat Endpoint - The API that the frontend will call.

When a user sends a message, this endpoint:
1. Receives the question
2. Passes it to the ContextEngine (RAG)
3. Returns the response to the frontend
"""

from fastapi import APIRouter
from pydantic import BaseModel

#Import context engine
from engines.context_engine import ContextEngine

#Create router
router = APIRouter(prefix="/api")

#Initialize the context engine once when the server starts to avoid re-connecting to ChromaDB on every request.
engine = ContextEngine()

class HistoryMessage(BaseModel):
    #Keep Message history
    role: str      # 'user' or 'twin'
    content: str   # The message text


class ChatRequest(BaseModel):
    """
    Defines what the frontend must send us.

    Example valid request body:
        {"query": "What's your background?", "history": []}
    """
    query: str
    history: list[HistoryMessage] = []  #Previous messages


class ChatResponse(BaseModel):
    """
    Defines what we send back to the frontend.

    Having a response model:
    - Documents the API clearly
    - Ensures consistent response format
    - Shows up in auto-generated API docs
    """
    response: str       #Generated answer
    sources: list[str]  # Which documents were used


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint.

    POST /api/chat
    Body: {"query": "your question here"}
    Returns: {"response": "answer", "sources": ["file1.md", "file2.md"]}

    When Endpoint is called:
    1. FastAPI validates the request body against ChatRequest
    2. Query passed to ContextEngine
    3. ContextEngine retrieves relevant docs from ChromaDB
    4. ContextEngine sends docs + query to GPT-4o-mini
    5. Return Response 
    """

    # Convert history to simple list of dicts for the engine
    history = [{"role": msg.role, "content": msg.content} for msg in req.history]

    # Call the context engine's ask() method for RAG
    result = engine.ask(req.query, history=history)

    # Return the response
    return ChatResponse(
        response=result["response"],
        sources=result["sources"]
    )