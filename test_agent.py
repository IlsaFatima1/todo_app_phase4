#!/usr/bin/env python3
"""
Test script to verify the AI agent implementation
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_agent_import():
    """Test that the agent can be imported without errors"""
    print("Testing agent import...")
    try:
        from src.agents.todo_agent import TodoAgent
        print("[OK] Successfully imported TodoAgent")
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import TodoAgent: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing TodoAgent: {e}")
        return False

def test_agent_initialization():
    """Test that the agent can be initialized without errors"""
    print("\nTesting agent initialization...")

    # Set a dummy API key for testing
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "dummy-key-for-testing"

    try:
        from src.agents.todo_agent import TodoAgent
        agent = TodoAgent()
        print("[OK] Successfully initialized TodoAgent")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize TodoAgent: {e}")
        return False

async def test_agent_process_message():
    """Test that the agent can process a message"""
    print("\nTesting agent message processing...")

    # Set a dummy API key for testing
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "dummy-key-for-testing"

    try:
        from src.agents.todo_agent import TodoAgent
        agent = TodoAgent()

        # This will likely fail due to the API call, but we want to see if the structure is correct
        result = await agent.process_message("Hello", "test-conversation-123")
        print(f"[OK] Successfully processed message: {result}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")
        return False

async def main():
    """Run all tests"""
    print("Starting AI Agent tests...\n")

    success = True

    success &= test_agent_import()
    success &= test_agent_initialization()

    # Only run the process message test if the previous tests passed
    if success:
        success &= await test_agent_process_message()

    print(f"\n{'='*50}")
    if success:
        print("[OK] All tests passed!")
    else:
        print("[ERROR] Some tests failed!")
    print(f"{'='*50}")

    return success

if __name__ == "__main__":
    # Set up basic logging to see what's happening
    logging.basicConfig(level=logging.INFO)

    # Run the async main function
    success = asyncio.run(main())

    # Exit with appropriate code
    sys.exit(0 if success else 1)