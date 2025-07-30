#!/usr/bin/env python3
"""
API routes for MAXINE.
"""
from typing import Dict, Any


def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "message": "MAXINE API",
        "docs": "/docs",
        "agent_endpoint": "/agent",
        "playground": "/agent/playground",
    }


def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Export the route functions
__all__ = [
    "root",
    "health_check",
]
