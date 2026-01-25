"""Authentication module for Todo application using Better Auth."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlmodel import Session, select
from database import get_session
from models import User
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os


# Initialize security scheme
security = HTTPBearer()


def verify_token(token: str) -> Optional[int]:
    """Verify the authentication token and return user ID.

    Args:
        token: The authentication token to verify

    Returns:
        User ID if token is valid, None otherwise
    """
    # In a real implementation, this would verify the token against Better Auth
    # For now, we'll implement a basic JWT verification
    # In production, you would integrate with Better Auth's token verification

    # Get the secret key from environment variables
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> int:
    """Get the current user ID from the authentication token.

    This function verifies the authentication token and returns the user ID
    of the authenticated user. It raises an HTTPException if the token is
    invalid or the user doesn't exist.

    Args:
        credentials: HTTP authorization credentials from the request
        session: Database session for querying user information

    Returns:
        The ID of the authenticated user

    Raises:
        HTTPException: If the token is invalid, expired, or user doesn't exist
    """
    import sys
    print(f"DEBUG: Authentication function called with credentials: {credentials.scheme if credentials else 'None'}", flush=True)

    token = credentials.credentials
    print(f"DEBUG: Token received: {token[:10] if token else 'None'}...", flush=True)

    user_id = verify_token(token)
    print(f"DEBUG: Token verification result: {user_id}", flush=True)

    if user_id is None:
        print("DEBUG: Token verification failed - raising 401", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify that the user exists in the database
    user = session.get(User, user_id)
    print(f"DEBUG: User lookup result: {user.id if user else 'None'}", flush=True)

    if user is None:
        print(f"DEBUG: User not found in database - raising 401 for user_id: {user_id}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"DEBUG: Authentication successful, returning user_id: {user_id}", flush=True)
    return user_id


def create_access_token(user_id: int) -> str:
    """Create an access token for the given user ID.

    Args:
        user_id: The ID of the user for whom to create the token

    Returns:
        The encoded JWT token
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"

    # Set token expiration (e.g., 24 hours)
    from datetime import timedelta
    expire = datetime.utcnow() + timedelta(hours=24)

    # Create the token payload
    payload = {
        "user_id": user_id,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp()
    }

    # Encode and return the token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token