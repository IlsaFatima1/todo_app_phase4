"""
Configuration for Context7 MCP Server Integration
"""
import os
from typing import Optional

class Context7Config:
    """Configuration class for Context7 integration"""

    # Context7 API Key
    CTX7_API_KEY: str = os.getenv("CTX7_API_KEY", "ctx7sk-00bd2980-5af6-4841-b960-0a3d6a66786b")

    # Context7 Base URL
    CTX7_BASE_URL: str = os.getenv("CTX7_BASE_URL", "https://api.context7.ai")

    # MCP Server Configuration for Context7
    CTX7_MCP_ENDPOINT: str = f"{CTX7_BASE_URL}/mcp/v1"

    # Timeout settings
    CTX7_TIMEOUT: int = int(os.getenv("CTX7_TIMEOUT", "30"))

    # Retry settings
    CTX7_MAX_RETRIES: int = int(os.getenv("CTX7_MAX_RETRIES", "3"))

    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required Context7 configuration is present"""
        return bool(cls.CTX7_API_KEY and cls.CTX7_BASE_URL)

    @classmethod
    def get_headers(cls) -> dict:
        """Get headers for Context7 API requests"""
        return {
            "Authorization": f"Bearer {cls.CTX7_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Todo-AI-Chatbot-MCP-Server/1.0"
        }

# Initialize the configuration
CTX7_CONFIG = Context7Config()

__all__ = ['CTX7_CONFIG', 'Context7Config']