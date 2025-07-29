"""
Test include guard detection and removal functionality.

Tests detection and removal of both #pragma once and traditional
#ifndef/#define/#endif include guard patterns.
"""

from tests.test_utils import ExporterTestCase
import unittest
import sys
from pathlib import Path

# Add the tests directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestIncludeGuardRemoval(ExporterTestCase):
    """Test include guard detection and removal."""

    def test_pragma_once_removal(self):
        """Test removal of #pragma once directives."""
        header_content = """#pragma once

#include <iostream>

class Example {
public:
    void doSomething();
};"""

        main_content = '#include "example.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["example.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("example.h", header_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # #pragma once should be removed
        self.assertNotIn("#pragma once", result.stdout)

        # But class content should remain
        self.assertIn("class Example", result.stdout)
        self.assertIn("doSomething", result.stdout)

        # System include should be preserved
        self.assertIn("#include <iostream>", result.stdout)

    def test_pragma_once_with_whitespace(self):
        """Test pragma once with various whitespace patterns."""
        test_cases = [
            "  #pragma once  ",
            "\t#pragma once\t",
            " \t #pragma once \t ",
            "#pragma once\n\n",
            "\n#pragma once\n"
        ]

        for i, pragma_line in enumerate(test_cases):
            with self.subTest(case=i):
                header_content = f"""{pragma_line}
class Test{i} {{}};"""

                main_content = (f'#include "test{i}.h"\n'
                                f'int main() {{ return 0; }}')

                deps_file = self.create_dependency_file(
                    f"main{i}.o", f"main{i}.cpp", [f"test{i}.h"])
                self.create_temp_file(f"main{i}.cpp", main_content)
                self.create_temp_file(f"test{i}.h", header_content)

                result = self.run_export_script([deps_file])
                self.assertSuccessful(result)

                # pragma once should be removed regardless of whitespace
                self.assertNotIn("#pragma once", result.stdout)
                self.assertIn(f"Test{i}", result.stdout)

    def test_multiple_pragma_once(self):
        """Test handling of multiple pragma once in single file."""
        header_content = """#pragma once
// First pragma once

#pragma once
// Second pragma once (shouldn't normally happen)

class Example {};"""

        main_content = '#include "example.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["example.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("example.h", header_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # All pragma once directives should be removed
        self.assertNotIn("#pragma once", result.stdout)
        self.assertIn("class Example", result.stdout)


class TestTraditionalIncludeGuards(ExporterTestCase):
    """Test traditional #ifndef/#define/#endif include guard patterns."""

    def test_simple_include_guard_removal(self):
        """Test removal of basic #ifndef/#define/#endif pattern."""
        header_content = """#ifndef EXAMPLE_H
#define EXAMPLE_H

#include <string>

class Example {
private:
    std::string name;
public:
    Example(const std::string& n) : name(n) {}
    void print();
};

#endif // EXAMPLE_H"""

        main_content = '#include "example.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["example.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("example.h", header_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Include guard should be removed
        self.assertNotIn("#ifndef EXAMPLE_H", result.stdout)
        self.assertNotIn("#define EXAMPLE_H", result.stdout)
        self.assertNotIn("#endif", result.stdout)

        # Content should remain
        self.assertIn("class Example", result.stdout)
        self.assertIn("#include <string>", result.stdout)

    def test_include_guard_with_whitespace(self):
        """Test guards with extra spaces and newlines."""
        header_content = """  #ifndef   UTILS_H
  #define   UTILS_H

void utility_function();

  #endif  // UTILS_H  """

        main_content = '#include "utils.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["utils.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("utils.h", header_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Guard should be removed despite whitespace
        self.assertNotIn("#ifndef", result.stdout)
        self.assertNotIn("#define", result.stdout)
        self.assertNotIn("#endif", result.stdout)

        # Function should remain
        self.assertIn("utility_function", result.stdout)

    def test_nested_conditionals_with_guards(self):
        """Test guards with nested #if blocks inside."""
        header_content = """#ifndef CONFIG_H
#define CONFIG_H

#ifdef DEBUG
    #define LOG(x) printf(x)
#else
    #define LOG(x)
#endif

#if defined(PLATFORM_LINUX)
    #include <unistd.h>
#elif defined(PLATFORM_WINDOWS)
    #include <windows.h>
#endif

void configure();

#endif // CONFIG_H"""

        main_content = '#include "config.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["config.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("config.h", header_content)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Include guard should be removed
        self.assertNotIn("#ifndef CONFIG_H", result.stdout)
        self.assertNotIn("#define CONFIG_H", result.stdout)

        # But inner conditionals should remain
        self.assertIn("#ifdef DEBUG", result.stdout)
        self.assertIn("#if defined(PLATFORM_LINUX)", result.stdout)
        self.assertIn("configure", result.stdout)

        # Should not remove the wrong #endif
        remaining_endifs = result.stdout.count("#endif")
        self.assertGreater(
            remaining_endifs,
            0,
            "Inner #endif statements should remain")

    def test_complex_guard_patterns(self):
        """Test various include guard naming conventions."""
        guard_patterns = [
            ("SIMPLE_H", "simple.h"),
            ("LIB_COMPLEX_HEADER_HPP", "complex_header.hpp"),
            ("_PRIVATE_H_", "private.h"),
            ("NAMESPACE_CLASS_H", "class.h"),
            ("PROJECT_MODULE_UTILS_H", "utils.h")
        ]

        for guard_name, filename in guard_patterns:
            with self.subTest(guard=guard_name):
                header_content = f"""#ifndef {guard_name}
#define {guard_name}

void function_in_{filename.replace('.', '_')}();

#endif // {guard_name}"""

                main_content = (f'#include "{filename}"\n'
                                f'int main() {{ return 0; }}')

                deps_file = self.create_dependency_file(
                    "main.o", "main.cpp", [filename])
                self.create_temp_file("main.cpp", main_content)
                self.create_temp_file(filename, header_content)

                result = self.run_export_script([deps_file])
                self.assertSuccessful(result)

                # Guard should be removed
                self.assertNotIn(f"#ifndef {guard_name}", result.stdout)
                self.assertNotIn(f"#define {guard_name}", result.stdout)

                # Function should remain
                self.assertIn(
                    f"function_in_{
                        filename.replace(
                            '.',
                            '_')}",
                    result.stdout)


class TestIncludeGuardEdgeCases(ExporterTestCase):
    """Test edge cases and malformed include guards."""

    def test_partial_include_guards(self):
        """Test incomplete guard patterns."""
        # Missing #endif
        incomplete_guard = """#ifndef INCOMPLETE_H
#define INCOMPLETE_H

void function();
// Missing #endif"""

        main_content = '#include "incomplete.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["incomplete.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("incomplete.h", incomplete_guard)

        self.run_export_script([deps_file])
        # Should handle gracefully (implementation dependent)
        # May or may not remove partial guards

    def test_guard_without_endif(self):
        """Test #ifndef/#define without matching #endif."""
        malformed_guard = """#ifndef MALFORMED_H
#define MALFORMED_H

void function();"""

        main_content = '#include "malformed.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["malformed.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("malformed.h", malformed_guard)

        self.run_export_script([deps_file])
        # Should handle gracefully without crashing

    def test_multiple_guards_per_file(self):
        """Test files with multiple guard attempts."""
        multi_guard = """#ifndef FIRST_GUARD_H
#define FIRST_GUARD_H

#ifndef SECOND_GUARD_H
#define SECOND_GUARD_H

void function();

#endif // SECOND_GUARD_H
#endif // FIRST_GUARD_H"""

        main_content = '#include "multi.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["multi.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("multi.h", multi_guard)

        result = self.run_export_script([deps_file])
        self.assertSuccessful(result)

        # Should handle nested guards appropriately
        self.assertIn("function", result.stdout)

    def test_guards_in_wrong_order(self):
        """Test #define before #ifndef (malformed)."""
        wrong_order = """#define WRONG_ORDER_H
#ifndef WRONG_ORDER_H

void function();

#endif // WRONG_ORDER_H"""

        main_content = '#include "wrong.h"\nint main() { return 0; }'

        deps_file = self.create_dependency_file(
            "main.o", "main.cpp", ["wrong.h"])
        self.create_temp_file("main.cpp", main_content)
        self.create_temp_file("wrong.h", wrong_order)

        self.run_export_script([deps_file])
        # Should handle gracefully

    def test_guard_with_different_comment_styles(self):
        """Test various comment styles in #endif."""
        comment_styles = [
            "#endif // HEADER_H",
            "#endif /* HEADER_H */",
            "#endif // !HEADER_H",
            "#endif /* !HEADER_H */",
            "#endif  // End of HEADER_H",
            "#endif // HEADER_H_INCLUDED"
        ]

        for i, endif_line in enumerate(comment_styles):
            with self.subTest(style=i):
                header_content = f"""#ifndef HEADER_{i}_H
#define HEADER_{i}_H

void func{i}();

{endif_line}"""

                main_content = (f'#include "test{i}.h"\n'
                                f'int main() {{ return 0; }}')

                deps_file = self.create_dependency_file(
                    f"main{i}.o", f"main{i}.cpp", [f"test{i}.h"])
                self.create_temp_file(f"main{i}.cpp", main_content)
                self.create_temp_file(f"test{i}.h", header_content)

                result = self.run_export_script([deps_file])
                self.assertSuccessful(result)

                # Guard should be removed regardless of comment style
                self.assertNotIn(f"#ifndef HEADER_{i}_H", result.stdout)
                self.assertNotIn(f"#define HEADER_{i}_H", result.stdout)
                self.assertNotIn("#endif", result.stdout)

                # Function should remain
                self.assertIn(f"func{i}", result.stdout)


if __name__ == '__main__':
    unittest.main()
