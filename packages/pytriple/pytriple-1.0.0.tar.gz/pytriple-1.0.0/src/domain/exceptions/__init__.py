"""
Domain exceptions for multiline string indentation fixer.
"""

from .base_exceptions import (
    MultilineStringFixerException,
    DomainException,
    ValidationException,
    BusinessRuleException
)

from .entity_exceptions import (
    MultilineStringException,
    EmptyStringContentException,
    InvalidIndentationException,
    NotMultilineStringException,
    SourceFileException,
    InvalidFileTypeException,
    EmptyFileContentException,
    IndentationFixingException
)

from .parsing_exceptions import (
    ParsingException,
    SyntaxValidationException,
    ASTParsingException,
    MultilineStringDetectionException
)

from .file_exceptions import (
    FileOperationException,
    FileReadException,
    FileWriteException,
    FileNotFoundCustomException,
    InvalidFilePermissionException,
    BackupCreationException,
    DirectoryAccessException
)

__all__ = [
    # Base exceptions
    'MultilineStringFixerException',
    'DomainException',
    'ValidationException',
    'BusinessRuleException',
    
    # Entity exceptions
    'MultilineStringException',
    'EmptyStringContentException',
    'InvalidIndentationException',
    'NotMultilineStringException',
    'SourceFileException',
    'InvalidFileTypeException',
    'EmptyFileContentException',
    'IndentationFixingException',
    
    # Parsing exceptions
    'ParsingException',
    'SyntaxValidationException',
    'ASTParsingException',
    'MultilineStringDetectionException',
    
    # File exceptions
    'FileOperationException',
    'FileReadException',
    'FileWriteException',
    'FileNotFoundCustomException',
    'InvalidFilePermissionException',
    'BackupCreationException',
    'DirectoryAccessException',
]