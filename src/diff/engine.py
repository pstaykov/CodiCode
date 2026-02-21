"""
Diff and patch engine for safe file modifications.
Generates unified diffs and applies patches with validation.
"""

import difflib
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class DiffResult:
    """Result of a diff operation."""
    has_changes: bool
    unified_diff: str
    additions: int = 0
    deletions: int = 0


@dataclass
class PatchResult:
    """Result of a patch operation."""
    success: bool
    message: str
    error: Optional[str] = None


class DiffEngine:
    """
    Engine for generating diffs and applying patches safely.
    Implements unified diff format with validation.
    """

    def __init__(self):
        self.backup_enabled = True

    def generate_diff(
        self,
        original: str,
        modified: str,
        filepath: str = "file"
    ) -> DiffResult:
        """
        Generate a unified diff between original and modified content.

        Args:
            original: Original content
            modified: Modified content
            filepath: File path for diff header

        Returns:
            DiffResult with unified diff and statistics
        """
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
            lineterm=''
        ))

        if not diff_lines:
            return DiffResult(
                has_changes=False,
                unified_diff="(no changes)"
            )

        # Count additions and deletions
        additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))

        unified_diff = "\n".join(diff_lines)

        return DiffResult(
            has_changes=True,
            unified_diff=unified_diff,
            additions=additions,
            deletions=deletions
        )

    def apply_patch(
        self,
        filepath: str,
        new_content: str,
        require_approval: bool = True
    ) -> PatchResult:
        """
        Apply changes to a file.

        Args:
            filepath: Path to file to modify
            new_content: New content to write
            require_approval: If True, creates backup first

        Returns:
            PatchResult with success status
        """
        try:
            file_path = Path(filepath)

            # Read original content if file exists
            original_content = ""
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

            # Generate diff for logging
            diff_result = self.generate_diff(
                original_content,
                new_content,
                filepath
            )

            # Create backup if enabled
            if self.backup_enabled and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

            # Write new content
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return PatchResult(
                success=True,
                message=f"Successfully patched {filepath} (+{diff_result.additions}/-{diff_result.deletions})"
            )

        except Exception as e:
            return PatchResult(
                success=False,
                message="Patch failed",
                error=str(e)
            )

    def rollback(self, filepath: str) -> PatchResult:
        """
        Rollback a file to its backup.

        Args:
            filepath: Path to file to rollback

        Returns:
            PatchResult with success status
        """
        try:
            file_path = Path(filepath)
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')

            if not backup_path.exists():
                return PatchResult(
                    success=False,
                    message="Rollback failed",
                    error=f"No backup found for {filepath}"
                )

            # Restore from backup
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)

            # Remove backup
            backup_path.unlink()

            return PatchResult(
                success=True,
                message=f"Successfully rolled back {filepath}"
            )

        except Exception as e:
            return PatchResult(
                success=False,
                message="Rollback failed",
                error=str(e)
            )

    def validate_patch(self, original: str, patch: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a patch can be applied.

        Args:
            original: Original content
            patch: Patch to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - check patch format
        if not patch.strip():
            return False, "Empty patch"

        if not any(line.startswith('@@') for line in patch.split('\n')):
            return False, "Invalid patch format - missing hunk headers"

        return True, None

    def format_diff_for_display(self, diff: str, context_lines: int = 3) -> str:
        """
        Format diff for human-readable display with syntax highlighting hints.

        Args:
            diff: Unified diff string
            context_lines: Number of context lines to show

        Returns:
            Formatted diff string
        """
        lines = diff.split('\n')
        formatted_lines = []

        for line in lines:
            if line.startswith('+++') or line.startswith('---'):
                formatted_lines.append(f"[FILE] {line}")
            elif line.startswith('@@'):
                formatted_lines.append(f"[HUNK] {line}")
            elif line.startswith('+'):
                formatted_lines.append(f"[+] {line[1:]}")
            elif line.startswith('-'):
                formatted_lines.append(f"[-] {line[1:]}")
            else:
                formatted_lines.append(f"    {line}")

        return "\n".join(formatted_lines)
