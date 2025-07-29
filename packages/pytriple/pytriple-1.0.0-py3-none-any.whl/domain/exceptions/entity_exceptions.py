"""
Entity-specific exceptions for the multiline string indentation fixer.
"""

from .base_exceptions import ValidationException, BusinessRuleException

class MultilineStringException(ValidationException):
    """Base exception for MultilineString entity errors."""
    pass

class EmptyStringContentException(MultilineStringException):
    """Exception raised when multiline string content is empty."""
    
    def __init__(self):
        super().__init__("MultilineString content cannot be empty")

class InvalidIndentationException(MultilineStringException):
    """Exception raised when base indentation is invalid."""
    
    def __init__(self, indentation: int):
        super().__init__(
            f"Base indentation cannot be negative: {indentation}",
            f"Received indentation value: {indentation}"
        )

class NotMultilineStringException(MultilineStringException):
    """Exception raised when string is not actually multiline."""
    
    def __init__(self, content: str):
        super().__init__(
            "String must be multiline (contain newlines)",
            f"Content: {repr(content[:50])}..."
        )

class SourceFileException(ValidationException):
    """Base exception for SourceFile entity errors."""
    pass

class InvalidFileTypeException(SourceFileException):
    """Exception raised when file is not a Python file."""
    
    def __init__(self, file_path: str):
        super().__init__(
            f"File must be a Python file (.py): {file_path}",
            f"File extension: {file_path.split('.')[-1] if '.' in file_path else 'none'}"
        )

class EmptyFileContentException(SourceFileException):
    """Exception raised when file content is empty."""
    
    def __init__(self, file_path: str):
        super().__init__(
            f"File content cannot be empty: {file_path}"
        )

class IndentationFixingException(BusinessRuleException):
    """Exception raised when indentation fixing fails."""
    
    def __init__(self, reason: str, file_path: str = None):
        message = f"Failed to fix indentation: {reason}"
        details = f"File: {file_path}" if file_path else None
        super().__init__(message, details)