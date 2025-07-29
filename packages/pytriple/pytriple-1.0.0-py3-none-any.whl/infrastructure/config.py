"""
Configuration for the multiline string fixer.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    """Application configuration."""
    
    # File processing settings
    create_backups: bool = True
    backup_extension: str = ".backup"
    
    # Exclusion patterns
    default_exclude_patterns: List[str] = None
    
    # Validation settings
    validate_syntax: bool = True
    
    # Output settings
    verbose: bool = False
    colored_output: bool = True
    
    def __post_init__(self):
        if self.default_exclude_patterns is None:
            self.default_exclude_patterns = [
                'test_*',
                '*_test.py',
                'fix_*.py',
                '__pycache__/*',
                '.git/*',
                '.venv/*',
                'venv/*'
            ]

# Default configuration instance
default_config = Config()