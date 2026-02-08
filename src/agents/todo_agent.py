"""
AI Agent for Todo Chatbot using Google AI/Gemini
Maps natural language intents to MCP tool calls
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv
# Import the proper agents SDK components for Google AI
from openai import OpenAI
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents import function_tool

# Import the existing task tools
from ..tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

load_dotenv()

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
def complete_task_agent_tool(task_id: str, task_name:str) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
      
        task_name: The name of the task to complete (required)
        mark the task as complete based on task name 

    Returns:
        Dictionary with success status and updated task
    """
    arguments = {"task_name": task_name}
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

    def __init__(self, default_user_id: Optional[int] = None):
        # Initialize OpenAI-compatible client for Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Instead of raising an error, set a flag indicating API is not available
            self.api_available = False
            logger.warning("GEMINI_API_KEY environment variable not set. AI features will be disabled.")
        else:
            self.api_available = True
            try:
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
                # We'll create dynamic tools that can use the default user ID
                self.agent = Agent(
                    name="TodoAssistant",
                    instructions=(
                        "You are a helpful assistant for managing tasks. "
                        "Use the available tools to help the user manage their tasks. "
                        "NEVER ask for task IDs. Always find tasks by their title/name. "
                        "Use the delete_task_with_context, complete_task_with_context, and update_task_with_context tools "
                        "which take task names, not IDs. "
                        "Only call functions when needed based on user requests. "
                        "Always respond to the user in a friendly, helpful manner."
                    ),
                    tools=[
                        self._create_add_task_tool(),
                        self._create_list_tasks_tool(),
                        self._create_complete_task_tool(),
                        self._create_delete_task_tool(),
                        self._create_update_task_tool()
                    ],
                )
            except Exception as e:
                logger.error(f"Error initializing AI client: {str(e)}")
                self.api_available = False

        # Store the default user ID for context
        self.default_user_id = default_user_id

    def _create_add_task_tool(self):
        """Create add task tool with user context"""
        @function_tool
        def add_task_with_context(title: str, description: Optional[str] = None, status: Optional[str] = "pending") -> Dict[str, Any]:
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
            # Add the default user_id if available
            if self.default_user_id is not None:
                arguments["user_id"] = self.default_user_id

            return add_task_tool(arguments)
        return add_task_with_context

    def _create_list_tasks_tool(self):
        """Create list tasks tool"""
        @function_tool
        def list_tasks_with_context(status_filter: Optional[str] = None) -> Dict[str, Any]:
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
        return list_tasks_with_context

    def _create_complete_task_tool(self):
        """Complete a task using NAME instead of ID"""
        @function_tool
        def complete_task_with_context(task_name: str) -> Dict[str, Any]:
            # The complete_task_tool already accepts task_name, so we can call it directly
            arguments = {"task_name": task_name}

            if self.default_user_id is not None:
                arguments["user_id"] = self.default_user_id

            return complete_task_tool(arguments)

        return complete_task_with_context

    def _create_delete_task_tool(self):
        """Delete task using NAME instead of ID"""
        @function_tool
        def delete_task_with_context(task_name: str) -> Dict[str, Any]:
            all_tasks = list_tasks_tool({})
            tasks = all_tasks.get("data", {}).get("tasks", [])

            target = next((t for t in tasks if task_name.lower() in t["title"].lower()), None)

            if not target:
                return {"success": False, "message": f"Task '{task_name}' not found"}

            arguments = {"task_id": target["id"]}

            if self.default_user_id is not None:
                arguments["user_id"] = self.default_user_id

            return delete_task_tool(arguments)

        return delete_task_with_context


    def _create_update_task_tool(self):
        """Update task using NAME instead of ID"""
        @function_tool
        def update_task_with_context(task_name: str, title=None, description=None, status=None) -> Dict[str, Any]:

            # 1. find task by name
            all_tasks = list_tasks_tool({})
            tasks = all_tasks.get("data", {}).get("tasks", [])

            target = next((t for t in tasks if task_name.lower() in t["title"].lower()), None)

            if not target:
                return {"success": False, "message": f"Task '{task_name}' not found"}

            # 2. build arguments using ID
            arguments = {"task_id": target["id"]}

            if title is not None:
                arguments["title"] = title
            if description is not None:
                arguments["description"] = description
            if status is not None:
                arguments["status"] = status

            if self.default_user_id is not None:
                arguments["user_id"] = self.default_user_id

            return update_task_tool(arguments)

        return update_task_with_context

    async def process_message(self, user_message: str, conversation_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a user message through the AI agent and return an appropriate response

        Args:
            user_message: The message from the user
            conversation_id: ID of the conversation for context
            user_id: ID of the user for context (passed to tools)

        Returns:
            Dictionary containing the response and any tool calls made
        """
        try:
            # Update the agent's default user ID if a new one is provided
            old_default_user_id = self.default_user_id
            if user_id is not None:
                self.default_user_id = user_id

            # For task management operations, always use our custom fallback logic
            # to ensure no ID requests are made
            lower_msg = user_message.lower().strip()

            # Check if this is a task management request
            task_management_keywords = ['add', 'create', 'delete', 'remove', 'complete', 'done', 'finish', 'update', 'edit']
            is_task_related = any(keyword in lower_msg for keyword in task_management_keywords)

            if is_task_related:
                # Use our custom fallback logic to ensure no ID requests
                return self._handle_fallback_response(user_message, conversation_id, user_id)
            else:
                # For non-task related queries, try the AI agent
                try:
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

                except Exception as api_error:
                    logger.warning(f"API error (likely rate limit or network): {str(api_error)}")

                    # Fallback for non-task related queries too
                    return self._handle_fallback_response(user_message, conversation_id, user_id)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error processing message: {str(e)}"
            }
        finally:
            # Restore the old default user ID
            self.default_user_id = old_default_user_id

    def _handle_fallback_response(self, user_message: str, conversation_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Fallback method to handle user messages when API is unavailable.
        Parses the message and calls appropriate tools directly.

        Args:
            user_message: The message from the user
            conversation_id: ID of the conversation for context
            user_id: ID of the user for context (passed to tools)

        Returns:
            Dictionary containing the response and any tool calls made
        """
        import re

        # Convert user_message to lowercase for easier parsing
        lower_msg = user_message.lower().strip()

        # Parse the message to determine intent
        if any(word in lower_msg for word in ['add', 'create', 'make', 'new']):
            # Improved regex to extract task title after common phrases
            # Look for patterns like "add task to X", "add X", "create X", etc.
            task_title = ""

            # First, remove common prefixes
            cleaned_msg = user_message.strip()
            for prefix in ['add task to ', 'add a task to ', 'add task ', 'add a task ', 'add to ', 'add ', 'create task to ', 'create a task to ', 'create task ', 'create a task ', 'create to ', 'create ', 'make task ', 'make a task ', 'make ']:
                if cleaned_msg.lower().startswith(prefix):
                    task_title = cleaned_msg[len(prefix):].strip()
                    break

            if not task_title:
                # If no prefix matched, try to extract from other patterns
                # Look for "to [task]" pattern
                match = re.search(r'\b(to|that|for)\s+(.+?)(?:\s+and\s+|\s+or\s+|$)', user_message, re.IGNORECASE)
                if match:
                    task_title = match.group(2).strip()
                else:
                    # Just take everything after the first word if it contains action words
                    parts = user_message.split(None, 1)
                    if len(parts) > 1:
                        task_title = parts[1].strip()

            if task_title:
                # Clean up the task title by removing common trailing words
                task_title = re.sub(r'\.$', '', task_title)  # Remove trailing period
                # Remove common trailing phrases
                task_title = re.sub(r'\s+to\s+me$', '', task_title, flags=re.IGNORECASE)

                # Call add_task_tool directly with user_id
                tool_args = {"title": task_title}
                if user_id is not None:
                    tool_args["user_id"] = user_id

                result = add_task_tool(tool_args)

                if result.get("success"):
                    task_data = result.get("data", {})
                    response_text = f'OK. I\'ve added "{task_data.get("title", task_title)}" to your to-do list! Anything else?'
                else:
                    response_text = f'Sorry, I had trouble adding that task: {result.get("message", "Unknown error")}'
            else:
                response_text = "Sure, I can help you add a task. What would you like to add?"

        elif any(word in lower_msg for word in ['list', 'show', 'see', 'my']):
            # Call list_tasks_tool
            result = list_tasks_tool({})
            if result.get("success"):
                tasks_data = result.get("data", {})
                tasks = tasks_data.get("tasks", [])
                if tasks:
                    task_titles = [task.get("title", "Untitled") for task in tasks]
                    response_text = f"You have {len(tasks)} tasks: {', '.join(task_titles)}."
                else:
                    response_text = "You don't have any tasks on your list right now."
            else:
                response_text = f"Sorry, I couldn't retrieve your tasks: {result.get('message', 'Unknown error')}"

        elif any(word in lower_msg for word in ['complete', 'done', 'finish', 'finished', 'mark']):
            # Try to find a task by title mentioned in the message
            # Look for patterns like "complete task X", "mark X as done", "mark X", etc.
            import re

            # More flexible patterns to match various phrasings like:
            # "complete the task to wash the car", "mark wash the car", "finish the task wash the car", etc.
            task_patterns = [
                r'(?:complete|done|finish|finished|mark)\s+(?:the\s+|a\s+)?task\s+(?:to\s+)?(.+?)(?:\s+(?:as\s+)?(?:complete|done|finished))?(?:\s+task)?$',  # "complete task to X", "mark the task X", "finish task X task", "mark task X as complete"
                r'(?:complete|done|finish|finished|mark)\s+(?:the\s+|a\s+)?(.+?)\s+task$',  # "complete X task", "mark X task"
                r'(?:complete|done|finish|finished|mark)\s+(?:task\s+to\s+|to\s+)?(.+?)(?:\s+(?:as\s+)?(?:complete|done|finished))?$',  # "complete to X", "mark task to X", "finish X", "mark X as complete"
                r'(?:complete|done|finish|finished|mark)\s+(.+?)(?:\s+(?:as\s+)?(?:complete|done|finished))?$',  # "complete X", "mark X", "finish X", "mark X as complete"
                r'(?:the\s+)?task\s+to\s+(.+?)\s+(?:is\s+)?(?:complete|done|finished|marked)$',  # "task to X is done", "the task to X is marked"
                r'(?:make|set)\s+(?:the\s+)?(.+?)\s+(?:as\s+)?(?:complete|done|finished)$',  # "make X done", "set X as complete"
            ]

            task_title = None
            for pattern in task_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    task_title = match.group(1).strip()
                    break

            # Additional pattern: "mark X" where X is the task name without "as done" or similar
            # This is a special case for "mark X as complete" pattern
            if not task_title and 'mark' in lower_msg and ' as ' in lower_msg:
                # Handle "mark X as complete/done/finished" pattern
                mark_as_match = re.search(r'^mark\s+(.+?)\s+as\s+(?:complete|done|finished)', user_message, re.IGNORECASE)
                if mark_as_match:
                    task_title = mark_as_match.group(1).strip()

            if task_title:
                # Clean up common phrases that might be included
                # Remove common trailing/included words
                task_title = re.sub(r'\s+task$', '', task_title, flags=re.IGNORECASE)  # Remove trailing "task"
                task_title = re.sub(r'^to\s+', '', task_title, flags=re.IGNORECASE)     # Remove leading "to "
                task_title = re.sub(r'\s+(?:as\s+)?(?:done|complete|finished)$', '', task_title, flags=re.IGNORECASE)  # Remove "as done", "done", etc.

                # First, list all tasks to find the one to complete
                list_result = list_tasks_tool({})
                if list_result.get("success"):
                    tasks = list_result.get("data", {}).get("tasks", [])
                    target_task = None

                    # Find task by title (case-insensitive, partial match)
                    for task in tasks:
                        if task_title.lower() in task.get("title", "").lower():
                            target_task = task
                            break

                    # If no exact match, try to find by partial word matching
                    if not target_task:
                        for task in tasks:
                            # Split both the search term and task title into words and check for partial matches
                            search_words = set(task_title.lower().split())
                            task_words = set(task.get("title", "").lower().split())
                            # If at least half of the words match, consider it a match
                            if len(search_words.intersection(task_words)) >= max(1, len(search_words) // 2):
                                target_task = task
                                break

                    if target_task:
                        # Complete the task - use task name instead of ID for the updated tool
                        tool_args = {"task_name": task_title}
                        if user_id is not None:
                            tool_args["user_id"] = user_id

                        result = complete_task_tool(tool_args)

                        if result.get("success"):
                            response_text = f'I\'ve marked "{target_task["title"]}" as complete!'
                        else:
                            response_text = f'Sorry, I had trouble completing that task: {result.get("message", "Unknown error")}'
                    else:
                        response_text = f"I couldn't find a task containing '{task_title}' in your list."
                else:
                    response_text = f"Sorry, I couldn't retrieve your tasks to complete '{task_title}'."
            else:
                response_text = "I couldn't identify which task you'd like to complete. Please mention the task name."

        elif any(word in lower_msg for word in ['delete', 'remove']):
            # Try to find a task by title mentioned in the message
            # Look for patterns like "delete task X", "delete X task", "remove X", etc.
            import re

            # More flexible pattern to match various phrasings like:
            # "delete the task to wash the car", "delete wash the car task", "delete task wash the car", etc.
            task_patterns = [
                r'(?:delete|remove|cancel)\s+(?:the\s+|a\s+)?task\s+(?:to\s+)?(.+?)(?:\s+task)?$',  # "delete task to X", "delete the task X", "delete task X task"
                r'(?:delete|remove|cancel)\s+(?:the\s+|a\s+)?(.+?)\s+task$',  # "delete X task"
                r'(?:delete|remove|cancel)\s+(?:task\s+to\s+|to\s+)?(.+)$',  # "delete to X", "delete task to X"
                r'(?:delete|remove|cancel)\s+(.+)$'  # "delete X"
            ]

            task_title = None
            for pattern in task_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    task_title = match.group(1).strip()
                    break

            if task_title:
                # Clean up common phrases that might be included
                # Remove common trailing/included words
                task_title = re.sub(r'\s+task$', '', task_title, flags=re.IGNORECASE)  # Remove trailing "task"
                task_title = re.sub(r'^to\s+', '', task_title, flags=re.IGNORECASE)     # Remove leading "to "
                task_title = re.sub(r'\s+(?:from|off|out)\s+(?:my\s+)?(?:to-do\s+|todo\s+)?list$', '', task_title, flags=re.IGNORECASE)  # Remove "from my list", etc.

                # First, list all tasks to find the one to delete
                list_result = list_tasks_tool({})
                if list_result.get("success"):
                    tasks = list_result.get("data", {}).get("tasks", [])
                    target_task = None

                    # Find task by title (case-insensitive, partial match)
                    for task in tasks:
                        if task_title.lower() in task.get("title", "").lower():
                            target_task = task
                            break

                    # If no exact match, try to find by partial word matching
                    if not target_task:
                        for task in tasks:
                            # Split both the search term and task title into words and check for partial matches
                            search_words = set(task_title.lower().split())
                            task_words = set(task.get("title", "").lower().split())
                            # If at least half of the words match, consider it a match
                            if len(search_words.intersection(task_words)) >= max(1, len(search_words) // 2):
                                target_task = task
                                break

                    if target_task:
                        # Delete the task - use task name instead of ID for the updated tool
                        tool_args = {"task_name": target_task["title"]}
                        if user_id is not None:
                            tool_args["user_id"] = user_id

                        result = delete_task_tool(tool_args)

                        if result.get("success"):
                            response_text = f'I\'ve deleted "{target_task["title"]}" from your to-do list!'
                        else:
                            response_text = f'Sorry, I had trouble deleting that task: {result.get("message", "Unknown error")}'
                    else:
                        response_text = f"I couldn't find a task containing '{task_title}' in your list."
                else:
                    response_text = f"Sorry, I couldn't retrieve your tasks to delete '{task_title}'."
            else:
                response_text = "I couldn't identify which task you'd like to delete. Please mention the task name."

        elif any(word in lower_msg for word in ['hello', 'hi', 'hey', 'greet']):
            response_text = "Hello! I'm your task management assistant. How can I help you today?"

        elif any(word in lower_msg for word in ['edit', 'update', 'change', 'modify']):
            # Try to find a task by title mentioned in the message and update it
            # Look for patterns like "edit task X to Y", "update X to Y", "change X to Y", etc.
            import re

            # More flexible patterns to match various phrasings like:
            # "update the task to wash the car to wash the house", "edit wash the car to wash the cloth", etc.
            edit_patterns = [
                r'(?:edit|update|change|modify)\s+(?:the\s+|a\s+)?task\s+(?:to\s+)?(.+?)\s+(?:to|in to|into)\s+(.+)',  # "update task to X to Y", "edit the task X to Y"
                r'(?:edit|update|change|modify)\s+(.+?)\s+(?:to|in to|into)\s+(.+)',  # "update X to Y", "edit X to Y"
                r'(.+?)\s+(?:edited|updated|changed)\s+(?:to|in to|into)\s+(.+)',  # "X edited to Y", "X updated to Y"
                r'(?:edit|update|change|modify)\s+(?:task\s+)?(.+)',  # "update X" (when user doesn't specify what to change it to)
            ]

            old_task_title = None
            new_task_title = None

            for pattern in edit_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        old_task_title = match.group(1).strip()
                        new_task_title = match.group(2).strip()
                    elif len(match.groups()) == 1 and 'to' not in user_message.lower():
                        # Special case: only found one group and no "to" in message (meaning user wants to edit but didn't specify what to)
                        old_task_title = match.group(1).strip()
                    break

            if old_task_title:
                # Clean up common phrases that might be included
                old_task_title = re.sub(r'\s+task$', '', old_task_title, flags=re.IGNORECASE)  # Remove trailing "task"
                old_task_title = re.sub(r'^to\s+', '', old_task_title, flags=re.IGNORECASE)     # Remove leading "to "

                if new_task_title:
                    new_task_title = new_task_title.strip()

                # First, list all tasks to find the one to update
                list_result = list_tasks_tool({})
                if list_result.get("success"):
                    tasks = list_result.get("data", {}).get("tasks", [])
                    target_task = None

                    # Find task by title (case-insensitive, partial match)
                    for task in tasks:
                        if old_task_title.lower() in task.get("title", "").lower():
                            target_task = task
                            break

                    # If no exact match, try to find by partial word matching
                    if not target_task:
                        for task in tasks:
                            # Split both the search term and task title into words and check for partial matches
                            search_words = set(old_task_title.lower().split())
                            task_words = set(task.get("title", "").lower().split())
                            # If at least half of the words match, consider it a match
                            if len(search_words.intersection(task_words)) >= max(1, len(search_words) // 2):
                                target_task = task
                                break

                    if target_task:
                        if new_task_title:
                            # Update the task - use task name instead of ID for the updated tool
                            tool_args = {
                                "task_name": old_task_title,
                                "title": new_task_title
                            }
                            if user_id is not None:
                                tool_args["user_id"] = user_id

                            result = update_task_tool(tool_args)

                            if result.get("success"):
                                response_text = f'I\'ve updated "{old_task_title}" to "{new_task_title}" in your to-do list!'
                            else:
                                response_text = f'Sorry, I had trouble updating that task: {result.get("message", "Unknown error")}'
                        else:
                            response_text = f"I found the task '{target_task['title']}', but I need to know what you'd like to change it to. Please specify the new task name."
                    else:
                        response_text = f"I couldn't find a task containing '{old_task_title}' in your list."
                else:
                    response_text = f"Sorry, I couldn't retrieve your tasks to update '{old_task_title}'."
            else:
                response_text = "I couldn't identify which task you'd like to edit. Please specify which task to edit and what to change it to. For example: 'Update wash the car to wash the house' or 'Change buy groceries to buy food'."

        else:
            response_text = "I'm your task management assistant. I can help you add, list, complete, delete, or update tasks by name. For example: 'Add a task to buy groceries', 'Complete wash the car', 'Delete wash the car', or 'Update wash the car to wash the house'."

        return {
            "success": True,
            "data": {
                "response": response_text,
                "conversation_id": conversation_id,
                "tool_calls": []  # No actual tool calls in fallback
            },
            "message": "Message processed successfully (fallback mode)"
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
