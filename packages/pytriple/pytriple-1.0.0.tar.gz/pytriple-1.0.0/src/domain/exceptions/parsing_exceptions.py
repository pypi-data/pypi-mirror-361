"""
Parsing-related exceptions for the multiline string indentation fixer.
"""

from .base_exceptions import MultilineStringFixerException

class ParsingException(MultilineStringFixerException):
    """Base exception for parsing-related errors."""
    pass

class SyntaxValidationException(ParsingException):
    """Exception raised when Python syntax validation fails."""
    
    def __init__(self, error_message: str, line_number: int = None):
        message = f"Invalid Python syntax: {error_message}"
        details = f"Line {line_number}" if line_number else None
        super().__init__(message, details)

class ASTParsingException(ParsingException):
    """Exception raised when AST parsing fails."""
    
    def __init__(self, error_message: str, content_preview: str = None):
        message = f"Failed to parse AST: {error_message}"
        details = f"Content preview: {content_preview[:100]}..." if content_preview else None
        super().__init__(message, details)

class MultilineStringDetectionException(ParsingException):
    """Exception raised when multiline string detection fails."""
    
    def __init__(self, line_number: int, error_message: str):
        message = f"Failed to detect multiline string at line {line_number}"
        super().__init__(message, error_message)