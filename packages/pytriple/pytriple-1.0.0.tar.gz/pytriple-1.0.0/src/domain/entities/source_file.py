"""
Domain entity representing a Python source file.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from domain.entities.multiline_string import MultilineString
from domain.exceptions import (
    InvalidFileTypeException
)

@dataclass
class SourceFile:
    """
    Domain entity representing a Python source file that may contain multiline strings.
    """
    path: Path
    content: str
    multiline_strings: List[MultilineString]
    
    def __post_init__(self):
        if not self.path.suffix == '.py':
            raise InvalidFileTypeException(str(self.path))
        # Empty files are allowed - they will be skipped during processing
    
    @property
    def needs_fixing(self) -> bool:
        """Check if this file contains multiline strings that need fixing."""
        # Empty files don't need fixing
        if not self.content.strip():
            return False
        return any(ms.needs_fixing for ms in self.multiline_strings)
    
    @property
    def fixable_strings(self) -> List[MultilineString]:
        """Get all multiline strings that need fixing."""
        return [ms for ms in self.multiline_strings if ms.needs_fixing]
    
    def get_fixed_content(self) -> str:
        """Generate the file content with fixed multiline string indentation."""
        if not self.needs_fixing:
            return self.content
        
        # Empty files return as-is
        if not self.content.strip():
            return self.content
        
        # Sort strings by location (reverse order to avoid offset issues)
        strings_to_fix = sorted(self.fixable_strings, 
                               key=lambda ms: ms.location.start.line, 
                               reverse=True)
        
        lines = self.content.splitlines(keepends=True)
        
        for string in strings_to_fix:
            start_line = string.location.start.line - 1  # Convert to 0-based
            end_line = string.location.end.line - 1
            
            # Get the assignment/return line
            assignment_line = lines[start_line].rstrip()
            
            # Find where the string content starts
            if '"""' in assignment_line:
                prefix = assignment_line[:assignment_line.rfind('"""')]
                quote_type = '"""'
            else:
                prefix = assignment_line[:assignment_line.rfind("'''")]
                quote_type = "'''"
            
            # Create the fixed string
            base_indent = ' ' * string.base_indentation
            fixed_content = string.get_fixed_content()
            
            # Build replacement lines
            new_lines = []
            new_lines.append(prefix + quote_type + '\n')
            
            # Add content lines
            for line in fixed_content.split('\n')[1:-1]:  # Skip first/last empty lines
                if line.strip() or line == '':
                    new_lines.append(line + '\n')
            
            # Add closing line
            new_lines.append(base_indent + quote_type + '\n')
            
            # Replace in the original content
            lines[start_line:end_line + 1] = new_lines
        
        return ''.join(lines)
    
    def create_backup_path(self) -> Path:
        """Create a backup file path."""
        return self.path.with_suffix(f"{self.path.suffix}.backup")