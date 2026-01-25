# Practical Agent Examples

This document provides practical examples of agents in real-world scenarios, including the RAG chatbot we built for the Physical AI & Humanoid Robotics textbook.

## Table of Contents
- [RAG Chatbot Agent](#rag-chatbot-agent)
- [Research Assistant](#research-assistant)
- [Code Review Agent](#code-review-agent)
- [Data Analysis Agent](#data-analysis-agent)
- [Content Creation Agent](#content-creation-agent)

## RAG Chatbot Agent

This is the agent we built for the Physical AI & Humanoid Robotics textbook project:

### Configuration

```python
import os
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from .tools import book_retriever  # Custom retrieval tool
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


config = RunConfig(
    model=model,  # Use the model object instead of string
    model_provider=client,
    tracing_disabled=True  # Disable tracing to avoid API key warnings
)

# Create the RAG agent
agent = Agent(
    name="BookRAGAgent",
    instructions=(
        "You are a RAG assistant for a technical book. "
        "Always use the retrieved context to answer. "
        "If the answer is not found, say you don't know."
    ),
    tools=[book_retriever],  # Custom tool for retrieving book content
)

# Async function to run the agent
async def run_agent(query: str) -> str:
    try:
        response = await Runner.run(agent, query, run_config=config)
        return response.final_output
    except Exception as e:
        return f"Agent error: {str(e)}"
```

## Todo AI Chatbot Agent (Real-World Implementation)

This is a real-world implementation of a Todo AI Chatbot that uses MCP tools for task management:

### Complete Implementation

```python
"""
AI Agent for Todo Chatbot using Google AI/Gemini
Maps natural language intents to MCP tool calls
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Import the proper agents SDK components for Google AI
from openai import OpenAI
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool

# Import the existing task tools
from src.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

logger = logging.getLogger(__name__)

# Define function tools for the agent using the proper @function_tool decorator
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


class TodoAIError(Exception):
    """Custom exception for Todo AI operations"""
    pass


class TodoAgent:
    """
    AI Agent that interprets natural language and orchestrates MCP tool calls
    """

    def __init__(self):
        # Initialize OpenAI-compatible client for Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise TodoAIError("GEMINI_API_KEY environment variable not set")

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
            logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error processing message: {str(e)}"
            }

    def confirm_action(self, action_description: str) -> bool:
        """
        Confirm with the user before executing potentially destructive actions

        Args:
            action_description: Description of the action to confirm

        Returns:
            True if user confirms, False otherwise
        """
        # In a real implementation, this would send a message to the user
        # and wait for their response. For now, we'll return True.
        logger.info(f"Action confirmation requested: {action_description}")
        return True  # Default to True for automated processing
```

This real-world implementation demonstrates:
- How to wrap existing MCP tools with `@function_tool` decorator
- How to structure a complete agent class with proper error handling
- How to integrate with external systems (database through MCP tools)
- How to maintain conversation context and state
- How to handle natural language processing for task management

### Custom Tool for Book Retrieval

```python
from agents import function_tool
from .retrieval import RetrievalSystem
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize ONCE (important)
_retrieval_system = None

def get_retrieval_system() -> RetrievalSystem:
    global _retrieval_system
    if _retrieval_system is None:
        _retrieval_system = RetrievalSystem(
            cohere_api_key=os.getenv("COHERE_API_KEY"),
            qdrant_url=os.getenv("QDRANT_URL", "localhost"),
            qdrant_port=int(os.getenv("QDRANT_PORT", 6333)),
            qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
            collection_name=os.getenv("QDRANT_COLLECTION", "rag_embedding"),
        )
    return _retrieval_system

@function_tool
def book_retriever(query: str) -> str:
    """
    Retrieve relevant book content for a user query.
    """
    retrieval_system = get_retrieval_system()

    try:
        results = retrieval_system.retrieve(query, top_k=6)

        if not results:
            return "No relevant content found in the book."

        # Keep output SMALL & clean (important for agents)
        chunks = []
        for r in results:
            chunks.append(r["content"])

        result = "\n\n".join(chunks)
        return result
    except Exception as e:
        raise e
```

### API Integration

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import os
from datetime import datetime

from rag_agent.agent import run_agent

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="RAG Chat API",
    version="1.0.0"
)

# CORS (frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        message = body.get("message")

        if not message:
            return JSONResponse(
                status_code=200,
                content={"answer": "No message provided"}
            )

        # Call the RAG agent
        answer = await run_agent(message)

        response = {
            "answer": str(answer),
            "created": int(time.time())
        }
        return response

    except Exception as e:
        logger.exception("Chat error")
        return JSONResponse(
            status_code=200,   # frontend-safe
            content={
                "answer": "Sorry, something went wrong. Please try again.",
                "error": str(e) if os.getenv("DEBUG") == "true" else None
            }
        )
```

## Research Assistant

An agent that helps with research tasks by combining web search, document analysis, and synthesis:

```python
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool
import requests
import os

@function_tool
def web_search_tool(query: str, num_results: int = 5) -> str:
    """
    Search the web for information on a topic.
    """
    # Implementation would use a search API like Google Custom Search
    # or other search service
    pass

@function_tool
def document_analyzer_tool(document_content: str, query: str) -> str:
    """
    Analyze a document and extract information relevant to the query.
    """
    # Implementation would use embedding search or LLM analysis
    pass

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)

research_agent = Agent(
    name="ResearchAssistant",
    instructions=(
        "You are a research assistant. When a user asks for information, "
        "first search the web for recent information, then analyze any "
        "provided documents, and finally synthesize a comprehensive answer. "
        "Always cite your sources and indicate the recency of information."
    ),
    tools=[web_search_tool, document_analyzer_tool],
)

async def research(query: str) -> str:
    response = await Runner.run(research_agent, query, run_config=config)
    return response.final_output
```

## Code Review Agent

An agent that helps with code review tasks:

```python
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool
import os

@function_tool
def code_analyzer_tool(code: str, language: str = "python") -> str:
    """
    Analyze code for potential issues, best practices, and improvements.
    """
    # Implementation would analyze code for:
    # - Syntax errors
    # - Security vulnerabilities
    # - Performance issues
    # - Best practice violations
    # - Code style issues
    pass

@function_tool
def test_generator_tool(code: str, language: str = "python") -> str:
    """
    Generate unit tests for the given code.
    """
    # Implementation would generate appropriate unit tests
    pass

code_review_agent = Agent(
    name="CodeReviewer",
    instructions=(
        "You are an expert code reviewer. Analyze the provided code for "
        "potential issues, suggest improvements, and generate appropriate "
        "tests. Focus on security, performance, readability, and maintainability. "
        "Provide specific, actionable feedback."
    ),
    tools=[code_analyzer_tool, test_generator_tool],
)

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


config = RunConfig(model=model, model_provider=client, tracing_disabled=True)
```

## Data Analysis Agent

An agent that helps with data analysis tasks:

```python
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool
import pandas as pd
import os

@function_tool
def data_loader_tool(file_path: str) -> str:
    """
    Load data from a file and return basic information about it.
    """
    try:
        df = pd.read_csv(file_path)
        info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": str(df.dtypes.to_dict()),
            "head": df.head().to_dict()
        }
        return str(info)
    except Exception as e:
        return f"Error loading data: {str(e)}"

@function_tool
def statistical_analysis_tool(data_summary: str, analysis_type: str) -> str:
    """
    Perform statistical analysis on the data.
    """
    # Implementation would perform various statistical analyses
    # based on the analysis_type parameter
    pass

@function_tool
def visualization_tool(data_summary: str, chart_type: str) -> str:
    """
    Generate visualization code for the data.
    """
    # Implementation would generate appropriate visualization code
    pass

data_analysis_agent = Agent(
    name="DataAnalyst",
    instructions=(
        "You are a data analyst. When provided with data, perform appropriate "
        "statistical analysis and suggest visualizations. Explain your findings "
        "in clear, non-technical terms when possible."
    ),
    tools=[data_loader_tool, statistical_analysis_tool, visualization_tool],
)
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


config = RunConfig(model=model, model_provider=client, tracing_disabled=True)
```

## Content Creation Agent

An agent that helps with content creation:

```python
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool
import os

@function_tool
def content_research_tool(topic: str, num_sources: int = 3) -> str:
    """
    Research a topic and return key points from reliable sources.
    """
    # Implementation would research the topic and return key information
    pass

@function_tool
def fact_checker_tool(content: str) -> str:
    """
    Check the facts in the provided content.
    """
    # Implementation would verify facts in the content
    pass

@function_tool
def seo_analyzer_tool(content: str, target_keywords: str) -> str:
    """
    Analyze content for SEO optimization.
    """
    # Implementation would analyze SEO elements
    pass

content_creation_agent = Agent(
    name="ContentCreator",
    instructions=(
        "You are a content creator. Create high-quality, engaging content "
        "based on the user's requirements. Research the topic thoroughly, "
        "ensure accuracy, and optimize for the target audience. "
        "Consider SEO when appropriate."
    ),
    tools=[content_research_tool, fact_checker_tool, seo_analyzer_tool],
)

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
),


config = RunConfig(model=model, model_provider=client, tracing_disabled=True)
```

## Best Practices for Each Use Case

### RAG Systems
- Use appropriate chunking strategies for document retrieval
- Implement caching for frequently accessed content
- Monitor retrieval quality and relevance
- Handle edge cases where no relevant content is found

### Research Assistants
- Always cite sources and indicate information recency
- Cross-reference multiple sources when possible
- Distinguish between facts and opinions
- Handle ambiguous queries by asking for clarification

### Code Review Agents
- Maintain consistency with team coding standards
- Prioritize security issues
- Provide both high-level architecture feedback and low-level implementation details
- Suggest specific, actionable improvements

### Data Analysis Agents
- Validate data quality before analysis
- Choose appropriate statistical methods
- Create clear, informative visualizations
- Explain statistical concepts in accessible terms

### Content Creation Agents
- Maintain brand voice and style guidelines
- Ensure factual accuracy
- Optimize for target audience and platform
- Consider accessibility and inclusivity

## Common Patterns

### Error Handling
Always implement proper error handling in your agents and tools:

```python
async def run_agent_with_error_handling(query: str) -> str:
    try:
        response = await Runner.run(agent, query, run_config=config)
        return response.final_output
    except Exception as e:
        print(f"Agent error: {e}")
        import traceback
        print(f"Error traceback: {traceback.format_exc()}")
        return "Sorry, I encountered an error processing your request."
```

### Tool Validation
Validate tool inputs to prevent errors:

```python
@function_tool
def validated_tool(param: str) -> str:
    """
    A tool with input validation.
    """
    if not param or len(param) > 1000:
        return "Error: Invalid parameter - must be provided and less than 1000 characters"

    # Process the valid input
    return f"Processed: {param[:50]}..."
```

### State Management
For agents that need to maintain context across conversations:

```python
class StatefulAgent:
    def __init__(self):
        self.conversation_history = []

    async def run_with_context(self, query: str) -> str:
        # Add current query to history
        self.conversation_history.append({"role": "user", "content": query})

        # Include history in agent run if supported by your SDK
        # Implementation depends on specific SDK capabilities
        pass
```