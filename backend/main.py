"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from services.database import init_db
from api.chat import router as chat_router
from api.conversations import router as conversations_router
from api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    print("✅ Database initialized")
    print("🚀 Multi-Agent AI System ready!")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="Multi-Agent AI System",
    description="AI-powered multi-agent platform with streaming responses",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "name": "Multi-Agent AI System",
        "version": "1.0.0",
        "docs": "/docs",
        "agents": ["planner", "coder", "writer", "researcher", "reviewer"]
    }
