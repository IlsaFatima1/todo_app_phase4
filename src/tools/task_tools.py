from typing import Dict, Any, Optional
from sqlmodel import select
import sys
import os

# Use the backend's Todo model instead of the Task model
# Need to add backend to path to import from there
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from models import Todo, TodoCreate, TodoUpdate, TodoRead  # Changed to use backend's Todo model
from database import get_session_context  # Changed to use backend's database connection
from src.utils.helpers import (
    validate_input,
    sanitize_input,
    validate_task_title,
    validate_task_status,
    create_success_response,
    create_error_response,
    handle_exception,
    create_missing_field_error,
    MCPError
)
from uuid import UUID
import json


# Define JSON schemas for input validation
ADD_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 255},
        "description": {"type": "string", "maxLength": 1000},
        "status": {"type": "string", "enum": ["pending", "completed"], "default": "pending"}
    },
    "required": ["title"]
}

LIST_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "status_filter": {"type": "string", "enum": ["pending", "completed"]}
    }
}

COMPLETE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "task_name": {"type": "string"}
    },
    "required": ["task_name"]
}

DELETE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "task_name": {"type": "string"}
    },
    "required": ["task_name"]
}

UPDATE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "task_name": {"type": "string"},
        "title": {"type": "string", "minLength": 1, "maxLength": 255},
        "description": {"type": "string", "maxLength": 1000},
        "status": {"type": "string", "enum": ["pending", "completed"]}
    },
    "required": ["task_name"]
}


def add_task_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool to create a new task in the database.

    Args:
        arguments: Dictionary containing task properties

    Returns:
        Dictionary with success status and task data
    """
    try:
        # Validate input against schema
        validation_result = validate_input(arguments, ADD_TASK_SCHEMA)
        if validation_result.get("errors"):
            raise MCPError(
                f"Input validation failed: {'; '.join(validation_result['errors'])}",
                "VALIDATION_ERROR",
                {"validation_errors": validation_result["errors"]}
            )

        # Sanitize input
        sanitized_args = sanitize_input(arguments)

        # Validate specific business rules
        title_errors = validate_task_title(sanitized_args.get("title", ""))
        if title_errors:
            raise MCPError(
                f"Title validation failed: {'; '.join(title_errors)}",
                "VALIDATION_ERROR",
                {"title_errors": title_errors}
            )

        # For the Todo model, we need to convert status to completed flag
        status_arg = sanitized_args.get("status", "pending")
        completed = (status_arg.lower() == "completed")

        # Create todo object using the backend's Todo model
        todo_create_data = TodoCreate(
            title=sanitized_args["title"],
            description=sanitized_args.get("description"),
            completed=completed
        )

        # Extract user_id from arguments or use default
        # For the AI agent, we'll use a default user_id of 1 (admin/user for automated tasks)
        # In a real implementation, this would come from authentication context
        user_id = arguments.get("user_id", 1)

        # Save to database
        with get_session_context() as session:
            # Create todo from the input data
            # The Todo model expects user_id, so we'll use the user_id from context
            # Let the model handle the datetime fields (created_at, updated_at) automatically
            todo = Todo(
                title=todo_create_data.title,
                description=todo_create_data.description,
                completed=todo_create_data.completed,
                user_id=user_id
            )
            session.add(todo)
            session.commit()  # Commit to save and let the model set timestamps
            session.refresh(todo)  # Refresh to get the updated object with timestamps

            # Convert to read format using TodoRead schema
            todo_read = TodoRead.model_validate(todo) if hasattr(TodoRead, 'model_validate') else TodoRead(
                id=todo.id,
                title=todo.title,
                description=todo.description,
                completed=todo.completed,
                created_at=todo.created_at,
                updated_at=todo.updated_at,
                user_id=todo.user_id
            )

            todo_read_dict = todo_read.model_dump() if hasattr(todo_read, 'model_dump') else {k: v for k, v in todo_read.__dict__.items() if not k.startswith('_')}

        return create_success_response(
            data=todo_read_dict,
            message="Task created successfully"
        )

    except Exception as e:
        return handle_exception(e)


def list_tasks_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool to retrieve all tasks from the database, optionally filtered by status.

    Args:
        arguments: Dictionary containing optional status filter

    Returns:
        Dictionary with success status and list of tasks
    """
    try:
        # Validate input against schema
        validation_result = validate_input(arguments, LIST_TASKS_SCHEMA)
        if validation_result.get("errors"):
            raise MCPError(
                f"Input validation failed: {'; '.join(validation_result['errors'])}",
                "VALIDATION_ERROR",
                {"validation_errors": validation_result["errors"]}
            )

        # Get filter parameters
        status_filter = arguments.get("status_filter")

        if status_filter:
            status_errors = validate_task_status(status_filter)
            if status_errors:
                raise MCPError(
                    f"Status filter validation failed: {'; '.join(status_errors)}",
                    "VALIDATION_ERROR",
                    {"status_errors": status_errors}
                )

        # Query database - filter by user_id as well
        with get_session_context() as session:
            query = select(Todo).where(Todo.user_id == arguments.get("user_id", 1))

            if status_filter:
                # Convert status filter to completed flag for Todo model
                if status_filter.lower() == "completed":
                    query = query.where(Todo.completed == True)
                elif status_filter.lower() == "pending":
                    query = query.where(Todo.completed == False)

            todos = session.exec(query).all()

            # Convert to read format
            todos_data = []
            for todo in todos:
                # Convert to TodoRead format
                todo_read = TodoRead.model_validate(todo) if hasattr(TodoRead, 'model_validate') else TodoRead(
                    id=todo.id,
                    title=todo.title,
                    description=todo.description,
                    completed=todo.completed,
                    created_at=todo.created_at,
                    updated_at=todo.updated_at,
                    user_id=todo.user_id
                )

                todo_dict = todo_read.model_dump() if hasattr(todo_read, 'model_dump') else {k: v for k, v in todo_read.__dict__.items() if not k.startswith('_')}
                todos_data.append(todo_dict)

        return create_success_response(
            data={
                "tasks": todos_data,
                "count": len(todos_data)
            },
            message=f"Retrieved {len(todos_data)} tasks"
        )

    except Exception as e:
        return handle_exception(e)


def complete_task_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool to mark a task as completed in the database.

    Args:
        arguments: Dictionary containing task name and optionally user_id

    Returns:
        Dictionary with success status and updated task
    """
    try:
        # Validate input against schema
        validation_result = validate_input(arguments, COMPLETE_TASK_SCHEMA)
        if validation_result.get("errors"):
            raise MCPError(
                f"Input validation failed: {'; '.join(validation_result['errors'])}",
                "VALIDATION_ERROR",
                {"validation_errors": validation_result["errors"]}
            )

        task_name_str = arguments.get("task_name")
        user_id = arguments.get("user_id", 1)  # Default to user 1 if not provided

        if not task_name_str:
            raise create_missing_field_error("task_name")

        # Find the task by name for the specific user
        with get_session_context() as session:
            # Query for the todo by title AND user_id (case-insensitive partial match)
            statement = select(Todo).where(
                Todo.title.ilike(f"%{task_name_str}%"),  # Use ilike for case-insensitive partial match
                Todo.user_id == user_id  # Filter by user_id
            )
            result = session.exec(statement)
            todos = result.all()

            # Find the best match among results
            target_todo = None
            for todo in todos:
                if task_name_str.lower() in todo.title.lower():
                    target_todo = todo
                    break

            if not target_todo:
                raise MCPError(
                    f"Todo with name containing '{task_name_str}' not found for user {user_id}",
                    "RECORD_NOT_FOUND",
                    {"task_name": task_name_str, "user_id": user_id}
                )

            todo = target_todo

            # Update completed status for Todo model
            todo.completed = True
            session.add(todo)
            session.commit()  # Commit the transaction to persist changes

            # Refresh to get full todo with updated timestamps
            session.refresh(todo)

            # Convert to TodoRead format
            todo_read = TodoRead.model_validate(todo) if hasattr(TodoRead, 'model_validate') else TodoRead(
                id=todo.id,
                title=todo.title,
                description=todo.description,
                completed=todo.completed,
                created_at=todo.created_at,
                updated_at=todo.updated_at,
                user_id=todo.user_id
            )

            todo_dict = todo_read.model_dump() if hasattr(todo_read, 'model_dump') else {k: v for k, v in todo_read.__dict__.items() if not k.startswith('_')}

        return create_success_response(
            data=todo_dict,
            message="Task completed successfully"
        )

    except Exception as e:
        return handle_exception(e)


def delete_task_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool to remove a task from the database.

    Args:
        arguments: Dictionary containing task name and optionally user_id

    Returns:
        Dictionary with success status and deleted task ID
    """
    try:
        # Validate input against schema
        validation_result = validate_input(arguments, DELETE_TASK_SCHEMA)
        if validation_result.get("errors"):
            raise MCPError(
                f"Input validation failed: {'; '.join(validation_result['errors'])}",
                "VALIDATION_ERROR",
                {"validation_errors": validation_result["errors"]}
            )

        task_name_str = arguments.get("task_name")
        user_id = arguments.get("user_id", 1)  # Default to user 1 if not provided

        if not task_name_str:
            raise create_missing_field_error("task_name")

        # Find the task by name instead of using an ID
        with get_session_context() as session:
            # Query for the todo by title AND user_id (case-insensitive partial match)
            statement = select(Todo).where(
                Todo.title.ilike(f"%{task_name_str}%"),  # Use ilike for case-insensitive partial match
                Todo.user_id == user_id  # Filter by user_id
            )
            result = session.exec(statement)
            todos = result.all()

            # Find the best match among results
            target_todo = None
            for todo in todos:
                if task_name_str.lower() in todo.title.lower():
                    target_todo = todo
                    break

            if not target_todo:
                raise MCPError(
                    f"Todo with name containing '{task_name_str}' not found for user {user_id}",
                    "RECORD_NOT_FOUND",
                    {"task_name": task_name_str, "user_id": user_id}
                )

            # Delete the todo
            session.delete(target_todo)
            session.commit()  # Commit the transaction to persist changes

        return create_success_response(
            data={"deleted_task_id": str(target_todo.id)},  # Return the ID of the deleted todo
            message="Task deleted successfully"
        )

    except Exception as e:
        return handle_exception(e)


def update_task_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool to modify task properties in the database.

    Args:
        arguments: Dictionary containing task name, properties to update, and optionally user_id

    Returns:
        Dictionary with success status and updated task
    """
    try:
        # Validate input against schema
        validation_result = validate_input(arguments, UPDATE_TASK_SCHEMA)
        if validation_result.get("errors"):
            raise MCPError(
                f"Input validation failed: {'; '.join(validation_result['errors'])}",
                "VALIDATION_ERROR",
                {"validation_errors": validation_result["errors"]}
            )

        task_name_str = arguments.get("task_name")

        if not task_name_str:
            raise create_missing_field_error("task_name")

        # Check for title validation if provided
        if "title" in arguments:
            title_errors = validate_task_title(arguments["title"])
            if title_errors:
                raise MCPError(
                    f"Title validation failed: {'; '.join(title_errors)}",
                    "VALIDATION_ERROR",
                    {"title_errors": title_errors}
                )

        # Check for status validation if provided
        if "status" in arguments:
            status_arg = arguments["status"]
            status_errors = validate_task_status(status_arg)
            if status_errors:
                raise MCPError(
                    f"Status validation failed: {'; '.join(status_errors)}",
                    "VALIDATION_ERROR",
                    {"status_errors": status_errors}
                )

        # Find the task by name instead of using an ID
        with get_session_context() as session:
            # Query for the todo by title AND user_id (case-insensitive partial match)
            user_id = arguments.get("user_id", 1)  # Default to user 1 if not provided
            statement = select(Todo).where(
                Todo.title.ilike(f"%{task_name_str}%"),  # Use ilike for case-insensitive partial match
                Todo.user_id == user_id  # Filter by user_id
            )
            result = session.exec(statement)
            todos = result.all()

            # Find the best match among results
            target_todo = None
            for todo in todos:
                if task_name_str.lower() in todo.title.lower():
                    target_todo = todo
                    break

            if not target_todo:
                raise MCPError(
                    f"Todo with name containing '{task_name_str}' not found for user {user_id}",
                    "RECORD_NOT_FOUND",
                    {"task_name": task_name_str, "user_id": user_id}
                )

            # Update todo properties
            if "title" in arguments:
                target_todo.title = arguments["title"]
            if "description" in arguments:
                target_todo.description = arguments.get("description")
            if "status" in arguments:
                # Convert status to completed flag for Todo model
                status_arg = arguments["status"]
                target_todo.completed = (status_arg.lower() == "completed")

            session.add(target_todo)
            session.commit()  # Commit the transaction to persist changes

            # Refresh to get full todo with updated timestamps
            session.refresh(target_todo)

            # Convert to TodoRead format
            todo_read = TodoRead.model_validate(target_todo) if hasattr(TodoRead, 'model_validate') else TodoRead(
                id=target_todo.id,
                title=target_todo.title,
                description=target_todo.description,
                completed=target_todo.completed,
                created_at=target_todo.created_at,
                updated_at=target_todo.updated_at,
                user_id=target_todo.user_id
            )

            todo_dict = todo_read.model_dump() if hasattr(todo_read, 'model_dump') else {k: v for k, v in todo_read.__dict__.items() if not k.startswith('_')}

        return create_success_response(
            data=todo_dict,
            message="Task updated successfully"
        )

    except Exception as e:
        return handle_exception(e)