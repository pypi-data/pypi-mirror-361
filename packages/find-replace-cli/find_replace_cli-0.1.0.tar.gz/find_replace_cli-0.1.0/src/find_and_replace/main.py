#!/usr/bin/env python3
"""
find-and-replace: A CLI tool to find and replace text in files using regular expressions
"""

import argparse
import glob
import os
import re
import sys
from enum import Enum
from pathlib import Path
from typing import List


class Colors(Enum):
    """ANSI color codes for terminal output."""

    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: Colors = Colors.NC) -> None:
    """Print message with color."""
    print(f"{color.value}{message}{Colors.NC.value}")


def find_files(file_pattern: str, directory: str, recursive: bool = False) -> List[str]:
    """
    Find files matching the pattern in the specified directory.

    Args:
        file_pattern: Glob pattern for file names
        directory: Directory to search in
        recursive: Whether to search recursively

    Returns:
        List of file paths matching the pattern
    """

    base_path = Path(directory)
    if not base_path.exists():
        print_colored(f"Error: Directory '{directory}' does not exist.", Colors.RED)
        return []

    if recursive:
        files = [str(f) for f in base_path.rglob(file_pattern) if f.is_file()]
    else:
        search_pattern = os.path.join(directory, file_pattern)
        files = [f for f in glob.glob(search_pattern) if os.path.isfile(f)]

    return sorted(files)


def show_matches_for_confirmation(matches: List, content: str, replacement: str) -> bool:
    """Show matches and get user confirmation."""
    for i, match in enumerate(matches, 1):
        start, _ = match.span()
        line_num = content[:start].count("\n") + 1
        lines = content.split("\n")
        context_line = lines[line_num - 1] if line_num <= len(lines) else ""

        print_colored(f"\nMatch {i} (line {line_num}):", Colors.GREEN)
        print_colored(f"  Found: '{match.group()}'", Colors.NC)
        print_colored(f"  Context: {context_line}", Colors.NC)
        print_colored(f"  Replace with: '{replacement}'", Colors.NC)

    response = input(f"\nReplace all {len(matches)} match(es) in this file? (y/n/q): ").lower()

    if response == "q":
        print_colored("Operation cancelled by user.", Colors.YELLOW)
        sys.exit(0)
    return response == "y"


def read_file_content(file_path: str) -> str:
    """Read file content with proper error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        print_colored(f"Error: Cannot read file '{file_path}' - not a text file or encoding issue", Colors.RED)
        return ""
    except PermissionError:
        print_colored(f"Error: Permission denied accessing file '{file_path}'", Colors.RED)
        return ""
    except Exception as e:
        print_colored(f"Error reading file '{file_path}': {e}", Colors.RED)
        return ""


def write_file_content(file_path: str, content: str) -> bool:
    """Write file content with proper error handling."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return True
    except PermissionError:
        print_colored(f"Error: Permission denied writing to file '{file_path}'", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"Error writing to file '{file_path}': {e}", Colors.RED)
        return False


def process_file(file_path: str, pattern: str, replacement: str, no_confirm: bool = False) -> bool:
    """
    Process a single file for find and replace operations.

    Args:
        file_path: Path to the file to process
        pattern: Regular expression pattern to find
        replacement: Text to replace matches with
        no_confirm: Whether to skip confirmation prompts

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = read_file_content(file_path)
        if not content:
            return False

        regex = re.compile(pattern)
        matches = list(regex.finditer(content))

        if not matches:
            print_colored(f"No matches found in: {file_path}", Colors.YELLOW)
            return False

        print_colored(f"\nFile: {file_path}", Colors.BLUE)
        print_colored(f"Found {len(matches)} match(es)", Colors.GREEN)

        if not no_confirm and not show_matches_for_confirmation(matches, content, replacement):
            print_colored("Skipping file.", Colors.YELLOW)
            return False

        new_content = regex.sub(replacement, content)

        if not write_file_content(file_path, new_content):
            return False

        print_colored(f"✓ Successfully replaced {len(matches)} match(es) in: {file_path}", Colors.GREEN)
        return True

    except re.error as e:
        print_colored(f"Error: Invalid regular expression - {e}", Colors.RED)
        return False


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Find and replace text in files using regular expressions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
  find-and-replace "*.py" /path/to/project "old_function" "new_function"
  find-and-replace "*.txt" . "hello.*world" "hi universe" -r -n
  find-and-replace "config.json" ~/projects "\"version\":\s*\"[^\"]*\"" "\"version\": \"2.0.0\"" -r
        """,
    )

    parser.add_argument("file_name", help="File name pattern (supports glob expressions like *.py, config.*, etc.)")
    parser.add_argument("directory", help="Directory to search in (supports glob expressions)")
    parser.add_argument("text_to_find", help="Regular expression pattern to find")
    parser.add_argument(
        "text_to_replace", help="Text to replace matches with (can include regex groups like \\1, \\2)"
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively search subdirectories")
    parser.add_argument(
        "-n", "--no-confirm", action="store_true", help="Do not ask for confirmation before making changes"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without making actual changes"
    )
    return parser


def validate_regex_pattern(pattern: str) -> None:
    """Validate the regex pattern."""
    try:
        re.compile(pattern)
    except re.error as e:
        print_colored(f"Error: Invalid regular expression pattern '{pattern}' - {e}", Colors.RED)
        sys.exit(1)


def get_user_confirmation(file_count: int) -> bool:
    """Get user confirmation to proceed with processing files."""
    response = input(f"\nProceed with processing {file_count} file(s)? (y/n): ").lower()
    return response == "y"


def process_dry_run(file_path: str, pattern: str) -> bool:
    """Process a file in dry run mode."""
    try:
        content = read_file_content(file_path)
        if not content:
            return False

        regex = re.compile(pattern)
        matches = list(regex.finditer(content))

        if matches:
            print_colored(f"\n[DRY RUN] Would process: {file_path}", Colors.BLUE)
            print_colored(f"[DRY RUN] Found {len(matches)} match(es)", Colors.GREEN)
            return True
        return False
    except Exception as e:
        print_colored(f"[DRY RUN] Error reading file '{file_path}': {e}", Colors.RED)
        return False


def print_summary(dry_run: bool, modified_count: int, total_files: int) -> None:
    """Print operation summary."""
    print_colored(f"\n{'=' * 50}", Colors.NC)
    if dry_run:
        print_colored(f"DRY RUN COMPLETE: {modified_count} file(s) would be modified", Colors.BLUE)
    else:
        print_colored(f"OPERATION COMPLETE: {modified_count} file(s) modified", Colors.BLUE)
    print_colored(f"Total files processed: {total_files}", Colors.BLUE)


def main() -> None:
    """Main function to handle CLI arguments and orchestrate the find-and-replace operation."""
    parser = create_argument_parser()
    args = parser.parse_args()

    validate_regex_pattern(args.text_to_find)

    directory = str(Path(os.path.expanduser(args.directory)).resolve())

    print_colored(f"Searching for files matching '{args.file_name}' in '{directory}'", Colors.BLUE)
    if args.recursive:
        print_colored("(Searching recursively)", Colors.BLUE)

    files = find_files(args.file_name, directory, args.recursive)

    if not files:
        print_colored("No matching files found.", Colors.YELLOW)
        sys.exit(0)

    print_colored(f"Found {len(files)} file(s) to process:", Colors.GREEN)
    for file_path in files:
        print_colored(f"  {file_path}", Colors.NC)

    if not args.no_confirm and not args.dry_run and not get_user_confirmation(len(files)):
        print_colored("Operation cancelled.", Colors.YELLOW)
        sys.exit(0)

    modified_count = 0
    for file_path in files:
        if args.dry_run:
            if process_dry_run(file_path, args.text_to_find):
                modified_count += 1
        elif process_file(file_path, args.text_to_find, args.text_to_replace, args.no_confirm):
            modified_count += 1

    print_summary(args.dry_run, modified_count, len(files))


if __name__ == "__main__":
    main()
