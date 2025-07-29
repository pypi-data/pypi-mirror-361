"""
Use case for fixing multiline string indentation in all Python files in a directory.
"""
from pathlib import Path
from typing import List
from domain.repositories.file_repository import FileRepository
from domain.repositories.parser_repository import ParserRepository
from application.use_cases.fix_file_indentation import FixFileIndentationUseCase
from application.dtos.fix_file_result import FixFileResult
from application.dtos.fix_directory_result import FixDirectoryResult

class FixDirectoryIndentationUseCase:
    """Use case for fixing multiline string indentation in all Python files in a directory."""
    
    def __init__(self, file_repo: FileRepository, parser_repo: ParserRepository):
        self.file_repo = file_repo
        self.parser_repo = parser_repo
        self.fix_file_use_case = FixFileIndentationUseCase(file_repo, parser_repo)
    
    def execute(self, directory_path: Path, create_backup: bool = True, 
                exclude_patterns: List[str] = None) -> FixDirectoryResult:
        """
        Fix multiline string indentation in all Python files in a directory.
        
        Args:
            directory_path: Path to the directory to process
            create_backup: Whether to create backups before modifying
            exclude_patterns: List of patterns to exclude (e.g., ['test_*', '*_test.py'])
            
        Returns:
            FixDirectoryResult with details about the operation
        """
        if exclude_patterns is None:
            exclude_patterns = ['test_*', '*_test.py', 'fix_*.py']
        
        try:
            # Find all Python files
            python_files = self.file_repo.find_python_files(directory_path)
            
            # Filter out excluded files
            filtered_files = []
            for file_path in python_files:
                should_exclude = any(
                    file_path.match(pattern) for pattern in exclude_patterns
                )
                if not should_exclude:
                    filtered_files.append(file_path)
            
            # Process each file
            file_results = []
            errors = []
            files_modified = 0
            total_strings_fixed = 0
            
            for file_path in filtered_files:
                result = self.fix_file_use_case.execute(file_path, create_backup)
                file_results.append(result)
                
                if result.error:
                    errors.append(f"{file_path}: {result.error}")
                elif result.was_modified:
                    files_modified += 1
                    total_strings_fixed += result.strings_fixed
            
            return FixDirectoryResult(
                directory_path=directory_path,
                files_processed=len(filtered_files),
                files_modified=files_modified,
                total_strings_fixed=total_strings_fixed,
                errors=errors,
                file_results=file_results
            )
            
        except Exception as e:
            return FixDirectoryResult(
                directory_path=directory_path,
                files_processed=0,
                files_modified=0,
                total_strings_fixed=0,
                errors=[f"Directory processing error: {str(e)}"],
                file_results=[]
            )