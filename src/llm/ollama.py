"""
Ollama backend implementation for local LLM.
"""

import json
import requests
from typing import List, Dict, Any, Iterator, Optional
from .base import BaseLLM, Message, LLMResponse, ToolCall


class OllamaLLM(BaseLLM):
    """
    Ollama backend for running local LLMs.
    Requires Ollama to be running on localhost:11434
    """

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        super().__init__(model_name, **kwargs)
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    def _format_messages(self, messages: List[Message]) -> List[Dict]:
        """Convert Message objects to Ollama format."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def _parse_tool_calls(self, response_text: str) -> Optional[List[ToolCall]]:
        """
        Parse tool calls from LLM response.
        Expects JSON format: {"tool": "tool_name", "arguments": {...}}
        """
        try:
            # Look for tool call markers
            if "<tool_call>" in response_text and "</tool_call>" in response_text:
                start = response_text.index("<tool_call>") + len("<tool_call>")
                end = response_text.index("</tool_call>")
                tool_json = response_text[start:end].strip()
                tool_data = json.loads(tool_json)

                return [ToolCall(
                    id=f"call_{hash(tool_json)}",
                    name=tool_data["tool"],
                    arguments=tool_data.get("arguments", {})
                )]
        except (ValueError, KeyError, json.JSONDecodeError):
            pass

        return None

    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> LLMResponse:
        """Generate response from Ollama."""

        # Add tool instructions to system message if tools provided
        formatted_messages = self._format_messages(messages)
        if tools:
            tool_prompt = self._build_tool_prompt(tools)
            formatted_messages.insert(0, {
                "role": "system",
                "content": tool_prompt
            })

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            content = data["message"]["content"]
            tool_calls = self._parse_tool_calls(content)

            # Estimate tokens (rough approximation)
            tokens = len(content.split()) * 1.3
            self.update_token_count(int(tokens))

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                tokens_used=int(tokens)
            )

        except requests.exceptions.RequestException as e:
            return LLMResponse(
                content=f"Error communicating with Ollama: {str(e)}",
                finish_reason="error"
            )

    def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """Stream response from Ollama."""

        formatted_messages = self._format_messages(messages)
        if tools:
            tool_prompt = self._build_tool_prompt(tools)
            formatted_messages.insert(0, {
                "role": "system",
                "content": tool_prompt
            })

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        chunk = data["message"].get("content", "")
                        if chunk:
                            yield chunk

        except requests.exceptions.RequestException as e:
            yield f"[Error: {str(e)}]"

    def _build_tool_prompt(self, tools: List[Dict]) -> str:
        """Build system prompt describing available tools."""
        tool_descriptions = []
        for tool in tools:
            func = tool.get("function", {})
            tool_descriptions.append(
                f"- {func['name']}: {func['description']}\n"
                f"  Parameters: {json.dumps(func['parameters'], indent=2)}"
            )

        return f"""You are an autonomous coding agent with access to tools.

Available tools:
{chr(10).join(tool_descriptions)}

To use a tool, respond with:
<tool_call>
{{"tool": "tool_name", "arguments": {{"param": "value"}}}}
</tool_call>

If you don't need a tool, respond normally."""
