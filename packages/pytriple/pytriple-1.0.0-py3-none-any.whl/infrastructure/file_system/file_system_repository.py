"""
File system implementation of file repository.
"""
import os
from pathlib import Path
from typing import List, Optional
from domain.entities.source_file import SourceFile
from domain.repositories.parser_repository import ParserRepository
from domain.exceptions import FileReadException, FileWriteException

class FileSystemRepository:
    """File system implementation of file repository."""
    
    def __init__(self, parser_repo: ParserRepository):
        self.parser_repo = parser_repo
    
    def read_file(self, path: Path) -> Optional[SourceFile]:
        """Read a Python source file."""
        if not path.exists() or not path.is_file():
            return None
        
        if path.suffix != '.py':
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileReadException(f"File not found: {path}")
        except PermissionError:
            raise FileReadException(f"Permission denied reading file: {path}")
        except UnicodeDecodeError:
            raise FileReadException(f"File is not valid UTF-8: {path}")
        except Exception as e:
            raise FileReadException(f"Error reading file {path}: {str(e)}")
        
        # Parse multiline strings (empty files will have no strings)
        multiline_strings = []
        if content.strip():  # Only parse non-empty files
            try:
                multiline_strings = self.parser_repo.parse_multiline_strings(content)
            except Exception:
                # Don't fail on parse errors - file might have syntax errors
                pass
        
        return SourceFile(
            path=path,
            content=content,
            multiline_strings=multiline_strings
        )
    
    def write_file(self, source_file: SourceFile) -> bool:
        """Write a source file with fixed content."""
        try:
            with open(source_file.path, 'w', encoding='utf-8') as f:
                f.write(source_file.content)
            return True
        except PermissionError:
            raise FileWriteException(f"Permission denied writing file: {source_file.path}")
        except OSError as e:
            if e.errno == 28:  # No space left on device
                raise FileWriteException(f"No space left on device: {source_file.path}")
            raise FileWriteException(f"OS error writing file {source_file.path}: {str(e)}")
        except Exception as e:
            raise FileWriteException(f"Error writing file {source_file.path}: {str(e)}")
    
    def create_backup(self, source_file: SourceFile) -> bool:
        """Create a backup of the source file."""
        backup_path = source_file.create_backup_path()
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(source_file.content)
            return True
        except PermissionError:
            raise FileWriteException(f"Permission denied creating backup: {backup_path}")
        except OSError as e:
            if e.errno == 28:  # No space left on device
                raise FileWriteException(f"No space left on device for backup: {backup_path}")
            raise FileWriteException(f"OS error creating backup {backup_path}: {str(e)}")
        except Exception as e:
            raise FileWriteException(f"Error creating backup {backup_path}: {str(e)}")
    
    def find_python_files(self, directory: Path) -> List[Path]:
        """Find all Python files in a directory."""
        python_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(Path(root) / file)
            
            return python_files
            
        except Exception as e:
            print(f"Error finding Python files in {directory}: {e}")
            return []
    
    def file_exists(self, path: Path) -> bool:
        """Check if a file exists."""
        return path.exists() and path.is_file()