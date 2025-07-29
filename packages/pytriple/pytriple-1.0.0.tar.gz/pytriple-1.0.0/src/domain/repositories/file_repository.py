"""
Repository interface for file operations.
"""
from pathlib import Path
from typing import List, Optional, Protocol
from ..entities.source_file import SourceFile

class FileRepository(Protocol):
    """Repository protocol for file operations."""
    
    def read_file(self, path: Path) -> Optional[SourceFile]:
        """Read a Python source file."""
        ...
    
    def write_file(self, source_file: SourceFile) -> bool:
        """Write a source file with fixed content."""
        ...
    
    def create_backup(self, source_file: SourceFile) -> bool:
        """Create a backup of the source file."""
        ...
    
    def find_python_files(self, directory: Path) -> List[Path]:
        """Find all Python files in a directory."""
        ...
    
    def file_exists(self, path: Path) -> bool:
        """Check if a file exists."""
        ...