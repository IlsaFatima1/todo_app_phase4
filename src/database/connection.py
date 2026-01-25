from sqlmodel import create_engine, Session
from contextlib import contextmanager
from typing import Generator
import os


# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_mcp_db")

# Create engine with connection pooling settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with proper cleanup.

    Yields:
        Session: A SQLModel session for database operations
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """
    Context manager for database sessions with automatic cleanup.

    Usage:
        with get_session_context() as session:
            # Perform database operations
            session.add(task)
            session.commit()
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Initialize the database by creating all tables.
    This should be called when the application starts.
    """
    from src.models.task import Task  # Import here to avoid circular imports

    # Create all tables defined in the models
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)