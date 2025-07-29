"""
Test utilities and common functionality for the C++ Exporter test suite.

This module provides shared utilities, fixtures, and helper functions
for testing the export script functionality.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import unittest
from typing import Dict, List, Optional


class ExporterTestCase(unittest.TestCase):
    """Base test case class with common functionality for exporter tests."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)

        # Add the scripts directory to Python path for imports
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
        if str(self.scripts_dir) not in sys.path:
            sys.path.insert(0, str(self.scripts_dir))

    def create_temp_file(self, filename: str, content: str) -> str:
        """Create a temporary file with given content."""
        filepath = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def create_dependency_file(
            self,
            target: str,
            source: str,
            headers: List[str]) -> str:
        """Create a .d dependency file with proper format."""
        deps_content = f"{target}: {source}"
        if headers:
            deps_content += " " + " ".join(headers)

        deps_filename = source.replace('.cpp', '.d').replace('.c', '.d')
        return self.create_temp_file(deps_filename, deps_content)

    def run_export_script(
            self,
            deps_files: List[str],
            output_file: Optional[str] = None,
            verbose: bool = False,
            add_separators: bool = False,
            follow_symlinks: bool = False) -> subprocess.CompletedProcess:
        """Run the export script with given parameters."""
        cmd = [sys.executable, str(self.scripts_dir / "singleston.py")]

        if output_file:
            cmd.extend(["-o", output_file])
        if verbose:
            cmd.append("--verbose")
        if add_separators:
            cmd.append("--add-separators")
        if follow_symlinks:
            cmd.append("--follow-symlinks")

        cmd.extend(deps_files)

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.temp_dir)

    def assertErrorMessage(
            self,
            result: subprocess.CompletedProcess,
            expected_message: str):
        """Assert that the command failed with expected error message."""
        self.assertNotEqual(result.returncode, 0, "Expected command to fail")
        self.assertIn(expected_message, result.stderr)

    def assertSuccessful(self, result: subprocess.CompletedProcess):
        """Assert that the command completed successfully."""
        if result.returncode != 0:
            self.fail(f"Command failed with error: {result.stderr}")


def create_sample_cpp_file(filename: str,
                           includes: Optional[List[str]] = None,
                           content: Optional[str] = None,
                           pragma_once: bool = False,
                           include_guard: Optional[str] = None) -> str:
    """Create a sample C++ file with specified includes and content."""
    lines = []

    # Add include guard or pragma once
    if pragma_once:
        lines.append("#pragma once")
        lines.append("")
    elif include_guard:
        lines.append(f"#ifndef {include_guard}")
        lines.append(f"#define {include_guard}")
        lines.append("")

    # Add includes
    if includes:
        for include in includes:
            if include.startswith('<') and include.endswith('>'):
                lines.append(f"#include {include}")
            else:
                lines.append(f'#include "{include}"')
        lines.append("")

    # Add content
    if content:
        lines.append(content)
    else:
        lines.append("// Default content")
        lines.append("int main() { return 0; }")

    # Close include guard
    if include_guard:
        lines.append("")
        lines.append(f"#endif // {include_guard}")

    return "\n".join(lines)


def create_sample_header(filename: str,
                         guard_name: Optional[str] = None,
                         includes: Optional[List[str]] = None,
                         content: Optional[str] = None) -> str:
    """Create a sample header file with include guards."""
    if guard_name is None:
        guard_name = filename.upper().replace('.', '_').replace('/', '_')

    default_content = """
class Example {
public:
    Example();
    ~Example();
    void doSomething();
};
"""

    return create_sample_cpp_file(
        filename=filename,
        includes=includes,
        content=content or default_content,
        include_guard=guard_name
    )


class MockFileSystem:
    """Mock file system for testing file operations without actual files."""

    def __init__(self):
        self.files: Dict[str, str] = {}
        self.directories: set = set()

    def create_file(self, path: str, content: str):
        """Create a mock file with content."""
        self.files[path] = content
        # Add parent directories
        parent = str(Path(path).parent)
        while parent != '.' and parent != '/':
            self.directories.add(parent)
            parent = str(Path(parent).parent)

    def exists(self, path: str) -> bool:
        """Check if path exists in mock filesystem."""
        return path in self.files or path in self.directories

    def read_file(self, path: str) -> str:
        """Read content from mock file."""
        if path not in self.files:
            raise FileNotFoundError(f"Mock file not found: {path}")
        return self.files[path]

    def list_files(self, pattern: str = "*") -> List[str]:
        """List all files matching pattern."""
        return list(self.files.keys())
