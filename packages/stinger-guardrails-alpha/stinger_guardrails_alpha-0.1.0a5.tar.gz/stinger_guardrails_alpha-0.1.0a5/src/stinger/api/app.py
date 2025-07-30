"""
FastAPI application for Stinger API service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stinger.api.endpoints import check, health, rules

# Create FastAPI app
app = FastAPI(
    title="Stinger Guardrails API",
    description="REST API for Stinger Guardrails Framework",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for browser extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "moz-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(check.router, prefix="/v1", tags=["guardrails"])
app.include_router(rules.router, prefix="/v1", tags=["configuration"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Stinger Guardrails API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
