"""
Database session management utilities for the Todo AI Chatbot
"""
from contextlib import contextmanager
from typing import Generator
from sqlmodel import Session, select
from .connection import get_session, get_session_context
from src.models.conversation import Conversation, MessageHistory
from src.models.task import Task
from uuid import UUID


def get_conversation_by_id(conversation_id: UUID, session: Session) -> Conversation:
    """
    Retrieve a conversation by its ID

    Args:
        conversation_id: The UUID of the conversation to retrieve
        session: Database session

    Returns:
        The conversation object
    """
    statement = select(Conversation).where(Conversation.id == conversation_id)
    conversation = session.exec(statement).first()
    return conversation


def get_messages_by_conversation(conversation_id: UUID, session: Session) -> list[MessageHistory]:
    """
    Retrieve all messages for a specific conversation

    Args:
        conversation_id: The UUID of the conversation
        session: Database session

    Returns:
        List of message history objects
    """
    statement = select(MessageHistory).where(
        MessageHistory.conversation_id == conversation_id
    ).order_by(MessageHistory.timestamp)
    messages = session.exec(statement).all()
    return messages


def save_conversation(conversation: Conversation, session: Session) -> Conversation:
    """
    Save or update a conversation

    Args:
        conversation: The conversation object to save
        session: Database session

    Returns:
        The saved conversation object
    """
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def save_message(message: MessageHistory, session: Session) -> MessageHistory:
    """
    Save a message to the database

    Args:
        message: The message object to save
        session: Database session

    Returns:
        The saved message object
    """
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def create_new_conversation(user_id: str, session: Session) -> Conversation:
    """
    Create a new conversation for a user

    Args:
        user_id: The ID of the user creating the conversation
        session: Database session

    Returns:
        The newly created conversation object
    """
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


# Export the main session utility functions
__all__ = [
    "get_session",
    "get_session_context",
    "get_conversation_by_id",
    "get_messages_by_conversation",
    "save_conversation",
    "save_message",
    "create_new_conversation"
]