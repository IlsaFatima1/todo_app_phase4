"""
Authentication middleware for the Todo AI Chatbot
"""
from fastapi import HTTPException, status, Request
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from src.auth.jwt import verify_token


logger = logging.getLogger(__name__)


class AuthMiddleware:
    """
    Authentication middleware to handle JWT token verification
    """

    def __init__(self):
        self.security = HTTPBearer(auto_error=False)  # Don't auto-raise HTTPException

    async def __call__(self, request: Request):
        """
        Process the request and validate authentication

        Args:
            request: The incoming request

        Returns:
            user_id if authentication is successful, None otherwise
        """
        # Extract credentials from the request
        credentials: Optional[HTTPAuthorizationCredentials] = await self.security.__call__(request)

        if credentials is None:
            # No authorization header provided
            request.state.user_id = None
            return None

        # Verify the token
        token = credentials.credentials
        user_id = verify_token(token)

        if user_id is None:
            # Invalid token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Store user ID in request state for later use
        request.state.user_id = user_id
        return user_id


# Create a global instance of the middleware
auth_middleware = AuthMiddleware()


def get_current_user_id(request: Request) -> Optional[int]:
    """
    Helper function to get the current user ID from request state

    Args:
        request: The incoming request

    Returns:
        User ID if authenticated, None otherwise
    """
    return getattr(request.state, 'user_id', None)


__all__ = [
    "auth_middleware",
    "get_current_user_id",
    "AuthMiddleware"
]