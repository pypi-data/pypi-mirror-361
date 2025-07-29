"""
Test dependency file parsing functionality.

Tests parsing of .d files, extraction of source files and dependencies,
handling of multiline continuations, and various edge cases.
"""

from tests.test_utils import ExporterTestCase
import unittest
import os
import sys
from pathlib import Path

# Add the tests directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestDependencyParsing(ExporterTestCase):
    """Test parsing of dependency files (.d format)."""

    def test_simple_dependency_parsing(self):
        """Test parsing single-line dependency files."""
        deps_content = "srcs/main.o: srcs/main.cpp include/plugin.hpp"
        deps_file = self.create_temp_file("main.d", deps_content)

        # Create corresponding files
        self.create_temp_file(
            "srcs/main.cpp",
            '#include "include/plugin.hpp"\nint main() { return 0; }')
        self.create_temp_file("include/plugin.hpp",
                              '#pragma once\nclass Plugin {};'
                              )

        result = self.run_export_script([deps_file], verbose=True)
        self.assertSuccessful(result)

    def test_multiline_dependency_parsing(self):
        """Test parsing dependency files with line continuations."""
        deps_content = """srcs/main.o: \\
    srcs/main.cpp \\
    include/plugin.hpp \\
    include/utils.hpp"""

        deps_file = self.create_temp_file("main.d", deps_content)

        # Create corresponding files
        self.create_temp_file(
            "srcs/main.cpp",
            ('#include "include/plugin.hpp"\n'
             '#include "include/utils.hpp"\n'
             'int main() { return 0; }'))
        self.create_temp_file("include/plugin.hpp",
                              '#pragma once\nclass Plugin {};'
                              )
        self.create_temp_file("include/utils.hpp",
                              '#pragma once\nvoid utility();'
                              )

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

    def test_whitespace_handling(self):
        """Test handling of extra spaces and tabs in dependency files."""
        deps_content = ("  srcs/main.o:\t srcs/main.cpp  \t "
                        "include/plugin.hpp \t")
        deps_file = self.create_temp_file("main.d", deps_content)

        self.create_temp_file(
            "srcs/main.cpp",
            '#include "include/plugin.hpp"\nint main() { return 0; }')
        self.create_temp_file("include/plugin.hpp",
                              '#pragma once\nclass Plugin {};'
                              )

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

    def test_source_file_extraction(self):
        """Test extraction of source file (first dependency after colon)."""
        deps_content = ("srcs/main.o: srcs/main.cpp include/header1.h "
                        "include/header2.h")
        deps_file = self.create_temp_file("main.d", deps_content)

        # Create all referenced files
        self.create_temp_file(
            "srcs/main.cpp",
            ('#include "include/header1.h"\n'
             '#include "include/header2.h"\n'
             'int main() { return 0; }'))
        self.create_temp_file(
            "include/header1.h",
            ('#ifndef HEADER1_H\n'
             '#define HEADER1_H\n'
             'void func1();\n'
             '#endif'))
        self.create_temp_file(
            "include/header2.h",
            '#ifndef HEADER2_H\n#define HEADER2_H\nvoid func2();\n#endif')

        result = self.run_export_script([deps_file], verbose=True)
        self.assertSuccessful(result)

        # Should process main.cpp as source, headers as dependencies
        self.assertIn("srcs/main.cpp", result.stderr)

    def test_multiple_dependency_files(self):
        """Test merging dependencies from multiple .d files."""
        # First dependency file
        deps1_content = "srcs/main.o: srcs/main.cpp include/shared.h"
        deps1_file = self.create_temp_file("main.d", deps1_content)

        # Second dependency file
        deps2_content = "srcs/utils.o: srcs/utils.cpp include/shared.h"
        deps2_file = self.create_temp_file("utils.d", deps2_content)

        # Create source files
        self.create_temp_file(
            "srcs/main.cpp",
            '#include "include/shared.h"\nint main() { return 0; }')
        self.create_temp_file("srcs/utils.cpp",
                              '#include "include/shared.h"\nvoid utility() {}'
                              )
        self.create_temp_file("include/shared.h",
                              '#pragma once\nstruct Shared {};'
                              )

        result = self.run_export_script([deps1_file, deps2_file])
        self.assertSuccessful(result)

    def test_overlapping_dependencies(self):
        """Test same header appearing in multiple dependency files."""
        deps1_content = "main.o: main.cpp common.h specific1.h"
        deps2_content = "utils.o: utils.cpp common.h specific2.h"

        deps1_file = self.create_temp_file("main.d", deps1_content)
        deps2_file = self.create_temp_file("utils.d", deps2_content)

        # Create all files
        self.create_temp_file(
            "main.cpp",
            ('#include "common.h"\n'
             '#include "specific1.h"\n'
             'int main() { return 0; }'))
        self.create_temp_file(
            "utils.cpp",
            '#include "common.h"\n#include "specific2.h"\nvoid utility() {}')
        self.create_temp_file("common.h",
                              '#pragma once\nstruct Common {};'
                              )
        self.create_temp_file("specific1.h",
                              '#pragma once\nvoid func1();'
                              )
        self.create_temp_file("specific2.h",
                              '#pragma once\nvoid func2();'
                              )

        result = self.run_export_script([deps1_file, deps2_file])
        self.assertSuccessful(result)

        # common.h should appear only once in output
        common_count = result.stdout.count("struct Common")
        self.assertEqual(common_count, 1, "Header should appear only once")


class TestDependencyEdgeCases(ExporterTestCase):
    """Test edge cases and error conditions in dependency parsing."""

    def test_empty_dependency_file(self):
        """Test handling of empty dependency files."""
        empty_deps = self.create_temp_file("empty.d", "")
        self.run_export_script([empty_deps])

        # Should handle gracefully
        # Exact behavior depends on implementation

    def test_malformed_dependency_syntax(self):
        """Test handling of malformed dependency file syntax."""
        malformed_content = "this is not a valid dependency format"
        malformed_file = self.create_temp_file(
            "malformed.d", malformed_content)

        self.run_export_script([malformed_file])
        # Should either handle gracefully or provide clear error

    def test_missing_colon_separator(self):
        """Test dependency files without colon separator."""
        no_colon_content = "main.o main.cpp header.h"
        no_colon_file = self.create_temp_file("no_colon.d", no_colon_content)

        self.run_export_script([no_colon_file])
        # Should handle gracefully or provide clear error

    def test_dependency_with_comments(self):
        """Test handling of comments in dependency files."""
        # Note: Standard .d files shouldn't have comments, but test robustness
        deps_with_comment = """# This is a comment
main.o: main.cpp header.h
# Another comment"""

        deps_file = self.create_temp_file("commented.d", deps_with_comment)
        self.create_temp_file("main.cpp", 'int main() { return 0; }')
        self.create_temp_file("header.h", '#pragma once\nvoid func();')

        self.run_export_script([deps_file])
        # Should handle gracefully

    def test_absolute_vs_relative_paths(self):
        """Test path normalization in dependency files."""
        # Mix of absolute and relative paths
        abs_path = os.path.abspath(os.path.join(self.temp_dir, "main.cpp"))
        rel_path = "header.h"

        deps_content = f"main.o: {abs_path} {rel_path}"
        deps_file = self.create_temp_file("mixed_paths.d", deps_content)

        self.create_temp_file("main.cpp", 'int main() { return 0; }')
        self.create_temp_file("header.h", '#pragma once\nvoid func();')

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

    def test_very_long_dependency_lines(self):
        """Test handling of very long dependency lines."""
        # Create a dependency with many headers
        headers = [f"header{i}.h" for i in range(50)]
        deps_content = f"main.o: main.cpp {' '.join(headers)}"

        deps_file = self.create_temp_file("long_deps.d", deps_content)
        self.create_temp_file("main.cpp", 'int main() { return 0; }')

        # Create all header files
        for header in headers:
            self.create_temp_file(
                header, f'#pragma once\nvoid func_{
                    header.replace(
                        ".", "_")}();')

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

    def test_multiline_with_mixed_continuations(self):
        """Test complex multiline continuations."""
        deps_content = """main.o: main.cpp \\
header1.h \\
  header2.h\\
\theader3.h \\
header4.h"""

        deps_file = self.create_temp_file("complex_multiline.d", deps_content)

        # Create all files
        files = [
            "main.cpp",
            "header1.h",
            "header2.h",
            "header3.h",
            "header4.h"]
        for i, filename in enumerate(files):
            if filename.endswith('.cpp'):
                content = f'int main() {{ return {i}; }}'
            else:
                content = f'#pragma once\nvoid func{i}();'
            self.create_temp_file(filename, content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)


if __name__ == '__main__':
    unittest.main()
