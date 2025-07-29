#!/usr/bin/env python3
"""
C/C++ source file amalgamator that uses compiler-generated dependency files
to resolve local includes and creates a single output file with proper dependency ordering.
"""

import argparse
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple
from datetime import datetime

try:
    from scripts.version import __version__, AUTHOR, HOMEPAGE, DESCRIPTION
except ImportError:
    # When running directly, adjust the import path
    import sys
    from pathlib import Path
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir.parent))
    from scripts.version import __version__, AUTHOR, HOMEPAGE, DESCRIPTION


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog=f'singleston.py v{__version__}',
        description=f'{DESCRIPTION}. Uses compiler-generated dependency files '
        'to resolve local includes and creates a single output file with proper dependency ordering. '
        'Supports both C and C++ files with any header extension (.h, .hh, .hpp, etc.).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Prerequisites:
  The project must be compiled first to generate dependency files.

Example workflow:
  # 1. Build project with dependency generation (-MMD flag)
  make  # Generates individual .d files for each source

  # 2. Run the exporter with all dependency files
  ./singleston.py srcs/*.d -o export.cpp

  # 3. With verbose output and file separators
  ./singleston.py srcs/*.d -o export.cpp --verbose --add-separators
        ''')

    # Output file option
    parser.add_argument(
        '-o', '--output',
        metavar='OUTPUT_FILE',
        type=str,
        help='Output file path (default: stdout)'
    )

    # Verbose option
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for debugging'
    )

    # Add separators option
    parser.add_argument(
        '--add-separators',
        action='store_true',
        help='Add file boundary markers in output'
    )

    # Follow symlinks option
    parser.add_argument(
        '--follow-symlinks',
        action='store_true',
        help='Follow symbolic links in include paths'
    )

    # Version option
    parser.add_argument(
        '--version',
        action='version',
        version=f'Singleston v{__version__} - {DESCRIPTION}'
    )

    # Dependency files (required positional arguments)
    parser.add_argument(
        'deps_files',
        metavar='DEPS_FILE',
        nargs='+',
        type=str,
        help='One or more compiler-generated dependency files (.d format from gcc/clang -MMD)'
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line arguments and check file existence."""
    # Check if all dependency files exist and are readable
    for deps_file in args.deps_files:
        deps_path = Path(deps_file)
        if not deps_path.exists():
            print(
                f"\033[91merror\033[0m: dependency file not found: \"{deps_file}\"",
                file=sys.stderr)
            sys.exit(1)
        if not deps_path.is_file():
            print(
                f"\033[91merror\033[0m: \"{deps_file}\" is not a file",
                file=sys.stderr)
            sys.exit(1)
        if not os.access(deps_path, os.R_OK):
            print(
                f"\033[91merror\033[0m: cannot read dependency file: \"{deps_file}\" (permission denied)",
                file=sys.stderr)
            sys.exit(1)

    # Check output file writability if specified
    if args.output:
        output_path = Path(args.output)
        # Check if parent directory exists and is writable
        parent_dir = output_path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(
                    f"\033[91merror\033[0m: cannot create output directory: \"{parent_dir}\" ({e})",
                    file=sys.stderr)
                sys.exit(1)

        if not os.access(parent_dir, os.W_OK):
            print(
                f"\033[91merror\033[0m: cannot write to output directory: \"{parent_dir}\" (permission denied)",
                file=sys.stderr)
            sys.exit(1)

        # Check if output file exists and is writable
        if output_path.exists() and not os.access(output_path, os.W_OK):
            print(
                f"\033[91merror\033[0m: cannot write output file: \"{args.output}\" (permission denied)",
                file=sys.stderr)
            sys.exit(1)


def verbose_print(message: str, verbose: bool = False) -> None:
    """Print verbose messages if verbose mode is enabled."""
    if verbose:
        print(f"> {message}", file=sys.stderr)


def parse_dependency_files(
        deps_files: List[str], verbose: bool = False) -> Tuple[Dict[str, Set[str]], List[str]]:
    """Parse dependency files and return dependency graph and file order."""
    dependency_graph = {}
    file_order = []  # Track order of first appearance across all files

    # Common system header patterns that should be ignored
    system_headers = {
        'stdio.h', 'stdlib.h', 'string.h', 'math.h', 'time.h', 'assert.h',
        'ctype.h', 'errno.h', 'float.h', 'limits.h', 'locale.h', 'setjmp.h',
        'signal.h', 'stdarg.h', 'stddef.h', 'wchar.h', 'wctype.h',
        'iostream', 'string', 'vector', 'map', 'set', 'algorithm', 'memory',
        'fstream', 'sstream', 'iomanip', 'cassert', 'cmath', 'cstdlib'
    }

    for deps_file in deps_files:
        verbose_print(f"Parsing dependency file: {deps_file}", verbose)

        with open(deps_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse .d file format: target: source dependencies...
        # Handle multiline continuations with backslashes
        content = re.sub(r'\\\s*\n\s*', ' ', content)

        for line in content.strip().split('\n'):
            if ':' in line:
                target, deps = line.split(':', 1)
                target = target.strip()

                # Extract the source file from target (.o -> .cpp/.c)
                if target.endswith('.o'):
                    source_file = None
                    deps_list = deps.strip().split()

                    # Find the source file (first .cpp/.c file in dependencies)
                    for dep in deps_list:
                        if dep.endswith(('.cpp', '.c', '.cc', '.cxx')):
                            source_file = dep
                            break

                    if source_file:
                        # Track file order
                        if source_file not in file_order:
                            file_order.append(source_file)

                        # Get header dependencies (excluding the source file
                        # itself and system headers)
                        headers = []
                        for dep in deps_list:
                            if dep != source_file:
                                # Skip obvious system headers
                                dep_name = os.path.basename(dep)
                                if dep_name not in system_headers and not dep.startswith(
                                        '/usr/'):
                                    headers.append(dep)

                        for header in headers:
                            if header not in file_order:
                                file_order.append(header)

                        dependency_graph[source_file] = set(headers)
                        verbose_print(
                            f"  {source_file} depends on: {headers}", verbose)

    verbose_print(f"File appearance order: {file_order}", verbose)
    return dependency_graph, file_order


def resolve_dependency_order(
        dependency_graph: Dict[str, Set[str]], file_order: List[str], verbose: bool = False) -> List[str]:
    """Resolve the order in which files should be processed using the tracked file order."""
    verbose_print("Resolving dependency order...", verbose)

    # Separate headers and sources based on the tracked order
    headers = [
        f for f in file_order if f.endswith(
            ('.h', '.hpp', '.hh', '.hxx'))]
    sources = [
        f for f in file_order if f.endswith(
            ('.cpp', '.c', '.cc', '.cxx'))]

    verbose_print(
        f"Found {len(headers)} headers and {len(sources)} sources",
        verbose)

    # Analyze header dependencies and reorder them properly
    ordered_files = analyze_header_dependencies(file_order, verbose)

    # For sources, use simple dependency-aware ordering, but respecting first
    # appearance order
    headers = [
        f for f in ordered_files if f.endswith(
            ('.h', '.hpp', '.hh', '.hxx'))]
    sources = [
        f for f in ordered_files if f.endswith(
            ('.cpp', '.c', '.cc', '.cxx'))]

    ordered = []
    ordered.extend(headers)

    remaining_sources = set(sources)
    added_sources = set()

    while remaining_sources:
        # Find sources with no unresolved dependencies
        ready_sources = []
        for source in sources:  # Iterate in original order
            if source not in remaining_sources:
                continue
            deps = dependency_graph.get(source, set())
            # Check if all header dependencies are already included
            unresolved_deps = deps - set(ordered) - added_sources
            if not unresolved_deps:
                ready_sources.append(source)

        if not ready_sources:
            # Circular dependency or missing file - just add first remaining in
            # order
            for source in sources:
                if source in remaining_sources:
                    ready_sources = [source]
                    break
            verbose_print(
                f"Warning: Possible circular dependency, adding {ready_sources[0]}", verbose)

        # Add ready sources in order of first appearance
        for source in ready_sources:
            ordered.append(source)
            added_sources.add(source)
            remaining_sources.remove(source)

    verbose_print(f"File processing order: {ordered}", verbose)
    return ordered


def remove_include_guards(content: str, filepath: str) -> str:
    """Remove include guards from header content."""
    lines = content.split('\n')

    # Handle #pragma once
    if any('#pragma once' in line for line in lines):
        lines = [line for line in lines if '#pragma once' not in line]
        # Remove empty lines at the start
        while lines and lines[0].strip() == '':
            lines.pop(0)
        return '\n'.join(lines)

    # Handle traditional include guards
    # Look for pattern: #ifndef GUARD_NAME followed by #define GUARD_NAME
    if len(lines) < 3:
        return content

    guard_name = None
    ifndef_line_idx = -1
    define_line_idx = -1
    endif_line_idx = -1

    # Find #ifndef (usually in first few lines, skip comments/empty lines)
    for i in range(min(5, len(lines))):
        stripped = lines[i].strip()
        ifndef_match = re.match(
            r'^\s*#ifndef\s+([A-Za-z_][A-Za-z0-9_]*)', stripped)
        if ifndef_match:
            guard_name = ifndef_match.group(1)
            ifndef_line_idx = i
            break

    if guard_name is None:
        return content

    # Find matching #define (should be shortly after #ifndef)
    for i in range(ifndef_line_idx + 1, min(ifndef_line_idx + 3, len(lines))):
        stripped = lines[i].strip()
        define_match = re.match(
            fr'^\s*#\s*define\s+{re.escape(guard_name)}', stripped)
        if define_match:
            define_line_idx = i
            break

    if define_line_idx == -1:
        return content

    # Find closing #endif (usually at the end, may have comments after)
    for i in range(len(lines) - 1, max(len(lines) - 10, define_line_idx), -1):
        stripped = lines[i].strip()
        if re.match(r'^\s*#endif', stripped):
            # Check if this could be the matching endif
            # Look ahead to see if there's only whitespace/comments after
            remaining_lines = lines[i + 1:]
            has_substantial_content = any(line.strip() and not line.strip().startswith(
                '//') and not line.strip().startswith('/*') for line in remaining_lines)
            if not has_substantial_content:
                endif_line_idx = i
                break

    if endif_line_idx == -1:
        return content

    # Remove the guard lines and return the content between them
    result_lines = []

    # Add lines before the guard
    for i in range(ifndef_line_idx):
        result_lines.append(lines[i])

    # Add lines between define and endif
    for i in range(define_line_idx + 1, endif_line_idx):
        result_lines.append(lines[i])

    # Add lines after endif
    for i in range(endif_line_idx + 1, len(lines)):
        result_lines.append(lines[i])

    # Clean up empty lines at start and end
    while result_lines and result_lines[0].strip() == '':
        result_lines.pop(0)
    while result_lines and result_lines[-1].strip() == '':
        result_lines.pop()

    return '\n'.join(result_lines)


def process_includes(content: str, filepath: str,
                     processed_headers: Set[str]) -> Tuple[str, List[str]]:
    """Process includes in a file, separating system and local includes."""
    lines = content.split('\n')
    result_lines = []
    system_includes = []

    for line in lines:
        stripped = line.strip()

        # Check for system includes (keep them)
        if stripped.startswith('#include <') and stripped.endswith('>'):
            include_match = re.match(r'#include\s*<([^>]+)>', stripped)
            if include_match:
                include = include_match.group(1)
                if include not in system_includes:
                    system_includes.append(include)
            continue

        # Check for local includes (remove them - content will be inlined)
        elif stripped.startswith('#include "') and stripped.endswith('"'):
            # Skip local includes - their content should be inlined
            continue

        # Keep all other lines
        result_lines.append(line)

    return '\n'.join(result_lines), system_includes


def amalgamate_files(ordered_files: List[str],
                     dependency_graph: Dict[str,
                                            Set[str]],
                     add_separators: bool,
                     follow_symlinks: bool,
                     verbose: bool) -> str:
    """Amalgamate all files into a single output."""
    verbose_print("Starting file amalgamation...", verbose)

    result_lines = []
    processed_files = set()  # Track which files we've already processed
    all_system_includes = []

    for filepath in ordered_files:
        # Skip if we've already processed this file
        if filepath in processed_files:
            verbose_print(
                f"Skipping already processed file: {filepath}",
                verbose)
            continue

        if not os.path.exists(filepath):
            is_header = filepath.endswith(('.h', '.hpp', '.hh', '.hxx'))
            file_type = "header" if is_header else "source"
            raise FileNotFoundError(f"{file_type} file not found: {filepath}")

        verbose_print(f"Processing file: {filepath}", verbose)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except PermissionError:
            raise PermissionError(
                f"permission denied reading file: {filepath}")
        except Exception as e:
            raise RuntimeError(f"could not read {filepath}: {e}")

        is_header = filepath.endswith(('.h', '.hpp', '.hh', '.hxx'))

        if add_separators:
            result_lines.append(f"// === {filepath} ===")

        if is_header:
            # Remove include guards from headers
            content = remove_include_guards(content, filepath)

        # Process includes
        processed_content, system_includes = process_includes(
            content, filepath, processed_files)

        # Collect system includes
        for include in system_includes:
            if include not in all_system_includes:
                all_system_includes.append(include)

        # Add the processed content
        if processed_content.strip():
            result_lines.append(processed_content)

        # Mark this file as processed
        processed_files.add(filepath)

        if add_separators:
            result_lines.append("")

    # Prepare final output
    final_lines = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    final_lines.extend([
        "/*",
        " * AMALGAMATED C/C++ SOURCE FILE",
        f" * Generated by Singleston v{__version__}",
        f" * {DESCRIPTION}",
        " *",
        f" * Generation Date: {timestamp}",
        f" * Author: {AUTHOR}",
        f" * Homepage: {HOMEPAGE}",
        " *",
        " * This file contains the amalgamated source code from multiple",
        " * source files. It has been automatically generated and should",
        " * not be edited manually.",
        " *",
        " * Original project structure has been flattened into this single",
        " * file while preserving all functionality and dependencies.",
        " */",
        ""
    ])

    # Add system includes
    if all_system_includes:
        for include in sorted(all_system_includes):
            final_lines.append(f"#include <{include}>")
        final_lines.append("")

    # Add the processed content
    final_lines.extend(result_lines)

    return '\n'.join(final_lines)


def analyze_header_dependencies(
        file_order: List[str],
        verbose: bool = False) -> List[str]:
    """Analyze #include dependencies within header files to determine proper order."""
    verbose_print("Analyzing header dependencies...", verbose)

    headers = [
        f for f in file_order if f.endswith(
            ('.h', '.hpp', '.hh', '.hxx'))]
    sources = [
        f for f in file_order if f.endswith(
            ('.cpp', '.c', '.cc', '.cxx'))]

    if len(headers) <= 1:
        return file_order  # No reordering needed

    # Build a dependency graph among headers
    header_deps = {}
    has_dependencies = False

    for header in headers:
        header_deps[header] = set()

        if not os.path.exists(header):
            continue

        try:
            with open(header, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find local includes within this header
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped.startswith(
                        '#include "') and stripped.endswith('"'):
                    # Remove '#include "' and '"'
                    included_file = stripped[10:-1]

                    # Resolve relative path
                    header_dir = os.path.dirname(header)
                    if header_dir:
                        full_include_path = os.path.join(
                            header_dir, included_file)
                    else:
                        full_include_path = included_file

                    # Check if this included file is in our header list
                    for h in headers:
                        if h == full_include_path or os.path.basename(
                                h) == os.path.basename(included_file):
                            header_deps[header].add(h)
                            has_dependencies = True
                            verbose_print(
                                f"  {header} depends on {h}", verbose)
                            break

        except Exception as e:
            verbose_print(
                f"Warning: Could not analyze dependencies for {header}: {e}",
                verbose)

    # If no dependencies found, preserve original order
    if not has_dependencies:
        verbose_print(
            "No header dependencies found, preserving original order",
            verbose)
        return file_order

    # Topological sort of headers
    ordered_headers = []
    remaining_headers = set(headers)

    while remaining_headers:
        # Find headers with no unresolved dependencies
        ready_headers = []
        for header in headers:  # Preserve original order for tie-breaking
            if header not in remaining_headers:
                continue
            unresolved_deps = header_deps[header] & remaining_headers
            if not unresolved_deps:
                ready_headers.append(header)

        if not ready_headers:
            # Circular dependency or issue - just add remaining in original
            # order
            ready_headers = [h for h in headers if h in remaining_headers]
            verbose_print(
                f"Warning: Possible circular dependency among headers",
                verbose)

        for header in ready_headers:
            if header in remaining_headers:
                ordered_headers.append(header)
                remaining_headers.remove(header)

    verbose_print(f"Reordered headers: {ordered_headers}", verbose)

    # Return the new order: reordered headers + sources
    return ordered_headers + sources


def main() -> int:
    """Main entry point of the application."""
    parser = create_parser()

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse calls sys.exit() on error, we catch it to return proper exit
        # code
        return int(e.code) if e.code is not None else 1

    # Validate arguments
    try:
        validate_arguments(args)
    except SystemExit as e:
        return int(e.code) if e.code is not None else 1

    # Print initial verbose information
    verbose_print(
        f"Processing dependency files: {', '.join(args.deps_files)}",
        args.verbose)

    if args.output:
        verbose_print(f"Output file: {args.output}", args.verbose)
    else:
        verbose_print("Output: stdout", args.verbose)

    if args.add_separators:
        verbose_print("File boundary markers enabled", args.verbose)

    if args.follow_symlinks:
        verbose_print("Following symbolic links", args.verbose)

    # TODO: Implement the actual amalgamation logic here
    verbose_print("Starting dependency file parsing phase...", args.verbose)

    try:
        # Parse dependency files and build dependency graph
        dependency_graph, file_order = parse_dependency_files(
            args.deps_files, args.verbose)
        verbose_print(
            f"Found {len(dependency_graph)} source files",
            args.verbose)

        # Resolve dependency order
        ordered_files = resolve_dependency_order(
            dependency_graph, file_order, args.verbose)
        verbose_print(f"Dependency resolution complete", args.verbose)

        # Analyze header dependencies and reorder if necessary
        ordered_files = analyze_header_dependencies(
            ordered_files, args.verbose)
        verbose_print(f"Header dependency analysis complete", args.verbose)

        # Process and amalgamate files
        amalgamated_content = amalgamate_files(
            ordered_files,
            dependency_graph,
            args.add_separators,
            args.follow_symlinks,
            args.verbose
        )

        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(amalgamated_content)
            verbose_print(f"Output written to {args.output}", args.verbose)
        else:
            print(amalgamated_content, end='')

    except Exception as e:
        print(f"\033[91merror\033[0m: {e}", file=sys.stderr)
        return 1

    verbose_print("Export completed successfully", args.verbose)
    return 0


if __name__ == '__main__':
    sys.exit(main())
