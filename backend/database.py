"""Database module for Todo application with SQLModel and Neon PostgreSQL."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """Initialize the database by creating all tables."""
    # Import models to register them with SQLModel metadata
    from models import Todo, User
    try:
        # Create all tables with the current schema (only if they don't exist)
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error initializing database: {e}")
        raise


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """Get a database session with proper cleanup."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Function for FastAPI dependency injection
def get_session() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session."""
    with get_session_context() as session:
        yield session