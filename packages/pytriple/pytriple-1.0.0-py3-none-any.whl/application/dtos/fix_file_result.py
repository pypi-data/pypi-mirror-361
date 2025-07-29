"""Result DTO for file fixing operations."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class FixFileResult:
    """Result of fixing a file's indentation."""
    file_path: Path
    was_modified: bool
    backup_created: bool
    error: Optional[str] = None
    strings_fixed: int = 0