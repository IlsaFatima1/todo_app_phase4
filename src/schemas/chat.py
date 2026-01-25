"""
Pydantic models for chat endpoint request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint
    """
    message: str = Field(..., min_length=1, max_length=10000, description="User message content")
    conversation_id: Optional[str] = Field(None, description="Optional conversation identifier")
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")


class ToolCall(BaseModel):
    """
    Model representing a tool call executed by the AI agent
    """
    id: str
    function: Dict[str, Any]
    type: str = "function"


class ChatResponseData(BaseModel):
    """
    Data model for the chat response
    """
    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Identifier for the conversation")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Array of tool calls executed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the response")


class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint
    """
    success: bool = Field(..., description="Indicates if the request was successful")
    data: Optional[ChatResponseData] = Field(None, description="Response data if successful")
    message: str = Field(..., description="Human-readable message about the operation")


class ErrorResponse(ChatResponse):
    """
    Error response model for the chat endpoint
    """
    success: bool = False
    data: Optional[ChatResponseData] = None
    message: str = Field(..., description="Error message")