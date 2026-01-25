from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import uuid
from src.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)
from src.database.connection import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Todo AI Chatbot MCP Tools", version="1.0.0")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler to return consistent error format
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "message": exc.detail}
    )

# Handle validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "data": None, "message": f"Validation error: {exc}"}
    )


@app.on_event("startup")
def startup_event():
    """Initialize the database when the application starts."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.post("/api/mcp/add_task")
def add_task_api(arguments: Dict[str, Any]):
    """
    API endpoint for the add_task MCP tool.

    Args:
        arguments: Dictionary containing task properties

    Returns:
        Dictionary with success status and task data
    """
    try:
        logger.info(f"Executing add_task with arguments: {arguments}")
        result = add_task_tool(arguments)
        logger.info("add_task executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in add_task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@app.post("/api/mcp/list_tasks")
def list_tasks_api(arguments: Dict[str, Any]):
    """
    API endpoint for the list_tasks MCP tool.

    Args:
        arguments: Dictionary containing optional status filter

    Returns:
        Dictionary with success status and list of tasks
    """
    try:
        logger.info(f"Executing list_tasks with arguments: {arguments}")
        result = list_tasks_tool(arguments)
        logger.info("list_tasks executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in list_tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tasks: {str(e)}"
        )


@app.post("/api/mcp/complete_task")
def complete_task_api(arguments: Dict[str, Any]):
    """
    API endpoint for the complete_task MCP tool.

    Args:
        arguments: Dictionary containing task ID

    Returns:
        Dictionary with success status and updated task
    """
    try:
        logger.info(f"Executing complete_task with arguments: {arguments}")
        result = complete_task_tool(arguments)
        logger.info("complete_task executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in complete_task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing task: {str(e)}"
        )


@app.post("/api/mcp/delete_task")
def delete_task_api(arguments: Dict[str, Any]):
    """
    API endpoint for the delete_task MCP tool.

    Args:
        arguments: Dictionary containing task ID

    Returns:
        Dictionary with success status and deleted task ID
    """
    try:
        logger.info(f"Executing delete_task with arguments: {arguments}")
        result = delete_task_tool(arguments)
        logger.info("delete_task executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in delete_task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        )


@app.post("/api/mcp/update_task")
def update_task_api(arguments: Dict[str, Any]):
    """
    API endpoint for the update_task MCP tool.

    Args:
        arguments: Dictionary containing task ID and properties to update

    Returns:
        Dictionary with success status and updated task
    """
    try:
        logger.info(f"Executing update_task with arguments: {arguments}")
        result = update_task_tool(arguments)
        logger.info("update_task executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in update_task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}"
        )


@app.get("/api/mcp/health")
def health_check():
    """
    Health check endpoint to verify the MCP tools API is running.

    Returns:
        Dictionary with health status
    """
    return {
        "success": True,
        "data": {"status": "healthy", "service": "Todo AI Chatbot MCP Tools"},
        "message": "MCP tools API is running"
    }


if __name__ == "__main__":
    import uvicorn
    # Run the server using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")