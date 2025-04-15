"""
Main API router for the Intelligent Multi-Agent Email Automation System.
This file imports and includes all the individual router modules.
"""

from fastapi import APIRouter
from .routers import ingestion, classification, summarization, response, integration

# Create main API router
api_router = APIRouter()

# Include all the individual routers
api_router.include_router(ingestion.router)
api_router.include_router(classification.router)
api_router.include_router(summarization.router)
api_router.include_router(response.router)
api_router.include_router(integration.router)
