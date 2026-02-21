"""
Persistent vector store implementation using FAISS.
Provides efficient similarity search with disk persistence.
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json
import pickle
from .vectorstore import VectorEntry


class FAISSVectorStore:
    """
    Production vector store using FAISS for efficient similarity search.
    Supports persistence to disk.
    """

    def __init__(self, dimension: int, index_type: str = "Flat"):
        """
        Initialize FAISS vector store.

        Args:
            dimension: Embedding dimension
            index_type: FAISS index type:
                - "Flat" - Exact search (slower, accurate)
                - "IVF" - Approximate search (faster)
                - "HNSW" - Hierarchical graph (fast + accurate)
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.entries: List[VectorEntry] = []
        self.id_to_idx: Dict[str, int] = {}
        self._initialize_index()

    def _initialize_index(self):
        """Initialize FAISS index."""
        try:
            import faiss

            if self.index_type == "Flat":
                # Exact search using L2 distance
                self.index = faiss.IndexFlatL2(self.dimension)

            elif self.index_type == "IVF":
                # Approximate search with inverted file index
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(
                    quantizer,
                    self.dimension,
                    min(100, max(1, len(self.entries) // 100))  # nlist
                )

            elif self.index_type == "HNSW":
                # Hierarchical Navigable Small World graph
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)

            else:
                raise ValueError(f"Unknown index type: {self.index_type}")

            print(f"[FAISS] Initialized {self.index_type} index (dim={self.dimension})")

        except ImportError:
            raise ImportError(
                "faiss not installed. "
                "Install with: pip install faiss-cpu (or faiss-gpu)"
            )

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
        import numpy as np

        if metadata is None:
            metadata = {}

        entry = VectorEntry(
            id=id,
            vector=vector,
            text=text,
            metadata=metadata
        )

        if id in self.id_to_idx:
            # Update existing entry
            idx = self.id_to_idx[id]
            self.entries[idx] = entry
            # Note: FAISS doesn't support in-place updates
            # Need to rebuild index for updates
        else:
            # Add new entry
            self.id_to_idx[id] = len(self.entries)
            self.entries.append(entry)

            # Add to FAISS index
            vector_array = np.array([vector], dtype=np.float32)
            self.index.add(vector_array)

    def add_batch(
        self,
        ids: List[str],
        vectors: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """Add multiple vectors efficiently."""
        import numpy as np

        if metadatas is None:
            metadatas = [{}] * len(ids)

        # Add entries
        for id, vector, text, metadata in zip(ids, vectors, texts, metadatas):
            if id not in self.id_to_idx:
                entry = VectorEntry(
                    id=id,
                    vector=vector,
                    text=text,
                    metadata=metadata
                )
                self.id_to_idx[id] = len(self.entries)
                self.entries.append(entry)

        # Add all vectors to FAISS at once
        vectors_array = np.array(vectors, dtype=np.float32)
        self.index.add(vectors_array)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Tuple[VectorEntry, float]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            top_k: Number of results
            filter_metadata: Optional metadata filter

        Returns:
            List of (entry, similarity_score) tuples
        """
        import numpy as np

        if len(self.entries) == 0:
            return []

        # Convert query to numpy array
        query_array = np.array([query_vector], dtype=np.float32)

        # Search FAISS index
        # Get more results if filtering
        search_k = top_k * 10 if filter_metadata else top_k
        distances, indices = self.index.search(query_array, min(search_k, len(self.entries)))

        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.entries):
                continue

            entry = self.entries[idx]

            # Apply metadata filter
            if filter_metadata:
                if not self._matches_filter(entry.metadata, filter_metadata):
                    continue

            # Convert L2 distance to similarity score (inverse)
            similarity = 1.0 / (1.0 + float(dist))
            results.append((entry, similarity))

            if len(results) >= top_k:
                break

        return results

    def save(self, directory: str) -> None:
        """
        Save index and metadata to disk.

        Args:
            directory: Directory to save to
        """
        import faiss

        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = dir_path / "index.faiss"
        faiss.write_index(self.index, str(index_path))

        # Save entries and metadata
        entries_path = dir_path / "entries.pkl"
        with open(entries_path, 'wb') as f:
            pickle.dump({
                'entries': self.entries,
                'id_to_idx': self.id_to_idx
            }, f)

        # Save config
        config_path = dir_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump({
                'dimension': self.dimension,
                'index_type': self.index_type,
                'num_vectors': len(self.entries)
            }, f, indent=2)

        print(f"[FAISS] Saved index to {directory}")

    def load(self, directory: str) -> None:
        """
        Load index and metadata from disk.

        Args:
            directory: Directory to load from
        """
        import faiss

        dir_path = Path(directory)

        # Load config
        config_path = dir_path / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.dimension = config['dimension']
        self.index_type = config['index_type']

        # Load FAISS index
        index_path = dir_path / "index.faiss"
        self.index = faiss.read_index(str(index_path))

        # Load entries
        entries_path = dir_path / "entries.pkl"
        with open(entries_path, 'rb') as f:
            data = pickle.load(f)
            self.entries = data['entries']
            self.id_to_idx = data['id_to_idx']

        print(f"[FAISS] Loaded index from {directory} ({len(self.entries)} vectors)")

    def get(self, id: str) -> Optional[VectorEntry]:
        """Get entry by ID."""
        if id not in self.id_to_idx:
            return None
        return self.entries[self.id_to_idx[id]]

    def delete(self, id: str) -> bool:
        """
        Delete entry by ID.
        Note: FAISS doesn't support deletion, requires rebuild.
        """
        if id not in self.id_to_idx:
            return False

        # Remove from entries
        idx = self.id_to_idx[id]
        del self.entries[idx]
        del self.id_to_idx[id]

        # Rebuild index mappings
        self.id_to_idx = {
            entry.id: i for i, entry in enumerate(self.entries)
        }

        # Need to rebuild FAISS index
        self._rebuild_index()
        return True

    def _rebuild_index(self):
        """Rebuild FAISS index from scratch."""
        import numpy as np

        self._initialize_index()

        if self.entries:
            vectors = np.array(
                [entry.vector for entry in self.entries],
                dtype=np.float32
            )
            self.index.add(vectors)

    def size(self) -> int:
        """Get number of vectors."""
        return len(self.entries)

    def clear(self) -> None:
        """Clear all vectors."""
        self.entries.clear()
        self.id_to_idx.clear()
        self._initialize_index()

    def _matches_filter(self, metadata: Dict, filter: Dict) -> bool:
        """Check if metadata matches filter."""
        for key, value in filter.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True


class CodebaseFAISSStore(FAISSVectorStore):
    """
    Specialized FAISS store for code with helper methods.
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
        """Add a code chunk."""
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
        """Search within specific file."""
        return self.search(
            query_vector,
            top_k=top_k,
            filter_metadata={"file_path": file_path}
        )
