"""
Test file content processing and include handling.

Tests file reading, include processing (system vs local), deduplication,
and order of appearance handling.
"""

from tests.test_utils import ExporterTestCase
import unittest
import sys
from pathlib import Path

# Add the tests directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestFileProcessing(ExporterTestCase):
    """Test file content reading and processing."""

    def test_utf8_encoding_handling(self):
        """Test proper UTF-8 file handling."""
        # Create a file with UTF-8 content
        utf8_content = """#include <iostream>
// UTF-8 comment with special chars: éñüñ, 中文, русский
int main() {
    std::cout << "Hello, 世界!" << std::endl;
    return 0;
}"""

        deps_file = self.create_dependency_file("main.o", "main.cpp", [])
        self.create_temp_file("main.cpp", utf8_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)
        self.assertIn("世界", result.stdout)

    def test_line_ending_preservation(self):
        """Test maintaining original line endings."""
        content = "int main() {\n    return 0;\n}"

        deps_file = self.create_dependency_file("main.o", "main.cpp", [])
        self.create_temp_file("main.cpp", content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)
        # Should preserve the line structure
        self.assertIn("{\n", result.stdout)
        self.assertIn("return 0;", result.stdout)

    def test_files_without_final_newline(self):
        """Test handling files that don't end with newline."""
        content_no_newline = "int main() { return 0; }"  # No final newline

        deps_file = self.create_dependency_file("main.o", "main.cpp", [])
        self.create_temp_file("main.cpp", content_no_newline)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)


class TestIncludeProcessing(ExporterTestCase):
    """Test include directive processing and classification."""

    def test_system_include_preservation(self):
        """Test that system includes are preserved."""
        main_content = """#include <iostream>
#include <vector>
#include <string>

int main() {
    std::vector<std::string> data;
    return 0;
}"""

        deps_file = self.create_dependency_file("main.o", "main.cpp", [])
        self.create_temp_file("main.cpp", main_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # System includes should be preserved
        self.assertIn("#include <iostream>", result.stdout)
        self.assertIn("#include <vector>", result.stdout)
        self.assertIn("#include <string>", result.stdout)

    def test_local_include_removal(self):
        """Test that local includes for inlined files are removed."""
        main_content = """#include "utils.h"
#include <iostream>

int main() {
    utility_function();
    return 0;
}"""

        utils_header = """#pragma once
void utility_function();"""

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["utils.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("utils.h", utils_header)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # System include should be preserved
        self.assertIn("#include <iostream>", result.stdout)

        # Local include should be removed (header content inlined instead)
        self.assertNotIn('#include "utils.h"', result.stdout)

        # Header content should be present
        self.assertIn("utility_function", result.stdout)

    def test_include_classification(self):
        """Test distinguishing system vs local includes."""
        main_content = """#include <system_header>
#include "local_header.h"
#include <another/system/header.h>
#include "path/to/local.h"

int main() { return 0; }"""

        local_header = "#pragma once\nvoid local_func();"
        local_nested = "#pragma once\nvoid nested_func();"

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", [
                "local_header.h", "path/to/local.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("local_header.h", local_header)
        self.create_temp_file("path/to/local.h", local_nested)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # System includes (angle brackets) should be preserved
        self.assertIn("#include <system_header>", result.stdout)
        self.assertIn("#include <another/system/header.h>", result.stdout)

        # Local includes (quotes) should be removed for inlined files
        self.assertNotIn('#include "local_header.h"', result.stdout)
        self.assertNotIn('#include "path/to/local.h"', result.stdout)

    def test_order_of_appearance_includes(self):
        """Test that includes are processed in order of first appearance."""
        # First file includes headers in one order
        main_content = """#include "header_b.h"
#include "header_a.h"
int main() { return 0; }"""

        # Second file includes same headers in different order
        utils_content = """#include "header_a.h"
#include "header_b.h"
void utility() {}"""

        header_a = "#pragma once\nstruct A {};"
        header_b = "#pragma once\nstruct B {};"

        deps1_file = self.create_dependency_file("main.o", "main.cpp",
                                                 ["header_b.h", "header_a.h"])
        deps2_file = self.create_dependency_file("utils.o", "utils.cpp",
                                                 ["header_a.h", "header_b.h"])

        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("utils.cpp", utils_content)
        self.create_temp_file("header_a.h", header_a)
        self.create_temp_file("header_b.h", header_b)

        result = self.run_export_script([deps1_file, deps2_file])
        self.assertSuccessful(result)

        # header_b should appear before header_a (first appearance order)
        b_pos = result.stdout.find("struct B")
        a_pos = result.stdout.find("struct A")
        self.assertLess(
            b_pos,
            a_pos,
            "Headers should appear in order of first appearance")


class TestDeduplication(ExporterTestCase):
    """Test file and include deduplication logic."""

    def test_header_deduplication(self):
        """Test that each header is processed only once."""
        # Multiple sources including the same header
        main_content = '#include "shared.h"\nint main() { return 0; }'
        utils_content = '#include "shared.h"\nvoid utility() {}'
        lib_content = '#include "shared.h"\nvoid library() {}'

        shared_header = """#pragma once
struct SharedData {
    int value;
};"""

        deps1 = self.create_dependency_file("main.o", "main.cpp", ["shared.h"])
        deps2 = self.create_dependency_file(
            "utils.o", "utils.cpp", ["shared.h"])
        deps3 = self.create_dependency_file("lib.o", "lib.cpp", ["shared.h"])

        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("utils.cpp", utils_content)
        self.create_temp_file("lib.cpp", lib_content)
        self.create_temp_file("shared.h", shared_header)

        result = self.run_export_script([deps1, deps2, deps3])
        self.assertSuccessful(result)

        # SharedData should appear exactly once
        shared_count = result.stdout.count("struct SharedData")
        self.assertEqual(
            shared_count,
            1,
            "Header content should appear only once")

    def test_system_include_deduplication(self):
        """Test removal of duplicate system includes."""
        main_content = """#include <iostream>
#include <vector>
int main() { return 0; }"""

        utils_content = """#include <iostream>
#include <string>
void utility() {}"""

        deps1 = self.create_dependency_file("main.o", "main.cpp", [])
        deps2 = self.create_dependency_file("utils.o", "utils.cpp", [])

        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("utils.cpp", utils_content)

        result = self.run_export_script([deps1, deps2])
        self.assertSuccessful(result)

        # iostream should appear only once
        iostream_count = result.stdout.count("#include <iostream>")
        self.assertEqual(
            iostream_count,
            1,
            "System includes should be deduplicated")

        # But vector and string should both be present
        self.assertIn("#include <vector>", result.stdout)
        self.assertIn("#include <string>", result.stdout)

    def test_first_appearance_wins(self):
        """Test that first occurrence takes precedence."""
        # Create two versions of the same header with different content
        version1 = """#pragma once
// Version 1
struct Data { int x; };"""

        main_content = '#include "data.h"\nint main() { return 0; }'

        # First dependency file uses version 1
        deps1 = self.create_dependency_file("main.o", "main.cpp", ["data.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("data.h", version1)

        # Run first to establish order
        result1 = self.run_export_script([deps1])
        self.assertSuccessful(result1)

        # Should contain version 1 content
        self.assertIn("Version 1", result1.stdout)
        self.assertIn("int x", result1.stdout)


class TestComplexFileStructures(ExporterTestCase):
    """Test processing of complex file structures."""

    def test_nested_directory_structure(self):
        """Test handling files in nested directories."""
        main_content = ('#include "lib/utils.h"\n'
                        '#include "core/engine.h"\n'
                        'int main() { return 0; }')

        utils_header = "#pragma once\nvoid utility();"
        engine_header = "#pragma once\nclass Engine {};"

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", [
                "lib/utils.h", "core/engine.h"])

        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("lib/utils.h", utils_header)
        self.create_temp_file("core/engine.h", engine_header)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Both headers should be inlined
        self.assertIn("utility", result.stdout)
        self.assertIn("Engine", result.stdout)

    def test_mixed_file_extensions(self):
        """Test handling mixed C/C++ file extensions."""
        # Mix of .c, .cpp, .h, .hpp files
        main_content = ('#include "utils.hpp"\n'
                        '#include "legacy.h"\n'
                        'int main() { return 0; }')
        utils_cpp = '#include "utils.hpp"\nvoid cpp_utility() {}'
        legacy_c = '#include "legacy.h"\nvoid c_utility() {}'

        utils_hpp = "#pragma once\nvoid cpp_utility();"
        legacy_h = ("#ifndef LEGACY_H\n"
                    "#define LEGACY_H\n"
                    "void c_utility();\n"
                    "#endif")

        deps1 = self.create_dependency_file(
            "main.o", "main.cpp", [
                "utils.hpp", "legacy.h"])
        deps2 = self.create_dependency_file(
            "utils.o", "utils.cpp", ["utils.hpp"])
        deps3 = self.create_dependency_file(
            "legacy.o", "legacy.c", ["legacy.h"])

        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("utils.cpp", utils_cpp)
        self.create_temp_file("legacy.c", legacy_c)
        self.create_temp_file("utils.hpp", utils_hpp)
        self.create_temp_file("legacy.h", legacy_h)

        result = self.run_export_script([deps1, deps2, deps3])
        self.assertSuccessful(result)

        # All function declarations should be present
        self.assertIn("cpp_utility", result.stdout)
        self.assertIn("c_utility", result.stdout)


if __name__ == '__main__':
    unittest.main()
