"""
Click-based CLI for multiline string indentation fixer.
"""
import click
import sys
from pathlib import Path
from typing import List
from infrastructure.container import Container

class CLIContext:
    """Context object for CLI commands."""
    
    def __init__(self):
        self.container = Container()
        self.container.wire(modules=[__name__])
        
        # Get use cases from container
        self.fix_file_use_case = self.container.fix_file_use_case()
        self.fix_directory_use_case = self.container.fix_directory_use_case()
        
        # Access repositories if needed
        self.file_repo = self.container.file_repository()
        self.parser_repo = self.container.parser_repository()

@click.group()
@click.version_option(version='1.0.0', prog_name='pytriple')
@click.pass_context
def cli(ctx):
    """
    pytriple - Python Triple-Quoted String Formatter
    
    Automatically fixes the base indentation of triple-quoted strings in Python files
    while preserving the relative indentation structure within the strings.
    
    This ensures that the hierarchical structure of SQL queries, JSON data,
    HTML templates, YAML configs, etc. remains exactly as the developer intended.
    
    Examples:
      pytriple check script.py              # Check if a file needs fixing
      pytriple fix-file script.py           # Fix a single file
      pytriple fix-directory src/           # Fix all Python files in a directory
      pytriple fix-file --dry-run file.py  # Preview changes without modifying
    """
    ctx.ensure_object(CLIContext)

@cli.command()
@click.argument('file_path', type=click.Path(exists=True, path_type=Path))
@click.option('--backup/--no-backup', default=True, 
              help='Create backup before modifying file (default: create backup)')
@click.option('--dry-run', is_flag=True, 
              help='Show what would be changed without modifying files')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed information about changes')
@click.pass_obj
def fix_file(ctx: CLIContext, file_path: Path, backup: bool, dry_run: bool, verbose: bool):
    """
    Fix multiline string indentation in a single Python file.
    
    This command adjusts the base indentation of triple-quoted strings to match
    Python conventions (parent indentation + 4 spaces) while preserving the
    relative indentation of content within the strings.
    
    By default, creates a backup with .backup extension before modifying.
    """
    
    if not file_path.suffix == '.py':
        click.echo(click.style(f"Error: {file_path} is not a Python file", fg='red'))
        sys.exit(1)
    
    if dry_run:
        click.echo(click.style(f"[DRY RUN] Checking: {file_path}", fg='yellow'))
        
        source_file = ctx.file_repo.read_file(file_path)
        if not source_file:
            click.echo(click.style(f"Error: Could not read file {file_path}", fg='red'))
            return
        
        if source_file.needs_fixing:
            fixable_strings = source_file.fixable_strings
            click.echo(click.style(f"Would fix {len(fixable_strings)} multiline strings", fg='yellow'))
            if verbose:
                for i, ms in enumerate(fixable_strings, 1):
                    click.echo(f"  {i}. Lines {ms.location.start.line}-{ms.location.end.line}: {ms.context.get_description()}")
        else:
            click.echo(click.style("No changes needed", fg='green'))
        return
    
    if verbose:
        click.echo(f"Processing file: {file_path}")
    
    result = ctx.fix_file_use_case.execute(file_path, backup)
    
    if result.error:
        click.echo(click.style(f"Error: {result.error}", fg='red'))
        sys.exit(1)
    
    if result.was_modified:
        click.echo(click.style(f"✅ Fixed {result.strings_fixed} multiline strings", fg='green'))
        if verbose and result.strings_fixed > 0:
            source_file = ctx.file_repo.read_file(file_path)
            if source_file:
                click.echo("Fixed strings at:")
                # Read the original file to show what was fixed
                original_content = None
                if result.backup_created:
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    try:
                        with open(backup_path, 'r') as f:
                            original_content = f.read()
                    except:
                        pass
                
                if original_content:
                    # Parse original to show what was fixed
                    original_strings = ctx.parser_repo.parse_multiline_strings(original_content)
                    for i, ms in enumerate([s for s in original_strings if s.needs_fixing], 1):
                        click.echo(f"  - Lines {ms.location.start.line}-{ms.location.end.line}: {ms.context.get_description()}")
        
        if result.backup_created:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            click.echo(f"📁 Backup created: {backup_path}")
    else:
        click.echo(click.style("ℹ️  No changes needed", fg='blue'))

@cli.command()
@click.argument('directory_path', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--backup/--no-backup', default=True,
              help='Create backups before modifying files (default: create backups)')
@click.option('--dry-run', is_flag=True,
              help='Show what would be changed without modifying files')
@click.option('--exclude', multiple=True, 
              help='Exclude files matching pattern (can be used multiple times)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed output for each file')
@click.pass_obj
def fix_directory(ctx: CLIContext, directory_path: Path, backup: bool, 
                  dry_run: bool, exclude: List[str], verbose: bool):
    """
    Fix multiline string indentation in all Python files in a directory.
    
    Recursively processes all .py files in the specified directory and its
    subdirectories. By default, excludes test files and files starting with 'fix_'.
    
    Use --exclude to specify additional patterns to skip (supports glob patterns).
    Use --verbose to see detailed progress for each file.
    """
    
    if dry_run:
        click.echo(click.style(f"[DRY RUN] Checking directory: {directory_path}", fg='yellow'))
        
        # Get Python files
        python_files = ctx.file_repo.find_python_files(directory_path)
        
        # Apply exclude patterns
        exclude_patterns = list(exclude) if exclude else ['test_*', '*_test.py', 'fix_*.py']
        filtered_files = [
            f for f in python_files
            if not any(f.match(pattern) for pattern in exclude_patterns)
        ]
        
        if exclude_patterns:
            click.echo(f"Excluding patterns: {', '.join(exclude_patterns)}")
        
        click.echo(f"Found {len(filtered_files)} Python files to check")
        
        total_fixes_needed = 0
        files_needing_fixes = 0
        
        for file_path in filtered_files:
            source_file = ctx.file_repo.read_file(file_path)
            if source_file and source_file.needs_fixing:
                fixable_count = len(source_file.fixable_strings)
                total_fixes_needed += fixable_count
                files_needing_fixes += 1
                if verbose:
                    click.echo(f"  {file_path}: {fixable_count} strings need fixing")
        
        click.echo(f"\n📊 Dry Run Summary:")
        click.echo(f"  Files that would be modified: {files_needing_fixes}")
        click.echo(f"  Total strings that would be fixed: {total_fixes_needed}")
        
        if files_needing_fixes > 0:
            click.echo(click.style(f"\nRun without --dry-run to apply these fixes", fg='yellow'))
        else:
            click.echo(click.style("\nNo fixes needed!", fg='green'))
        return
    
    click.echo(f"Processing directory: {directory_path}")
    
    # Convert exclude patterns
    exclude_patterns = list(exclude) if exclude else ['test_*', '*_test.py', 'fix_*.py']
    
    if exclude_patterns:
        click.echo(f"Excluding patterns: {', '.join(exclude_patterns)}")
    
    result = ctx.fix_directory_use_case.execute(directory_path, backup, exclude_patterns)
    
    if result.errors:
        click.echo(click.style("⚠️  Errors occurred:", fg='yellow'))
        for error in result.errors:
            click.echo(click.style(f"  {error}", fg='red'))
    
    if verbose:
        click.echo("\nFile details:")
        for file_result in result.file_results:
            status = "✅" if file_result.was_modified else "➖"
            click.echo(f"  {status} {file_result.file_path}")
            if file_result.was_modified:
                click.echo(f"    Fixed {file_result.strings_fixed} strings")
    
    # Summary
    click.echo(f"\n📊 Summary:")
    click.echo(f"  Files processed: {result.files_processed}")
    click.echo(f"  Files modified: {result.files_modified}")
    click.echo(f"  Total strings fixed: {result.total_strings_fixed}")
    
    if result.files_modified > 0:
        click.echo(click.style(f"✅ Successfully fixed {result.total_strings_fixed} multiline strings!", fg='green'))
    else:
        click.echo(click.style("ℹ️  No files needed fixing", fg='blue'))

@cli.command()
@click.argument('file_path', type=click.Path(exists=True, path_type=Path))
@click.pass_obj
def check(ctx: CLIContext, file_path: Path):
    """
    Check if a file has multiline strings that need fixing (without modifying).
    
    This command analyzes the file and reports any triple-quoted strings where
    the base indentation doesn't match Python conventions. No files are modified.
    
    Exit codes:
      0 - All strings are properly indented
      1 - One or more strings need fixing
    """
    
    if not file_path.suffix == '.py':
        click.echo(click.style(f"Error: {file_path} is not a Python file", fg='red'))
        sys.exit(1)
    
    source_file = ctx.file_repo.read_file(file_path)
    
    if not source_file:
        click.echo(click.style(f"Error: Could not read file {file_path}", fg='red'))
        sys.exit(1)
    
    if source_file.needs_fixing:
        fixable_strings = source_file.fixable_strings
        click.echo(click.style(f"⚠️  {len(fixable_strings)} multiline strings need fixing:", fg='yellow'))
        
        for i, ms in enumerate(fixable_strings, 1):
            click.echo(f"  {i}. Lines {ms.location.start.line}-{ms.location.end.line}: {ms.context.get_description()}")
        
        sys.exit(1)  # Exit with error code if fixes are needed
    else:
        click.echo(click.style("✅ All multiline strings are properly indented", fg='green'))


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()