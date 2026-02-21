"""
Main agent controller - the autonomous loop that drives task execution.
"""

from typing import List, Optional
from ..llm.base import BaseLLM, Message, LLMResponse
from ..tools.registry import ToolRegistry
from .planner import TaskPlanner, StepStatus
import json


class AgentController:
    """
    Main controller for the autonomous coding agent.
    Implements the core agent loop: plan -> act -> observe -> repeat.
    """

    def __init__(
        self,
        llm: BaseLLM,
        tool_registry: ToolRegistry,
        max_steps: int = 50,
        max_tool_errors: int = 5
    ):
        self.llm = llm
        self.tool_registry = tool_registry
        self.planner = TaskPlanner()
        self.max_steps = max_steps
        self.max_tool_errors = max_tool_errors

        # State tracking
        self.conversation_history: List[Message] = []
        self.step_count = 0
        self.tool_error_count = 0
        self.is_task_complete = False

    def execute_task(self, user_request: str) -> str:
        """
        Execute a task from start to finish.

        Agent Loop:
        1. Get LLM response (may include reasoning + tool calls)
        2. If tool calls exist, execute them
        3. Feed results back to LLM
        4. Repeat until task complete or max steps reached

        Args:
            user_request: The user's task description

        Returns:
            Final response or status message
        """
        print(f"\n[Agent] Starting task: {user_request}\n")

        # Initialize conversation
        self.conversation_history = [
            Message(role="user", content=user_request)
        ]

        # Main agent loop
        while not self.is_task_complete and self.step_count < self.max_steps:
            self.step_count += 1
            print(f"\n[Agent] Step {self.step_count}/{self.max_steps}")

            # Check for too many errors
            if self.tool_error_count >= self.max_tool_errors:
                return f"Task aborted: Too many tool errors ({self.tool_error_count})"

            # Get LLM response
            response = self._get_llm_response()

            # Check if LLM indicates completion
            if self._is_response_final(response):
                self.is_task_complete = True
                return response.content

            # If no tool calls, might be waiting for user or done
            if not response.has_tool_calls():
                # Check if response seems conclusive
                if any(phrase in response.content.lower() for phrase in
                       ["complete", "done", "finished", "successfully"]):
                    self.is_task_complete = True
                return response.content

            # Execute tool calls
            tool_results = self._execute_tool_calls(response)

            # Add tool results to conversation
            self._add_tool_results_to_history(tool_results)

        # Max steps reached
        if self.step_count >= self.max_steps:
            return f"Task incomplete: Reached maximum step limit ({self.max_steps})"

        return "Task completed"

    def _get_llm_response(self) -> LLMResponse:
        """Get response from LLM with available tools."""
        tools = self.tool_registry.get_tools_for_llm()

        response = self.llm.generate(
            messages=self.conversation_history,
            tools=tools,
            temperature=0.7
        )

        # Add assistant response to history
        self.conversation_history.append(
            Message(role="assistant", content=response.content)
        )

        return response

    def _execute_tool_calls(self, response: LLMResponse) -> List[dict]:
        """Execute all tool calls from LLM response."""
        results = []

        for tool_call in response.tool_calls:
            print(f"[Agent] Executing tool: {tool_call.name}")
            print(f"[Agent] Arguments: {json.dumps(tool_call.arguments, indent=2)}")

            # Execute the tool
            result = self.tool_registry.execute(
                tool_call.name,
                **tool_call.arguments
            )

            if not result.success:
                self.tool_error_count += 1
                print(f"[Agent] Tool error: {result.error}")

            results.append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_call.name,
                "result": result.to_dict()
            })

        return results

    def _add_tool_results_to_history(self, tool_results: List[dict]) -> None:
        """Add tool execution results back to conversation."""
        # Format tool results as a message
        results_text = "Tool execution results:\n"
        for tr in tool_results:
            results_text += f"\n{tr['tool_name']}:\n"
            if tr['result']['success']:
                results_text += f"  Success: {tr['result']['data']}\n"
            else:
                results_text += f"  Error: {tr['result']['error']}\n"

        self.conversation_history.append(
            Message(role="user", content=results_text)
        )

    def _is_response_final(self, response: LLMResponse) -> bool:
        """
        Heuristic to determine if response is final.
        Can be enhanced with explicit markers from LLM.
        """
        content_lower = response.content.lower()

        # Check for completion indicators
        completion_phrases = [
            "task complete",
            "task is complete",
            "finished the task",
            "successfully completed",
            "all done"
        ]

        return any(phrase in content_lower for phrase in completion_phrases)

    def get_conversation_history(self) -> List[Message]:
        """Get full conversation history."""
        return self.conversation_history.copy()

    def reset(self) -> None:
        """Reset agent state for new task."""
        self.conversation_history.clear()
        self.planner.clear_plan()
        self.step_count = 0
        self.tool_error_count = 0
        self.is_task_complete = False
        print("[Agent] Reset complete")
