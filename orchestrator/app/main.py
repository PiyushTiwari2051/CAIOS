from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .core.database import init_db
from .routers import (
    context_router,
    suggest_router,
    execute_router,
    actions_router,
    control_router,
    causal_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db()
    yield

app = FastAPI(
    title="CAIOS Causal-Adaptive Intelligence OS",
    description="Causal-Adaptive Intelligence OS — Causal Graph Modeling, 4-Step DoWhy Pipeline & Adaptive Control",
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for localhost dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Sub-Routers
app.include_router(context_router)
app.include_router(suggest_router)
app.include_router(execute_router)
app.include_router(actions_router)
app.include_router(control_router)
app.include_router(causal_router)

@app.get("/")
async def root():
    return {
        "name": "CAIOS Causal-Adaptive Intelligence OS",
        "version": settings.VERSION,
        "status": "online",
        "causal_engine": "active",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
