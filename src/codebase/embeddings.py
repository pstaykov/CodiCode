"""
Embedding interface for code chunks.
Phase 1: Stub implementation for future embedding support.
"""

from typing import List, Optional
from abc import ABC, abstractmethod
import hashlib


class EmbeddingProvider(ABC):
    """
    Abstract interface for embedding providers.
    Can be implemented with local models (sentence-transformers, etc.)
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass


class StubEmbeddingProvider(EmbeddingProvider):
    """
    Stub implementation that returns hash-based mock embeddings.
    Replace with actual embedding model in production.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """
        Generate a deterministic mock embedding based on text hash.
        NOT suitable for production - use actual embedding model.
        """
        # Create deterministic hash-based vector
        text_hash = hashlib.md5(text.encode()).digest()

        # Expand hash to desired dimension
        vector = []
        for i in range(self.dimension):
            byte_idx = i % len(text_hash)
            value = (text_hash[byte_idx] / 255.0) - 0.5  # Normalize to [-0.5, 0.5]
            vector.append(value)

        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for batch of texts."""
        return [self.embed_text(text) for text in texts]


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Placeholder for local embedding model integration.
    Could use sentence-transformers, instructor embeddings, etc.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        # In production, initialize model here:
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding using local model."""
        # Placeholder implementation
        if self.model is None:
            print(f"[Embeddings] Warning: Using stub embeddings. "
                  f"Install sentence-transformers for real embeddings.")
            return StubEmbeddingProvider().embed_text(text)

        # In production:
        # return self.model.encode(text).tolist()
        return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        if self.model is None:
            return StubEmbeddingProvider().embed_batch(texts)

        # In production:
        # return self.model.encode(texts).tolist()
        return []


def get_embedding_provider(provider_type: str = "stub") -> EmbeddingProvider:
    """
    Factory function to get embedding provider.

    Args:
        provider_type: "stub" or "local"

    Returns:
        EmbeddingProvider instance
    """
    if provider_type == "stub":
        return StubEmbeddingProvider()
    elif provider_type == "local":
        return LocalEmbeddingProvider()
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
