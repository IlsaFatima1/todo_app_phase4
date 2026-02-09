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
from src.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

load_dotenv()

logger = logging.getLogger(__name__)


class TodoAIError(Exception):
    """Custom exception for Todo AI operations"""
    pass


class TodoAgent:
    """
    AI Agent that interprets natural language and orchestrates MCP tool calls
    """

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
                        "You are a helpful task management assistant. Your role is to help users manage their to-do list naturally.\n\n"
                        "CORE PRINCIPLES:\n"
                        "- NEVER ask users for task IDs - always work with task names/titles\n"
                        "- Parse user intent from natural language and call the appropriate tools\n"
                        "- Be conversational and friendly in your responses\n"
                        "- Confirm actions after completing them\n\n"
                        "TOOL USAGE GUIDELINES:\n"
                        "1. ADD TASKS: When users say things like 'add', 'create', 'make a task', 'new task', extract the task title and use add_task_with_context\n"
                        "   - Examples: 'add buy groceries', 'create a task to call mom', 'make a task for the meeting'\n"
                        "   - Extract the task title from their message and add it\n\n"
                        "2. LIST TASKS: When users say 'list', 'show', 'see', 'what are my tasks', use list_tasks_with_context\n"
                        "   - If they specify 'pending' or 'completed', pass that as the status_filter parameter\n"
                        "   - Examples: 'show all tasks' (no filter), 'show pending tasks' (status_filter='pending'), 'show completed tasks' (status_filter='completed')\n"
                        "   - Present tasks in a friendly, readable format\n"
                        "   - If no tasks exist, let them know their list is empty\n\n"
                        "3. COMPLETE TASKS: When users say 'complete', 'done', 'finish', 'mark as done', use complete_task_with_context\n"
                        "   - Extract the task name from their message\n"
                        "   - Examples: 'complete buy groceries', 'mark wash car as done', 'finish the meeting task'\n\n"
                        "4. DELETE TASKS: When users say 'delete', 'remove', 'cancel', use delete_task_with_context\n"
                        "   - Extract the task name from their message\n"
                        "   - Examples: 'delete buy groceries', 'remove the car task', 'cancel meeting'\n\n"
                        "5. UPDATE TASKS: When users say 'update', 'edit', 'change', 'modify', use update_task_with_context\n"
                        "   - Extract both the old task name and the new title\n"
                        "   - Examples: 'update buy groceries to buy food', 'change car wash to house wash'\n\n"
                        "6. GREETINGS & GENERAL: For greetings or general questions, respond naturally without calling tools\n"
                        "   - Introduce yourself and your capabilities\n"
                        "   - Be helpful and guide users on what you can do\n\n"
                        "RESPONSE STYLE:\n"
                        "- Use natural, conversational language\n"
                        "- Confirm successful actions (e.g., 'I've added \"buy groceries\" to your list!')\n"
                        "- If you can't find a task, suggest alternatives or ask for clarification\n"
                        "- Keep responses concise but friendly"
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
        def add_task_with_context(title: str, description: Optional[str] = None, status: Optional[str] = "pending") -> str:
            """
            Add a new task to the todo list.

            Args:
                title: The title of the task (required)
                description: Detailed description of the task (optional)
                status: Status of the task, either 'pending' or 'completed' (default: 'pending')

            Returns:
                String message indicating success or failure
            """
            arguments = {"title": title}
            if description is not None:
                arguments["description"] = description
            if status is not None:
                arguments["status"] = status
            # IMPORTANT: Access self.default_user_id directly, not from closure
            current_user_id = self.default_user_id
            if current_user_id is not None:
                arguments["user_id"] = current_user_id
                logger.info(f"Adding task for user_id: {current_user_id}")

            result = add_task_tool(arguments)

            # Return a simple string response for the agent
            if result.get("success"):
                task_data = result.get("data", {})
                return f"Successfully added task '{task_data.get('title', title)}' to your list."
            else:
                return f"Failed to add task: {result.get('message', 'Unknown error')}"

        return add_task_with_context

    def _create_list_tasks_tool(self):
        """Create list tasks tool"""
        @function_tool
        def list_tasks_with_context(status_filter: Optional[str] = None) -> str:
            """
            Retrieve all tasks or filter by status.

            Args:
                status_filter: Filter tasks by status ('pending' or 'completed') (optional)

            Returns:
                String message with the list of tasks
            """
            arguments = {}
            if status_filter is not None:
                arguments["status_filter"] = status_filter

            # IMPORTANT: Access self.default_user_id directly, not from closure
            current_user_id = self.default_user_id
            if current_user_id is not None:
                arguments["user_id"] = current_user_id
                logger.info(f"Listing tasks for user_id: {current_user_id}")
            else:
                logger.warning("No default_user_id set, will use default from task_tools")

            result = list_tasks_tool(arguments)
            logger.info(f"List tasks result: {result}")

            # Return a simple string response for the agent
            if result.get("success"):
                tasks_data = result.get("data", {})
                tasks = tasks_data.get("tasks", [])
                if tasks:
                    task_list = "\n".join([f"- {task.get('title', 'Untitled')} (Status: {'Completed' if task.get('completed') else 'Pending'})" for task in tasks])
                    return f"You have {len(tasks)} task(s):\n{task_list}"
                else:
                    return "You don't have any tasks in your list."
            else:
                return f"Failed to retrieve tasks: {result.get('message', 'Unknown error')}"

        return list_tasks_with_context

    def _create_complete_task_tool(self):
        """Complete a task using NAME instead of ID"""
        @function_tool
        def complete_task_with_context(task_name: str) -> str:
            """
            Mark a task as completed by its name.

            Args:
                task_name: The name/title of the task to complete (required)

            Returns:
                String message indicating success or failure
            """
            arguments = {"task_name": task_name}

            # IMPORTANT: Access self.default_user_id directly, not from closure
            current_user_id = self.default_user_id
            if current_user_id is not None:
                arguments["user_id"] = current_user_id
                logger.info(f"Completing task for user_id: {current_user_id}")

            result = complete_task_tool(arguments)

            # Return a simple string response for the agent
            if result.get("success"):
                task_data = result.get("data", {})
                return f"Successfully marked task '{task_data.get('title', task_name)}' as completed."
            else:
                return f"Failed to complete task: {result.get('message', 'Unknown error')}"

        return complete_task_with_context

    def _create_delete_task_tool(self):
        """Delete task using NAME instead of ID"""
        @function_tool
        def delete_task_with_context(task_name: str) -> str:
            """
            Delete a task from the list by its name.

            Args:
                task_name: The name/title of the task to delete (required)

            Returns:
                String message indicating success or failure
            """
            arguments = {"task_name": task_name}

            # IMPORTANT: Access self.default_user_id directly, not from closure
            current_user_id = self.default_user_id
            if current_user_id is not None:
                arguments["user_id"] = current_user_id
                logger.info(f"Deleting task for user_id: {current_user_id}")

            result = delete_task_tool(arguments)

            # Return a simple string response for the agent
            if result.get("success"):
                return f"Successfully deleted task '{task_name}'."
            else:
                return f"Failed to delete task: {result.get('message', 'Unknown error')}"

        return delete_task_with_context


    def _create_update_task_tool(self):
        """Update task using NAME instead of ID"""
        @function_tool
        def update_task_with_context(task_name: str, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> str:
            """
            Update properties of an existing task by its name.

            Args:
                task_name: The name/title of the task to update (required)
                title: The new title for the task (optional)
                description: The new description for the task (optional)
                status: The new status for the task (optional)

            Returns:
                String message indicating success or failure
            """
            arguments = {"task_name": task_name}

            if title is not None:
                arguments["title"] = title
            if description is not None:
                arguments["description"] = description
            if status is not None:
                arguments["status"] = status

            # IMPORTANT: Access self.default_user_id directly, not from closure
            current_user_id = self.default_user_id
            if current_user_id is not None:
                arguments["user_id"] = current_user_id
                logger.info(f"Updating task for user_id: {current_user_id}")

            result = update_task_tool(arguments)

            # Return a simple string response for the agent
            if result.get("success"):
                task_data = result.get("data", {})
                updates = []
                if title:
                    updates.append(f"title to '{title}'")
                if description:
                    updates.append(f"description")
                if status:
                    updates.append(f"status to '{status}'")

                update_str = ", ".join(updates) if updates else "properties"
                return f"Successfully updated task '{task_name}' ({update_str})."
            else:
                return f"Failed to update task: {result.get('message', 'Unknown error')}"

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
            # Check if API is available
            if not self.api_available:
                return {
                    "success": False,
                    "data": None,
                    "message": "AI agent is not available. Please check GEMINI_API_KEY configuration."
                }

            # Update the agent's default user ID if a new one is provided
            old_default_user_id = self.default_user_id
            if user_id is not None:
                self.default_user_id = user_id
                logger.info(f"Updated agent default_user_id to: {user_id}")
            else:
                logger.warning(f"No user_id provided, using default: {self.default_user_id}")

            # Always use the AI agent - let it handle all queries dynamically
            logger.info(f"Processing message with agent for user {self.default_user_id}: {user_message}")
            response = await Runner.run(self.agent, user_message, run_config=self.config)
            logger.info(f"Agent response received: {response}")

            # Extract the final output from the response
            final_output = response.final_output if hasattr(response, 'final_output') else str(response)
            logger.info(f"Final output: {final_output}")

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
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "data": None,
                "message": f"Error processing message: {str(e)}"
            }
        finally:
            # Restore the old default user ID
            if user_id is not None:
                self.default_user_id = old_default_user_id
                logger.info(f"Restored agent default_user_id to: {old_default_user_id}")


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
