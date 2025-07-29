"""
AST-based parser for multiline strings.
"""
import ast
from typing import List, Optional
from domain.entities.multiline_string import (
    MultilineString, QuoteType, StringContext, Position, SourceLocation
)
from domain.exceptions import ParsingException

class ASTParser:
    """AST-based implementation of parser repository."""
    
    def parse_multiline_strings(self, content: str) -> List[MultilineString]:
        """Parse multiline strings from Python source code using AST."""
        # Handle empty or whitespace-only content
        if not content.strip():
            return []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ParsingException(f"Invalid Python syntax at line {e.lineno}: {e.msg}")
        except Exception as e:
            raise ParsingException(f"Error parsing content: {str(e)}")
        
        multiline_strings = []
        lines = content.splitlines()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if '\n' in node.value:  # Only multiline strings
                    multiline_string = self._create_multiline_string(
                        node, lines
                    )
                    if multiline_string:
                        multiline_strings.append(multiline_string)
        
        return multiline_strings
    
    def validate_syntax(self, content: str) -> bool:
        """Validate that the content has valid Python syntax."""
        try:
            # Empty files are valid Python
            if not content.strip():
                return True
            ast.parse(content)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _create_multiline_string(self, node: ast.Constant, lines: List[str]) -> Optional[MultilineString]:
        """Create a MultilineString entity from an AST node."""
        try:
            # Get source location
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            start_col = node.col_offset
            end_col = node.end_col_offset or start_col
            
            location = SourceLocation(
                start=Position(line=start_line, column=start_col),
                end=Position(line=end_line, column=end_col)
            )
            
            # Get the line containing the string start
            line_idx = start_line - 1
            if line_idx >= len(lines):
                return None
                
            assignment_line = lines[line_idx]
            
            # Determine quote type
            quote_type = self._determine_quote_type(assignment_line)
            if not quote_type:
                return None
            
            # Determine context
            context = self._determine_context(assignment_line)
            
            # Calculate base indentation
            base_indentation = len(assignment_line) - len(assignment_line.lstrip())
            
            # Get original lines for the string
            original_lines = lines[line_idx:end_line]
            
            return MultilineString(
                content=node.value,
                quote_type=quote_type,
                location=location,
                context=context,
                base_indentation=base_indentation,
                original_lines=original_lines
            )
            
        except Exception:
            return None
    
    def _determine_quote_type(self, line: str) -> Optional[QuoteType]:
        """Determine the quote type used in the line."""
        if '"""' in line:
            return QuoteType.TRIPLE_DOUBLE
        elif "'''" in line:
            return QuoteType.TRIPLE_SINGLE
        return None
    
    def _determine_context(self, line: str) -> StringContext:
        """Determine the context of the string (assignment, return, etc.)."""
        stripped = line.strip()
        
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return StringContext.DOCSTRING
        elif 'return' in line:
            return StringContext.RETURN_STATEMENT
        elif '=' in line:
            return StringContext.ASSIGNMENT
        else:
            return StringContext.FUNCTION_CALL