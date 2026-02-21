"""
AST-based semantic chunking for Python code.
Splits code by functions, classes, and logical blocks.
"""

import ast
from typing import List, Dict, Optional
from pathlib import Path
from .chunker import CodeChunk


class ASTChunker:
    """
    Semantic code chunker using Python AST.
    Extracts functions, classes, and methods as semantic units.
    """

    def __init__(self, include_docstrings: bool = True):
        """
        Initialize AST chunker.

        Args:
            include_docstrings: Whether to include docstrings in chunks
        """
        self.include_docstrings = include_docstrings

    def chunk_file(self, filepath: str) -> List[CodeChunk]:
        """
        Chunk a Python file into semantic units.

        Args:
            filepath: Path to Python file

        Returns:
            List of CodeChunk objects
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            # Parse AST
            tree = ast.parse(source, filename=filepath)

            # Extract chunks
            chunks = []
            lines = source.split('\n')

            for node in ast.walk(tree):
                chunk = self._node_to_chunk(node, lines, filepath)
                if chunk:
                    chunks.append(chunk)

            return chunks

        except SyntaxError as e:
            print(f"[ASTChunker] Syntax error in {filepath}: {str(e)}")
            return []
        except Exception as e:
            print(f"[ASTChunker] Error chunking {filepath}: {str(e)}")
            return []

    def _node_to_chunk(
        self,
        node: ast.AST,
        lines: List[str],
        filepath: str
    ) -> Optional[CodeChunk]:
        """Convert AST node to CodeChunk."""

        # Only process function and class definitions
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            return None

        # Get line numbers
        start_line = node.lineno
        end_line = node.end_lineno

        if start_line is None or end_line is None:
            return None

        # Extract source code
        chunk_lines = lines[start_line - 1:end_line]
        content = '\n'.join(chunk_lines)

        # Determine chunk type
        if isinstance(node, ast.ClassDef):
            chunk_type = "class"
            name = node.name
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunk_type = "function"
            name = node.name
        else:
            chunk_type = "unknown"
            name = "unnamed"

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Build metadata
        metadata = {
            "name": name,
            "type": chunk_type,
            "docstring": docstring if self.include_docstrings else None,
            "num_lines": end_line - start_line + 1
        }

        # Add function-specific metadata
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metadata["args"] = [arg.arg for arg in node.args.args]
            metadata["is_async"] = isinstance(node, ast.AsyncFunctionDef)

        # Add class-specific metadata
        if isinstance(node, ast.ClassDef):
            metadata["bases"] = [
                self._get_name(base) for base in node.bases
            ]
            metadata["methods"] = [
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

        return CodeChunk(
            file_path=filepath,
            start_line=start_line,
            end_line=end_line,
            content=content,
            chunk_type=chunk_type,
            metadata=metadata
        )

    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)

    def chunk_directory(
        self,
        directory: str,
        file_pattern: str = "*.py"
    ) -> Dict[str, List[CodeChunk]]:
        """
        Chunk all Python files in a directory.

        Args:
            directory: Directory path
            file_pattern: File pattern to match

        Returns:
            Dict mapping file paths to chunks
        """
        dir_path = Path(directory)
        chunks_by_file = {}

        for file_path in dir_path.rglob(file_pattern):
            if file_path.is_file():
                chunks = self.chunk_file(str(file_path))
                if chunks:
                    chunks_by_file[str(file_path)] = chunks

        return chunks_by_file

    def extract_imports(self, filepath: str) -> List[str]:
        """
        Extract all imports from a file.

        Args:
            filepath: Path to Python file

        Returns:
            List of import statements
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            return imports

        except Exception as e:
            print(f"[ASTChunker] Error extracting imports: {str(e)}")
            return []

    def get_function_calls(self, filepath: str) -> Dict[str, List[str]]:
        """
        Extract function calls from each function.

        Args:
            filepath: Path to Python file

        Returns:
            Dict mapping function names to called functions
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            calls_by_function = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    calls = []
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call):
                            func_name = self._get_call_name(subnode.func)
                            if func_name:
                                calls.append(func_name)

                    calls_by_function[node.name] = calls

            return calls_by_function

        except Exception as e:
            print(f"[ASTChunker] Error extracting calls: {str(e)}")
            return {}

    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        """Get function name from Call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
