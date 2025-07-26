#!/usr/bin/env python3
"""
Namma Krushi - AI-powered farming assistant for Karnataka farmers.
Main entry point for the application.
"""

import uvicorn


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
