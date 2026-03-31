"""Vault path helpers and file operations for the AI Employee system.

Provides utilities for interacting with the Obsidian vault directory structure.
"""

import os
import shutil
from pathlib import Path


VAULT_DIRECTORIES = [
    "Inbox",
    "Needs_Action",
    "Plans",
    "Done",
    "Logs",
    "skills",
]


def get_vault_path() -> str:
    """Read vault path from VAULT_PATH environment variable.

    Returns:
        Absolute path to the vault directory.

    Raises:
        RuntimeError: If VAULT_PATH is not set or directory doesn't exist.
    """
    vault_path = os.environ.get("VAULT_PATH", "./AI_Employee_Vault")
    abs_path = os.path.abspath(vault_path)
    if not os.path.isdir(abs_path):
        raise RuntimeError(
            f"Vault directory not found: {abs_path}. "
            "Set VAULT_PATH in .env or create the directory."
        )
    return abs_path


def ensure_vault_structure(vault_path: str) -> list[str]:
    """Create any missing vault subdirectories.

    Args:
        vault_path: Absolute path to the vault root.

    Returns:
        List of directories that were created.
    """
    created = []
    for dirname in VAULT_DIRECTORIES:
        dir_path = Path(vault_path) / dirname
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(str(dir_path))
    return created


def count_files(directory: str, extension: str = ".md") -> int:
    """Count files with the given extension in a directory.

    Args:
        directory: Path to the directory to scan.
        extension: File extension to match (default: ".md").

    Returns:
        Number of matching files (non-recursive).
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return 0
    return sum(1 for f in dir_path.iterdir() if f.is_file() and f.suffix == extension)


def list_files(directory: str, extension: str = ".md") -> list[str]:
    """List files in a directory sorted by modification time (oldest first).

    Args:
        directory: Path to the directory to scan.
        extension: File extension to match (default: ".md").

    Returns:
        List of absolute file paths, sorted oldest-first (FIFO).
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return []
    files = [f for f in dir_path.iterdir() if f.is_file() and f.suffix == extension]
    files.sort(key=lambda f: f.stat().st_mtime)
    return [str(f) for f in files]


def move_file(src: str, dst_dir: str) -> str:
    """Move a file to a destination directory.

    Args:
        src: Path to the source file.
        dst_dir: Path to the destination directory.

    Returns:
        Path to the moved file.

    Raises:
        FileNotFoundError: If source file doesn't exist.
        NotADirectoryError: If destination is not a directory.
    """
    src_path = Path(src)
    dst_path = Path(dst_dir)

    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src}")
    if not dst_path.is_dir():
        raise NotADirectoryError(f"Destination is not a directory: {dst_dir}")

    destination = dst_path / src_path.name
    shutil.move(str(src_path), str(destination))
    return str(destination)
