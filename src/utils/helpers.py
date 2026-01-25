from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import ValidationError
import json


class ErrorCode(Enum):
    """Enumeration of standard error codes for MCP tools."""

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


class MCPError(Exception):
    """Base exception class for MCP tool errors."""

    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            "success": False,
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details
            }
        }


def validate_input(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate input data against a schema.

    Args:
        data: Input data to validate
        schema: Schema to validate against

    Returns:
        Dictionary containing validation errors if any
    """
    errors = []

    # Check required fields
    if "required" in schema:
        for required_field in schema["required"]:
            if required_field not in data:
                errors.append(f"Missing required field: {required_field}")

    # Check field types and constraints
    if "properties" in schema:
        for field, field_spec in schema["properties"].items():
            if field in data:
                value = data[field]

                # Validate type
                if "type" in field_spec:
                    expected_type = field_spec["type"]

                    if expected_type == "string" and not isinstance(value, str):
                        errors.append(f"Field '{field}' must be a string")
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        errors.append(f"Field '{field}' must be a number")
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        errors.append(f"Field '{field}' must be a boolean")
                    elif expected_type == "array" and not isinstance(value, list):
                        errors.append(f"Field '{field}' must be an array")
                    elif expected_type == "object" and not isinstance(value, dict):
                        errors.append(f"Field '{field}' must be an object")

                # Validate string length constraints
                if expected_type == "string":
                    if "minLength" in field_spec and len(value) < field_spec["minLength"]:
                        errors.append(f"Field '{field}' must be at least {field_spec['minLength']} characters long")
                    if "maxLength" in field_spec and len(value) > field_spec["maxLength"]:
                        errors.append(f"Field '{field}' must be at most {field_spec['maxLength']} characters long")

                # Validate numeric constraints
                if expected_type in ["number", "integer"]:
                    if "minimum" in field_spec and value < field_spec["minimum"]:
                        errors.append(f"Field '{field}' must be at least {field_spec['minimum']}")
                    if "maximum" in field_spec and value > field_spec["maximum"]:
                        errors.append(f"Field '{field}' must be at most {field_spec['maximum']}")

                # Validate enum values
                if "enum" in field_spec and value not in field_spec["enum"]:
                    errors.append(f"Field '{field}' must be one of {field_spec['enum']}")

    return {"errors": errors} if errors else {}


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data by removing potentially harmful content.

    Args:
        data: Input data to sanitize

    Returns:
        Sanitized input data
    """
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            # Basic sanitization for strings
            # Remove potential SQL injection patterns (basic implementation)
            sanitized_value = value.replace("'", "''")  # Escape single quotes
            sanitized_value = sanitized_value.strip()  # Remove leading/trailing whitespace

            sanitized[key] = sanitized_value
        else:
            sanitized[key] = value

    return sanitized


def validate_task_title(title: str) -> List[str]:
    """
    Validate a task title according to business rules.

    Args:
        title: Task title to validate

    Returns:
        List of validation errors if any
    """
    errors = []

    if not title or not title.strip():
        errors.append("Task title cannot be empty")

    if len(title) > 255:
        errors.append("Task title cannot exceed 255 characters")

    return errors


def validate_task_status(status: str) -> List[str]:
    """
    Validate a task status according to business rules.

    Args:
        status: Task status to validate

    Returns:
        List of validation errors if any
    """
    errors = []

    valid_statuses = ["pending", "completed"]

    if status not in valid_statuses:
        errors.append(f"Task status must be one of: {valid_statuses}")

    return errors


def create_success_response(data: Any, message: str = "Operation successful") -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "success": True,
        "data": data,
        "message": message
    }


def create_error_response(error: MCPError) -> Dict[str, Any]:
    """Create a standardized error response from an MCPError."""
    return error.to_dict()


def handle_exception(exception: Exception) -> Dict[str, Any]:
    """Convert an exception to a standardized error response."""
    if isinstance(exception, MCPError):
        return create_error_response(exception)
    else:
        # For unexpected errors, create a generic internal error response
        error = MCPError(
            message="An unexpected error occurred",
            error_code=ErrorCode.UNEXPECTED_ERROR,
            details={
                "original_error": str(exception),
                "error_type": type(exception).__name__
            }
        )
        return create_error_response(error)


def create_validation_error(field: str, expected: str, actual: Any) -> MCPError:
    """Create a validation error for a specific field."""
    message = f"Invalid value for field '{field}'. Expected {expected}, got {type(actual).__name__}"
    details = {
        "field": field,
        "expected_type": expected,
        "actual_value": actual,
        "actual_type": type(actual).__name__
    }
    return MCPError(message, ErrorCode.VALIDATION_ERROR, details)


def create_missing_field_error(field: str) -> MCPError:
    """Create a validation error for a missing required field."""
    message = f"Required field '{field}' is missing"
    details = {"field": field}
    return MCPError(message, ErrorCode.MISSING_REQUIRED_FIELD, details)