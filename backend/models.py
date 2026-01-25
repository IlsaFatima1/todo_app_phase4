from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum
import sqlalchemy as sa


# Base classes and enums
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


# Existing User and Todo models (for compatibility)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)  # Added name field
    email: str = Field(unique=True, max_length=255)
    password_hash: str
    profile_picture: Optional[str] = Field(default=None, max_length=500)  # Added profile picture field
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)

    # Relationship to todos
    todos: List["Todo"] = Relationship(back_populates="user")


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")  # Required field for authenticated users

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="todos")


# New Todo AI Chatbot models
class UserChatbotBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    username: Optional[str] = Field(default=None, unique=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserChatbot(UUIDPrimaryKey, UserChatbotBase, TimestampMixin, table=True):
    __tablename__ = "users_chatbot"

    email: str = Field(unique=True, nullable=False, max_length=255)
    username: Optional[str] = Field(default=None, unique=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)

    # Relationships - using string references to avoid circular imports
    todos_created: List["TodoChatbot"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[TodoChatbot.created_by]"}
    )
    todos_assigned: List["TodoChatbot"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "[TodoChatbot.assigned_to]"}
    )
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages_sent: List["Message"] = Relationship(back_populates="sender")


class TodoChatbotBase(SQLModel):
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    extra_data: Optional[str] = Field(default=None)


class TodoChatbot(UUIDPrimaryKey, TodoChatbotBase, TimestampMixin, table=True):
    __tablename__ = "todos_chatbot"

    # Foreign Keys
    created_by: uuid.UUID = Field(foreign_key="users_chatbot.id", nullable=False)
    assigned_to: Optional[uuid.UUID] = Field(foreign_key="users_chatbot.id")

    # Relationships
    creator: "UserChatbot" = Relationship(
        back_populates="todos_created",
        sa_relationship_kwargs={"foreign_keys": "[TodoChatbot.created_by]"}
    )
    assignee: Optional["UserChatbot"] = Relationship(
        back_populates="todos_assigned",
        sa_relationship_kwargs={"foreign_keys": "[TodoChatbot.assigned_to]"}
    )
    conversation_links: List["TodoConversationLink"] = Relationship(back_populates="todo")


class ConversationBase(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    extra_data: Optional[str] = Field(default=None)


class Conversation(UUIDPrimaryKey, ConversationBase, TimestampMixin, table=True):
    __tablename__ = "conversations"

    # Foreign Key
    user_id: uuid.UUID = Field(foreign_key="users_chatbot.id", nullable=False)

    # Relationships
    user: "UserChatbot" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
    todo_links: List["TodoConversationLink"] = Relationship(back_populates="conversation")


class MessageBase(SQLModel):
    sender_type: SenderType = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)  # Max 10k characters
    message_type: MessageType = Field(default=MessageType.TEXT)
    extra_data: Optional[str] = Field(default=None)


class Message(UUIDPrimaryKey, MessageBase, TimestampMixin, table=True):
    __tablename__ = "messages"

    # Foreign Keys
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)
    sender_id: Optional[uuid.UUID] = Field(foreign_key="users_chatbot.id")  # Optional for system messages

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    sender: Optional["UserChatbot"] = Relationship(back_populates="messages_sent")


class TodoConversationLinkBase(SQLModel):
    relationship_type: RelationshipType = Field(default=RelationshipType.DISCUSSION)


class TodoConversationLink(UUIDPrimaryKey, TodoConversationLinkBase, TimestampMixin, table=True):
    __tablename__ = "todo_conversation_links"

    # Foreign Keys
    todo_id: uuid.UUID = Field(foreign_key="todos_chatbot.id", nullable=False)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)

    # Relationships
    todo: "TodoChatbot" = Relationship(back_populates="conversation_links")
    conversation: "Conversation" = Relationship(back_populates="todo_links")


# Pydantic Schemas for API
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    name: str  # Added name field
    password: str


class UserRead(UserBase):
    id: int
    name: str  # Added name field
    profile_picture: Optional[str] = None  # Added profile picture field
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoRead(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int  # Required for authenticated todos

    model_config = {"from_attributes": True}


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoComplete(BaseModel):
    completed: bool


# New Chatbot Pydantic Schemas
class UserChatbotRead(UserChatbotBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserChatbotCreate(UserChatbotBase):
    password: str  # Will be hashed before storing


class UserChatbotUpdate(SQLModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class TodoChatbotRead(TodoChatbotBase):
    id: uuid.UUID
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class TodoChatbotCreate(TodoChatbotBase):
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID] = None


class TodoChatbotUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    extra_data: Optional[dict] = None


class ConversationRead(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationCreate(ConversationBase):
    user_id: uuid.UUID


class ConversationUpdate(SQLModel):
    title: Optional[str] = None
    extra_data: Optional[dict] = None


class MessageRead(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: Optional[uuid.UUID]
    created_at: datetime


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID
    sender_id: Optional[uuid.UUID] = None


class MessageUpdate(SQLModel):
    content: Optional[str] = None
    message_type: Optional[MessageType] = None
    extra_data: Optional[dict] = None


class TodoConversationLinkRead(TodoConversationLinkBase):
    id: uuid.UUID
    todo_id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime


class TodoConversationLinkCreate(TodoConversationLinkBase):
    todo_id: uuid.UUID
    conversation_id: uuid.UUID