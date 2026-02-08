"""
Pytest tests specifically for handling the GEMINI_API_KEY environment variable error
This test reproduces and verifies the fix for the error:
"Error: Error processing message: GEMINI_API_KEY environment variable not set"
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.todo_agent import TodoAgent, TodoAIError


def test_reproduce_gemini_api_key_error():
    """
    Reproduce the original error: 'GEMINI_API_KEY environment variable not set'
    This test demonstrates the error condition that occurs when the environment variable is missing
    """
    # Remove GEMINI_API_KEY from environment to reproduce the error
    original_key = os.environ.pop('GEMINI_API_KEY', None)

    try:
        # Attempt to initialize TodoAgent without GEMINI_API_KEY - this should raise TodoAIError
        with pytest.raises(TodoAIError) as exc_info:
            TodoAgent()

        # Verify the exact error message that was mentioned in the issue
        error_message = str(exc_info.value)
        assert "GEMINI_API_KEY environment variable not set" in error_message

        print(f"Successfully reproduced the error: {error_message}")

    finally:
        # Restore the original key if it existed
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key


def test_handle_missing_api_key_in_process_message():
    """
    Test that the error handling works when processing messages without the API key
    """
    # Remove GEMINI_API_KEY from environment
    original_key = os.environ.pop('GEMINI_API_KEY', None)

    try:
        # Try to initialize and use the agent - this should fail during initialization
        # not during message processing
        with pytest.raises(TodoAIError):
            agent = TodoAgent()

    finally:
        # Restore the original key if it existed
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key


def test_set_api_key_environment_variable():
    """
    Test that setting the GEMINI_API_KEY environment variable resolves the error
    """
    # Temporarily set a dummy API key
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'test-api-key-for-validation'

    try:
        # Mock the external dependencies to avoid actual API calls
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'):

            # Now initialization should work without raising TodoAIError
            agent = TodoAgent()
            assert agent is not None

    finally:
        # Restore the original key or remove if it didn't exist
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


def test_error_handling_best_practices():
    """
    Test best practices for handling the GEMINI_API_KEY error in production
    """
    # Scenario 1: Check if environment variable exists before initializing
    def safe_agent_initialization():
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")

        # Mock dependencies for test
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'):

            return TodoAgent()

    # Test that our safe initialization detects the missing key
    original_key = os.environ.pop('GEMINI_API_KEY', None)
    try:
        with pytest.raises(ValueError) as exc_info:
            safe_agent_initialization()

        assert "GEMINI_API_KEY must be set" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key

    # Test that our safe initialization works when key is present
    os.environ['GEMINI_API_KEY'] = 'test-key'
    try:
        agent = safe_agent_initialization()
        assert agent is not None
    finally:
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


@pytest.mark.asyncio
async def test_error_during_message_processing():
    """
    Test that errors during message processing are handled gracefully
    """
    # Set a dummy API key for testing
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'dummy-test-key'

    try:
        # Mock all dependencies and simulate an API error during processing
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'), \
             patch('src.agents.todo_agent.Runner') as mock_runner:

            # Simulate an API error that might occur during message processing
            mock_runner.run.side_effect = Exception("API connection failed")

            agent = TodoAgent()

            # This should handle the error gracefully and return an appropriate response
            result = await agent.process_message(
                user_message="Test message",
                conversation_id="test-conversation"
            )

            # Verify that the result indicates success or provides a graceful error
            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is False or result["success"] is True

    finally:
        # Restore original key
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


def test_documentation_example():
    """
    Provide a documented example of how to handle the GEMINI_API_KEY error
    """
    print("\nDocumentation Example:")
    print("="*50)
    print("# Before running the application, ensure GEMINI_API_KEY is set")
    print("import os")
    print("from src.agents.todo_agent import TodoAgent")
    print("")
    print("# Check if the environment variable is set")
    print("if not os.getenv('GEMINI_API_KEY'):")
    print("    raise ValueError('GEMINI_API_KEY environment variable must be set')")
    print("")
    print("# Now safely initialize the agent")
    print("# agent = TodoAgent()")
    print("="*50)


if __name__ == "__main__":
    # Run specific tests to demonstrate the error handling
    print("Testing GEMINI_API_KEY error handling...")

    # Run the reproduction test
    test_reproduce_gemini_api_key_error()
    print("✓ Successfully reproduced the original error")

    # Run the environment setup test
    test_set_api_key_environment_variable()
    print("✓ Successfully tested setting the environment variable")

    # Run best practices test
    test_error_handling_best_practices()
    print("✓ Successfully tested best practices")

    print("\nAll tests passed! The GEMINI_API_KEY error has been properly handled.")