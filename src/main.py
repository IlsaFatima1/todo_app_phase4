"""
Main entry point for the Todo AI Chatbot MCP Tools server.
This extends the existing backend with MCP tool endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import the MCP tools router
from src.mcp_server import app as mcp_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the main application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Todo AI Chatbot MCP Tools server...")
    # Startup events
    yield
    # Shutdown events
    logger.info("Shutting down Todo AI Chatbot MCP Tools server...")

# Main application
main_app = FastAPI(
    title="Todo AI Chatbot MCP Tools API",
    description="API endpoints for MCP tools that enable AI agents to manage tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the MCP tools routes
# Mount the routes under the /api/mcp prefix
main_app.include_router(mcp_app.routes[0].router, prefix="/api/mcp") if hasattr(mcp_app, 'routes') else None

# Alternative: Add the routes directly to the main app
# Add the routes from mcp_server to the main app
for route in mcp_app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        # Copy the route to the main app
        main_app.router.routes.append(route)

# If we're running this as the main module, start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:main_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )