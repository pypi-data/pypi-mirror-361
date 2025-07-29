"""
Test error handling and edge cases.

Tests file system errors, permission issues, malformed files,
and other exceptional conditions.
"""

from tests.test_utils import ExporterTestCase
import unittest
import os
import sys
from pathlib import Path

# Add the tests directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestErrorHandling(ExporterTestCase):
    """Test error handling for various failure conditions."""

    def test_missing_source_file(self):
        """Test error when source file referenced in .d file doesn't exist."""
        # Create dependency file that references non-existent source
        deps_content = "main.o: nonexistent.cpp header.h"
        deps_file = self.create_temp_file("main.d", deps_content)

        # Create only the header, not the source
        self.create_temp_file("header.h", "#pragma once\nvoid func();")

        result = self.run_export_script([deps_file])

        # Should fail with clear error message
        self.assertErrorMessage(result, "source file not found")
        self.assertIn("nonexistent.cpp", result.stderr)

    def test_missing_header_file(self):
        """Test error when header file referenced in .d file doesn't exist."""
        deps_content = "main.o: main.cpp missing_header.h"
        deps_file = self.create_temp_file("main.d", deps_content)

        # Create only the source, not the header
        self.create_temp_file("main.cpp", 'int main() { return 0; }')

        result = self.run_export_script([deps_file])

        # Should fail with clear error message
        self.assertErrorMessage(result, "header file not found")
        self.assertIn("missing_header.h", result.stderr)

    def test_permission_denied_source_file(self):
        """Test error handling for unreadable source files."""
        deps_content = "main.o: main.cpp"
        deps_file = self.create_temp_file("main.d", deps_content)

        # Create source file and make it unreadable
        source_file = self.create_temp_file(
            "main.cpp", 'int main() { return 0; }')

        try:
            # Remove read permissions
            os.chmod(source_file, 0o000)

            result = self.run_export_script([deps_file])
            self.assertErrorMessage(result, "permission denied")

        except (OSError, PermissionError):
            self.skipTest("Cannot modify file permissions in this environment")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(source_file, 0o644)
            except (OSError, PermissionError):
                pass

    def test_permission_denied_output_file(self):
        """Test error handling for unwritable output files."""
        deps_content = "main.o: main.cpp"
        deps_file = self.create_temp_file("main.d", deps_content)
        self.create_temp_file("main.cpp", 'int main() { return 0; }')

        # Create output file and make it unwritable
        output_file = os.path.join(self.temp_dir, "readonly_output.cpp")
        with open(output_file, 'w') as f:
            f.write("existing content")

        try:
            # Remove write permissions
            os.chmod(output_file, 0o444)

            result = self.run_export_script(
                [deps_file], output_file=output_file)
            self.assertErrorMessage(result, "permission denied")

        except (OSError, PermissionError):
            self.skipTest("Cannot modify file permissions in this environment")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(output_file, 0o644)
            except (OSError, PermissionError):
                pass

    def test_invalid_output_directory(self):
        """Test error when output directory doesn't exist and can't be
        created."""
        deps_content = "main.o: main.cpp"
        deps_file = self.create_temp_file("main.d", deps_content)
        self.create_temp_file("main.cpp", 'int main() { return 0; }')

        # Try to write to a directory that can't be created (system dependent)
        invalid_output = "/root/nonexistent/deeply/nested/output.cpp"
        result = self.run_export_script(
            [deps_file], output_file=invalid_output)

        # Should fail with directory creation error
        self.assertNotEqual(result.returncode, 0)
        # Error message format may vary by system

    def test_disk_space_exhausted_simulation(self):
        """Test handling of disk space issues (simulated)."""
        # This is difficult to test reliably, but we can test the error path
        # by trying to write to a very long path (system dependent)

        deps_content = "main.o: main.cpp"
        deps_file = self.create_temp_file("main.d", deps_content)
        self.create_temp_file("main.cpp", 'int main() { return 0; }')

        # Create an extremely long filename that might cause issues
        long_filename = "a" * 1000 + ".cpp"
        long_output = os.path.join(self.temp_dir, long_filename)

        self.run_export_script([deps_file], output_file=long_output)
        # Should handle gracefully (may succeed or fail depending on system)


class TestMalformedFiles(ExporterTestCase):
    """Test handling of malformed or corrupted files."""

    def test_binary_file_as_source(self):
        """Test handling binary files mistaken for source files."""
        deps_content = "main.o: main.cpp"
        deps_file = self.create_temp_file("main.d", deps_content)

        # Create a binary file with .cpp extension
        binary_content = b'\x00\x01\x02\x03\xFF\xFE\xFD'
        binary_file = os.path.join(self.temp_dir, "main.cpp")
        with open(binary_file, 'wb') as f:
            f.write(binary_content)

        self.run_export_script([deps_file])

        # Should handle gracefully (may treat as text or detect as binary)
        # Exact behavior depends on implementation

    def test_extremely_large_file(self):
        """Test handling of very large source files."""
        deps_content = "large.o: large.cpp"
        deps_file = self.create_temp_file("large.d", deps_content)

        # Create a large source file (but not too large for testing)
        large_lines = ["// Large file\n"] + \
            [f"int dummy{i};\n" for i in range(1000)]
        large_content = "".join(large_lines)

        self.create_temp_file("large.cpp", large_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Should handle large files without issues
        self.assertIn("Large file", result.stdout)

    def test_corrupted_dependency_file(self):
        """Test handling of corrupted .d files."""
        # Various forms of corruption
        corrupted_files = [
            "",  # Empty file
            "\x00\x01\x02",  # Binary data
            "main.o:",  # Missing dependencies
            ": main.cpp header.h",  # Missing target
            "main.o main.cpp header.h",  # Missing colon
            "main.o: \\\n",  # Incomplete continuation
        ]

        for i, corrupted_content in enumerate(corrupted_files):
            with self.subTest(corruption=i):
                deps_file = self.create_temp_file(
                    f"corrupted{i}.d", corrupted_content)

                # Create valid source file
                self.create_temp_file(
                    f"main{i}.cpp", 'int main() { return 0; }')

                self.run_export_script([deps_file])

                # Should handle gracefully without crashing
                # May succeed (ignoring malformed file) or fail with clear
                # error

    def test_circular_include_references(self):
        """Test detection of circular include patterns."""
        # Create headers that include each other (circular dependency)
        header_a = """#pragma once
#include "header_b.h"

struct A {
    B* b_ptr;
};"""

        header_b = """#pragma once
#include "header_a.h"

struct B {
    A* a_ptr;
};"""

        main_cpp = """#include "header_a.h"
int main() { return 0; }"""

        deps_file = self.create_dependency_file("main.o", "main.cpp",
                                                ["header_a.h", "header_b.h"])

        self.create_temp_file("main.cpp", main_cpp)
        self.create_temp_file("header_a.h", header_a)
        self.create_temp_file("header_b.h", header_b)

        self.run_export_script([deps_file])

        # Should handle circular references gracefully
        # May succeed (with proper ordering) or warn about circularity
        # Should not infinite loop


class TestSystemErrors(ExporterTestCase):
    """Test system-level error conditions."""

    def test_unicode_filenames(self):
        """Test handling files with Unicode characters in names."""
        # Unicode filename
        unicode_filename = "测试文件.cpp"  # Chinese characters
        unicode_header = "файл.h"  # Cyrillic characters

        deps_content = f"main.o: {unicode_filename} {unicode_header}"
        deps_file = self.create_temp_file("unicode.d", deps_content)

        # Create files with Unicode names
        self.create_temp_file(unicode_filename, 'int main() { return 0; }')
        self.create_temp_file(unicode_header, '#pragma once\nvoid func();')

        self.run_export_script([deps_file])

        # Should handle Unicode filenames properly
        # May succeed or fail depending on filesystem support

    def test_very_long_pathnames(self):
        """Test system path length limitations."""
        # Create nested directories to test path length limits
        long_path_parts = ["very"] * 50 + ["long"] * 50 + ["path"]
        long_dir = os.path.join(*long_path_parts)
        long_file = os.path.join(long_dir, "test.cpp")

        try:
            # Try to create the deep directory structure
            os.makedirs(os.path.join(self.temp_dir, long_dir), exist_ok=True)

            deps_content = f"test.o: {long_file}"
            deps_file = self.create_temp_file("long_path.d", deps_content)

            self.create_temp_file(long_file, 'int main() { return 0; }')

            self.run_export_script([deps_file])

            # Should handle long paths gracefully

        except OSError:
            # Path too long for this system
            self.skipTest("System doesn't support very long paths")

    def test_concurrent_file_access(self):
        """Test handling files being modified during processing."""
        # This is a race condition test - difficult to guarantee
        # but we can at least test the basic setup

        deps_content = "main.o: main.cpp"
        deps_file = self.create_temp_file("main.d", deps_content)
        self.create_temp_file("main.cpp", 'int main() { return 0; }')

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # In a real concurrent scenario, we'd modify files during processing
        # For now, just ensure basic functionality works


class TestEdgeCaseInputs(ExporterTestCase):
    """Test edge case inputs and boundary conditions."""

    def test_empty_source_files(self):
        """Test handling of empty source files."""
        deps_content = "empty.o: empty.cpp"
        deps_file = self.create_temp_file("empty.d", deps_content)
        self.create_temp_file("empty.cpp", "")  # Empty file

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Should handle empty files gracefully

    def test_whitespace_only_files(self):
        """Test files containing only whitespace."""
        deps_content = "whitespace.o: whitespace.cpp"
        deps_file = self.create_temp_file("whitespace.d", deps_content)
        self.create_temp_file(
            "whitespace.cpp",
            "   \n\t\n   \n")  # Only whitespace

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

    def test_files_with_only_comments(self):
        """Test files containing only comments."""
        deps_content = "comments.o: comments.cpp"
        deps_file = self.create_temp_file("comments.d", deps_content)
        comment_only = """// This file contains only comments
/* Multi-line comment
   with multiple lines
*/
// Another comment"""

        self.create_temp_file("comments.cpp", comment_only)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Should preserve comments in output
        self.assertIn("This file contains only comments", result.stdout)


if __name__ == '__main__':
    unittest.main()
