[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/find-replace-cli.svg)](https://badge.fury.io/py/find-replace-cli)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/find-and-replace/badge/?version=latest)](https://find-and-replace.readthedocs.io/en/latest/?badge=latest)

# Find and Replace

A command-line tool for finding and replacing text in files using regular expressions. This tool provides an intuitive interface for bulk text operations across your project files.

## Features

- **Regular Expression Support**: Use regex patterns for complex search and replace operations
- **Glob Pattern Matching**: Find files using glob expressions like `*.py`, `config.*`, etc.
- **Recursive Search**: Search through directory trees with the `-r/--recursive` flag
- **Interactive Confirmation**: Review matches before making changes (unless using `--no-confirm`)
- **Dry Run Mode**: Preview what would be changed without making actual modifications
- **Error Handling**: Graceful handling of permission errors, encoding issues, and invalid regex patterns
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### Installation

Install from PyPI:

```bash
pip install find-replace-cli
```

### Basic Usage

Replace all instances of "old_function" with "new_function" in Python files:

```bash
find-and-replace "*.py" /path/to/project "old_function" "new_function"
```

### Common Examples

**Replace text in all files recursively:**
```bash
find-and-replace "*.txt" . "hello.*world" "hi universe" -r
```

**Update version strings in configuration files:**
```bash
find-and-replace "config.json" ~/projects "\"version\":\s*\"[^\"]*\"" "\"version\": \"2.0.0\"" -r
```

**Dry run to preview changes:**
```bash
find-and-replace "*.py" . "old_pattern" "new_pattern" --dry-run
```

**No confirmation prompts (automation-friendly):**
```bash
find-and-replace "*.md" . "old_text" "new_text" -r -n
```

## Use Cases

- **Code Refactoring**: Rename functions, variables, or classes across your codebase
- **Configuration Updates**: Update configuration values across multiple files
- **Documentation Maintenance**: Update links, references, or terminology in documentation
- **Migration Tasks**: Update import statements, API calls, or deprecated syntax
- **Bulk Text Processing**: Any scenario requiring consistent text changes across multiple files

## Safety Features

- **Interactive Confirmation**: By default, the tool shows you what will be changed and asks for confirmation
- **Dry Run Mode**: Test your patterns without making any changes
- **Detailed Output**: See exactly what files were processed and how many matches were found
- **Error Recovery**: Continues processing other files even if one file encounters an error

## Command Line Arguments

```
find-and-replace FILE_PATTERN DIRECTORY FIND_PATTERN REPLACE_TEXT [OPTIONS]
```

**Positional Arguments:**
- `FILE_PATTERN`: Glob pattern for file names (e.g., `*.py`, `config.*`)
- `DIRECTORY`: Directory to search in
- `FIND_PATTERN`: Regular expression pattern to find
- `REPLACE_TEXT`: Text to replace matches with (supports regex groups like `\1`, `\2`)

**Options:**
- `-r, --recursive`: Search subdirectories recursively
- `-n, --no-confirm`: Skip confirmation prompts
- `--dry-run`: Show what would be changed without making changes
- `-h, --help`: Show help message

## Getting Help

- **Documentation**: Read the full documentation at [find-and-replace.readthedocs.io](https://find-and-replace.readthedocs.io/)
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/apisani1/find-and-replace/issues)
- **Source Code**: View the source code on [GitHub](https://github.com/apisani1/find-and-replace)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/apisani1/find-and-replace/blob/main/LICENSE) file for details.
# Reference

This document provides detailed information about the find-and-replace CLI tool's components and functions.

## Command Line Interface

### Syntax

```
find-and-replace FILE_PATTERN DIRECTORY FIND_PATTERN REPLACE_TEXT [OPTIONS]
```

### Arguments

#### Positional Arguments

**`FILE_PATTERN`**
: Glob pattern for matching file names
: **Type**: `str`
: **Examples**: `*.py`, `*.txt`, `config.*`, `package.json`
: **Description**: Supports standard glob wildcards (`*`, `?`, `[...]`)

**`DIRECTORY`**
: Directory to search in
: **Type**: `str`  
: **Examples**: `.`, `/path/to/project`, `~/documents`
: **Description**: Can be absolute or relative path. Tilde (`~`) expansion is supported.

**`FIND_PATTERN`**
: Regular expression pattern to search for
: **Type**: `str`
: **Examples**: `old_function`, `hello.*world`, `"version":\s*"[^"]*"`
: **Description**: Full Python regex syntax supported. Remember to escape special characters in shell.

**`REPLACE_TEXT`**
: Replacement text (can include regex groups)
: **Type**: `str`
: **Examples**: `new_function`, `hi universe`, `"version": "2.0.0"`
: **Description**: Supports backreferences (`\1`, `\2`, etc.) for captured groups.

#### Optional Arguments

**`-r, --recursive`**
: Search subdirectories recursively
: **Type**: `flag`
: **Default**: `False`
: **Description**: When enabled, searches through all subdirectories.

**`-n, --no-confirm`**
: Skip confirmation prompts
: **Type**: `flag`
: **Default**: `False`
: **Description**: Useful for automation scripts. Applies changes without user interaction.

**`--dry-run`**
: Show what would be changed without making actual changes
: **Type**: `flag`
: **Default**: `False`
: **Description**: Safe way to test patterns before applying them.

**`-h, --help`**
: Show help message and exit
: **Type**: `flag`

## Regular Expression Examples

### Basic Patterns

- `hello`: Matches literal text "hello"
- `hello.*world`: Matches "hello" followed by anything, then "world"
- `\d+`: Matches one or more digits
- `\w+`: Matches one or more word characters

### Advanced Patterns

- `"version":\s*"[^"]*"`: Matches JSON version fields
- `import\s+(\w+)`: Captures module names in import statements
- `function\s+(\w+)\s*\(`: Captures function names

### Replacement Examples

- `new_function`: Simple text replacement
- `\1_new`: Prepend "new_" to captured group 1
- `"version": "2.0.0"`: Replace with specific version

## Error Handling

The tool handles various error conditions gracefully:

- **File not found**: Skips missing files with warning
- **Permission denied**: Reports permission errors and continues
- **Unicode decode errors**: Skips binary files with informative message
- **Invalid regex**: Validates patterns before processing
- **Keyboard interrupt**: Clean exit on Ctrl+C

## Performance Considerations

- Files are processed sequentially
- Entire file content is loaded into memory
- Regex compilation is done once per pattern
- Large files (>100MB) may cause memory issues

## Best Practices

1. **Test with `--dry-run`** before making actual changes
2. **Use version control** to track changes
3. **Escape shell metacharacters** in patterns
4. **Start with simple patterns** and build complexity gradually
5. **Use `--no-confirm`** only for tested, automated scripts