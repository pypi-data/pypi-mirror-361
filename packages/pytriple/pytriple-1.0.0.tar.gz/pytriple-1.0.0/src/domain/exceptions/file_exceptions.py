"""
File operation exceptions for the multiline string indentation fixer.
"""

from pathlib import Path
from .base_exceptions import MultilineStringFixerException

class FileOperationException(MultilineStringFixerException):
    """Base exception for file operation errors."""
    pass

class FileReadException(FileOperationException):
    """Exception raised when file reading fails."""
    
    def __init__(self, file_path: Path, error_message: str):
        message = f"Failed to read file: {file_path}"
        super().__init__(message, error_message)

class FileWriteException(FileOperationException):
    """Exception raised when file writing fails."""
    
    def __init__(self, file_path: Path, error_message: str):
        message = f"Failed to write file: {file_path}"
        super().__init__(message, error_message)

class FileNotFoundCustomException(FileOperationException):
    """Exception raised when file is not found."""
    
    def __init__(self, file_path: Path):
        message = f"File not found: {file_path}"
        details = f"Absolute path: {file_path.absolute()}"
        super().__init__(message, details)

class InvalidFilePermissionException(FileOperationException):
    """Exception raised when file permissions are insufficient."""
    
    def __init__(self, file_path: Path, operation: str):
        message = f"Insufficient permissions for {operation}: {file_path}"
        super().__init__(message)

class BackupCreationException(FileOperationException):
    """Exception raised when backup creation fails."""
    
    def __init__(self, file_path: Path, backup_path: Path, error_message: str):
        message = f"Failed to create backup for {file_path}"
        details = f"Backup path: {backup_path}, Error: {error_message}"
        super().__init__(message, details)

class DirectoryAccessException(FileOperationException):
    """Exception raised when directory access fails."""
    
    def __init__(self, directory_path: Path, error_message: str):
        message = f"Failed to access directory: {directory_path}"
        super().__init__(message, error_message)