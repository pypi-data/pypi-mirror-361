"""Comprehensive coding tools for LoopLM.

This module provides tools for code analysis, file manipulation, search operations,
git integration, and project structure analysis - everything needed for a coding agent.
"""

import re
import subprocess
from pathlib import Path
from typing import List

from looplm.tools.base import tool


# File Operations Tools
@tool(
    description="Write content to a file, creating it if it doesn't exist",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file to write"},
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
            "overwrite": {
                "type": "boolean",
                "description": "Whether to overwrite existing file",
                "default": False,
            },
        },
        "required": ["file_path", "content"],
    },
)
def write_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        overwrite: Whether to overwrite existing file

    Returns:
        str: Success or error message
    """
    try:
        target_path = Path(file_path).expanduser().resolve()

        # Check if file exists and overwrite is not allowed
        if target_path.exists() and not overwrite:
            return f"Error: File '{file_path}' already exists. Use overwrite=true to replace it"

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with target_path.open("w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to '{file_path}'"

    except PermissionError:
        return f"Error: Permission denied writing to '{file_path}'"
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"


@tool(
    description="Append content to an existing file",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to append to",
            },
            "content": {
                "type": "string",
                "description": "Content to append to the file",
            },
        },
        "required": ["file_path", "content"],
    },
)
def append_to_file(file_path: str, content: str) -> str:
    """Append content to an existing file.

    Args:
        file_path: Path to the file to append to
        content: Content to append to the file

    Returns:
        str: Success or error message
    """
    try:
        target_path = Path(file_path).expanduser().resolve()

        if not target_path.exists():
            return f"Error: File '{file_path}' does not exist"

        with target_path.open("a", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully appended {len(content)} characters to '{file_path}'"

    except PermissionError:
        return f"Error: Permission denied writing to '{file_path}'"
    except Exception as e:
        return f"Error appending to file '{file_path}': {str(e)}"


@tool(
    description="Delete a file or directory",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file or directory to delete",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to delete directories recursively",
                "default": False,
            },
        },
        "required": ["path"],
    },
)
def delete_file(path: str, recursive: bool = False) -> str:
    """Delete a file or directory.

    Args:
        path: Path to the file or directory to delete
        recursive: Whether to delete directories recursively

    Returns:
        str: Success or error message
    """
    try:
        target_path = Path(path).expanduser().resolve()

        if not target_path.exists():
            return f"Error: Path '{path}' does not exist"

        if target_path.is_file():
            target_path.unlink()
            return f"Successfully deleted file '{path}'"
        elif target_path.is_dir():
            if recursive:
                import shutil

                shutil.rmtree(target_path)
                return f"Successfully deleted directory '{path}' and all its contents"
            else:
                if any(target_path.iterdir()):
                    return f"Error: Directory '{path}' is not empty. Use recursive=true to delete it"
                target_path.rmdir()
                return f"Successfully deleted empty directory '{path}'"
        else:
            return f"Error: '{path}' is neither a file nor a directory"

    except PermissionError:
        return f"Error: Permission denied deleting '{path}'"
    except Exception as e:
        return f"Error deleting '{path}': {str(e)}"


@tool(
    description="Copy a file or directory to another location",
    parameters={
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Source path to copy from"},
            "destination": {
                "type": "string",
                "description": "Destination path to copy to",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to copy directories recursively",
                "default": False,
            },
        },
        "required": ["source", "destination"],
    },
)
def copy_file(source: str, destination: str, recursive: bool = False) -> str:
    """Copy a file or directory to another location.

    Args:
        source: Source path to copy from
        destination: Destination path to copy to
        recursive: Whether to copy directories recursively

    Returns:
        str: Success or error message
    """
    try:
        import shutil

        source_path = Path(source).expanduser().resolve()
        dest_path = Path(destination).expanduser().resolve()

        if not source_path.exists():
            return f"Error: Source '{source}' does not exist"

        if source_path.is_file():
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            return f"Successfully copied file from '{source}' to '{destination}'"
        elif source_path.is_dir():
            if recursive:
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                return (
                    f"Successfully copied directory from '{source}' to '{destination}'"
                )
            else:
                return (
                    f"Error: '{source}' is a directory. Use recursive=true to copy it"
                )
        else:
            return f"Error: '{source}' is neither a file nor a directory"

    except PermissionError:
        return f"Error: Permission denied copying from '{source}' to '{destination}'"
    except Exception as e:
        return f"Error copying from '{source}' to '{destination}': {str(e)}"


# Search Tools
@tool(
    description="Search for text patterns in files using grep-like functionality",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Text pattern to search for (supports regex)",
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in",
                "default": ".",
            },
            "file_pattern": {
                "type": "string",
                "description": "File pattern to include (e.g., '*.py')",
                "default": "*",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search recursively",
                "default": True,
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether search is case sensitive",
                "default": False,
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 50,
            },
        },
        "required": ["pattern"],
    },
)
def grep_search(
    pattern: str,
    directory: str = ".",
    file_pattern: str = "*",
    recursive: bool = True,
    case_sensitive: bool = False,
    max_results: int = 50,
) -> str:
    """Search for text patterns in files.

    Args:
        pattern: Text pattern to search for (supports regex)
        directory: Directory to search in
        file_pattern: File pattern to include (e.g., '*.py')
        recursive: Whether to search recursively
        case_sensitive: Whether search is case sensitive
        max_results: Maximum number of results to return

    Returns:
        str: Search results or error message
    """
    try:
        search_dir = Path(directory).expanduser().resolve()

        if not search_dir.exists():
            return f"Error: Directory '{directory}' does not exist"

        if not search_dir.is_dir():
            return f"Error: '{directory}' is not a directory"

        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            return f"Error: Invalid regex pattern '{pattern}': {str(e)}"

        results = []
        total_matches = 0

        # Get file pattern for glob
        glob_pattern = f"**/{file_pattern}" if recursive else file_pattern

        for file_path in search_dir.glob(glob_pattern):
            if not file_path.is_file() or total_matches >= max_results:
                break

            try:
                with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if total_matches >= max_results:
                            break

                        match = compiled_pattern.search(line)
                        if match:
                            relative_path = file_path.relative_to(search_dir)
                            results.append(
                                f"{relative_path}:{line_num}: {line.strip()}"
                            )
                            total_matches += 1

            except (PermissionError, UnicodeDecodeError):
                continue  # Skip files we can't read

        if not results:
            return f"No matches found for pattern '{pattern}' in '{directory}'"

        result_text = f"Found {total_matches} matches for pattern '{pattern}':\n\n"
        result_text += "\n".join(results)

        if total_matches >= max_results:
            result_text += f"\n\n... (showing first {max_results} results)"

        return result_text

    except Exception as e:
        return f"Error searching for pattern '{pattern}': {str(e)}"


@tool(
    description="Find files by name pattern",
    parameters={
        "type": "object",
        "properties": {
            "name_pattern": {
                "type": "string",
                "description": "File name pattern to search for (supports wildcards)",
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in",
                "default": ".",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search recursively",
                "default": True,
            },
            "file_type": {
                "type": "string",
                "description": "Type of files to find: 'file', 'dir', or 'both'",
                "default": "both",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 100,
            },
        },
        "required": ["name_pattern"],
    },
)
def find_files(
    name_pattern: str,
    directory: str = ".",
    recursive: bool = True,
    file_type: str = "both",
    max_results: int = 100,
) -> str:
    """Find files by name pattern.

    Args:
        name_pattern: File name pattern to search for (supports wildcards)
        directory: Directory to search in
        recursive: Whether to search recursively
        file_type: Type of files to find: 'file', 'dir', or 'both'
        max_results: Maximum number of results to return

    Returns:
        str: List of found files or error message
    """
    try:
        search_dir = Path(directory).expanduser().resolve()

        if not search_dir.exists():
            return f"Error: Directory '{directory}' does not exist"

        if not search_dir.is_dir():
            return f"Error: '{directory}' is not a directory"

        # Get glob pattern
        glob_pattern = f"**/{name_pattern}" if recursive else name_pattern

        results = []
        count = 0

        for path in search_dir.glob(glob_pattern):
            if count >= max_results:
                break

            relative_path = path.relative_to(search_dir)

            if file_type == "file" and path.is_file():
                results.append(f"[FILE] {relative_path}")
                count += 1
            elif file_type == "dir" and path.is_dir():
                results.append(f"[DIR]  {relative_path}/")
                count += 1
            elif file_type == "both":
                if path.is_file():
                    results.append(f"[FILE] {relative_path}")
                elif path.is_dir():
                    results.append(f"[DIR]  {relative_path}/")
                count += 1

        if not results:
            return f"No files found matching pattern '{name_pattern}' in '{directory}'"

        result_text = (
            f"Found {len(results)} files matching pattern '{name_pattern}':\n\n"
        )
        result_text += "\n".join(results)

        if count >= max_results:
            result_text += f"\n\n... (showing first {max_results} results)"

        return result_text

    except Exception as e:
        return f"Error finding files with pattern '{name_pattern}': {str(e)}"


@tool(
    description="Search and replace text in a file",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to modify",
            },
            "search_pattern": {
                "type": "string",
                "description": "Text pattern to search for (supports regex)",
            },
            "replacement": {
                "type": "string",
                "description": "Text to replace matches with",
            },
            "regex": {
                "type": "boolean",
                "description": "Whether to treat search_pattern as regex",
                "default": False,
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether search is case sensitive",
                "default": True,
            },
            "max_replacements": {
                "type": "integer",
                "description": "Maximum number of replacements (0 = unlimited)",
                "default": 0,
            },
        },
        "required": ["file_path", "search_pattern", "replacement"],
    },
)
def search_and_replace(
    file_path: str,
    search_pattern: str,
    replacement: str,
    regex: bool = False,
    case_sensitive: bool = True,
    max_replacements: int = 0,
) -> str:
    """Search and replace text in a file.

    Args:
        file_path: Path to the file to modify
        search_pattern: Text pattern to search for (supports regex)
        replacement: Text to replace matches with
        regex: Whether to treat search_pattern as regex
        case_sensitive: Whether search is case sensitive
        max_replacements: Maximum number of replacements (0 = unlimited)

    Returns:
        str: Success message with replacement count or error message
    """
    try:
        target_path = Path(file_path).expanduser().resolve()

        if not target_path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not target_path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Read file content
        with target_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Perform replacement
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                compiled_pattern = re.compile(search_pattern, flags)
                if max_replacements > 0:
                    new_content, count = compiled_pattern.subn(
                        replacement, content, count=max_replacements
                    )
                else:
                    new_content, count = compiled_pattern.subn(replacement, content)
            except re.error as e:
                return f"Error: Invalid regex pattern '{search_pattern}': {str(e)}"
        else:
            # Simple string replacement
            if case_sensitive:
                if max_replacements > 0:
                    parts = content.split(search_pattern, max_replacements)
                    new_content = replacement.join(parts)
                    count = len(parts) - 1
                else:
                    count = content.count(search_pattern)
                    new_content = content.replace(search_pattern, replacement)
            else:
                # Case-insensitive string replacement
                flags = re.IGNORECASE
                escaped_pattern = re.escape(search_pattern)
                compiled_pattern = re.compile(escaped_pattern, flags)
                if max_replacements > 0:
                    new_content, count = compiled_pattern.subn(
                        replacement, content, count=max_replacements
                    )
                else:
                    new_content, count = compiled_pattern.subn(replacement, content)

        if count == 0:
            return f"No matches found for pattern '{search_pattern}' in '{file_path}'"

        # Write back to file
        with target_path.open("w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Successfully replaced {count} occurrence(s) of '{search_pattern}' in '{file_path}'"

    except PermissionError:
        return f"Error: Permission denied modifying '{file_path}'"
    except Exception as e:
        return f"Error performing search and replace in '{file_path}': {str(e)}"


# Git Tools
@tool(
    description="Get git status for the current repository",
    parameters={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory to check git status in",
                "default": ".",
            },
        },
        "required": [],
    },
)
def git_status(directory: str = ".") -> str:
    """Get git status for the current repository.

    Args:
        directory: Directory to check git status in

    Returns:
        str: Git status output or error message
    """
    try:
        work_dir = Path(directory).expanduser().resolve()

        if not work_dir.exists():
            return f"Error: Directory '{directory}' does not exist"

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            if "not a git repository" in result.stderr.lower():
                return f"Error: '{directory}' is not a git repository"
            return f"Git error: {result.stderr.strip()}"

        if not result.stdout.strip():
            return "Working directory is clean - no changes detected"

        # Parse git status output
        lines = result.stdout.strip().split("\n")
        status_info = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": [],
            "untracked": [],
        }

        for line in lines:
            if len(line) >= 3:
                status_code = line[:2]
                file_path = line[3:]

                if status_code[0] == "M" or status_code[1] == "M":
                    status_info["modified"].append(file_path)
                elif status_code[0] == "A":
                    status_info["added"].append(file_path)
                elif status_code[0] == "D" or status_code[1] == "D":
                    status_info["deleted"].append(file_path)
                elif status_code[0] == "R":
                    status_info["renamed"].append(file_path)
                elif status_code == "??":
                    status_info["untracked"].append(file_path)

        # Format output
        output = ["Git Status:"]

        for status_type, files in status_info.items():
            if files:
                output.append(f"\n{status_type.capitalize()}:")
                for file_path in files:
                    output.append(f"  {file_path}")

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return f"Error: Git status command timed out in '{directory}'"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"
    except Exception as e:
        return f"Error getting git status in '{directory}': {str(e)}"


@tool(
    description="Get git diff for changes in the repository",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Specific file to show diff for (optional)",
            },
            "staged": {
                "type": "boolean",
                "description": "Show staged changes only",
                "default": False,
            },
            "directory": {
                "type": "string",
                "description": "Directory to run git diff in",
                "default": ".",
            },
        },
        "required": [],
    },
)
def git_diff(file_path: str = "", staged: bool = False, directory: str = ".") -> str:
    """Get git diff for changes in the repository.

    Args:
        file_path: Specific file to show diff for (optional)
        staged: Show staged changes only
        directory: Directory to run git diff in

    Returns:
        str: Git diff output or error message
    """
    try:
        work_dir = Path(directory).expanduser().resolve()

        if not work_dir.exists():
            return f"Error: Directory '{directory}' does not exist"

        # Build git diff command
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--cached")
        if file_path:
            cmd.append(file_path)

        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            if "not a git repository" in result.stderr.lower():
                return f"Error: '{directory}' is not a git repository"
            return f"Git error: {result.stderr.strip()}"

        if not result.stdout.strip():
            if staged:
                return "No staged changes found"
            elif file_path:
                return f"No changes found for file '{file_path}'"
            else:
                return "No changes found in working directory"

        return f"Git Diff{'(staged)' if staged else ''}:\n\n{result.stdout}"

    except subprocess.TimeoutExpired:
        return f"Error: Git diff command timed out in '{directory}'"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"
    except Exception as e:
        return f"Error getting git diff in '{directory}': {str(e)}"


@tool(
    description="Get git log with commit history",
    parameters={
        "type": "object",
        "properties": {
            "max_commits": {
                "type": "integer",
                "description": "Maximum number of commits to show",
                "default": 10,
            },
            "file_path": {
                "type": "string",
                "description": "Show history for specific file (optional)",
            },
            "oneline": {
                "type": "boolean",
                "description": "Show one line per commit",
                "default": True,
            },
            "directory": {
                "type": "string",
                "description": "Directory to run git log in",
                "default": ".",
            },
        },
        "required": [],
    },
)
def git_log(
    max_commits: int = 10,
    file_path: str = "",
    oneline: bool = True,
    directory: str = ".",
) -> str:
    """Get git log with commit history.

    Args:
        max_commits: Maximum number of commits to show
        file_path: Show history for specific file (optional)
        oneline: Show one line per commit
        directory: Directory to run git log in

    Returns:
        str: Git log output or error message
    """
    try:
        work_dir = Path(directory).expanduser().resolve()

        if not work_dir.exists():
            return f"Error: Directory '{directory}' does not exist"

        # Build git log command
        cmd = ["git", "log", f"-{max_commits}"]
        if oneline:
            cmd.append("--oneline")
        else:
            cmd.extend(["--pretty=format:%h - %an, %ar: %s"])

        if file_path:
            cmd.append(file_path)

        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            if "not a git repository" in result.stderr.lower():
                return f"Error: '{directory}' is not a git repository"
            return f"Git error: {result.stderr.strip()}"

        if not result.stdout.strip():
            return "No commit history found"

        return f"Git Log (last {max_commits} commits):\n\n{result.stdout}"

    except subprocess.TimeoutExpired:
        return f"Error: Git log command timed out in '{directory}'"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"
    except Exception as e:
        return f"Error getting git log in '{directory}': {str(e)}"


# Code Analysis Tools
@tool(
    description="Get detailed information about a file including size, type, and basic structure",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to analyze",
            },
            "include_preview": {
                "type": "boolean",
                "description": "Include file content preview",
                "default": True,
            },
            "preview_lines": {
                "type": "integer",
                "description": "Number of lines to include in preview",
                "default": 20,
            },
        },
        "required": ["file_path"],
    },
)
def get_file_info(
    file_path: str, include_preview: bool = True, preview_lines: int = 20
) -> str:
    """Get detailed information about a file.

    Args:
        file_path: Path to the file to analyze
        include_preview: Include file content preview
        preview_lines: Number of lines to include in preview

    Returns:
        str: File information or error message
    """
    try:
        target_path = Path(file_path).expanduser().resolve()

        if not target_path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not target_path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Get file stats
        stat_info = target_path.stat()
        file_size = stat_info.st_size

        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"

        # Determine file type
        file_extension = target_path.suffix.lower()
        file_type = "text"

        binary_extensions = {
            ".exe",
            ".bin",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".mp3",
            ".mp4",
            ".mov",
        }
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".cs",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".kt",
            ".swift",
        }

        if file_extension in binary_extensions:
            file_type = "binary"
        elif file_extension in code_extensions:
            file_type = "source code"

        info_lines = [
            f"File: {target_path}",
            f"Size: {size_str}",
            f"Type: {file_type}",
            f"Extension: {file_extension or 'none'}",
        ]

        # Try to read file for additional info
        if file_type != "binary" and include_preview:
            try:
                with target_path.open("r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    total_lines = len(lines)

                    info_lines.append(f"Total lines: {total_lines}")

                    # Add preview
                    if lines:
                        info_lines.append(
                            f"\nFirst {min(preview_lines, total_lines)} lines:"
                        )
                        info_lines.append("-" * 40)

                        for i, line in enumerate(lines[:preview_lines], 1):
                            info_lines.append(f"{i:3d}: {line.rstrip()}")

                        if total_lines > preview_lines:
                            info_lines.append(
                                f"... ({total_lines - preview_lines} more lines)"
                            )

            except Exception as e:
                info_lines.append(f"Warning: Could not read file content: {str(e)}")

        return "\n".join(info_lines)

    except Exception as e:
        return f"Error analyzing file '{file_path}': {str(e)}"


@tool(
    description="Find function definitions in Python, JavaScript, and other code files",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the code file to analyze",
            },
            "language": {
                "type": "string",
                "description": "Programming language hint (python, javascript, etc.)",
                "default": "auto",
            },
        },
        "required": ["file_path"],
    },
)
def find_functions(file_path: str, language: str = "auto") -> str:
    """Find function definitions in code files.

    Args:
        file_path: Path to the code file to analyze
        language: Programming language hint (python, javascript, etc.)

    Returns:
        str: List of found functions or error message
    """
    try:
        target_path = Path(file_path).expanduser().resolve()

        if not target_path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not target_path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Auto-detect language if needed
        if language == "auto":
            extension = target_path.suffix.lower()
            lang_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".cpp": "cpp",
                ".c": "c",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
                ".php": "php",
                ".rb": "ruby",
            }
            language = lang_map.get(extension, "unknown")

        # Define function patterns for different languages
        patterns = {
            "python": [
                r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
                r"^\s*async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            ],
            "javascript": [
                r"^\s*function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
                r"^\s*const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\(",
                r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*function\s*\(",
                r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=>\s*",
            ],
            "typescript": [
                r"^\s*function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
                r"^\s*const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\(",
                r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*function\s*\(",
                r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=>\s*",
            ],
            "java": [
                r"^\s*(?:public|private|protected)?\s*(?:static)?\s*\w+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            ],
            "cpp": [
                r"^\s*(?:\w+\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{",
            ],
            "c": [
                r"^\s*(?:\w+\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{",
            ],
        }

        function_patterns = patterns.get(
            language, patterns["python"]
        )  # Default to Python

        functions = []

        with target_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern in function_patterns:
                    match = re.search(pattern, line)
                    if match:
                        function_name = match.group(1)
                        functions.append(f"Line {line_num}: {function_name}()")

        if not functions:
            return (
                f"No functions found in '{file_path}' (detected language: {language})"
            )

        result = f"Functions found in '{file_path}' (language: {language}):\n\n"
        result += "\n".join(functions)

        return result

    except Exception as e:
        return f"Error finding functions in '{file_path}': {str(e)}"


@tool(
    description="Find class definitions in code files",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the code file to analyze",
            },
            "language": {
                "type": "string",
                "description": "Programming language hint (python, javascript, etc.)",
                "default": "auto",
            },
        },
        "required": ["file_path"],
    },
)
def find_classes(file_path: str, language: str = "auto") -> str:
    """Find class definitions in code files.

    Args:
        file_path: Path to the code file to analyze
        language: Programming language hint (python, javascript, etc.)

    Returns:
        str: List of found classes or error message
    """
    try:
        target_path = Path(file_path).expanduser().resolve()

        if not target_path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not target_path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Auto-detect language if needed
        if language == "auto":
            extension = target_path.suffix.lower()
            lang_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".cpp": "cpp",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
                ".php": "php",
                ".rb": "ruby",
            }
            language = lang_map.get(extension, "unknown")

        # Define class patterns for different languages
        patterns = {
            "python": [
                r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]",
            ],
            "javascript": [
                r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*{",
                r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+extends\s+",
            ],
            "typescript": [
                r"^\s*(?:export\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*{",
                r"^\s*(?:export\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+extends\s+",
            ],
            "java": [
                r"^\s*(?:public|private|protected)?\s*(?:abstract)?\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*",
            ],
            "cpp": [
                r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*{",
            ],
            "csharp": [
                r"^\s*(?:public|private|protected|internal)?\s*(?:abstract|sealed)?\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*",
            ],
        }

        class_patterns = patterns.get(language, patterns["python"])  # Default to Python

        classes = []

        with target_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern in class_patterns:
                    match = re.search(pattern, line)
                    if match:
                        class_name = match.group(1)
                        classes.append(f"Line {line_num}: {class_name}")

        if not classes:
            return f"No classes found in '{file_path}' (detected language: {language})"

        result = f"Classes found in '{file_path}' (language: {language}):\n\n"
        result += "\n".join(classes)

        return result

    except Exception as e:
        return f"Error finding classes in '{file_path}': {str(e)}"


@tool(
    description="Get a tree-like structure of a directory and its contents",
    parameters={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory to analyze",
                "default": ".",
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum depth to traverse",
                "default": 3,
            },
            "show_hidden": {
                "type": "boolean",
                "description": "Whether to show hidden files",
                "default": False,
            },
            "exclude_patterns": {
                "type": "string",
                "description": "Comma-separated patterns to exclude (e.g., '__pycache__,*.pyc')",
                "default": "",
            },
        },
        "required": [],
    },
)
def get_project_structure(
    directory: str = ".",
    max_depth: int = 3,
    show_hidden: bool = False,
    exclude_patterns: str = "",
) -> str:
    """Get a tree-like structure of a directory and its contents.

    Args:
        directory: Directory to analyze
        max_depth: Maximum depth to traverse
        show_hidden: Whether to show hidden files
        exclude_patterns: Comma-separated patterns to exclude

    Returns:
        str: Directory tree structure or error message
    """
    try:
        root_dir = Path(directory).expanduser().resolve()

        if not root_dir.exists():
            return f"Error: Directory '{directory}' does not exist"

        if not root_dir.is_dir():
            return f"Error: '{directory}' is not a directory"

        # Parse exclude patterns
        exclude_list = []
        if exclude_patterns:
            exclude_list = [
                pattern.strip()
                for pattern in exclude_patterns.split(",")
                if pattern.strip()
            ]

        def should_exclude(path_name: str) -> bool:
            """Check if a path should be excluded."""
            if not show_hidden and path_name.startswith("."):
                return True

            for pattern in exclude_list:
                if "*" in pattern:
                    # Simple glob pattern matching
                    import fnmatch

                    if fnmatch.fnmatch(path_name, pattern):
                        return True
                elif pattern in path_name:
                    return True

            return False

        def build_tree(
            current_path: Path, prefix: str = "", depth: int = 0
        ) -> List[str]:
            """Recursively build directory tree."""
            if depth > max_depth:
                return []

            items = []
            try:
                # Get all items in directory
                all_items = list(current_path.iterdir())
                # Filter out excluded items
                filtered_items = [
                    item for item in all_items if not should_exclude(item.name)
                ]
                # Sort: directories first, then files
                sorted_items = sorted(
                    filtered_items, key=lambda x: (x.is_file(), x.name.lower())
                )

                for i, item in enumerate(sorted_items):
                    is_last = i == len(sorted_items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "

                    if item.is_dir():
                        items.append(f"{prefix}{current_prefix}{item.name}/")
                        if depth < max_depth:
                            items.extend(
                                build_tree(item, prefix + next_prefix, depth + 1)
                            )
                    else:
                        # Add file size for files
                        size = item.stat().st_size
                        if size < 1024:
                            size_str = f"{size}B"
                        elif size < 1024 * 1024:
                            size_str = f"{size/1024:.0f}K"
                        else:
                            size_str = f"{size/(1024*1024):.1f}M"
                        items.append(
                            f"{prefix}{current_prefix}{item.name} ({size_str})"
                        )

            except PermissionError:
                items.append(f"{prefix}└── [Permission Denied]")

            return items

        tree_lines = [f"{root_dir}/"]
        tree_lines.extend(build_tree(root_dir))

        result = f"Project structure for '{directory}':\n\n"
        result += "\n".join(tree_lines)

        if exclude_patterns:
            result += f"\n\nExcluded patterns: {exclude_patterns}"

        return result

    except Exception as e:
        return f"Error getting project structure for '{directory}': {str(e)}"
