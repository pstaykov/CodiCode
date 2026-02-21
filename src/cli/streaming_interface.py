"""
Enhanced CLI with streaming LLM responses.
"""

import sys
from typing import Optional
from ..agent.controller import AgentController
from ..llm.base import Message
from .display import Display


class StreamingCLI:
    """
    Enhanced CLI with streaming support for better UX.
    Shows LLM responses as they're generated.
    """

    def __init__(
        self,
        agent: AgentController,
        display: Optional[Display] = None
    ):
        self.agent = agent
        self.display = display or Display()
        self.running = True

    def run(self) -> None:
        """Main loop with streaming."""
        self.display.print_header("CodiCode - Streaming Mode")
        self.display.print_info("Responses will stream in real-time")
        self.display.print_info("Type 'quit' to exit, 'help' for commands")

        while self.running:
            try:
                self.display.print("\n" + ">"*3, None)
                user_input = input().strip()

                if not user_input:
                    continue

                if self._handle_command(user_input):
                    continue

                self._execute_task_streaming(user_input)

            except KeyboardInterrupt:
                self.display.print_warning("\nInterrupted")
                if self.display.confirm("Exit?", default=True):
                    self.running = False
            except EOFError:
                self.running = False
            except Exception as e:
                self.display.print_error(f"Error: {str(e)}")

        self.display.print_info("Goodbye!")

    def _execute_task_streaming(self, task: str) -> None:
        """Execute task with streaming output."""
        self.display.print_separator()
        self.display.print_info(f"Task: {task}")
        self.display.print_separator()

        # Initialize conversation
        self.agent.conversation_history = [
            Message(role="user", content=task)
        ]

        step = 0
        max_steps = self.agent.max_steps

        while not self.agent.is_task_complete and step < max_steps:
            step += 1
            self.display.print(f"\n[Step {step}/{max_steps}]", None)

            # Get streaming response
            response_text = self._stream_llm_response()

            # Parse for tool calls
            tool_calls = self._parse_tool_calls(response_text)

            if not tool_calls:
                # No tool calls, task might be complete
                if self._is_conclusive(response_text):
                    self.agent.is_task_complete = True
                    break
                else:
                    self.display.print_warning("No tool calls detected")
                    break

            # Execute tools
            tool_results = self._execute_tools(tool_calls)

            # Add results to history
            self._add_results_to_history(tool_results)

        self.display.print_separator()
        if self.agent.is_task_complete:
            self.display.print_success("Task completed!")
        else:
            self.display.print_warning("Task incomplete")

    def _stream_llm_response(self) -> str:
        """Stream LLM response and collect full text."""
        tools = self.agent.tool_registry.get_tools_for_llm()

        self.display.print("\n🤖 ", None)

        full_response = ""

        try:
            # Use streaming generation
            for chunk in self.agent.llm.generate_stream(
                messages=self.agent.conversation_history,
                tools=tools
            ):
                self.display.stream_text(chunk)
                full_response += chunk

            print()  # Newline after streaming

            # Add to history
            self.agent.conversation_history.append(
                Message(role="assistant", content=full_response)
            )

            return full_response

        except Exception as e:
            self.display.print_error(f"\nStreaming error: {str(e)}")
            return ""

    def _parse_tool_calls(self, response: str) -> list:
        """Parse tool calls from response."""
        import json

        tool_calls = []

        # Look for <tool_call> markers
        if "<tool_call>" not in response:
            return []

        try:
            start = response.index("<tool_call>") + len("<tool_call>")
            end = response.index("</tool_call>")
            tool_json = response[start:end].strip()
            tool_data = json.loads(tool_json)

            tool_calls.append({
                "id": f"call_{hash(tool_json)}",
                "name": tool_data["tool"],
                "arguments": tool_data.get("arguments", {})
            })

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            self.display.print_warning(f"Failed to parse tool call: {str(e)}")

        return tool_calls

    def _execute_tools(self, tool_calls: list) -> list:
        """Execute tool calls with visual feedback."""
        results = []

        for tool_call in tool_calls:
            self.display.print_tool_call(
                tool_call["name"],
                tool_call["arguments"]
            )

            result = self.agent.tool_registry.execute(
                tool_call["name"],
                **tool_call["arguments"]
            )

            self.display.print_tool_result(result.success, str(result.data or result.error))

            results.append({
                "tool_call_id": tool_call["id"],
                "tool_name": tool_call["name"],
                "result": result.to_dict()
            })

        return results

    def _add_results_to_history(self, tool_results: list) -> None:
        """Add tool results to conversation."""
        results_text = "Tool results:\n"
        for tr in tool_results:
            results_text += f"\n{tr['tool_name']}:\n"
            if tr['result']['success']:
                results_text += f"  {tr['result']['data']}\n"
            else:
                results_text += f"  Error: {tr['result']['error']}\n"

        self.agent.conversation_history.append(
            Message(role="user", content=results_text)
        )

    def _is_conclusive(self, text: str) -> bool:
        """Check if response indicates completion."""
        conclusive_phrases = [
            "task complete",
            "finished",
            "done",
            "successfully completed"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in conclusive_phrases)

    def _handle_command(self, user_input: str) -> bool:
        """Handle special commands."""
        command = user_input.lower()

        if command in ['quit', 'exit', 'q']:
            self.running = False
            return True

        if command == 'help':
            self._show_help()
            return True

        if command == 'reset':
            self.agent.reset()
            self.display.print_success("Agent reset")
            return True

        if command == 'status':
            self._show_status()
            return True

        if command == 'tools':
            self._show_tools()
            return True

        return False

    def _show_help(self) -> None:
        """Show help."""
        help_text = """
Commands:
  help   - Show this help
  quit   - Exit
  reset  - Reset agent
  status - Show status
  tools  - List tools

Simply type your coding task to begin.
        """
        self.display.print(help_text, None)

    def _show_status(self) -> None:
        """Show agent status."""
        self.display.print_header("Status")
        self.display.print(f"Steps: {self.agent.step_count}/{self.agent.max_steps}", None)
        self.display.print(f"Errors: {self.agent.tool_error_count}", None)
        self.display.print(f"Complete: {self.agent.is_task_complete}", None)

    def _show_tools(self) -> None:
        """Show available tools."""
        self.display.print_header("Available Tools")
        for tool_name in self.agent.tool_registry.list_tools():
            tool = self.agent.tool_registry.get_tool(tool_name)
            self.display.print(f"  • {tool_name}: {tool.description}", None)


def create_streaming_cli(agent: AgentController) -> StreamingCLI:
    """Factory for streaming CLI."""
    return StreamingCLI(agent=agent, display=Display())
