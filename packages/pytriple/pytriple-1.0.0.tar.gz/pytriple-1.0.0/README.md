# pytriple

A Python tool for automatically fixing triple-quoted string indentation while preserving relative indentation structure.

## Features

- **Automatic Detection**: Uses AST parsing to accurately detect multiline strings
- **Preserves Relative Indentation**: Maintains the relative indentation structure within strings, ensuring that the hierarchical structure of SQL, JSON, HTML, YAML, etc. is preserved exactly as the developer intended
- **Clean Architecture**: Built with Domain-Driven Design principles
- **Backup Support**: Creates backups before modifying files (default behavior)
- **CLI Interface**: User-friendly command line interface
- **Comprehensive**: Handles all triple-quoted strings in assignments, returns, and function calls

## Installation

```bash
pip install pytriple
```

## Usage

### Fix a single file
```bash
pytriple fix-file example.py
```

### Fix all files in a directory
```bash
pytriple fix-directory /path/to/project
```

### Check a file without modifying
```bash
pytriple check example.py
```

### Command Options

#### fix-file
- `--no-backup`: Skip creating backup files
- `--dry-run`: Preview changes without modifying files
- `--verbose`, `-v`: Show detailed information about changes

#### fix-directory
- `--no-backup`: Skip creating backup files
- `--dry-run`: Preview changes without modifying files
- `--exclude`: Exclude files matching pattern (can be used multiple times)
- `--verbose`, `-v`: Show detailed output for each file

## Architecture

The project follows clean architecture principles:

- **Domain Layer**: Core business entities and rules
- **Application Layer**: Use cases for fixing files and directories
- **Infrastructure Layer**: File system operations and AST parsing
- **Presentation Layer**: CLI interface

## Example

Before:
```python
class DatabaseManager:
    def __init__(self):
        self.query = """
    SELECT u.id,
        u.username,
            u.email
    FROM users u
        WHERE u.active = 1
        """
```

After:
```python
class DatabaseManager:
    def __init__(self):
        self.query = """
            SELECT u.id,
                u.username,
                u.email
            FROM users u
                WHERE u.active = 1
        """
```

## How It Works

pytriple analyzes Python files using AST (Abstract Syntax Tree) parsing to find triple-quoted strings. It then:

1. Identifies strings where the base indentation doesn't match Python conventions
2. Calculates the minimum indentation level of content lines
3. Adjusts only the base indentation to match the code context (parent indentation + 4 spaces)
4. **Preserves all relative indentation** within the string content
5. Writes the corrected content back to the file

This approach ensures that:
- Python code follows consistent indentation practices
- The internal structure of SQL queries, JSON data, HTML templates, YAML configs, etc. remains exactly as intended
- Complex hierarchical content maintains its readability and structure

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/MartinKalema/pytriple.git
cd pytriple

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Martin Kalema