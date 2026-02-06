# Entry Point for the Backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, chat, auth, status

app = FastAPI(title="Aaran Digital Twin - Backend")

# CORS Configuration
# Allows frontend (port 3000) to call backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://digital-twin-indol-ten.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(health.router)    # GET /api/health
app.include_router(chat.router)      # POST /api/chat
app.include_router(auth.router)      # GET /auth/login, /auth/callback, /auth/status
app.include_router(status.router)    # GET /api/status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
