# OpenAI Agent SDK Guide

This document provides comprehensive information about creating and using agents with the OpenAI Agent SDK, including patterns, best practices, and examples.

## Table of Contents
- [Introduction](#introduction)
- [Agent Creation Patterns](#agent-creation-patterns)
- [Core Components](#core-components)
- [Configuration Options](#configuration-options)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Introduction

The OpenAI Agent SDK provides a framework for creating intelligent agents that can interact with various tools, maintain conversation context, and perform complex tasks. Agents are built around the concept of using Large Language Models (LLMs) with function calling capabilities.

## Agent Creation Patterns

### Basic Agent Structure

```python
from openai import OpenAI
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
import os

 client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),

# Create run configuration
config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,  # Set to False for debugging
)

# Create the agent
agent = Agent(
    name="MyAgent",
    instructions="You are a helpful assistant...",
    tools=[tool1, tool2],  # Optional: list of tools the agent can use
)
```

### Async Agent Pattern

For async applications, use the async pattern:

```python
import asyncio
from agents import Agent, Runner

async def run_agent(query: str) -> str:
    response = await Runner.run(agent, query, run_config=config)
    return response.final_output

# Usage
async def main():
    result = await run_agent("Hello, what can you do?")
    print(result)
```

## Core Components

### 1. Client Configuration
The client handles communication with the LLM provider:

```python
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


### 3. Run Configuration
The run configuration defines how the agent executes:

```python
config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
    # Additional configuration options...
)
```

### 4. Agent Definition
The agent combines all components:

```python
agent = Agent(
    name="AgentName",  # Unique identifier for the agent
    instructions="System prompt for the agent",  # Behavior instructions
    tools=[tool1, tool2],  # Tools the agent can use
)
```

## Configuration Options

### RunConfig Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | Model object | The LLM model to use |
| `model_provider` | Client | The API client |
| `tracing_disabled` | bool | Enable/disable tracing |
| `max_steps` | int | Maximum steps for the agent |
| `temperature` | float | Creativity parameter (0.0-2.0) |

### Agent Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Unique name for the agent |
| `instructions` | str | System prompt/behavior instructions |
| `tools` | list | List of tools the agent can use |
| `description` | str | Optional description |

## Best Practices

### 1. Environment Variables
Always use environment variables for sensitive information:

```python
import os
from dotenv import load_dotenv

load_dotenv()
```

### 2. Error Handling
Include proper error handling in your agent functions:

```python
async def run_agent(query: str) -> str:
    try:
        response = await Runner.run(agent, query, run_config=config)
        return response.final_output
    except Exception as e:
        print(f"Agent error: {e}")
        return "Sorry, I encountered an error processing your request."
```

### 3. Tool Functions
Create well-defined tool functions:

```python
from agents import function_tool

@function_tool
def search_tool(query: str) -> str:
    """
    Search for information based on the query.
    """
    # Implementation here
    return results
```

### 4. Resource Management
Properly manage resources and connections:

```python
# Initialize tools and agents once, not on every request
# Use connection pooling where appropriate
# Consider caching for expensive operations
```

## Examples

### Simple Q&A Agent

```python
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
import os

# Initialize client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),

# Create run configuration
config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)

# Create agent
simple_agent = Agent(
    name="SimpleQA",
    instructions="You are a helpful assistant that answers questions concisely.",
)

# Run the agent
async def ask_question(question: str) -> str:
    response = await Runner.run(simple_agent, question, run_config=config)
    return response.final_output
```

### Agent with Tools

```python
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool
import os

# Define a tool
@function_tool
def calculator_tool(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.
    """
    try:
        # Safe evaluation (in real applications, use more secure methods)
        result = eval(expression)
        return str(result)
    except Exception:
        return "Error: Invalid expression"

# Initialize client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


# Create run configuration
config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)

# Create agent with tools
math_agent = Agent(
    name="MathAssistant",
    instructions="You are a math assistant. Use the calculator tool for complex calculations.",
    tools=[calculator_tool],
)
```

### Multi-Agent System

```python
# You can create multiple specialized agents
research_agent = Agent(
    name="Researcher",
    instructions="You are a research assistant that finds and summarizes information.",
    tools=[search_tool, web_scraping_tool]
)

writer_agent = Agent(
    name="Writer",
    instructions="You are a writing assistant that creates well-structured content.",
)

analyst_agent = Agent(
    name="Analyst",
    instructions="You are an analysis assistant that interprets data and provides insights.",
    tools=[data_analysis_tool]
)
```

### Real-World Example: Todo Management Agent

Here's a practical example of a Todo Management Agent that uses multiple tools to manage tasks:

```python
import os
import json
from typing import Dict, Any, Optional
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool

# Import your existing tools
from src.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

# Define wrapper functions with proper type hints for the agent
@function_tool
def add_task_agent_tool(title: str, description: Optional[str] = None, status: Optional[str] = "pending") -> Dict[str, Any]:
    """
    Add a new task to the todo list.

    Args:
        title: The title of the task (required)
        description: Detailed description of the task (optional)
        status: Status of the task, either 'pending' or 'completed' (default: 'pending')

    Returns:
        Dictionary with success status and task data
    """
    arguments = {"title": title}
    if description is not None:
        arguments["description"] = description
    if status is not None:
        arguments["status"] = status

    return add_task_tool(arguments)

@function_tool
def list_tasks_agent_tool(status_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve all tasks or filter by status.

    Args:
        status_filter: Filter tasks by status ('pending' or 'completed') (optional)

    Returns:
        Dictionary with success status and list of tasks
    """
    arguments = {}
    if status_filter is not None:
        arguments["status_filter"] = status_filter

    return list_tasks_tool(arguments)

@function_tool
def complete_task_agent_tool(task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete (required)

    Returns:
        Dictionary with success status and updated task
    """
    arguments = {"task_id": task_id}
    return complete_task_tool(arguments)

@function_tool
def delete_task_agent_tool(task_id: str) -> Dict[str, Any]:
    """
    Delete a task from the list.

    Args:
        task_id: The ID of the task to delete (required)

    Returns:
        Dictionary with success status and deleted task ID
    """
    arguments = {"task_id": task_id}
    return delete_task_tool(arguments)

@function_tool
def update_task_agent_tool(task_id: str, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Update properties of an existing task.

    Args:
        task_id: The ID of the task to update (required)
        title: The new title for the task (optional)
        description: The new description for the task (optional)
        status: The new status for the task (optional)

    Returns:
        Dictionary with success status and updated task
    """
    arguments = {"task_id": task_id}
    if title is not None:
        arguments["title"] = title
    if description is not None:
        arguments["description"] = description
    if status is not None:
        arguments["status"] = status

    return update_task_tool(arguments)

class TodoAgent:
    """
    AI Agent that interprets natural language and orchestrates MCP tool calls
    """

    def __init__(self):
        # Initialize OpenAI-compatible client for Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY environment variable not set")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",  # Gemini API endpoint
        )

        # Create model configuration for Gemini
        self.model = OpenAIChatCompletionsModel(  # Using the correct model class name from documentation
            model="gemini-2.5-flash",  # Using a Gemini model
            openai_client=self.client,
        )

        # Create run configuration
        self.config = RunConfig(
            model=self.model,
            model_provider=self.client,
            tracing_disabled=True,  # Set to False for debugging
        )

        # Create the agent with instructions and tools
        self.agent = Agent(
            name="TodoAssistant",
            instructions=(
                "You are a helpful assistant for managing tasks. "
                "Use the available tools to help the user manage their tasks. "
                "Only call functions when needed based on user requests. "
                "Always respond to the user in a friendly, helpful manner."
            ),
            tools=[
                add_task_agent_tool,
                list_tasks_agent_tool,
                complete_task_agent_tool,
                delete_task_agent_tool,
                update_task_agent_tool
            ],
        )

    async def process_message(self, user_message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Process a user message through the AI agent and return an appropriate response

        Args:
            user_message: The message from the user
            conversation_id: ID of the conversation for context

        Returns:
            Dictionary containing the response and any tool calls made
        """
        try:
            # Run the agent with the user message
            response = await Runner.run(self.agent, user_message, run_config=self.config)

            # Extract the final output from the response
            final_output = response.final_output if hasattr(response, 'final_output') else str(response)

            # Prepare the response
            result = {
                "success": True,
                "data": {
                    "response": final_output,
                    "conversation_id": conversation_id,
                    "tool_calls": []  # The SDK handles tool calls internally
                },
                "message": "Message processed successfully"
            }

            return result

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error processing message: {str(e)}"
            }
```

This example demonstrates:
- How to wrap existing MCP tools with `@function_tool` decorator
- How to create proper type hints for tool functions
- How to structure a real-world agent class
- How to handle errors appropriately
- How to maintain conversation context
- How to integrate with external systems (database, etc.)

## Advanced Topics

### Custom Models
You can use non-OpenAI models through providers like LiteLLM:

```python
# Using a different provider
client = AsyncOpenAI(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url="https://api.anthropic.com/v1",  # Example
)
```

### Streaming Responses
For real-time applications, you can stream responses:

```python
async def stream_agent_response(query: str):
    async for chunk in Runner.stream(agent, query, run_config=config):
        yield chunk
```

### State Management
Agents can maintain state between conversations:

```python
# For stateful agents, you may need to implement custom state management
# depending on your specific SDK implementation
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API key is properly set in environment variables
2. **Model Not Found**: Verify the model name is correct and available
3. **Tool Not Working**: Check that tool functions are properly decorated with `@function_tool`
4. **Rate Limits**: Implement proper retry logic and rate limiting

### Debugging Tips

- Enable tracing temporarily to see detailed execution logs
- Check environment variables are properly loaded
- Verify network connectivity to the API endpoint
- Test tools individually before integrating with agents