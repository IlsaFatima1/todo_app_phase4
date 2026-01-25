"""
Conversation and MessageHistory models for AI Agent context management
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class MessageRole(str, Enum):
    """Enumeration of possible message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Conversation(SQLModel, table=True):
    """Model representing a conversation between user and AI agent"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(max_length=255)  # Identifier for the user
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    context_data: Dict[str, Any] = Field(default={}, sa_column_kwargs={"server_default": "'{}'::jsonb"})
    thread_id: Optional[str] = Field(default=None, max_length=255)  # OpenAI thread reference

    # Relationship to message history
    messages: list["MessageHistory"] = Relationship(back_populates="conversation")


class MessageHistory(SQLModel, table=True):
    """Model representing a message in a conversation"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    role: MessageRole = Field(sa_column_kwargs={"server_default": "'user'::message_role"})
    content: str = Field(max_length=10000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default={}, sa_column_kwargs={"server_default": "'{}'::jsonb"})
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    tool_name: Optional[str] = Field(default=None, max_length=255)

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")