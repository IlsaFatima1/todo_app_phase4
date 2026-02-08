"""
Pytest tests for TodoAgent with proper handling of GEMINI_API_KEY environment variable
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.todo_agent import TodoAgent, TodoAIError


def test_todo_agent_import():
    """Test that the TodoAgent can be imported without errors"""
    from src.agents.todo_agent import TodoAgent
    assert TodoAgent is not None


def test_todo_agent_raises_error_without_api_key():
    """Test that TodoAgent raises TodoAIError when GEMINI_API_KEY is not set"""
    # Temporarily remove the GEMINI_API_KEY if it exists
    original_key = os.environ.pop('GEMINI_API_KEY', None)

    try:
        # Attempt to initialize TodoAgent without GEMINI_API_KEY
        with pytest.raises(TodoAIError) as exc_info:
            TodoAgent()

        # Verify the error message
        assert "GEMINI_API_KEY environment variable not set" in str(exc_info.value)
    finally:
        # Restore the original key if it existed
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key


def test_todo_agent_initializes_with_api_key():
    """Test that TodoAgent initializes successfully when GEMINI_API_KEY is set"""
    # Set a dummy API key for testing
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'dummy-test-key'

    try:
        # Mock the external dependencies to avoid actual API calls
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'):

            # Initialize the agent - this should not raise an exception
            agent = TodoAgent()

            # Verify the agent was created
            assert agent is not None

    finally:
        # Restore the original key if it existed, or remove the dummy key
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


def test_todo_agent_initializes_with_default_user_id():
    """Test that TodoAgent can be initialized with a default user ID"""
    # Set a dummy API key for testing
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'dummy-test-key'

    try:
        # Mock the external dependencies to avoid actual API calls
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'):

            # Initialize the agent with a default user ID
            user_id = 123
            agent = TodoAgent(default_user_id=user_id)

            # Verify the agent was created and user ID is stored
            assert agent is not None
            assert agent.default_user_id == user_id

    finally:
        # Restore the original key if it existed, or remove the dummy key
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


@pytest.mark.asyncio
async def test_todo_agent_process_message_with_mocked_dependencies():
    """Test that TodoAgent can process a message with mocked dependencies"""
    # Set a dummy API key for testing
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'dummy-test-key'

    try:
        # Mock all external dependencies
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'), \
             patch('src.agents.todo_agent.Runner') as mock_runner:

            # Mock the runner response
            mock_response = MagicMock()
            mock_response.final_output = "Test response"
            mock_runner.run = MagicMock(return_value=mock_response)

            # Initialize the agent
            agent = TodoAgent()

            # Test processing a message
            result = await agent.process_message(
                user_message="Test message",
                conversation_id="test-conversation-id"
            )

            # Verify the result structure
            assert isinstance(result, dict)
            assert "success" in result
            assert "data" in result
            assert "message" in result

    finally:
        # Restore the original key if it existed, or remove the dummy key
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


@pytest.mark.asyncio
async def test_todo_agent_process_message_fallback_mode():
    """Test that TodoAgent falls back to local processing when API is unavailable"""
    # Set a dummy API key for testing
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'dummy-test-key'

    try:
        # Mock all external dependencies but simulate API failure
        with patch('src.agents.todo_agent.AsyncOpenAI'), \
             patch('src.agents.todo_agent.OpenAIChatCompletionsModel'), \
             patch('src.agents.todo_agent.RunConfig'), \
             patch('src.agents.todo_agent.Agent'), \
             patch('src.agents.todo_agent.Runner') as mock_runner:

            # Make the runner raise an exception to trigger fallback mode
            mock_runner.run.side_effect = Exception("API Error")

            # Initialize the agent
            agent = TodoAgent()

            # Test processing a message that should trigger fallback
            result = await agent.process_message(
                user_message="Add task to buy groceries",
                conversation_id="test-conversation-id"
            )

            # Verify the result structure
            assert isinstance(result, dict)
            assert "success" in result
            assert "data" in result
            assert "message" in result
            # In fallback mode, the message should indicate fallback mode
            assert "fallback mode" in result["message"] or "successfully" in result["message"]

    finally:
        # Restore the original key if it existed, or remove the dummy key
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)


def test_todo_agent_handles_missing_api_key_gracefully():
    """Test that TodoAgent handles missing API key gracefully in a realistic scenario"""
    # Ensure GEMINI_API_KEY is not set
    original_key = os.environ.pop('GEMINI_API_KEY', None)

    try:
        # Try to create an agent without API key - this should raise an exception
        with pytest.raises(TodoAIError) as exc_info:
            TodoAgent()

        # Verify the error message contains the expected text
        error_msg = str(exc_info.value)
        assert "GEMINI_API_KEY" in error_msg
        assert "not set" in error_msg

    finally:
        # Restore the original key if it existed
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key


if __name__ == "__main__":
    # This allows running the test file directly with python
    pytest.main([__file__])