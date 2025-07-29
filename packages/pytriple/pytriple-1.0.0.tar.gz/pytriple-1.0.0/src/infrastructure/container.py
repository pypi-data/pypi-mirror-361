"""
Dependency injection container for the multiline string fixer.
"""
from dependency_injector import containers, providers

from infrastructure.config import default_config
from infrastructure.parsers.ast_parser import ASTParser
from infrastructure.file_system.file_system_repository import FileSystemRepository
from application.use_cases.fix_file_indentation import FixFileIndentationUseCase
from application.use_cases.fix_directory_indentation import FixDirectoryIndentationUseCase


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""
    
    # Configuration
    config = providers.Object(default_config)
    
    # Infrastructure layer - Repositories
    parser_repository = providers.Singleton(ASTParser)
    
    file_repository = providers.Singleton(
        FileSystemRepository,
        parser_repo=parser_repository
    )
    
    # Application layer - Use cases
    fix_file_use_case = providers.Factory(
        FixFileIndentationUseCase,
        file_repo=file_repository,
        parser_repo=parser_repository
    )
    
    fix_directory_use_case = providers.Factory(
        FixDirectoryIndentationUseCase,
        file_repo=file_repository,
        parser_repo=parser_repository
    )