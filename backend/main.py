from fastapi import FastAPI, HTTPException, status, Depends, Form, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime
from sqlmodel import select
from dotenv import load_dotenv
load_dotenv()



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend.models.todo import TodoCreate, TodoUpdate, TodoComplete, TodoRead
from backend.models.user import UserCreate, User
from schemas import Todo
from database import get_session
from crud import get_todos, create_todo, update_todo, delete_todo, complete_todo
from user_service import create_user, authenticate_user
from auth import get_current_user_id, create_access_token
from sqlmodel import Session

# Import MCP tools - adjust paths since we're running from backend directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # Add parent directory to path

# Import backend models and database for consistency
from models import Todo
from database import init_db as init_backend_db

from src.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

# Import AI Agent (optional - graceful handling if agents module is missing)
try:
    from src.agents.todo_agent import TodoAgent
except ImportError as e:
    print(f"Warning: Could not import TodoAgent: {e}")
    print("AI agent functionality will be disabled.")
    TodoAgent = None

# Import Context7 configuration
from config.context7_config import CTX7_CONFIG
import httpx
import asyncio
from typing import Dict, Any, Optional

# Global AI agent instance (without default user ID initially)
todo_agent: Optional[TodoAgent] = None


# Initialize the AI agent if the module is available
if TodoAgent is not None:
    try:
        todo_agent = TodoAgent()
    except Exception as e:
        print(f"Warning: Could not initialize TodoAgent: {e}")
        print("AI agent functionality will be disabled.")
        todo_agent = None

app = FastAPI(title="Todo API", version="1.0.0")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global HTTP client for Context7 connections
ctx7_client: Optional[httpx.AsyncClient] = None


@app.on_event("startup")
def startup_event():
    """Initialize the database, Context7 connection, and AI agent when the application starts."""
    global ctx7_client, todo_agent

    logger.info("Initializing database for MCP tools...")
    init_backend_db()  # Use backend database initialization
    logger.info("Database initialized successfully for MCP tools")

    # Initialize Context7 client
    logger.info("Initializing Context7 connection...")
    ctx7_client = httpx.AsyncClient(
        base_url=CTX7_CONFIG.CTX7_MCP_ENDPOINT,
        headers=CTX7_CONFIG.get_headers(),
        timeout=CTX7_CONFIG.CTX7_TIMEOUT
    )
    logger.info("Context7 connection initialized successfully")

    # Initialize AI agent
    if TodoAgent is not None:
        logger.info("Initializing AI agent...")
        try:
            todo_agent = TodoAgent(default_user_id=None)  # No default user for global instance
            logger.info("AI agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {str(e)}")
            logger.warning("AI agent functionality will be disabled.")
            todo_agent = None
    else:
        logger.warning("AI agent module not available. AI agent functionality will be disabled.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources when the application shuts down."""
    global ctx7_client

    logger.info("Shutting down Context7 connection...")
    if ctx7_client:
        await ctx7_client.aclose()
        ctx7_client = None
    logger.info("Context7 connection closed successfully")


async def connect_to_ctx7(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connect to Context7 API and execute MCP tool.

    Args:
        tool_name: Name of the MCP tool to execute
        arguments: Arguments for the tool

    Returns:
        Response from Context7 API
    """
    global ctx7_client

    if not ctx7_client:
        logger.error("Context7 client not initialized")
        return {
            "success": False,
            "data": None,
            "message": "Context7 client not initialized"
        }

    try:
        # Prepare the request payload
        payload = {
            "tool_name": tool_name,
            "arguments": arguments
        }

        logger.info(f"Sending request to Context7 for tool: {tool_name}")

        # Send request to Context7
        response = await ctx7_client.post(
            "/execute",
            json=payload
        )

        # Check if the request was successful
        response.raise_for_status()

        # Return the response
        result = response.json()
        logger.info(f"Successfully executed tool {tool_name} via Context7")
        return result

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error when connecting to Context7: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"HTTP error connecting to Context7: {str(e)}"
        }
    except httpx.RequestError as e:
        logger.error(f"Request error when connecting to Context7: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Request error connecting to Context7: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error when connecting to Context7: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Unexpected error connecting to Context7: {str(e)}"
        }

# Custom exception handler to return consistent error format
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "message": exc.detail}
    )

# Handle validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"data": None, "message": f"Validation error: {exc}"}
    )

@app.get("/api/v1/todos", response_model=dict)
def get_todos_endpoint(
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve all todos for the authenticated user
    """
    try:
        print("DEBUG: GET /api/v1/todos endpoint called", flush=True)
        print(f"DEBUG: Headers received: {[key for key in request.headers.keys()]}", flush=True)  # Need to import Request
        print(f"DEBUG: Origin header: {request.headers.get('origin', 'None')}", flush=True)
        print(f"DEBUG: User agent: {request.headers.get('user-agent', 'None')}", flush=True)
        logger.info(f"Fetching todos for user ID: {current_user_id}")
        todos = get_todos(session, current_user_id)
        print(f"DEBUG: Retrieved {len(todos)} todos from database", flush=True)
        logger.info(f"Retrieved {len(todos)} todos")
        # Convert SQLModel objects to Pydantic schemas using from_attributes
        todos_data = [TodoRead.model_validate(todo) for todo in todos]
        return {"data": todos_data, "message": "Todos retrieved successfully"}
    except Exception as e:
        print(f"DEBUG: Error in GET /api/v1/todos: {str(e)}", flush=True)
        logger.error(f"Error retrieving todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving todos"
        )


@app.post("/api/v1/todos", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_todo_endpoint(
    todo_data: TodoCreate,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Create a new todo for the authenticated user
    """
    try:
        print(f"DEBUG: POST /api/v1/todos endpoint called with data: {todo_data}")
        logger.info(f"Creating new todo with title: {todo_data.title} for user ID: {current_user_id}")
        todo = create_todo(session, todo_data.title, current_user_id, todo_data.description, todo_data.completed)
        print(f"DEBUG: Todo created successfully with ID: {todo.id}")
        logger.info(f"Todo created successfully with ID: {todo.id}")
        # Convert SQLModel object to Pydantic schema
        todo_response = TodoRead(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            user_id=todo.user_id
        )
        return {"data": todo_response, "message": "Todo created successfully"}
    except Exception as e:
        print(f"DEBUG: Error in POST /api/v1/todos: {str(e)}")
        logger.error(f"Error creating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating todo"
        )


@app.get("/api/v1/todos/{todo_id}", response_model=dict)
def get_todo_endpoint(
    todo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific todo by ID for the authenticated user
    """
    from models import Todo
    try:
        print(f"DEBUG: GET /api/v1/todos/{todo_id} endpoint called")
        logger.info(f"Fetching todo with ID: {todo_id} for user ID: {current_user_id}")
        # Get the specific todo by ID
        todo = session.get(Todo, todo_id)
        if not todo or todo.user_id != current_user_id:
            print(f"DEBUG: Todo not found with ID: {todo_id} or not owned by user {current_user_id}")
            logger.warning(f"Todo not found with ID: {todo_id} or not owned by user {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )
        print(f"DEBUG: Todo retrieved successfully with ID: {todo_id}")
        logger.info(f"Todo retrieved successfully with ID: {todo_id}")
        # Convert SQLModel object to Pydantic schema using from_attributes
        todo_data = TodoRead.model_validate(todo)
        return {"data": todo_data, "message": "Todo retrieved successfully"}
    except HTTPException:
        print(f"DEBUG: HTTPException in GET /api/v1/todos/{todo_id}")
        raise
    except Exception as e:
        print(f"DEBUG: Error in GET /api/v1/todos/{todo_id}: {str(e)}")
        logger.error(f"Error retrieving todo {todo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving todo"
        )


@app.put("/api/v1/todos/{todo_id}", response_model=dict)
def update_todo_endpoint(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Update a specific todo by ID for the authenticated user
    """
    try:
        print(f"DEBUG: PUT /api/v1/todos/{todo_id} endpoint called with data: {todo_data}")
        logger.info(f"Updating todo with ID: {todo_id} for user ID: {current_user_id}")
        todo = update_todo(
            session,
            todo_id,
            current_user_id,
            todo_data.title,
            todo_data.description,
            todo_data.completed
        )
        if not todo:
            print(f"DEBUG: Todo not found for update with ID: {todo_id} or not owned by user {current_user_id}")
            logger.warning(f"Todo not found for update with ID: {todo_id} or not owned by user {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )
        print(f"DEBUG: Todo updated successfully with ID: {todo_id}")
        logger.info(f"Todo updated successfully with ID: {todo_id}")
        # Convert SQLModel object to Pydantic schema using from_attributes
        todo_data_response = TodoRead.model_validate(todo)
        return {"data": todo_data_response, "message": "Todo updated successfully"}
    except HTTPException:
        print(f"DEBUG: HTTPException in PUT /api/v1/todos/{todo_id}")
        raise
    except Exception as e:
        print(f"DEBUG: Error in PUT /api/v1/todos/{todo_id}: {str(e)}")
        logger.error(f"Error updating todo {todo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating todo"
        )


@app.delete("/api/v1/todos/{todo_id}", response_model=dict)
def delete_todo_endpoint(
    todo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a specific todo by ID for the authenticated user
    """
    try:
        print(f"DEBUG: DELETE /api/v1/todos/{todo_id} endpoint called")
        logger.info(f"Deleting todo with ID: {todo_id} for user ID: {current_user_id}")
        success = delete_todo(session, todo_id, current_user_id)
        if not success:
            print(f"DEBUG: Todo not found for deletion with ID: {todo_id} or not owned by user {current_user_id}")
            logger.warning(f"Todo not found for deletion with ID: {todo_id} or not owned by user {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )
        print(f"DEBUG: Todo deleted successfully with ID: {todo_id}")
        logger.info(f"Todo deleted successfully with ID: {todo_id}")
        return {"data": None, "message": "Todo deleted successfully"}
    except HTTPException:
        print(f"DEBUG: HTTPException in DELETE /api/v1/todos/{todo_id}")
        raise
    except Exception as e:
        print(f"DEBUG: Error in DELETE /api/v1/todos/{todo_id}: {str(e)}")
        logger.error(f"Error deleting todo {todo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting todo"
        )


@app.get("/api/v1/health", response_model=dict)
def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {"data": {"status": "healthy", "timestamp": datetime.now()}, "message": "API is running"}


@app.delete("/api/v1/todos", response_model=dict)
def delete_all_todos_endpoint(
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete all todos for the authenticated user - for testing purposes
    """
    try:
        print(f"DEBUG: DELETE /api/v1/todos endpoint called - clearing all todos for user {current_user_id}")
        # Get all todos for the current user and delete them one by one
        all_todos = get_todos(session, current_user_id)
        for todo in all_todos:
            delete_todo(session, todo.id, current_user_id)
        print("DEBUG: All todos cleared from database")
        return {"data": None, "message": "All todos deleted successfully"}
    except Exception as e:
        print(f"DEBUG: Error in DELETE /api/v1/todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting all todos"
        )


@app.post("/api/v1/auth/register", response_model=dict)
def register_user_endpoint(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user with email and password
    """
    try:
        print(f"DEBUG: POST /api/v1/auth/register endpoint called with data: {user_data}")
        logger.info(f"Creating new user with email: {user_data.email}")

        # Validate input data
        print(f"DEBUG: Validating user data - email: {user_data.email}, password length: {len(user_data.password) if user_data.password else 0}")

        # Create the user
        user = create_user(session, user_data)

        print(f"DEBUG: User created successfully with ID: {user.id}")
        logger.info(f"User created successfully with ID: {user.id}")

        # Generate access token for the new user
        access_token = create_access_token(user.id)
        print(f"DEBUG: Generated access token for user ID: {user.id}")

        # Return user data and token
        user_response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

        print(f"DEBUG: Returning registration response for user ID: {user.id}")
        return {
            "data": {
                "user": user_response,
                "access_token": access_token,
                "token_type": "bearer"
            },
            "message": "User registered successfully"
        }
    except ValueError as e:
        print(f"DEBUG: ValueError in POST /api/v1/auth/register: {str(e)}")
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"DEBUG: Error in POST /api/v1/auth/register: {str(e)}")
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@app.post("/api/v1/auth/login", response_model=dict)
def login_user_endpoint(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    """
    Authenticate user with email and password
    """
    try:
        print(f"DEBUG: POST /api/v1/auth/login endpoint called with email: {email}")
        logger.info(f"Login attempt for user with email: {email}")

        # Validate input data
        print(f"DEBUG: Validating login data - email: {email}, password length: {len(password) if password else 0}")

        # Authenticate the user
        user = authenticate_user(session, email, password)

        if not user:
            print(f"DEBUG: Invalid credentials for email: {email}")
            logger.warning(f"Invalid login attempt for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        print(f"DEBUG: User authenticated successfully with ID: {user.id}")
        logger.info(f"User authenticated successfully with ID: {user.id}")

        # Generate access token for the authenticated user
        access_token = create_access_token(user.id)
        print(f"DEBUG: Generated access token for user ID: {user.id}")

        # Return user data and token
        user_response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

        print(f"DEBUG: Returning login response for user ID: {user.id}")
        return {
            "data": {
                "user": user_response,
                "access_token": access_token,
                "token_type": "bearer"
            },
            "message": "Login successful"
        }
    except HTTPException:
        print(f"DEBUG: HTTPException in POST /api/v1/auth/login")
        raise
    except Exception as e:
        print(f"DEBUG: Error in POST /api/v1/auth/login: {str(e)}")
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )


@app.post("/api/v1/auth/update_profile", response_model=dict)
def update_user_profile_endpoint(
    name: str = Form(...),
    email: str = Form(...),
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Update user profile information
    """
    try:
        print(f"DEBUG: POST /api/v1/auth/update_profile endpoint called for user ID: {current_user_id}")
        logger.info(f"Updating profile for user ID: {current_user_id}")

        # Get the user from the database
        user = session.get(User, current_user_id)
        print(f"DEBUG: Retrieved user from database: {user}")
        if not user:
            print(f"DEBUG: User with ID {current_user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if email is already taken by another user
        print(f"DEBUG: Checking for existing user with email: {email}")
        existing_user_query = select(User).where(User.email == email)
        print(f"DEBUG: Executing query: {existing_user_query}")
        existing_user = session.exec(existing_user_query).first()
        print(f"DEBUG: Found existing user: {existing_user}")

        if existing_user and existing_user.id != current_user_id:
            print(f"DEBUG: Email already in use by another user: {existing_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another user"
            )

        # Update user information
        print(f"DEBUG: Updating user info - name: {name}, email: {email}")
        user.name = name
        user.email = email
        user.updated_at = datetime.utcnow()

        # Commit changes to database
        print(f"DEBUG: Adding user to session and committing changes")
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"DEBUG: Changes committed and user refreshed")

        print(f"DEBUG: User profile updated successfully for user ID: {current_user_id}")
        logger.info(f"User profile updated successfully for user ID: {current_user_id}")

        # Return updated user data
        user_response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

        print(f"DEBUG: Returning response with user data")
        return {
            "data": user_response,
            "message": "Profile updated successfully"
        }
    except HTTPException as he:
        print(f"DEBUG: HTTPException in POST /api/v1/auth/update_profile: {he.detail}")
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in POST /api/v1/auth/update_profile: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )


@app.post("/api/v1/auth/update_profile_picture", response_model=dict)
def update_profile_picture_endpoint(
    profile_picture: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Update user profile picture
    """
    try:
        print(f"DEBUG: POST /api/v1/auth/update_profile_picture endpoint called for user ID: {current_user_id}")
        logger.info(f"Updating profile picture for user ID: {current_user_id}")

        # Get the user from the database
        user = session.get(User, current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if profile_picture.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, and GIF are allowed."
            )

        # Create uploads directory if it doesn't exist
        import os
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Limit file size (e.g., 5MB) - read file to check size
        import uuid
        contents = profile_picture.file.read()

        max_size = 5 * 1024 * 1024  # 5MB
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Maximum size is 5MB."
            )

        # Store the file in the uploads directory
        file_extension = profile_picture.filename.split('.')[-1] if profile_picture.filename else 'jpg'
        unique_filename = f"profile_{user.id}_{uuid.uuid4().hex}.{file_extension}"

        # Save the file to disk
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(contents)

        # Update user's profile picture field
        user.profile_picture = unique_filename  # This assumes you have a profile_picture field in your User model
        user.updated_at = datetime.utcnow()

        # Commit changes to database
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"DEBUG: Profile picture updated successfully for user ID: {current_user_id}")
        logger.info(f"Profile picture updated successfully for user ID: {current_user_id}")

        # Return updated user data
        user_response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "profile_picture": user.profile_picture,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

        return {
            "data": user_response,
            "message": "Profile picture updated successfully"
        }
    except HTTPException:
        print(f"DEBUG: HTTPException in POST /api/v1/auth/update_profile_picture")
        raise
    except Exception as e:
        print(f"DEBUG: Error in POST /api/v1/auth/update_profile_picture: {str(e)}")
        logger.error(f"Error updating profile picture: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile picture"
        )


@app.get("/api/user_images/{filename}")
def get_user_image(filename: str):
    """
    Serve user profile pictures
    """
    import os

    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or filename.startswith('.'):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join("uploads", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)


@app.post("/api/v1/auth/logout", response_model=dict)
def logout_user_endpoint(
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Logout the current user (token invalidation can be implemented later)
    """
    try:
        print(f"DEBUG: POST /api/v1/auth/logout endpoint called for user ID: {current_user_id}")
        logger.info(f"User logout for user ID: {current_user_id}")

        # In a real implementation, you might want to invalidate the token here
        print(f"DEBUG: User {current_user_id} logged out successfully")

        return {
            "data": None,
            "message": "Logout successful"
        }
    except Exception as e:
        print(f"DEBUG: Error in POST /api/v1/auth/logout: {str(e)}")
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )


# MCP Tools Endpoints
@app.post("/api/mcp/add_task")
def add_task_mcp(arguments: Dict[str, Any]):
    """
    MCP tool endpoint for creating a new task.

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
def list_tasks_mcp(arguments: Dict[str, Any] = None):
    """
    MCP tool endpoint for listing tasks.

    Args:
        arguments: Dictionary containing optional status filter

    Returns:
        Dictionary with success status and list of tasks
    """
    try:
        arguments = arguments or {}  # Default to empty dict if None
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
def complete_task_mcp(arguments: Dict[str, Any]):
    """
    MCP tool endpoint for completing a task.

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
def delete_task_mcp(arguments: Dict[str, Any]):
    """
    MCP tool endpoint for deleting a task.

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
def update_task_mcp(arguments: Dict[str, Any]):
    """
    MCP tool endpoint for updating a task.

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


@app.get("/api/debug/all_tasks")
def debug_all_tasks(session: Session = Depends(get_session)):
    """
    Debug endpoint to see all tasks in database with their user IDs
    """
    from models import Todo
    from sqlmodel import select

    try:
        todos = session.exec(select(Todo)).all()
        result = []
        for todo in todos:
            result.append({
                "id": todo.id,
                "title": todo.title,
                "user_id": todo.user_id,
                "completed": todo.completed
            })

        return {
            "success": True,
            "data": {
                "tasks": result,
                "count": len(result)
            },
            "message": f"Found {len(result)} total tasks in database"
        }
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"Error: {str(e)}"
        }


@app.get("/api/mcp/health")
def mcp_health_check():
    """
    Health check endpoint for MCP tools.

    Returns:
        Dictionary with health status
    """
    return {
        "success": True,
        "data": {"status": "healthy", "service": "Todo AI Chatbot MCP Tools"},
        "message": "MCP tools API is running"
    }


# Context7 Proxy Endpoints - Allow Context7 to execute our MCP tools
@app.post("/api/ctx7/proxy/{tool_name}")
async def ctx7_proxy_endpoint(tool_name: str, arguments: Dict[str, Any]):
    """
    Proxy endpoint for Context7 to execute our MCP tools.

    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments for the tool

    Returns:
        Result from executing the tool
    """
    logger.info(f"Context7 proxy request for tool: {tool_name}")

    # Validate tool name
    valid_tools = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
    if tool_name not in valid_tools:
        return {
            "success": False,
            "data": None,
            "message": f"Invalid tool name: {tool_name}. Valid tools: {valid_tools}"
        }

    try:
        # Execute the appropriate tool based on the tool name
        if tool_name == "add_task":
            result = add_task_mcp(arguments)
        elif tool_name == "list_tasks":
            result = list_tasks_mcp(arguments)
        elif tool_name == "complete_task":
            result = complete_task_mcp(arguments)
        elif tool_name == "delete_task":
            result = delete_task_mcp(arguments)
        elif tool_name == "update_task":
            result = update_task_mcp(arguments)
        else:
            return {
                "success": False,
                "data": None,
                "message": f"Tool not implemented: {tool_name}"
            }

        logger.info(f"Successfully executed {tool_name} via Context7 proxy")
        return result

    except Exception as e:
        logger.error(f"Error executing {tool_name} via Context7 proxy: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"Error executing tool {tool_name}: {str(e)}"
        }


@app.get("/api/ctx7/health")
async def ctx7_health_check():
    """
    Health check endpoint for Context7 connection.

    Returns:
        Dictionary with Context7 connection health status
    """
    is_connected = CTX7_CONFIG.validate_config()

    return {
        "success": True,
        "data": {
            "status": "healthy" if is_connected else "configuration_error",
            "service": "Context7 Connection",
            "connected": is_connected
        },
        "message": "Context7 connection is configured properly" if is_connected else "Context7 configuration issue"
    }


# AI Agent Endpoints


import uuid
from pydantic import BaseModel

class ProcessMessageRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class InitConversationRequest(BaseModel):
    user_id: str

class ExecuteToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    tool_call_id: str

@app.post("/api/ai/process_message")
async def process_user_message(request: ProcessMessageRequest, session: Session = Depends(get_session), current_user_id: int = Depends(get_current_user_id)):
    """
    Process a user message through the AI agent.

    Args:
        request: ProcessMessageRequest object containing message and optional conversation_id
        session: Database session for saving conversation history
        current_user_id: Current user ID from authentication

    Returns:
        Response from the AI agent with any tool calls made
    """
    from models import User, Conversation, Message, SenderType, MessageType

    logger.info(f"Processing user message: {request.message[:50]}...")
    logger.info(f"Authenticated user_id from token: {current_user_id}")

    try:
        # Use the authenticated user ID instead of the one from the request
        # This ensures that users can only access their own conversations
        user_id = current_user_id
        logger.info(f"Using user_id for agent: {user_id}")

        # Get or create conversation
        if not request.conversation_id:
            # Create a new conversation for the authenticated user
            import uuid
            conversation_id = str(uuid.uuid4())
        else:
            # Use the provided conversation ID directly (already validated by Pydantic as string)
            conversation_id = request.conversation_id

        # Create the agent - this should now work regardless of API key availability
        # The agent handles missing API keys gracefully by setting api_available=False
        logger.info(f"Creating TodoAgent with default_user_id={user_id}")
        temp_agent = TodoAgent(default_user_id=user_id)
        logger.info(f"TodoAgent created, default_user_id is: {temp_agent.default_user_id}")

        # Process the message - this will use fallback logic if API is not available
        logger.info(f"Calling process_message with user_id={user_id}")
        result = await temp_agent.process_message(request.message, conversation_id, user_id=user_id)

        logger.info("Message processed successfully by AI agent")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing user message: {str(e)}")
        # Return a fallback response instead of raising an HTTP exception
        fallback_response = {
            "success": True,
            "data": {
                "response": f"I'm sorry, I encountered an error processing your message: {str(e)}. I can still help you with basic task management. For example: 'Add a task to buy groceries', 'List my tasks', or 'Complete wash the car'.",
                "conversation_id": conversation_id if 'conversation_id' in locals() else str(uuid.uuid4()),
                "tool_calls": []
            },
            "message": "Message processed with fallback response due to error"
        }
        return fallback_response


@app.post("/api/ai/init_conversation")
def initialize_conversation(request: InitConversationRequest, session: Session = Depends(get_session), current_user_id: int = Depends(get_current_user_id)):
    """
    Initialize a new conversation with the AI agent.

    Args:
        request: InitConversationRequest object (not actually used, relies on authenticated user)
        session: Database session for creating conversation
        current_user_id: Current user ID from authentication

    Returns:
        Dictionary with conversation ID
    """
    from models import User, Conversation

    logger.info(f"Initializing conversation for user: {current_user_id}")

    try:
        # Use the authenticated user ID instead of the one from the request
        user_id = current_user_id

        # Create a new conversation for the authenticated user
        # For now, we'll return a simple conversation ID
        # In a real implementation, you'd create a proper conversation record
        import uuid
        conversation_id = str(uuid.uuid4())

        logger.info(f"Conversation initialized with ID: {conversation_id}")
        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id
            },
            "message": "Conversation initialized successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing conversation: {str(e)}"
        )


@app.get("/api/ai/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str, session: Session = Depends(get_session), current_user_id: int = Depends(get_current_user_id)):
    """
    Retrieve messages for a specific conversation.

    Args:
        conversation_id: ID of the conversation to retrieve messages for
        session: Database session for querying messages
        current_user_id: Current user ID from authentication

    Returns:
        List of messages in the conversation
    """
    from models import Message, Conversation, User

    logger.info(f"Retrieving messages for conversation: {conversation_id}")

    try:
        # For now, we'll just return an empty list since we're not storing conversation history
        # in the actual database records yet
        # In a real implementation, you'd validate the conversation belongs to the user
        # and return the actual messages

        logger.info(f"Retrieved 0 messages for conversation (placeholder)")
        return {
            "success": True,
            "data": {
                "messages": [],
                "count": 0
            },
            "message": "Messages retrieved successfully (placeholder)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )


@app.post("/api/ai/execute_tool")
def execute_mcp_tool(request: ExecuteToolRequest):
    """
    Execute an MCP tool as part of the AI agent's tool chaining process.

    Args:
        request: ExecuteToolRequest object containing tool_name, arguments, and tool_call_id

    Returns:
        Result of the tool execution
    """
    logger.info(f"Executing MCP tool: {request.tool_name} with call ID: {request.tool_call_id}")

    try:
        # Map tool names to actual functions
        tool_functions = {
            "add_task": add_task_tool,
            "list_tasks": list_tasks_tool,
            "complete_task": complete_task_tool,
            "delete_task": delete_task_tool,
            "update_task": update_task_tool
        }

        if request.tool_name not in tool_functions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown tool: {request.tool_name}"
            )

        # Execute the tool
        tool_func = tool_functions[request.tool_name]
        result = tool_func(request.arguments)

        logger.info(f"MCP tool {request.tool_name} executed successfully")
        return {
            "success": True,
            "data": {
                "result": result,
                "tool_call_id": request.tool_call_id
            },
            "message": "Tool executed successfully"
        }

    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing tool: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001, log_level="info")