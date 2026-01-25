"""Base model classes and enums for the Todo AI Chatbot system."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class TimestampMixin(SQLModel):
    """Mixin to add timestamp fields to models"""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def __setattr__(self, name, value):
        if name == "updated_at":
            super().__setattr__("updated_at", datetime.utcnow())
        super().__setattr__(name, value)


class UUIDPrimaryKey(SQLModel):
    """Mixin to add UUID primary key to models"""
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )


from enum import Enum

class TodoStatus(str, Enum):
    """Enumeration of possible todo statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TodoPriority(str, Enum):
    """Enumeration of possible todo priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SenderType(str, Enum):
    """Enumeration of possible message sender types"""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Enumeration of possible message types"""
    TEXT = "text"
    COMMAND = "command"
    RESPONSE = "response"
    ERROR = "error"


class RelationshipType(str, Enum):
    """Enumeration of possible relationship types between todos and conversations"""
    DISCUSSION = "discussion"
    UPDATE = "update"
    CREATION = "creation"