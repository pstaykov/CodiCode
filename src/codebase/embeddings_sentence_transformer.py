"""
Real embedding implementation using sentence-transformers.
Provides high-quality embeddings for code chunks.
"""

from typing import List, Optional
from .embeddings import EmbeddingProvider
import warnings


class SentenceTransformerEmbedding(EmbeddingProvider):
    """
    Production-ready embedding provider using sentence-transformers.
    Supports multiple models optimized for code.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Initialize with a sentence-transformer model.

        Args:
            model_name: Model to use. Recommended for code:
                - "all-MiniLM-L6-v2" (fast, 384 dim)
                - "all-mpnet-base-v2" (better quality, 768 dim)
                - "sentence-transformers/all-MiniLM-L12-v2"
            device: "cpu" or "cuda"
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Lazy load the model."""
        try:
            from sentence_transformers import SentenceTransformer

            print(f"[Embeddings] Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"[Embeddings] Model loaded successfully")

        except ImportError:
            warnings.warn(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            self.model = None
        except Exception as e:
            warnings.warn(f"Failed to load embedding model: {str(e)}")
            self.model = None

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.model is None:
            raise RuntimeError(
                "Model not loaded. Install sentence-transformers: "
                "pip install sentence-transformers"
            )

        # Encode single text
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if self.model is None:
            raise RuntimeError(
                "Model not loaded. Install sentence-transformers: "
                "pip install sentence-transformers"
            )

        # Batch encoding is more efficient
        embeddings = self.model.encode(
            texts,
            convert_to_tensor=False,
            show_progress_bar=len(texts) > 100
        )

        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self.model is None:
            return 0
        return self.model.get_sentence_embedding_dimension()


class CodeBERTEmbedding(EmbeddingProvider):
    """
    Specialized embedding provider for code using CodeBERT-like models.
    Better suited for code understanding tasks.
    """

    def __init__(self, model_name: str = "microsoft/codebert-base", device: str = "cpu"):
        """
        Initialize with a code-specific model.

        Args:
            model_name: Model to use:
                - "microsoft/codebert-base"
                - "microsoft/graphcodebert-base"
                - "huggingface/CodeBERTa-small-v1"
            device: "cpu" or "cuda"
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self._initialize_model()

    def _initialize_model(self):
        """Load CodeBERT model."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch

            print(f"[Embeddings] Loading CodeBERT: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.torch = torch
            print(f"[Embeddings] CodeBERT loaded successfully")

        except ImportError:
            warnings.warn(
                "transformers not installed. "
                "Install with: pip install transformers torch"
            )
        except Exception as e:
            warnings.warn(f"Failed to load CodeBERT: {str(e)}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding using CodeBERT."""
        if self.model is None:
            raise RuntimeError(
                "Model not loaded. Install transformers: "
                "pip install transformers torch"
            )

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Generate embedding
        with self.torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding
            embedding = outputs.last_hidden_state[:, 0, :].squeeze()

        return embedding.cpu().tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Tokenize batch
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Generate embeddings
        with self.torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embeddings
            embeddings = outputs.last_hidden_state[:, 0, :]

        return embeddings.cpu().tolist()


def get_production_embedding_provider(
    provider_type: str = "sentence-transformer",
    model_name: Optional[str] = None,
    device: str = "cpu"
) -> EmbeddingProvider:
    """
    Factory function for production embedding providers.

    Args:
        provider_type: "sentence-transformer" or "codebert"
        model_name: Optional model override
        device: "cpu" or "cuda"

    Returns:
        Configured EmbeddingProvider
    """
    if provider_type == "sentence-transformer":
        model = model_name or "all-MiniLM-L6-v2"
        return SentenceTransformerEmbedding(model, device)

    elif provider_type == "codebert":
        model = model_name or "microsoft/codebert-base"
        return CodeBERTEmbedding(model, device)

    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
