"""
Main application file for the Intelligent Multi-Agent Email Automation System.
This file initializes the FastAPI application with all routes and middleware.
"""

import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Import configuration
from .config import config

# Import database and cache
from .database import db
from .cache import cache

# Import authentication
from .auth import (
    Token, User, authenticate_user, create_access_token,
    get_current_active_user, has_role, ACCESS_TOKEN_EXPIRE_MINUTES,
    fake_users_db
)

# Import API router
from .api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get("logging.level", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.get("logging.file", None)
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Intelligent Multi-Agent Email Automation System",
    description="A comprehensive platform that automates email management through multiple specialized agents.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("api.cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for authentication.
    
    This endpoint authenticates a user and returns a JWT token for API access.
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "roles": user.roles},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get information about the current authenticated user.
    """
    return current_user

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "message": "Welcome to the Intelligent Multi-Agent Email Automation System API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    # Check database connection
    db_status = "healthy" if await db.connect() else "unhealthy"
    
    # Check cache connection
    cache_status = "healthy" if cache.connect() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy",
        "database": db_status,
        "cache": cache_status,
        "api": "healthy"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    
    This function is called when the application starts up.
    It initializes database and cache connections.
    """
    logger.info("Starting up the Intelligent Multi-Agent Email Automation System")
    
    # Connect to database
    db_connected = await db.connect()
    if db_connected:
        logger.info("Successfully connected to database")
    else:
        logger.warning("Failed to connect to database")
    
    # Connect to cache
    cache_connected = cache.connect()
    if cache_connected:
        logger.info("Successfully connected to cache")
    else:
        logger.warning("Failed to connect to cache")
    
    logger.info("Startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    
    This function is called when the application shuts down.
    It closes database and cache connections.
    """
    logger.info("Shutting down the Intelligent Multi-Agent Email Automation System")
    
    # Close database connection
    await db.close()
    logger.info("Closed database connection")
    
    # Close cache connection
    cache.close()
    logger.info("Closed cache connection")
    
    logger.info("Shutdown complete")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    host = config.get("api.host", "0.0.0.0")
    port = config.get("api.port", 8000)
    debug = config.get("api.debug", False)
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
