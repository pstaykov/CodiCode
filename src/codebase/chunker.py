"""
File chunking system for breaking down code into semantic chunks.
"""

from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeChunk:
    """
    Represents a semantic chunk of code.
    """
    file_path: str
    start_line: int
    end_line: int
    content: str
    chunk_type: str  # e.g., "function", "class", "block"
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FileChunker:
    """
    Chunks code files into semantic units.
    Phase 1: Simple line-based chunking with overlap.
    Phase 2: AST-based semantic chunking (future enhancement).
    """

    def __init__(
        self,
        chunk_size: int = 100,
        overlap: int = 20
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Number of lines per chunk
            overlap: Number of overlapping lines between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_file(self, filepath: str) -> List[CodeChunk]:
        """
        Chunk a file into segments.

        Args:
            filepath: Path to file to chunk

        Returns:
            List of CodeChunk objects
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            chunks = []
            total_lines = len(lines)

            # Create overlapping chunks
            start = 0
            chunk_id = 0

            while start < total_lines:
                end = min(start + self.chunk_size, total_lines)

                # Extract chunk content
                chunk_lines = lines[start:end]
                content = ''.join(chunk_lines)

                chunk = CodeChunk(
                    file_path=filepath,
                    start_line=start + 1,  # 1-indexed
                    end_line=end,
                    content=content,
                    chunk_type="block",
                    metadata={
                        "chunk_id": chunk_id,
                        "total_lines": end - start
                    }
                )

                chunks.append(chunk)

                # Move to next chunk with overlap
                start = end - self.overlap
                if start >= total_lines - self.overlap:
                    break

                chunk_id += 1

            return chunks

        except Exception as e:
            print(f"[Chunker] Error chunking file {filepath}: {str(e)}")
            return []

    def chunk_directory(
        self,
        directory: str,
        file_pattern: str = "*.py"
    ) -> Dict[str, List[CodeChunk]]:
        """
        Chunk all files in a directory.

        Args:
            directory: Directory path
            file_pattern: Glob pattern for files to chunk

        Returns:
            Dict mapping file paths to their chunks
        """
        dir_path = Path(directory)
        chunks_by_file = {}

        for file_path in dir_path.rglob(file_pattern):
            if file_path.is_file():
                chunks = self.chunk_file(str(file_path))
                if chunks:
                    chunks_by_file[str(file_path)] = chunks

        return chunks_by_file

    def get_chunk_context(
        self,
        chunk: CodeChunk,
        all_chunks: List[CodeChunk],
        context_radius: int = 1
    ) -> str:
        """
        Get surrounding context for a chunk.

        Args:
            chunk: Target chunk
            all_chunks: All chunks from the same file
            context_radius: Number of chunks before/after to include

        Returns:
            Context string with surrounding chunks
        """
        # Find chunk index
        try:
            chunk_index = all_chunks.index(chunk)
        except ValueError:
            return chunk.content

        # Get surrounding chunks
        start_idx = max(0, chunk_index - context_radius)
        end_idx = min(len(all_chunks), chunk_index + context_radius + 1)

        context_chunks = all_chunks[start_idx:end_idx]
        context_content = "\n".join(c.content for c in context_chunks)

        return context_content
