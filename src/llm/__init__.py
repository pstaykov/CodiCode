"""LLM abstraction layer."""

from .base import BaseLLM, Message, LLMResponse, ToolCall
from .ollama import OllamaLLM

__all__ = ['BaseLLM', 'Message', 'LLMResponse', 'ToolCall', 'OllamaLLM']
