from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    auth,
    crops,
    daily_logs,
    todos,
    sales,
    chat,
    weather,
    consumer_prices,
    streaming_auth,
    farmer_profile,
    gemini_live,
    schemes,
    disease_research,
    business_intelligence,
    reports,
)
from .config.database import create_tables
from .config.settings import settings

# Create database tables
create_tables()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered farming assistant for Karnataka farmers",
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(streaming_auth.router)
app.include_router(crops.router)
app.include_router(daily_logs.router)
app.include_router(todos.router)
app.include_router(sales.router)
app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(consumer_prices.router)
app.include_router(farmer_profile.router)
app.include_router(gemini_live.router)
app.include_router(schemes.router)
app.include_router(disease_research.router)
app.include_router(business_intelligence.router)
app.include_router(reports.router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}
