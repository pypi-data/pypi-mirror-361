"""
Domain entity representing a multiline string in Python source code.
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from ..exceptions import (
    EmptyStringContentException,
    InvalidIndentationException,
    NotMultilineStringException
)

class QuoteType(Enum):
    TRIPLE_DOUBLE = '"""'
    TRIPLE_SINGLE = "'''"

class StringContext(Enum):
    ASSIGNMENT = "assignment"
    RETURN_STATEMENT = "return"
    FUNCTION_CALL = "function_call"
    DOCSTRING = "docstring"
    
    def get_description(self) -> str:
        """Get user-friendly description of the context."""
        descriptions = {
            self.ASSIGNMENT: "variable assignment",
            self.RETURN_STATEMENT: "return statement",
            self.FUNCTION_CALL: "function argument",
            self.DOCSTRING: "docstring"
        }
        return descriptions.get(self, self.value)

@dataclass(frozen=True)
class Position:
    """Represents a position in source code."""
    line: int
    column: int

@dataclass(frozen=True)
class SourceLocation:
    """Represents a location range in source code."""
    start: Position
    end: Position

@dataclass
class MultilineString:
    """
    Domain entity representing a multiline string that needs indentation fixing.
    """
    content: str
    quote_type: QuoteType
    location: SourceLocation
    context: StringContext
    base_indentation: int
    original_lines: List[str]
    
    def __post_init__(self):
        if not self.content:
            raise EmptyStringContentException()
        if self.base_indentation < 0:
            raise InvalidIndentationException(self.base_indentation)
        if '\n' not in self.content:
            raise NotMultilineStringException(self.content)
    
    @property
    def needs_fixing(self) -> bool:
        """Check if this string needs indentation fixing."""
        if self.context == StringContext.DOCSTRING:
            return False
        
        lines = self.content.split('\n')
        if len(lines) <= 2:  # Only opening/closing lines
            return False
        
        # Check if content lines have proper base indentation
        content_lines = [line for line in lines[1:-1] if line.strip()]
        if not content_lines:
            return False
        
        # Find the minimum indentation of non-empty content lines
        min_indent = float('inf')
        for line in content_lines:
            actual_indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, actual_indent)
        
        # Check if the minimum indentation matches expected base + 4 spaces
        expected_min_indent = self.base_indentation + 4
        return min_indent != expected_min_indent
    
    def get_fixed_content(self) -> str:
        """Generate properly indented content."""
        if not self.needs_fixing:
            return self.content
        
        lines = self.content.split('\n')
        fixed_lines = []
        
        # Find the minimum indentation of non-empty lines (excluding first and last)
        min_indent = float('inf')
        for i, line in enumerate(lines):
            if 0 < i < len(lines) - 1 and line.strip():
                current_indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, current_indent)
        
        # If all lines were empty, no adjustment needed
        if min_indent == float('inf'):
            min_indent = 0
        
        # Expected base indentation for content
        content_base_indent = ' ' * (self.base_indentation + 4)
        
        for i, line in enumerate(lines):
            if i == 0 or i == len(lines) - 1:
                # First and last lines (usually empty)
                fixed_lines.append(line)
            else:
                # Content lines - preserve relative indentation
                if line.strip():
                    # Remove the minimum indentation and add the base indentation
                    current_indent = len(line) - len(line.lstrip())
                    relative_indent = current_indent - min_indent
                    fixed_line = content_base_indent + (' ' * relative_indent) + line.lstrip()
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append('')
        
        return '\n'.join(fixed_lines)
    
    def get_full_replacement(self) -> str:
        """Generate the full string replacement including quotes."""
        base_indent = ' ' * self.base_indentation
        fixed_content = self.get_fixed_content()
        
        return f"{self.quote_type.value}{fixed_content}{base_indent}{self.quote_type.value}"