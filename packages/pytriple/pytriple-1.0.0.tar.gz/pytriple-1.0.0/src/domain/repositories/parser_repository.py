"""
Repository interface for parsing operations.
"""
from typing import List, Protocol
from ..entities.multiline_string import MultilineString

class ParserRepository(Protocol):
    """Repository protocol for parsing operations."""
    
    def parse_multiline_strings(self, content: str) -> List[MultilineString]:
        """Parse multiline strings from Python source code."""
        ...
    
    def validate_syntax(self, content: str) -> bool:
        """Validate that the content has valid Python syntax."""
        ...