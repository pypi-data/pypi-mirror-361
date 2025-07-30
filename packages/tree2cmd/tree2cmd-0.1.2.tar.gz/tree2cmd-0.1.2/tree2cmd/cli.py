#!/usr/bin/env python3

import os
import re
import sys
import argparse
import logging
import unicodedata
from typing import List, Set
from tree2cmd.utils import tree_from_shell_commands

# ----------------------
# Logging Configuration
# ----------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger.setLevel(logging.DEBUG)

# Special shell characters to escape in paths
SPECIAL_CHARS = {'$', '&', '*', '(', ')', '[', ']', '{', '}', '!', '`', '"', '\\', "'", ' ', ';', '|', '<', '>', '?', '#', '~', '=', '%', ':'}

# ----------------------
# Step 1: Read Input
# ----------------------
def read_input(input_file: str = None, use_stdin: bool = False, encoding: str = 'utf-8') -> str:
    """Reads and returns input from a file or standard input."""
    if use_stdin:
        logger.debug("Reading from stdin...")
        try:
            content = sys.stdin.read()
        except Exception as e:
            logger.error(f"Error reading from stdin: {e}")
            sys.exit(1)
    elif input_file:
        if not os.path.exists(input_file) or not os.path.isfile(input_file):
            logger.error(f"Invalid file: {input_file}")
            sys.exit(1)
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                logger.debug(f"Reading file: {input_file}")
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file '{input_file}': {e}")
            sys.exit(1)
    else:
        logger.error("No input source provided. Use a file or --stdin.")
        sys.exit(1)
    # Normalize tabs to spaces (2 spaces per tab)
    content = content.replace('\t', '  ')
    return content

# ----------------------
# Step 2: Normalize Line
# ----------------------
def normalize_line(line: str) -> str:
    """Cleans visual clutter (tree symbols, emojis) from the line and returns only the name."""
    # Extract the name by removing tree characters, emojis, and whitespace
    patterns = [
        r'^[\s│├└┌─┐┬┴┼━┃╭╰╯╮╾╿╽╼╱╲╳📁📂📄📃🗂🗃🗄🗑🧾]*',  # tree characters and emojis
        r'[-+|`>*•○●→⇒]*\s*'  # ASCII decorations
    ]
    cleaned = line
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned)
    return unicodedata.normalize('NFKC', cleaned.strip()).rstrip('/')

# ----------------------
# Step 3: Indentation Detection
# ----------------------
def get_indent_level(line: str, indent_width: int = 2) -> int:
    """Returns indentation level based on leading whitespace (tabs converted to spaces)."""
    if not line.strip():
        return 0

    # Count leading spaces, ignoring tree characters and emojis
    tree_chars = r'[│├└┌─┐┬┴┼━┃╭╰╯╮╾╿╽╼╱╲╳📁📂📄📃🗂🗃🗄🗑🧾]'
    # Replace tree characters with spaces to preserve indentation
    cleaned = re.sub(tree_chars, lambda m: ' ' * len(m.group()), line.rstrip())
    # Extract leading whitespace
    leading_ws = re.match(r'^([ \t]*)', cleaned).group(1)
    # Expand tabs to spaces
    expanded = leading_ws.replace('\t', ' ' * indent_width)
    indent_level = len(expanded) // indent_width
    logger.debug(f"Calculated indent level: {indent_level} for line: {line!r}, cleaned: {cleaned!r}")
    return indent_level

# ----------------------
# Step 4: Folder Detection
# ----------------------
def is_folder(name: str, context_next_line: str = '', current_line: str = '') -> bool:
    """Heuristically determines whether a node is a folder based on structure and name."""
    name = name.strip()

    # Explicit markers
    if name.endswith('/') or name.startswith(('📁', '📂')):
        return True

    # Heuristic: No file extension and alphabetical start (e.g. `src`, `docs`)
    if '.' not in name and name.lower() not in {"license", "makefile", "dockerfile", "readme"}:
        return True

    # Structural inference based on indentation (only if next line exists)
    try:
        return get_indent_level(context_next_line) > get_indent_level(current_line)
    except Exception:
        return False

# ----------------------
# Step 5: Escape Paths
# ----------------------
def escape_path(path: str, is_dir: bool = False) -> str:
    """Escapes special characters and quotes the shell path."""
    # Escape special characters
    escaped = ''.join(f'\\{c}' if c in SPECIAL_CHARS else c for c in path)
    # Add trailing slash for directories, ensure no double slashes
    if is_dir:
        escaped = escaped.rstrip('/') + '/'
    # Wrap the entire path in double quotes
    return f'"{escaped}"'

# ----------------------
# Step 6: Convert Tree to Commands
# ----------------------
def convert_tree_to_commands(
    tree_text: str,
    *,
    dry_run: bool = True,
    verbose: bool = False,
    save_script: str = None,
    strict: bool = False,
    indent_width: int = 4
) -> List[str]:
    """Converts tree-style text into `mkdir`/`touch` shell commands."""
    lines = [line for line in tree_text.strip().splitlines() if line.strip()]
    commands: List[str] = []
    seen_dirs: Set[str] = set()
    seen_files: Set[str] = set()
    stack: List[str] = []

    for idx, raw in enumerate(lines):
        indent = get_indent_level(raw, indent_width)
        normalized = normalize_line(raw)
        next_line = lines[idx + 1] if idx + 1 < len(lines) else ''

        if not normalized:
            logger.warning(f"Line {idx+1}: Empty name, skipping")
            continue

        # Debug indentation and line content
        logger.debug(f"Line {idx+1}: indent={indent}, name={normalized}, raw={raw!r}, stack={stack}")

        # Adjust stack to match current indentation level
        while len(stack) > indent:
            stack.pop()

        # Cap indentation to prevent excessive nesting
        if indent > len(stack) + 1:
            logger.warning(f"Line {idx+1}: Skipped indentation level ({len(stack)} → {indent})")
            indent = len(stack) + 1

        # Detect folder
        force_folder = (idx == 0 and get_indent_level(next_line, indent_width) > 0)
        is_dir = is_folder(normalized, next_line, raw) or force_folder

        parent_path = os.path.join(*stack) if stack else ''
        full_path = os.path.normpath(os.path.join(parent_path, normalized))

        if is_dir:
            if full_path in seen_files:
                logger.warning(f"Line {idx+1}: {full_path} already created as file")

            if full_path not in seen_dirs:
                cmd = f'mkdir -p {escape_path(full_path, is_dir=True)}'
                commands.append(cmd)
                seen_dirs.add(full_path)
                if verbose:
                    logger.info(f"Folder: {cmd}")

            stack.append(normalized)
        else:
            if full_path in seen_dirs:
                logger.warning(f"Line {idx+1}: {full_path} already created as directory")

            if parent_path and parent_path not in seen_dirs:
                dir_cmd = f'mkdir -p {escape_path(parent_path, is_dir=True)}'
                commands.append(dir_cmd)
                seen_dirs.add(parent_path)
                if verbose:
                    logger.info(f"Ensure parent dir: {dir_cmd}")

            if full_path not in seen_files:
                file_cmd = f'touch {escape_path(full_path)}'
                commands.append(file_cmd)
                seen_files.add(full_path)
                if verbose:
                    logger.info(f"File: {file_cmd}")

    # Save script if requested
    if save_script:
        try:
            with open(save_script, 'w') as f:
                f.write("#!/bin/sh\n\n")
                f.writelines(cmd + "\n" for cmd in commands)
        except Exception as e:
            logger.error(f"Error saving script to {save_script}: {e}")
            if strict:
                sys.exit(1)

    if dry_run:
        return commands
    else:
        for cmd in commands:
            logger.info(f"Executing: {cmd}")
            os.system(cmd)
        return commands

# ----------------------
# CLI Entry Point
# ----------------------
def main():
    parser = argparse.ArgumentParser(description="Convert tree-style directory text into shell commands.")
    parser.add_argument("input", nargs="?", help="Input file or use --stdin")
    parser.add_argument("--stdin", action="store_true", help="Read from standard input")
    parser.add_argument("--run", action="store_true", help="Execute generated commands")
    parser.add_argument("--save", help="Save to shell script (.sh)")
    parser.add_argument("--strict", action="store_true", help="Fail on error")
    parser.add_argument("--no-verbose", action="store_true", help="Suppress output")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--tree", action="store_true", help="Print tree structure instead of shell commands")
    
    args = parser.parse_args()  

    if args.version:
        print("tree2cmd version 1.0.1")
        return

    content = read_input(args.input, args.stdin)

    commands = convert_tree_to_commands(
        content,
        dry_run=not args.run,
        verbose=not args.no_verbose,
        save_script=args.save,
        strict=args.strict
    )

    if args.tree:
        print(tree_from_shell_commands(commands))
        return

    if not args.run and not args.no_verbose:
        for cmd in commands:
            print(cmd)

if __name__ == "__main__":
    main()