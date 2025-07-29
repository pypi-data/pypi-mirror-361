"""Git diff scanner for analyzing security vulnerabilities in code changes."""

import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .scan_engine import EnhancedScanResult, ScanEngine
from .threat_engine import Language, Severity, ThreatEngine, ThreatMatch

logger = logging.getLogger(__name__)


class GitDiffError(Exception):
    """Exception raised when git diff operations fail."""

    pass


class DiffChunk:
    """Represents a chunk of changes in a git diff."""

    def __init__(
        self,
        file_path: str,
        old_start: int,
        old_count: int,
        new_start: int,
        new_count: int,
    ):
        self.file_path = file_path
        self.old_start = old_start
        self.old_count = old_count
        self.new_start = new_start
        self.new_count = new_count
        self.added_lines: List[Tuple[int, str]] = []  # (line_number, content)
        self.removed_lines: List[Tuple[int, str]] = []  # (line_number, content)
        self.context_lines: List[Tuple[int, str]] = []  # (line_number, content)

    def add_line(self, line_type: str, line_number: int, content: str) -> None:
        """Add a line to the diff chunk."""
        if line_type == "+":
            self.added_lines.append((line_number, content))
        elif line_type == "-":
            self.removed_lines.append((line_number, content))
        else:
            self.context_lines.append((line_number, content))

    def get_changed_code(self) -> str:
        """Get the changed code as a single string."""
        lines = []

        # Add context lines for better analysis
        for _, content in self.context_lines:
            lines.append(content)

        # Add added lines (new code to scan)
        for _, content in self.added_lines:
            lines.append(content)

        return "\n".join(lines)

    def get_added_lines_only(self) -> str:
        """Get only the added lines as a single string."""
        return "\n".join(content for _, content in self.added_lines)


class GitDiffParser:
    """Parser for git diff output."""

    def __init__(self):
        self.diff_header_pattern = re.compile(r"^diff --git a/(.*) b/(.*)$")
        self.chunk_header_pattern = re.compile(
            r"^@@\s*-(\d+)(?:,(\d+))?\s*\+(\d+)(?:,(\d+))?\s*@@"
        )
        self.file_header_pattern = re.compile(r"^(\+\+\+|---)\s+(.*)")

    def parse_diff(self, diff_output: str) -> Dict[str, List[DiffChunk]]:
        """Parse git diff output into structured chunks.

        Args:
            diff_output: Raw git diff output

        Returns:
            Dictionary mapping file paths to lists of DiffChunk objects
        """
        chunks_by_file: Dict[str, List[DiffChunk]] = {}
        current_file = None
        current_chunk = None
        old_line_num = 0
        new_line_num = 0

        for line in diff_output.split("\n"):
            # Check for file header
            diff_match = self.diff_header_pattern.match(line)
            if diff_match:
                current_file = diff_match.group(2)  # Use the 'b/' path (destination)
                chunks_by_file[current_file] = []
                continue

            # Check for chunk header
            chunk_match = self.chunk_header_pattern.match(line)
            if chunk_match and current_file:
                old_start = int(chunk_match.group(1))
                old_count = int(chunk_match.group(2) or "1")
                new_start = int(chunk_match.group(3))
                new_count = int(chunk_match.group(4) or "1")

                current_chunk = DiffChunk(
                    current_file, old_start, old_count, new_start, new_count
                )
                chunks_by_file[current_file].append(current_chunk)

                old_line_num = old_start
                new_line_num = new_start
                continue

            # Check for content lines
            if current_chunk and line:
                if line.startswith("+") and not line.startswith("+++"):
                    content = line[1:]  # Remove the '+' prefix
                    current_chunk.add_line("+", new_line_num, content)
                    new_line_num += 1
                elif line.startswith("-") and not line.startswith("---"):
                    content = line[1:]  # Remove the '-' prefix
                    current_chunk.add_line("-", old_line_num, content)
                    old_line_num += 1
                elif line.startswith(" "):
                    content = line[1:]  # Remove the ' ' prefix
                    current_chunk.add_line(" ", new_line_num, content)
                    old_line_num += 1
                    new_line_num += 1

        return chunks_by_file


class GitDiffScanner:
    """Scanner for analyzing security vulnerabilities in git diffs."""

    def __init__(
        self,
        scan_engine: Optional[ScanEngine] = None,
        working_dir: Optional[Path] = None,
    ):
        """Initialize the git diff scanner.

        Args:
            scan_engine: Scan engine for vulnerability detection
            working_dir: Working directory for git operations (defaults to current directory)
        """
        self.scan_engine = scan_engine or ScanEngine()
        self.working_dir = working_dir or Path.cwd()
        self.parser = GitDiffParser()

    def _run_git_command(
        self, args: List[str], working_dir: Optional[Path] = None
    ) -> str:
        """Run a git command and return its output.

        Args:
            args: Git command arguments
            working_dir: Working directory for git operations (uses self.working_dir if not specified)

        Returns:
            Command output as string

        Raises:
            GitDiffError: If the git command fails
        """
        target_dir = working_dir or self.working_dir
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise GitDiffError(f"Git command failed: {e.stderr.strip()}")
        except FileNotFoundError:
            raise GitDiffError(
                "Git command not found. Please ensure git is installed and in PATH."
            )

    def _validate_branches(
        self, source_branch: str, target_branch: str, working_dir: Optional[Path] = None
    ) -> None:
        """Validate that the specified branches exist.

        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            working_dir: Working directory for git operations (uses self.working_dir if not specified)

        Raises:
            GitDiffError: If either branch doesn't exist
        """
        try:
            # Check if source branch exists
            self._run_git_command(
                ["rev-parse", "--verify", f"{source_branch}^{{commit}}"], working_dir
            )

            # Check if target branch exists
            self._run_git_command(
                ["rev-parse", "--verify", f"{target_branch}^{{commit}}"], working_dir
            )

        except GitDiffError as e:
            raise GitDiffError(f"Branch validation failed: {e}")

    def _detect_language_from_path(self, file_path: str) -> Optional[Language]:
        """Detect programming language from file path.

        Args:
            file_path: Path to the file

        Returns:
            Detected language or None if not supported
        """
        extension = Path(file_path).suffix.lower()

        language_map = {
            ".py": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".jsx": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".tsx": Language.TYPESCRIPT,
        }

        return language_map.get(extension)

    def get_diff_changes(
        self, source_branch: str, target_branch: str, working_dir: Optional[Path] = None
    ) -> Dict[str, List[DiffChunk]]:
        """Get diff changes between two branches.

        Args:
            source_branch: Source branch (e.g., 'feature-branch')
            target_branch: Target branch (e.g., 'main')
            working_dir: Working directory for git operations (uses self.working_dir if not specified)

        Returns:
            Dictionary mapping file paths to lists of DiffChunk objects

        Raises:
            GitDiffError: If git operations fail
        """
        # Validate branches exist
        self._validate_branches(source_branch, target_branch, working_dir)

        # Get diff between branches
        diff_args = ["diff", f"{target_branch}...{source_branch}"]
        diff_output = self._run_git_command(diff_args, working_dir)

        if not diff_output.strip():
            logger.info(
                f"No differences found between {source_branch} and {target_branch}"
            )
            return {}

        # Parse the diff output
        return self.parser.parse_diff(diff_output)

    def scan_diff(
        self,
        source_branch: str,
        target_branch: str,
        working_dir: Optional[Path] = None,
        use_llm: bool = False,
        severity_threshold: Optional[Severity] = None,
    ) -> Dict[str, List[EnhancedScanResult]]:
        """Scan security vulnerabilities in git diff changes.

        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            working_dir: Working directory for git operations (uses self.working_dir if not specified)
            use_llm: Whether to use LLM analysis
            severity_threshold: Minimum severity threshold for filtering

        Returns:
            Dictionary mapping file paths to lists of scan results

        Raises:
            GitDiffError: If git operations fail
        """
        # Get diff changes
        diff_changes = self.get_diff_changes(source_branch, target_branch, working_dir)

        if not diff_changes:
            return {}

        scan_results: Dict[str, List[EnhancedScanResult]] = {}

        for file_path, chunks in diff_changes.items():
            # Skip non-code files
            language = self._detect_language_from_path(file_path)
            if not language:
                logger.debug(f"Skipping {file_path}: unsupported file type")
                continue

            # Combine all changed code from all chunks
            all_changed_code = []
            line_mapping = {}  # Map from combined code lines to original diff lines

            combined_line_num = 1
            for chunk in chunks:
                changed_code = chunk.get_changed_code()
                if changed_code.strip():
                    all_changed_code.append(changed_code)

                    # Map line numbers for accurate reporting
                    for i, line in enumerate(changed_code.split("\n")):
                        if line.strip():  # Skip empty lines
                            line_mapping[combined_line_num] = chunk.new_start + i
                        combined_line_num += 1

            if not all_changed_code:
                continue

            # Scan the combined changed code
            full_changed_code = "\n".join(all_changed_code)

            try:
                scan_result = self.scan_engine.scan_code(
                    source_code=full_changed_code,
                    file_path=file_path,
                    language=language,
                    use_llm=use_llm,
                    severity_threshold=severity_threshold,
                )

                # Update line numbers to match original file
                for threat in scan_result.all_threats:
                    if threat.line_number in line_mapping:
                        threat.line_number = line_mapping[threat.line_number]

                scan_results[file_path] = [scan_result]
                logger.info(
                    f"Scanned {file_path}: found {len(scan_result.all_threats)} threats"
                )

            except Exception as e:
                logger.error(f"Failed to scan {file_path}: {e}")
                continue

        return scan_results

    def get_diff_summary(
        self, source_branch: str, target_branch: str, working_dir: Optional[Path] = None
    ) -> Dict[str, any]:
        """Get a summary of the diff between two branches.

        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            working_dir: Working directory for git operations (uses self.working_dir if not specified)

        Returns:
            Dictionary with diff summary information
        """
        try:
            diff_changes = self.get_diff_changes(
                source_branch, target_branch, working_dir
            )

            total_files = len(diff_changes)
            total_chunks = sum(len(chunks) for chunks in diff_changes.values())

            lines_added = 0
            lines_removed = 0
            supported_files = 0

            for file_path, chunks in diff_changes.items():
                if self._detect_language_from_path(file_path):
                    supported_files += 1

                for chunk in chunks:
                    lines_added += len(chunk.added_lines)
                    lines_removed += len(chunk.removed_lines)

            return {
                "source_branch": source_branch,
                "target_branch": target_branch,
                "total_files_changed": total_files,
                "supported_files": supported_files,
                "total_chunks": total_chunks,
                "lines_added": lines_added,
                "lines_removed": lines_removed,
                "scannable_files": [
                    file_path
                    for file_path in diff_changes.keys()
                    if self._detect_language_from_path(file_path)
                ],
            }

        except GitDiffError:
            return {
                "source_branch": source_branch,
                "target_branch": target_branch,
                "error": "Failed to get diff summary",
            }
