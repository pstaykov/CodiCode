"""
Configuration management for the autonomous coding agent.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str = "ollama"  # "ollama", "llama.cpp", "vllm"
    model_name: str = "codellama:7b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class AgentConfig:
    """Agent configuration."""
    max_steps: int = 50
    max_tool_errors: int = 5
    require_approval: bool = True
    verbose: bool = True


@dataclass
class CodebaseConfig:
    """Codebase intelligence configuration."""
    chunk_size: int = 100
    chunk_overlap: int = 20
    embedding_provider: str = "stub"  # "stub", "local"
    enable_vectorstore: bool = False


@dataclass
class Config:
    """Main configuration."""
    llm: LLMConfig
    agent: AgentConfig
    codebase: CodebaseConfig

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "ollama"),
                model_name=os.getenv("LLM_MODEL", "codellama:7b"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096"))
            ),
            agent=AgentConfig(
                max_steps=int(os.getenv("AGENT_MAX_STEPS", "50")),
                max_tool_errors=int(os.getenv("AGENT_MAX_ERRORS", "5")),
                require_approval=os.getenv("AGENT_REQUIRE_APPROVAL", "true").lower() == "true",
                verbose=os.getenv("AGENT_VERBOSE", "true").lower() == "true"
            ),
            codebase=CodebaseConfig(
                chunk_size=int(os.getenv("CHUNK_SIZE", "100")),
                chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "20")),
                embedding_provider=os.getenv("EMBEDDING_PROVIDER", "stub"),
                enable_vectorstore=os.getenv("ENABLE_VECTORSTORE", "false").lower() == "true"
            )
        )

    @classmethod
    def default(cls) -> 'Config':
        """Get default configuration."""
        return cls(
            llm=LLMConfig(),
            agent=AgentConfig(),
            codebase=CodebaseConfig()
        )
