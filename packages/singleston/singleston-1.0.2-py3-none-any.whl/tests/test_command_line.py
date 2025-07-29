"""
Test command-line interface functionality of the C++ exporter.

Tests argument parsing, validation, help messages, and error handling
for command-line interface interactions.
"""

from tests.test_utils import ExporterTestCase
import unittest
import sys
import subprocess
import os
from pathlib import Path

# Add the tests directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestCommandLineInterface(ExporterTestCase):
    """Test command-line argument parsing and validation."""

    def test_help_message(self):
        """Test that --help displays correct usage information."""
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "singleston.py"),
             "--help"],
            capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("singleston.py", result.stdout)
        self.assertIn("dependency files", result.stdout.lower())
        self.assertIn("usage:", result.stdout.lower())

    def test_missing_required_arguments(self):
        """Test error when no dependency files are provided."""
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "singleston.py")],
            capture_output=True, text=True
        )

        self.assertNotEqual(result.returncode, 0)
        # Should indicate missing required arguments
        self.assertTrue(
            "required" in result.stderr.lower() or
            "usage:" in result.stderr.lower()
        )

    def test_nonexistent_dependency_file(self):
        """Test error handling for missing dependency files."""
        nonexistent_file = "nonexistent.d"
        result = self.run_export_script([nonexistent_file])

        self.assertErrorMessage(result, "dependency file not found")
        self.assertIn(nonexistent_file, result.stderr)

    def test_output_file_argument(self):
        """Test -o and --output argument handling."""
        # Create a simple dependency file
        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["stdio.h"]
        )
        self.create_temp_file(
            "main.cpp", '#include <stdio.h>\nint main() { return 0; }')

        output_file = os.path.join(self.temp_dir, "output.cpp")

        # Test -o flag
        result = self.run_export_script([deps_file], output_file=output_file)
        self.assertSuccessful(result)
        self.assertTrue(os.path.exists(output_file))

    def test_verbose_flag(self):
        """Test verbose output functionality."""
        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["stdio.h"]
        )
        self.create_temp_file(
            "main.cpp", '#include <stdio.h>\nint main() { return 0; }')

        result = self.run_export_script([deps_file], verbose=True)
        self.assertSuccessful(result)

        # Should contain verbose output markers
        self.assertIn(">", result.stderr)  # Verbose output uses > prefix

    def test_add_separators_flag(self):
        """Test --add-separators functionality."""
        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", []
        )
        self.create_temp_file("main.cpp",
                              'int main() { return 0; }'
                              )

        result = self.run_export_script([deps_file], add_separators=True)
        self.assertSuccessful(result)
        # Note: Actual separator testing will be in integration tests

    def test_follow_symlinks_flag(self):
        """Test --follow-symlinks flag handling."""
        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", []
        )
        self.create_temp_file("main.cpp",
                              'int main() { return 0; }'
                              )

        result = self.run_export_script([deps_file], follow_symlinks=True)
        self.assertSuccessful(result)

    def test_multiple_dependency_files(self):
        """Test handling multiple dependency files."""
        deps1 = self.create_dependency_file("main.o", "main.cpp", ["utils.h"])
        deps2 = self.create_dependency_file("utils.o", "utils.cpp", [])

        # Create corresponding source files
        self.create_temp_file("main.cpp",
                              '#include "utils.h"\nint main() { return 0; }'
                              )
        self.create_temp_file("utils.cpp",
                              'void utility() {}'
                              )
        self.create_temp_file("utils.h",
                              'void utility();'
                              )

        result = self.run_export_script([deps1, deps2])
        self.assertSuccessful(result)

    def test_invalid_output_directory(self):
        """Test error handling for invalid output directory."""
        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", []
        )
        self.create_temp_file("main.cpp",
                              'int main() { return 0; }'
                              )

        # Try to write to a path that requires permissions we don't have
        invalid_output = "/root/cannot_write_here.cpp"
        result = self.run_export_script(
            [deps_file], output_file=invalid_output)

        # Should fail with permission or directory error
        self.assertNotEqual(result.returncode, 0)

    def test_unreadable_dependency_file(self):
        """Test error handling for unreadable dependency files."""
        # Create a file and make it unreadable (if possible)
        deps_file = self.create_temp_file("test.d", "main.o: main.cpp")

        try:
            # Try to make file unreadable
            os.chmod(deps_file, 0o000)

            result = self.run_export_script([deps_file])
            self.assertErrorMessage(result, "permission denied")
        except (OSError, PermissionError):
            # If we can't change permissions, skip this test
            self.skipTest("Cannot modify file permissions in this environment")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(deps_file, 0o644)
            except (OSError, PermissionError):
                pass


class TestArgumentValidation(ExporterTestCase):
    """Test detailed argument validation logic."""

    def test_dependency_file_extension_ignored(self):
        """Test that any file extension is accepted for dependency files."""
        # Create files with different extensions
        files = [
            self.create_temp_file("test.d", "main.o: main.cpp"),
            self.create_temp_file("test.dep", "utils.o: utils.cpp"),
            self.create_temp_file("test.txt", "lib.o: lib.cpp")
        ]

        # Create corresponding source files
        for src in ["main.cpp", "utils.cpp", "lib.cpp"]:
            self.create_temp_file(src, f"// {src}")

        result = self.run_export_script(files)
        self.assertSuccessful(result)

    def test_relative_vs_absolute_paths(self):
        """Test handling of relative and absolute paths."""
        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", []
        )
        self.create_temp_file("main.cpp",
                              'int main() { return 0; }'
                              )

        # Test with absolute path
        result = self.run_export_script([os.path.abspath(deps_file)])
        self.assertSuccessful(result)

    def test_empty_dependency_file(self):
        """Test handling of empty dependency files."""
        empty_deps = self.create_temp_file("empty.d", "")

        self.run_export_script([empty_deps])
        # Should handle gracefully (might warn but shouldn't crash)
        # Exact behavior depends on implementation


if __name__ == '__main__':
    unittest.main()
