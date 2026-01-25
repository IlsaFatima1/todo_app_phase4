"""Todo model for the Todo AI Chatbot system."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .base import UUIDPrimaryKey, TimestampMixin, TodoStatus, TodoPriority
import uuid
from datetime import datetime


class TodoBase(SQLModel):
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = Field(default={})


class Todo(UUIDPrimaryKey, TodoBase, TimestampMixin, table=True):
    __tablename__ = "todos"

    # Foreign Keys
    created_by: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    assigned_to: Optional[uuid.UUID] = Field(foreign_key="users.id")

    # Relationships
    creator: "User" = Relationship(
        back_populates="todos_created",
        sa_relationship_kwargs={"foreign_keys": "[Todo.created_by]"}
    )
    assignee: Optional["User"] = Relationship(
        back_populates="todos_assigned",
        sa_relationship_kwargs={"foreign_keys": "[Todo.assigned_to]"}
    )
    conversation_links: List["TodoConversationLink"] = Relationship(back_populates="todo")


class TodoRead(TodoBase):
    id: uuid.UUID
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class TodoCreate(TodoBase):
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID] = None


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None