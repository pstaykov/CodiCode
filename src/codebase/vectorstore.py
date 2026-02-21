"""
Vector store abstraction for storing and searching code embeddings.
Phase 1: Simple in-memory implementation.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class VectorEntry:
    """Entry in the vector store."""
    id: str
    vector: List[float]
    metadata: Dict
    text: str


class VectorStore:
    """
    Abstract interface for vector storage and similarity search.
    In-memory implementation for Phase 1.
    """

    def __init__(self):
        self.entries: List[VectorEntry] = []
        self.index_map: Dict[str, int] = {}

    def add(
        self,
        id: str,
        vector: List[float],
        text: str,
        metadata: Dict = None
    ) -> None:
        """
        Add a vector to the store.

        Args:
            id: Unique identifier
            vector: Embedding vector
            text: Original text
            metadata: Additional metadata
        """
        if metadata is None:
            metadata = {}

        entry = VectorEntry(
            id=id,
            vector=vector,
            text=text,
            metadata=metadata
        )

        if id in self.index_map:
            # Update existing entry
            idx = self.index_map[id]
            self.entries[idx] = entry
        else:
            # Add new entry
            self.index_map[id] = len(self.entries)
            self.entries.append(entry)

    def add_batch(
        self,
        ids: List[str],
        vectors: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """Add multiple vectors at once."""
        if metadatas is None:
            metadatas = [{}] * len(ids)

        for id, vector, text, metadata in zip(ids, vectors, texts, metadatas):
            self.add(id, vector, text, metadata)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Tuple[VectorEntry, float]]:
        """
        Search for similar vectors using cosine similarity.

        Args:
            query_vector: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of (entry, similarity_score) tuples
        """
        if not self.entries:
            return []

        # Calculate similarities
        similarities = []
        for entry in self.entries:
            # Apply metadata filter if provided
            if filter_metadata:
                if not self._matches_filter(entry.metadata, filter_metadata):
                    continue

            similarity = self._cosine_similarity(query_vector, entry.vector)
            similarities.append((entry, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top k
        return similarities[:top_k]

    def get(self, id: str) -> Optional[VectorEntry]:
        """Get entry by ID."""
        if id not in self.index_map:
            return None
        return self.entries[self.index_map[id]]

    def delete(self, id: str) -> bool:
        """Delete entry by ID."""
        if id not in self.index_map:
            return False

        idx = self.index_map[id]
        del self.entries[idx]
        del self.index_map[id]

        # Rebuild index map
        self.index_map = {
            entry.id: i for i, entry in enumerate(self.entries)
        }
        return True

    def clear(self) -> None:
        """Clear all entries."""
        self.entries.clear()
        self.index_map.clear()

    def size(self) -> int:
        """Get number of entries."""
        return len(self.entries)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _matches_filter(self, metadata: Dict, filter: Dict) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True


class CodebaseVectorStore(VectorStore):
    """
    Specialized vector store for code chunks.
    Adds convenience methods for code-specific operations.
    """

    def add_code_chunk(
        self,
        chunk_id: str,
        vector: List[float],
        code: str,
        file_path: str,
        start_line: int,
        end_line: int
    ) -> None:
        """Add a code chunk with structured metadata."""
        self.add(
            id=chunk_id,
            vector=vector,
            text=code,
            metadata={
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "type": "code_chunk"
            }
        )

    def search_by_file(
        self,
        query_vector: List[float],
        file_path: str,
        top_k: int = 5
    ) -> List[Tuple[VectorEntry, float]]:
        """Search within a specific file."""
        return self.search(
            query_vector,
            top_k=top_k,
            filter_metadata={"file_path": file_path}
        )
