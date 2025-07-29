"""
Use case for fixing multiline string indentation in a single file.
"""
from pathlib import Path
from typing import Optional, List
from domain.repositories.file_repository import FileRepository
from domain.repositories.parser_repository import ParserRepository
from domain.entities.source_file import SourceFile
from domain.exceptions import FileReadException, FileWriteException, ParsingException
from application.dtos.fix_file_result import FixFileResult

class FixFileIndentationUseCase:
    """Use case for fixing multiline string indentation in a single file."""
    
    def __init__(self, file_repo: FileRepository, parser_repo: ParserRepository):
        self.file_repo = file_repo
        self.parser_repo = parser_repo
    
    def execute(self, file_path: Path, create_backup: bool = True) -> FixFileResult:
        """
        Fix multiline string indentation in a single file.
        
        Args:
            file_path: Path to the Python file to fix
            create_backup: Whether to create a backup before modifying
            
        Returns:
            FixFileResult with details about the operation
        """
        try:
            # Read the file
            try:
                source_file = self.file_repo.read_file(file_path)
                if not source_file:
                    return FixFileResult(
                        file_path=file_path,
                        was_modified=False,
                        backup_created=False,
                        error=f"Could not read file: {file_path}"
                    )
            except FileReadException as e:
                return FixFileResult(
                    file_path=file_path,
                    was_modified=False,
                    backup_created=False,
                    error=str(e)
                )
            
            # Check if file needs fixing
            if not source_file.needs_fixing:
                return FixFileResult(
                    file_path=file_path,
                    was_modified=False,
                    backup_created=False,
                    strings_fixed=0
                )
            
            # Create backup if requested
            backup_created = False
            if create_backup:
                try:
                    backup_created = self.file_repo.create_backup(source_file)
                except FileWriteException as e:
                    return FixFileResult(
                        file_path=file_path,
                        was_modified=False,
                        backup_created=False,
                        error=f"Failed to create backup: {str(e)}"
                    )
            
            # Get fixed content
            fixed_content = source_file.get_fixed_content()
            
            # Validate syntax of fixed content
            if not self.parser_repo.validate_syntax(fixed_content):
                return FixFileResult(
                    file_path=file_path,
                    was_modified=False,
                    backup_created=backup_created,
                    error="Fixed content has invalid syntax"
                )
            
            # Create updated source file
            updated_source_file = SourceFile(
                path=source_file.path,
                content=fixed_content,
                multiline_strings=source_file.multiline_strings
            )
            
            # Write the fixed file
            try:
                write_success = self.file_repo.write_file(updated_source_file)
                if not write_success:
                    return FixFileResult(
                        file_path=file_path,
                        was_modified=False,
                        backup_created=backup_created,
                        error="Could not write fixed file"
                    )
            except FileWriteException as e:
                return FixFileResult(
                    file_path=file_path,
                    was_modified=False,
                    backup_created=backup_created,
                    error=str(e)
                )
            
            return FixFileResult(
                file_path=file_path,
                was_modified=True,
                backup_created=backup_created,
                strings_fixed=len(source_file.fixable_strings)
            )
            
        except ParsingException as e:
            return FixFileResult(
                file_path=file_path,
                was_modified=False,
                backup_created=False,
                error=f"Parse error: {str(e)}"
            )
        except Exception as e:
            return FixFileResult(
                file_path=file_path,
                was_modified=False,
                backup_created=False,
                error=f"Unexpected error: {str(e)}"
            )