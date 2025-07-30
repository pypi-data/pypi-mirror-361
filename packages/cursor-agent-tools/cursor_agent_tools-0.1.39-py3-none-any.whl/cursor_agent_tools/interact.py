#!/usr/bin/env python3
"""
Interactive Agent Module for cursor_agent package.

This module provides functions for running interactive agent conversations,
allowing multi-step problem solving and task completion.
"""

import os
import sys
import time
import asyncio
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

from dotenv import load_dotenv

from .factory import create_agent
from .permissions import PermissionOptions
from .logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load environment variables from .env file
# Try to find the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.debug(f"Loaded environment variables from {env_path}")
else:
    # Try in the current directory
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.debug(f"Loaded environment variables from {env_path}")
    else:
        logger.debug("No .env file found")


# Add a NextAction class to better represent different continuation options
class ActionType(Enum):
    """Enumeration of possible next action types in the agent conversation."""
    COMPLETE = "complete"            # Task is complete, exit the loop
    USER_INPUT = "user_input"        # Agent needs user input to continue
    AUTO_CONTINUE = "auto_continue"  # Continue automatically
    MANUAL_CONTINUE = "manual"       # Prompt for user direction


class NextAction:
    """Represents the next action to take in the agent conversation."""
    def __init__(self, action_type: ActionType, prompt: Optional[str] = None):
        """
        Initialize a NextAction instance.

        Args:
            action_type: The type of action to take nex
            prompt: Optional prompt for user input (if action_type is USER_INPUT)
        """
        self.action_type = action_type
        self.prompt = prompt or ""  # Ensure prompt is always a string


# Define enhanced system prompt similar to what Cursor uses
CURSOR_SYSTEM_PROMPT = """
You are a powerful agentic AI coding assistant, powered by Claude. You operate in a coding environment.

You are pair programming with a USER to solve their coding task.
The task may require creating a new codebase, modifying or debugging an existing codebase, or simply answering a question.
Each time the USER sends a message, we automatically attach information about their current state, such as what files they have open, where their cursor is, recently viewed files, edit history in their session so far, and more.
This information may be relevant to the coding task, so consider it carefully.
Your main goal is to follow the USER's instructions at each message.

<tool_calling>
You have tools at your disposal to solve the coding task. Follow these rules regarding tool calls:
1. ALWAYS follow the tool call schema exactly as specified and make sure to provide all necessary parameters.
2. NEVER call tools that are not explicitly provided.
3. Only call tools when they are necessary. If the USER's task is general or you already know the answer, just respond without calling tools.
4. Before calling each tool, explain to the USER why you are calling it.
</tool_calling>

<making_code_changes>
When making code changes, NEVER output code to the USER, unless requested. Instead use the code edit tools to implement the change.
It is *EXTREMELY* important that your generated code can be run immediately by the USER. To ensure this, follow these instructions carefully:
1. Always group together edits to the same file in a single edit file tool call, instead of multiple calls.
2. If you're creating the codebase from scratch, create an appropriate dependency management file with package versions and a helpful README.
3. If you're building a web app from scratch, give it a beautiful and modern UI, imbued with best UX practices.
4. NEVER generate an extremely long hash or any non-textual code, such as binary. These are not helpful to the USER.
5. Unless you are appending some small edit to a file, or creating a new file, you MUST read the contents or section of what you're editing before editing it.
6. If you've introduced errors, fix them if clear how to. Do not make uneducated guesses.
</making_code_changes>

<searching_and_reading>
You have tools to search the codebase and read files. Follow these rules regarding tool calls:
1. If available, prefer the semantic search tool to grep search, file search, and list dir tools.
2. If you need to read a file, prefer to read larger sections of the file at once over multiple smaller calls.
3. If you have found a reasonable place to edit or answer, do not continue calling tools.
</searching_and_reading>

You MUST use the following format when citing code regions or blocks:
```12:15:app/components/Todo.tsx
// ... existing code ...
```
This is the ONLY acceptable format for code citations. The format is ```startLine:endLine:filepath where startLine and endLine are line numbers.

When breaking down complex tasks, consider each step carefully and use the appropriate tools for each part of the problem. Work iteratively toward a complete solution.
"""


# ANSI color codes for terminal output formatting
class Colors:
    HEADER = "\033[95m"  # Pink/Purple
    BLUE = "\033[94m"  # Blue
    CYAN = "\033[96m"  # Cyan
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    RED = "\033[91m"  # Red
    GRAY = "\033[90m"  # Gray
    ENDC = "\033[0m"  # End color
    BOLD = "\033[1m"  # Bold
    UNDERLINE = "\033[4m"  # Underline


async def print_status_before_agent(message: str, details: Optional[str] = None) -> None:
    """
    Simple utility function to print status messages before the agent is initialized.

    Args:
        message: The status message to prin
        details: Optional details to include
    """
    print(f"\nℹ️ {message}")
    if details:
        print(f"  {details}")


async def print_agent_information(agent: Any, information_type: str, content: str, details: Optional[Union[Dict[str, Any], str]] = None) -> None:
    """
    Print formatted information from the agent to the user using AI-generated formatting.
    Uses the agent itself to generate styling and formatting.

    Args:
        agent: The agent instance to use for generating formatted outpu
        information_type: Type of information (thinking, tool_call, tool_result, plan, etc.)
        content: The main content to display
        details: Optional details/metadata to display (dict or string)
    """
    try:
        # Convert details to a string representation if it's a dic
        details_str = ""
        if details:
            if isinstance(details, dict):
                details_str = "\n".join([f"{k}: {v}" for k, v in details.items()])
            else:
                details_str = str(details)

        # Create a temporary user info to avoid polluting the main conversation
        temp_user_info = {"temporary_context": True, "is_formatting_request": True}

        # Prepare the formatting promp
        format_prompt = f"""Format the following "{information_type}" information for console display:

CONTENT: {content}

{f"DETAILS: {details_str}" if details else ""}

Use ANSI color codes to style the output with appropriate colors depending on the type.
Thinking: Gray
Response: Green
Error: Red
Status: Cyan/Blue
Tools: Yellow
Plan: Green with numbering
File operation: Blue
Command: Green

Return ONLY the formatted text with ANSI codes that I can directly print to the console.
Do not include explanation text or markdown code blocks."""

        # Use the agent to generate the formatted outpu
        agent_response = await agent.chat(format_prompt, temp_user_info)

        # Handle structured response
        if isinstance(agent_response, dict):
            formatted_output = agent_response["message"]
        else:
            formatted_output = agent_response

        # Print the outpu
        print(formatted_output)

    except Exception:
        # Fallback to basic formatting if the agent call fails
        separator = "─" * 80
        print(f"\n{separator}")
        print(f"[{information_type.upper()}]: {content}")
        if details:
            print(f"Details: {details}")
        print(f"{separator}")


async def check_for_user_input_request(agent: Any, response: str) -> Union[str, bool]:
    """
    Use the AI to determine if the agent's response is explicitly requesting user input.

    Args:
        agent: The agent instance to use for analyzing the response
        response: The response from the agen

    Returns:
        False if no input is needed, or a string containing the input prompt if needed
    """
    logger.debug("Checking if response requests user input")
    try:
        # Create a temporary user info to avoid polluting the main conversation
        temp_user_info = {"temporary_context": True, "is_system_request": True}

        # Ask the agent to analyze if input is needed
        analysis_prompt = f"""Analyze the following AI assistant response and determine if it is explicitly requesting user input or clarification:

RESPONSE: {response}

Rules for determining if input is needed:
1. Look for direct questions that require an answer
2. Look for phrases like "could you provide", "can you provide", "please let me know", etc.
3. Ignore rhetorical questions or statements where the AI says "I could" or "I will"
4. Check for any explicit request for information, preference, decision, or guidance

If user input IS needed:
- Return a concise prompt to show the user that captures what information is being requested
- Format it as: "INPUT_NEEDED: your prompt here"

If user input is NOT needed:
- Return only: "NO_INPUT_NEEDED"
"""

        # Get the analysis from the agen
        logger.debug("Sending analysis prompt to agent")
        agent_response = await agent.chat(analysis_prompt, temp_user_info)

        # Handle structured response
        if isinstance(agent_response, dict):
            analysis = agent_response["message"]
        else:
            analysis = agent_response

        # Process the resul
        if "INPUT_NEEDED:" in analysis:
            # Extract the prompt from the response
            user_prompt = analysis.split("INPUT_NEEDED:", 1)[1].strip()
            logger.info(f"Input needed detected: {user_prompt}")
            return str(user_prompt)

        logger.debug("No input needed detected")
        return False

    except Exception as e:
        logger.warning(f"Error in check_for_user_input_request: {str(e)}")
        logger.info("Falling back to simpler input detection")
        # Fallback to simpler detection if the agent call fails
        # Check for common phrases that indicate the agent is asking for inpu
        input_request_phrases = [
            "could you provide", "can you provide", "please let me know",
            "what would you like", "how would you like", "do you have a preference"
        ]

        # Check for question marks (direct questions)
        if "?" in response:
            logger.info("Question mark detected in response - input needed")
            return "Please provide the requested information:"

        # Check for common phrases that request inpu
        for phrase in input_request_phrases:
            if phrase in response.lower():
                logger.info(f"Input request phrase detected: '{phrase}'")
                return "Please provide the requested information:"

        logger.debug("No input needed detected in fallback check")
        return False


async def run_single_query(agent: Any, query: str, user_info: Optional[Dict[str, Any]] = None, use_custom_system_prompt: bool = False) -> Union[str, Dict[str, Any]]:
    """
    Run a single query and return the response.

    Args:
        agent: The initialized agen
        query: The query to send
        user_info: Optional user context information
        use_custom_system_prompt: Whether to use the custom system promp

    Returns:
        Either the agent's response string or the structured response objec
    """
    logger.info("Running single query to agent")
    logger.debug(f"Query length: {len(query)} chars, using custom prompt: {use_custom_system_prompt}")

    try:
        # If we're using the custom system prompt, inject it into the agent
        if use_custom_system_prompt:
            logger.debug("Temporarily setting custom system prompt")
            original_system_prompt = agent.system_prompt
            agent.system_prompt = CURSOR_SYSTEM_PROMPT
            agent_response: Union[str, Dict[str, Any]] = await agent.chat(query, user_info)
            # Restore original system prompt
            logger.debug("Restoring original system prompt")
            agent.system_prompt = original_system_prompt
            return agent_response

        logger.debug("Sending query to agent with default system prompt")
        agent_response = await agent.chat(query, user_info)
        return agent_response
    except Exception as e:
        # Log error but still return something valid for the return type
        logger.error(f"Error in run_single_query: {str(e)}")
        if isinstance(e, ValueError) and str(e).startswith("Too many tokens"):
            logger.warning("Query too long for model, returning error message")
            return "Error: The query is too long for this model. Please make it shorter."
        return f"Error processing query: {str(e)}"


async def run_agent_interactive(
    model: str = "claude-3-5-sonnet-latest",
    initial_query: str = "",
    max_iterations: int = 10,
    auto_continue: bool = True,
    auto_continue_prompt: str = "auto continue",
    loop_delay: int = 5,
    tool_call_limit: int = 25,
    agent: Optional[Any] = None,
    on_iteration: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_user_info_update: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Union[str, Dict[str, Any]]:
    """
    Run the agent in interactive mode, allowing back-and-forth conversation.

    Args:
        model: The model to use (only used if agent not provided)
        initial_query: The initial task/query to send to the agent
        max_iterations: Maximum number of iterations to perform
        auto_continue: If True, continue automatically; otherwise prompt user after each step
        auto_continue_prompt: Custom prompt for auto-continuation
        loop_delay: Delay between iterations
        tool_call_limit: Maximum number of tool calls allowed throughout the entire session
        agent: Pre-configured agent instance (optional)
        on_iteration: Optional callback that receives data about each iteration
        on_user_info_update: Optional callback that receives updated user_info

    Returns:
        A summary of the conversation outcome or structured response with details
    """
    logger.info("Starting interactive agent session")
    logger.debug(f"Parameters: model={model}, max_iterations={max_iterations}, auto_continue={auto_continue}, tool_call_limit={tool_call_limit}")

    # Use provided agent or create one with default permissions
    if agent is None:
        await print_status_before_agent(f"Creating agent with model {model}...")
        logger.info(f"Creating new agent with model {model}")
        # Create agent with default permissions
        default_permissions = PermissionOptions(
            yolo_mode=False,
            command_allowlist=["ls", "cat"],
            delete_file_protection=True
        )
        agent = create_agent(model=model, permissions=default_permissions)
        agent.system_prompt = CURSOR_SYSTEM_PROMPT
        agent.register_default_tools()
    else:
        await print_status_before_agent("Using pre-configured agent")
        logger.info("Using pre-configured agent instance")

    # Now we can use the agent with our print function
    await print_agent_information(agent, "status", "Initializing conversation with initial task")
    await print_agent_information(agent, "status", "Task description", initial_query)
    logger.info("Initializing conversation with task: " + (initial_query[:100] + "..." if len(initial_query) > 100 else initial_query))

    # Initialize detailed conversation context (similar to Cursor)
    workspace_path = os.getcwd()
    user_info: Dict[str, Any] = {
        "open_files": [],  # Files currently open
        "cursor_position": None,  # Current cursor position
        "recent_files": [],  # Recently accessed files
        "os": sys.platform,  # OS information
        "workspace_path": workspace_path,  # Current workspace
        "command_history": [],  # Recently executed commands
        "tool_calls": [],  # History of tool calls
        "tool_results": [],  # Results of tool calls
        "file_contents": {},  # Cache of file contents
        "user_edits": [],  # Recent edits made by user
        "recent_errors": [],  # Recent errors encountered
    }

    # Track created/modified files to populate open_files
    created_or_modified_files: set[str] = set()

    # Multi-turn conversation loop
    iteration = 1
    query = initial_query

    # Track total tool calls made across all iterations
    total_tool_calls = 0

    # Prepend planning instructions only on first iteration
    if iteration == 1:
        await print_agent_information(agent, "thinking", "Breaking down the task and creating a plan...")
        query = f"""I'll help you complete this task step by step. I'll break it down and use tools like reading/creating/editing files and running commands as needed.

TASK: {initial_query}

First, I'll create a plan for how to approach this task, then implement it step by step.
"""

    while iteration <= max_iterations:
        await print_agent_information(agent, "status", f"Running iteration {iteration}/{max_iterations}")
        await print_agent_information(
            agent, "status", "Processing query", query[:100] + "..." if len(query) > 100 else query
        )

        try:
            # 1. Update workspace state
            user_info = update_workspace_state(user_info, created_or_modified_files)

            # Invoke callback with updated user_info if provided
            if on_user_info_update:
                logger.info(f"Calling on_user_info_update callback with user_info: {user_info}")
                try:
                    # Check if the callback is a coroutine function
                    if asyncio.iscoroutinefunction(on_user_info_update):
                        await on_user_info_update(user_info)
                    else:
                        on_user_info_update(user_info)
                except Exception as callback_error:
                    logger.warning(f"Error in on_user_info_update callback: {callback_error}")

            # 3. Process tool calls - returns updated tool call count and tool calls
            # Changed here - passing the full response object instead of extracted tool calls
            agent_response = await run_single_query(agent, query, user_info, use_custom_system_prompt=True)

            # Handle either string or structured response
            if isinstance(agent_response, dict):
                response = agent_response.get("message", "")
            else:
                response = str(agent_response)

            logger.info(f"Agent response: {agent_response}")
            # Update total tool calls across the entire session
            total_tool_calls, tool_calls = await process_tool_calls(
                agent, agent_response, user_info, created_or_modified_files, total_tool_calls
            )

            # 4. Check if global tool call limit reached
            continue_processing = await check_tool_call_limits(
                agent, total_tool_calls, tool_call_limit
            )

            if not continue_processing:
                # End the session if user doesn't want to continue
                logger.info(f"Ending session after reaching tool call limit ({total_tool_calls}/{tool_call_limit})")
                await print_agent_information(agent, "status", f"Session ended after reaching tool call limit ({total_tool_calls}/{tool_call_limit})")
                break

            # Check if we made tool calls in this iteration
            if len(tool_calls) > 0:
                logger.info(f"Made {len(tool_calls)} tool calls, will add to max_iterations")
                await print_agent_information(agent, "status", f"Made {len(tool_calls)} tool calls, will increase the max_iterations to {max_iterations + 1}")
                max_iterations += 1

            # 5. Determine next steps
            next_action = await determine_next_steps(agent, response, auto_continue, iteration)

            # 6. Handle different next actions
            if next_action.action_type == ActionType.COMPLETE:
                # Task complete, exit loop
                await print_agent_information(agent, "status", "Task has been completed successfully!")
                break

            elif next_action.action_type == ActionType.AUTO_CONTINUE:
                # Auto-continue to next step
                query = await get_continuation_prompt(agent, iteration, response, auto_continue_prompt)
                await print_agent_information(agent, "status", "Automatically continuing to next step...")
                await asyncio.sleep(loop_delay)  # Brief pause for readability

            elif next_action.action_type == ActionType.USER_INPUT:
                # Get user input and create continuation
                user_input = await get_user_input(next_action.prompt)
                query = await get_continuation_prompt(agent, iteration, response, user_input)
                iteration += 1
                continue

            elif next_action.action_type == ActionType.MANUAL_CONTINUE:
                # Get user direction for continuation
                await print_agent_information(agent, "response", "How can I help you further with this task? Please provide any guidance or specific requests.")
                user_input = await get_user_input(next_action.prompt)
                query = await get_continuation_prompt(agent, iteration, response, user_input)
                iteration += 1
                continue

            # 7. Manage context history
            user_info = await trim_context_history(user_info)

            # 8. Show progress messages
            await show_progress_messages(agent, auto_continue, response, iteration, max_iterations)

            # Invoke iteration callback if provided
            if on_iteration:
                # Convert NextAction to a serializable representation
                next_action_data = {
                    "action_type": next_action.action_type.name,
                    "prompt": next_action.prompt
                }

                iteration_data = {
                    "iteration": iteration,
                    "query": query,
                    "response": response,
                    "agent_response": agent_response,
                    "tool_calls": tool_calls,
                    "total_tool_calls": total_tool_calls,
                    "next_action": next_action_data
                }

                logger.info(f"Calling on_iteration callback with iteration data: {iteration_data}")
                try:
                    # Check if the callback is a coroutine function
                    if asyncio.iscoroutinefunction(on_iteration):
                        await on_iteration(iteration_data)
                    else:
                        on_iteration(iteration_data)
                except Exception as callback_error:
                    logger.warning(f"Error in on_iteration callback: {callback_error}")

            iteration += 1

        except Exception as e:
            # 9. Handle exceptions
            action = await handle_iteration_error(agent, e, iteration, user_info)

            if action == "RETRY":
                continue
            elif action == "CONTINUE_WITH_ERROR":
                query = f"There was an error in the previous step: {str(e)}. Please adjust your approach and continue."
                iteration += 1
            else:  # "END"
                break

    # End of conversation
    await print_agent_information(agent, "status", f"Conversation ended after {iteration - 1} iterations with {total_tool_calls} total tool calls.")
    logger.info(f"Interactive session complete: {iteration - 1} iterations, {total_tool_calls} tool calls")

    # Return a structured response with detailed information
    session_summary = f"Interactive session completed after {iteration-1} iterations with {total_tool_calls} tool calls."

    # Check if we have a final response
    final_message = response if 'response' in locals() else session_summary

    # Return detailed information if possible, or just the message for backward compatibility
    try:
        return {
            "message": final_message,
            "iterations": iteration - 1,
            "tool_calls": total_tool_calls,
            "user_info": user_info,
            "files_modified": list(created_or_modified_files),
            "final_response": agent_response if 'agent_response' in locals() else None
        }
    except Exception:
        # Fall back to simple string response for backward compatibility
        logger.warning("Error creating structured response, falling back to simple message")
        return {
            "message": final_message,
            "iterations": iteration - 1,
            "tool_calls": total_tool_calls or 0,
            "user_info": user_info or {},
            "files_modified": list(created_or_modified_files) or [],
            "final_response": agent_response if 'agent_response' in locals() else None
        }


def extract_tool_calls(response: str) -> List[Dict[str, Any]]:
    """
    Extract tool calls from the agent's response.

    Args:
        response: The response from the agent

    Returns:
        A list of tool call dictionaries
    """
    tool_calls = []

    # Simple extraction based on common patterns
    # In a real implementation, you would use more robust parsing

    # Look for patterns like "```python\nagent.create_file(...)" or "I'll create a file..."
    # followed by tool usage

    # This is a simplified example - Cursor uses more sophisticated parsing
    if "create_file" in response:
        # Extract file creation details
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "create_file" in line and i < len(lines) - 1:
                tool_calls.append(
                    {
                        "tool": "create_file",
                        "args": {
                            "file_path": (
                                lines[i + 1].strip().strip("\"'")
                                if "file_path" in line
                                else "unknown"
                            ),
                        },
                    }
                )

    if "edit_file" in response:
        # Extract file editing details
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "edit_file" in line and i < len(lines) - 1:
                tool_calls.append(
                    {
                        "tool": "edit_file",
                        "args": {
                            "target_file": (
                                lines[i + 1].strip().strip("\"'")
                                if "target_file" in line
                                else "unknown"
                            ),
                        },
                    }
                )

    if "run_terminal_cmd" in response:
        # Extract terminal commands
        lines = response.split("\n")
        for i, line in enumerate(lines):
            if "run_terminal_cmd" in line and i < len(lines) - 1:
                tool_calls.append(
                    {
                        "tool": "run_terminal_cmd",
                        "args": {
                            "command": (
                                lines[i + 1].strip().strip("\"'")
                                if "command" in line
                                else "unknown"
                            ),
                        },
                    }
                )

    return tool_calls


def is_task_complete(response: str) -> bool:
    """
    Analyze if the response suggests the task is complete.

    Args:
        response: The response from the agen

    Returns:
        True if the task appears to be complete, False otherwise
    """
    logger.debug("Checking if task is complete based on agent response")

    # Look for various forms of task completion statements
    completion_indicators = [
        "task complete",
        "task is complete",
        "completed all the required tasks",
        "successfully implemented all",
        "all requirements have been met",
        "implementation is now complete",
        "successfully created all the necessary",
        "the project is now ready",
        "everything is now implemented",
        "all features are now implemented",
    ]

    response_lower = response.lower()

    # Check for completion indicators with additional context check
    # (Cursor does more sophisticated analysis)
    for indicator in completion_indicators:
        if indicator in response_lower:
            # Check if it's a real completion and not part of a plan
            start_index = response_lower.index(indicator)
            end_index = min(start_index + 50, len(response_lower))
            if "next" not in response_lower[start_index:end_index]:
                logger.info(f"Task completion detected: '{indicator}'")
                return True

    # Check for summary sections that typically indicate completion
    if (
        "summary of what we've accomplished" in response_lower
        and "next steps" not in response_lower
    ):
        logger.info("Task completion detected: summary section without next steps")
        return True

    # Check for concluding sections
    if ("in conclusion" in response_lower or "to summarize" in response_lower) and (
        "all requirements" in response_lower or "all functionality" in response_lower
    ):
        logger.info("Task completion detected: conclusion section with requirements met")
        return True

    logger.debug("No task completion indicators detected")
    return False


async def get_continuation_prompt(agent: Any, iteration: int, last_response: str, user_input: Optional[str] = None) -> str:
    """
    Generate a continuation prompt for the next iteration.

    Args:
        agent: The agent instance
        iteration: Current iteration number
        last_response: Last response from the agen
        user_input: Optional user input to incorporate

    Returns:
        A prompt string for the agent to continue
    """
    try:
        # Create a temporary user info to avoid polluting the main conversation
        temp_user_info = {"temporary_context": True, "is_system_request": True}

        # Prepare the analysis prompt to determine the best continuation approach
        analysis_prompt = f"""You're helping implement a multi-step solution. Review the current status and determine how to continue.

    Current iteration: {iteration}
    Last response:
    {last_response}

    {f"User input for continuation: {user_input}" if user_input else "No additional user input provided."}

    What's the best continuation prompt for the next iteration? Consider:
    1. Summarize progress so far
    2. Identify next steps based on current status
    3. Incorporate any user inpu
    4. Frame the prompt to move the task forward

    Return ONLY the continuation prompt itself with no additional explanations or meta-text.
    """

        # Get the continuation prompt from the agen
        agent_response = await agent.chat(analysis_prompt, temp_user_info)

        # Handle structured response
        if isinstance(agent_response, dict):
            continuation_prompt: str = agent_response["message"]
        else:
            continuation_prompt = str(agent_response)

        # If user input was provided, make sure it's incorporated
        if user_input and user_input not in continuation_prompt:
            continuation_prompt = f"The user has provided the following input: '{user_input}'\n\n{continuation_prompt}"

        await print_agent_information(agent, "status", "Continuation prompt prepared for next iteration", continuation_prompt[:100] + "..." if len(continuation_prompt) > 100 else continuation_prompt)

        return continuation_prompt

    except Exception as ex:
        # If there's an error getting a continuation prompt, just return a simple fallback
        print(f"Error getting continuation prompt: {str(ex)}")
        # Return a default continuation promp
        return "Continue with the next steps based on the previous results."


def update_workspace_state(user_info: Dict[str, Any], created_or_modified_files: set) -> Dict[str, Any]:
    """
    Update the user_info with information about files that were created or modified.

    Args:
        user_info: The user information dictionary
        created_or_modified_files: Set of files that were created or modified

    Returns:
        Updated user_info dictionary
    """
    logger.debug("Updating workspace state")

    # Save the current workspace path
    workspace_path = user_info.get("workspace_path", os.getcwd())
    logger.debug(f"Current workspace path: {workspace_path}")

    # Update open_files with recently created/modified files
    # (in Cursor, this would reflect actually open files in the editor)
    if created_or_modified_files:
        logger.info(f"Updating open files with {len(created_or_modified_files)} created/modified files")
        if "open_files" not in user_info or not isinstance(user_info["open_files"], list):
            user_info["open_files"] = []

        for file_path in created_or_modified_files:
            if file_path not in user_info["open_files"]:
                user_info["open_files"].append(file_path)
                logger.debug(f"Added to open files: {file_path}")
                # Can't use async function in a sync function
                print(f"\n📄 File Operation: Added {file_path} to open files")

    # Simulate cursor position in the most recently modified file
    if "open_files" in user_info and isinstance(user_info["open_files"], list) and user_info["open_files"]:
        most_recent_file = user_info["open_files"][-1]
        try:
            line_count = 0
            with open(most_recent_file, "r") as f:
                line_count = len(f.readlines())

            user_info["cursor_position"] = {
                "file": most_recent_file,
                "line": min(10, line_count),  # Arbitrary position for simulation
                "column": 0,
            }
            logger.debug(f"Updated cursor position to file: {most_recent_file}, line: {min(10, line_count)}")
        except Exception as ex:
            logger.error(f"Error setting cursor position: {str(ex)}")
            print(f"Error setting cursor position: {str(ex)}")

    # Update list of recently modified files across the workspace
    logger.debug("Updating recent files list")
    recent_files = []
    try:
        for root, _, files in os.walk(workspace_path):
            for file in files:
                if file.endswith(
                    (".py", ".txt", ".md", ".json", ".yaml", ".yml", ".js", ".ts", ".html", ".css")
                ):
                    file_path = os.path.join(root, file)
                    try:
                        recent_files.append(
                            {"path": file_path, "modified": os.path.getmtime(file_path)}
                        )
                    except Exception as ex:
                        logger.warning(f"Error getting file info for {file_path}: {str(ex)}")
                        print(f"Error getting file info: {str(ex)}")

        # Sort by modification time and take the 10 most recen
        recent_files = sorted(recent_files, key=lambda x: x["modified"], reverse=True)[:10]
        recent_file_paths = [file["path"] for file in recent_files]
        user_info["recent_files"] = recent_file_paths
        logger.debug(f"Updated recent files list with {len(recent_file_paths)} files")

        # Update file_contents for open files
        # This is similar to how Cursor provides file contents in contex
        if "open_files" in user_info and isinstance(user_info["open_files"], list) and user_info["file_contents"] is not None:
            if not isinstance(user_info["file_contents"], dict):
                user_info["file_contents"] = {}

            logger.debug("Updating file contents cache")
            for file_path in user_info["open_files"]:
                try:
                    if os.path.isfile(file_path):
                        with open(file_path, "r") as f:
                            file_content = f.read()
                            user_info["file_contents"][file_path] = file_content
                            logger.debug(f"Cached contents of {file_path}: {len(file_content)} chars")
                except Exception as ex:
                    # Can't use async function in a sync function
                    logger.error(f"Error reading file {file_path}: {str(ex)}")
                    print(f"\n❌ Error: Error reading file {file_path}")
                    print(f"  {str(ex)}")

    except Exception as ex:
        # Can't use async function in a sync function
        logger.error(f"Error updating workspace state: {str(ex)}")
        print(f"\n❌ Error: Error updating workspace state: {str(ex)}")

    return user_info


async def run_agent_chat(
    model: str = "claude-3-5-sonnet-latest",
    query: str = "",
) -> str:
    """
    Run a simple one-shot agent chat.

    Args:
        model: The model to use (e.g., 'claude-3-5-sonnet-latest', 'gpt-4o')
        query: The query to send

    Returns:
        The agent's response
    """
    # Create and configure agen
    agent = create_agent(model=model)
    agent.register_default_tools()

    # Print promp
    await print_agent_information(agent, "status", f"Sending query to agent: {query}")
    agent_response = await agent.chat(query)

    # Handle either string or structured response
    if isinstance(agent_response, dict):
        response_text = agent_response["message"]
    else:
        response_text = agent_response

    await print_agent_information(agent, "response", response_text)

    return response_text


async def process_tool_calls(
    agent: Any,
    agent_response: Union[str, Dict[str, Any]],
    user_info: Dict[str, Any],
    created_or_modified_files: set,
    total_tool_calls: int
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Process tool calls from an agent response and update tracking information.

    Args:
        agent: The agent instance
        agent_response: Either a string response or a structured response dic
        user_info: User context information to update
        created_or_modified_files: Set of created/modified files to update
        total_tool_calls: Running total of tool calls across all iterations

    Returns:
        Tuple of (updated total tool calls, extracted tool calls list)
    """
    logger.info("Processing tool calls from agent response")

    # Extract tool calls from the response - check if it's a structured response or string
    if isinstance(agent_response, dict) and "tool_calls" in agent_response:
        # It's a structured response with tool_calls directly available
        logger.debug(f"Found {len(agent_response['tool_calls'])} tool calls in structured response")
        tool_calls = []
        for tc in agent_response['tool_calls']:
            # Convert to the format expected by the rest of the function
            tool_calls.append({
                "tool": tc["name"],
                "args": tc["parameters"],
                "result": tc["result"]
            })
    else:
        # It's a string response, need to extract tool calls from tex
        response_str = agent_response if isinstance(agent_response, str) else agent_response["message"]
        logger.debug("Extracting tool calls from text response")
        tool_calls = extract_tool_calls(response_str)
        logger.debug(f"Extracted {len(tool_calls)} tool calls from text")

    # Ensure total_tool_calls is an integer
    if not isinstance(total_tool_calls, int):
        total_tool_calls = 0
        logger.warning("Reset total_tool_calls to 0 because it was not an integer")

    for tool_call in tool_calls:
        tool_name = tool_call.get("tool", "")
        args = tool_call.get("args", {})

        # Ensure tool_name is a string
        logger.info(f"Processing tool call: {tool_name}")
        logger.debug(f"Tool arguments: {args}")
        await print_agent_information(agent, "tool_call", str(tool_name), args)

        # Make sure tool_calls is a list before appending
        if isinstance(user_info["tool_calls"], list):
            user_info["tool_calls"].append(tool_call)
        else:
            user_info["tool_calls"] = [tool_call]

        total_tool_calls += 1

        # Track file operations to update open_files
        if tool_call.get("tool") == "create_file" or tool_call.get("tool") == "edit_file":
            file_path = tool_call.get("args", {}).get("file_path") or tool_call.get(
                "args", {}
            ).get("target_file")
            if file_path:
                created_or_modified_files.add(file_path)
                logger.info(f"Tracked modified file: {file_path}")
                await print_agent_information(agent, "file_operation", f"Modified {file_path}")

        # Track terminal commands
        if tool_call.get("tool") == "run_terminal_cmd":
            command = tool_call.get("args", {}).get("command")
            if command:
                # Make sure command_history is a list before appending
                if isinstance(user_info["command_history"], list):
                    user_info["command_history"].append(command)
                else:
                    user_info["command_history"] = [command]
                # Convert command to string to ensure it's a valid type
                logger.info(f"Tracked terminal command: {command}")
                await print_agent_information(agent, "command", f"Executed command: {command}")

    logger.info(f"Processed {len(tool_calls)} tool calls, running total: {total_tool_calls}")
    return total_tool_calls, tool_calls


async def check_tool_call_limits(
    agent: Any,
    total_tool_calls: int,
    tool_call_limit: int
) -> bool:
    """
    Check if the tool call limit has been reached and ask the user whether to continue.

    Args:
        agent: The agent instance
        total_tool_calls: Total count of tool calls across all iterations
        tool_call_limit: Maximum allowed tool calls for the entire session

    Returns:
        True if continue_processing, False if end_session
    """
    logger.debug(f"Checking tool call limits: current={total_tool_calls}, max={tool_call_limit}")

    if total_tool_calls >= tool_call_limit:
        logger.info(f"Reached global tool call limit ({tool_call_limit})")
        await print_agent_information(
            agent,
            "status",
            f"Reached maximum of {tool_call_limit} total tool calls for this session"
        )
        print(f"\n{Colors.YELLOW}The agent has made {total_tool_calls} total tool calls in this session.{Colors.ENDC}")
        print(f"{Colors.YELLOW}Would you like to continue allowing the agent to make more changes?{Colors.ENDC}")
        choice = input(f"{Colors.GREEN}Continue? (y/n): {Colors.ENDC}")

        logger.info(f"User decision on continuing after max tool calls: {choice}")

        if choice.lower() != 'y':
            logger.info("User chose to stop after reaching tool call limit")
            await print_agent_information(agent, "status", "User requested to stop after reaching tool call limit.")
            return False
        else:
            # When user chooses to continue, we just let the function return True
            # The limit remains the same, but we allow more calls beyond the limi
            logger.info("User chose to continue beyond tool call limit")
            await print_agent_information(
                agent,
                "status",
                f"Continuing beyond the tool call limit. Current: {total_tool_calls}/{tool_call_limit}"
            )
            return True

    # If we haven't reached the limit yet, continue processing
    return True


async def get_user_input(prompt: str) -> str:
    """
    Get input from the user with colorized prompt.

    Args:
        prompt: The prompt to display to the user

    Returns:
        The user's inpu
    """
    logger.info(f"Requesting user input with prompt: {prompt}")
    user_input = input(f"{Colors.GREEN}{prompt} {Colors.ENDC}")
    logger.debug(f"Received user input: {user_input}")
    return user_input


async def trim_context_history(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim the history in user_info to prevent context overflow.

    Args:
        user_info: The user context information

    Returns:
        Updated user_info with trimmed history
    """
    logger.debug("Trimming context history to prevent overflow")

    # Limit length of tool calls history
    if isinstance(user_info["tool_calls"], list) and len(user_info["tool_calls"]) > 10:
        logger.debug(f"Trimming tool calls from {len(user_info['tool_calls'])} to 10")
        user_info["tool_calls"] = user_info["tool_calls"][-10:]

    # Limit length of command history
    if isinstance(user_info["command_history"], list) and len(user_info["command_history"]) > 5:
        logger.debug(f"Trimming command history from {len(user_info['command_history'])} to 5")
        user_info["command_history"] = user_info["command_history"][-5:]

    return user_info


async def show_progress_messages(
    agent: Any,
    auto_continue: bool,
    response: str,
    iteration: int,
    max_iterations: int
) -> None:
    """
    Show appropriate progress messages based on the current state.

    Args:
        agent: The agent instance
        auto_continue: Whether the agent is in auto-continue mode
        response: The agent's response
        iteration: Current iteration number
        max_iterations: Maximum iterations
    """
    # Print a message if the task seems to be in progress
    if auto_continue and "in progress" in response.lower() and iteration < max_iterations:
        print(f"{Colors.YELLOW}Task appears to be in progress. Continuing automatically...{Colors.ENDC}")

    # If this was the last iteration, inform the user
    if iteration >= max_iterations:
        print(f"{Colors.RED}Reached maximum iterations ({max_iterations}). Pausing.{Colors.ENDC}")


async def determine_next_steps(
    agent: Any,
    response: str,
    auto_continue: bool,
    iteration: int
) -> NextAction:
    """
    Determine the next steps based on the agent's response.

    Args:
        agent: The agent instance
        response: The response from the agen
        auto_continue: Whether auto-continue is enabled
        iteration: Current iteration number

    Returns:
        A NextAction instance indicating what to do nex
    """
    logger.debug(f"Determining next steps for iteration {iteration}")

    # Check if task is complete
    if is_task_complete(response):
        logger.info("Task completion detected - ending interactive session")
        return NextAction(ActionType.COMPLETE)

    # Determine continuation based on mode
    if auto_continue:
        logger.info("Auto-continue enabled - continuing automatically")
        return NextAction(ActionType.AUTO_CONTINUE)

    # Check if agent is asking for inpu
    user_input_request = await check_for_user_input_request(agent, response)
    if user_input_request and isinstance(user_input_request, str):
        logger.info("Agent is requesting user input")
        logger.debug(f"Input request: {user_input_request}")
        await print_agent_information(agent, "status", "The agent is requesting additional information from you.")
        return NextAction(ActionType.USER_INPUT, prompt=user_input_request)
    else:
        logger.info("Continuing with manual user input")
        # Ensure prompt is explicitly a string to avoid type error
        input_prompt: str = "Your input: "
        return NextAction(ActionType.MANUAL_CONTINUE, prompt=input_prompt)


async def handle_iteration_error(
    agent: Any,
    error: Exception,
    iteration: int,
    user_info: Dict[str, Any]
) -> str:
    """
    Handle exceptions that occur during an iteration.

    Args:
        agent: The agent instance
        error: The exception that occurred
        iteration: Current iteration number
        user_info: User context information to update

    Returns:
        Action to take: "RETRY", "CONTINUE_WITH_ERROR", or "END"
    """
    logger.error(f"Error in iteration {iteration}: {str(error)}")
    logger.debug(f"Error type: {type(error).__name__}")

    await print_agent_information(agent, "error", f"Error in iteration {iteration}", str(error))
    user_info["recent_errors"].append(str(error))

    print(f"\n{Colors.YELLOW}Options:{Colors.ENDC}")
    print(f"{Colors.YELLOW}1. Retry this iteration{Colors.ENDC}")
    print(f"{Colors.YELLOW}2. Continue with error information{Colors.ENDC}")
    print(f"{Colors.YELLOW}3. End the conversation{Colors.ENDC}")
    choice = input(f"{Colors.GREEN}Enter your choice (1-3): {Colors.ENDC}")

    logger.info(f"User chose error handling option: {choice}")

    if choice == "1":
        logger.info("Retrying iteration")
        return "RETRY"
    elif choice == "2":
        logger.info("Continuing with error information")
        return "CONTINUE_WITH_ERROR"
    else:
        logger.info("Ending conversation due to error")
        return "END"


async def process_query_and_get_response(
    agent: Any,
    query: str,
    user_info: Dict[str, Any]
) -> Tuple[str, float]:
    """
    Process a query and get the agent's response.

    Args:
        agent: The agent instance
        query: The query to send
        user_info: User context information

    Returns:
        Tuple of (response, duration)
    """
    logger.info("Processing query and getting response")
    logger.debug(f"Query length: {len(query)} chars")

    # Show thinking animation
    await print_agent_information(agent, "thinking", "Processing your request...")

    # Get agent response with Cursor-like system promp
    start_time = time.time()

    # Use the enhanced system prompt (like Cursor does)
    logger.debug("Sending query to agent with enhanced system prompt")
    agent_response: Union[str, Dict[str, Any]] = await run_single_query(
        agent, query, user_info, use_custom_system_prompt=True
    )

    # Handle either string or structured response
    if isinstance(agent_response, dict):
        logger.debug("Received structured response from agent")
        response = agent_response["message"]
    else:
        logger.debug("Received string response from agent")
        response = agent_response

    duration = time.time() - start_time
    logger.info(f"Response generated in {duration:.2f} seconds")
    logger.debug(f"Response length: {len(response)} chars")

    # Print full response
    await print_agent_information(agent, "response", response)
    await print_agent_information(agent, "status", f"Response generated in {duration:.2f} seconds")

    return response, duration


# Main entry point and argument handling remain in the original main.py file
# This module is designed to be imported and used by other modules
