"""Result DTO for directory fixing operations."""
from dataclasses import dataclass, field
from typing import List
from application.dtos.fix_file_result import FixFileResult

@dataclass
class FixDirectoryResult:
    """Result of fixing a directory's Python files."""
    directory_path: str
    files_processed: int = 0
    files_modified: int = 0
    total_strings_fixed: int = 0
    file_results: List[FixFileResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)