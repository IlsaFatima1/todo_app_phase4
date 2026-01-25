"""User model for the Todo AI Chatbot system."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .base import UUIDPrimaryKey, TimestampMixin
import uuid
from datetime import datetime


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    username: Optional[str] = Field(default=None, unique=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)


class User(UUIDPrimaryKey, UserBase, TimestampMixin, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, nullable=False, max_length=255)
    username: Optional[str] = Field(default=None, unique=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)

    # Relationships - using string references to avoid circular imports
    todos_created: List["Todo"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Todo.created_by]"}
    )
    todos_assigned: List["Todo"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "[Todo.assigned_to]"}
    )
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages_sent: List["Message"] = Relationship(back_populates="sender")


class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    password: str  # Will be hashed before storing


class UserUpdate(SQLModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None