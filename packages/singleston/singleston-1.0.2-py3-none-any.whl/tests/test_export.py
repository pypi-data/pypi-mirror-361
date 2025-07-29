"""
Test end-to-end export functionality and integration scenarios.

Tests complete export workflows, output generation, file separators,
and integration with real project structures.
"""

from tests.test_utils import ExporterTestCase
import unittest
import os
import sys
from pathlib import Path

# Add the tests directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestEndToEndExport(ExporterTestCase):
    """Test complete export workflows."""

    def test_simple_project_export(self):
        """Test end-to-end export with basic project structure."""
        # Create a simple project
        main_cpp = """#include "utils.h"
#include <iostream>

int main() {
    utility_function();
    std::cout << "Hello, world!" << std::endl;
    return 0;
}"""

        utils_h = """#ifndef UTILS_H
#define UTILS_H

void utility_function();

#endif // UTILS_H"""

        utils_cpp = """#include "utils.h"
#include <iostream>

void utility_function() {
    std::cout << "Utility called" << std::endl;
}"""

        # Create dependency files
        main_deps = self.create_dependency_file(
            "main.o", "main.cpp", ["utils.h"])
        utils_deps = self.create_dependency_file(
            "utils.o", "utils.cpp", ["utils.h"])

        # Create source files
        self.create_temp_file("main.cpp", main_cpp)
        self.create_temp_file("utils.h", utils_h)
        self.create_temp_file("utils.cpp", utils_cpp)

        # Export to file
        output_file = os.path.join(self.temp_dir, "exported.cpp")
        result = self.run_export_script(
            [main_deps, utils_deps], output_file=output_file)

        self.assertSuccessful(result)
        self.assertTrue(os.path.exists(output_file))

        # Read and verify output
        with open(output_file, 'r') as f:
            content = f.read()

        # Should contain system includes
        self.assertIn("#include <iostream>", content)

        # Should contain header content (without guards)
        self.assertIn("utility_function", content)
        self.assertNotIn("#ifndef UTILS_H", content)
        self.assertNotIn("#endif", content)

        # Should contain source content (without local includes)
        self.assertIn("Hello, world!", content)
        self.assertIn("Utility called", content)
        self.assertNotIn('#include "utils.h"', content)

    def test_stdout_output(self):
        """Test default output to stdout."""
        main_cpp = """#include <iostream>
int main() {
    std::cout << "Test" << std::endl;
    return 0;
}"""

        deps_file = self.create_dependency_file("main.o", "main.cpp", [])
        self.create_temp_file("main.cpp", main_cpp)

        result = self.run_export_script(
            [deps_file])  # No output file specified
        self.assertSuccessful(result)

        # Output should go to stdout
        self.assertIn("#include <iostream>", result.stdout)
        self.assertIn("Test", result.stdout)

    def test_file_separators_enabled(self):
        """Test --add-separators functionality."""
        main_cpp = 'int main() { return 0; }'
        utils_cpp = 'void utility() {}'

        main_deps = self.create_dependency_file("main.o", "main.cpp", [])
        utils_deps = self.create_dependency_file("utils.o", "utils.cpp", [])

        self.create_temp_file("main.cpp", main_cpp)
        self.create_temp_file("utils.cpp", utils_cpp)

        result = self.run_export_script(
            [main_deps, utils_deps], add_separators=True)
        self.assertSuccessful(result)

        # Should contain file boundary markers
        # Exact format depends on implementation, but should have some kind of
        # separator
        output_lines = result.stdout.split('\n')
        separator_lines = [
            line for line in output_lines
            if 'main.cpp' in line or 'utils.cpp' in line]
        self.assertGreater(
            len(separator_lines),
            0,
            "Should contain file separators")

    def test_complex_project_structure(self):
        """Test export with complex project structure."""
        # Create a more complex project with multiple headers and dependencies

        # Main application
        main_cpp = """#include "core/engine.h"
#include "utils/logger.h"
#include <iostream>

int main() {
    Engine engine;
    Logger::info("Starting application");
    engine.run();
    return 0;
}"""

        # Engine header and implementation
        engine_h = """#pragma once
#include "utils/logger.h"

class Engine {
public:
    void run();
private:
    void initialize();
};"""

        engine_cpp = """#include "core/engine.h"
#include <iostream>

void Engine::run() {
    initialize();
    std::cout << "Engine running" << std::endl;
}

void Engine::initialize() {
    Logger::debug("Engine initialized");
}"""

        # Logger header and implementation
        logger_h = """#ifndef LOGGER_H
#define LOGGER_H

#include <string>

class Logger {
public:
    static void info(const std::string& message);
    static void debug(const std::string& message);
};

#endif // LOGGER_H"""

        logger_cpp = """#include "utils/logger.h"
#include <iostream>

void Logger::info(const std::string& message) {
    std::cout << "[INFO] " << message << std::endl;
}

void Logger::debug(const std::string& message) {
    std::cout << "[DEBUG] " << message << std::endl;
}"""

        # Create dependency files
        main_deps = self.create_dependency_file(
            "main.o", "main.cpp", [
                "core/engine.h", "utils/logger.h"])
        engine_deps = self.create_dependency_file(
            "core/engine.o", "core/engine.cpp",
            ["core/engine.h", "utils/logger.h"])
        logger_deps = self.create_dependency_file(
            "utils/logger.o", "utils/logger.cpp", ["utils/logger.h"])

        # Create all files
        self.create_temp_file("main.cpp", main_cpp)
        self.create_temp_file("core/engine.h", engine_h)
        self.create_temp_file("core/engine.cpp", engine_cpp)
        self.create_temp_file("utils/logger.h", logger_h)
        self.create_temp_file("utils/logger.cpp", logger_cpp)

        # Export with verbose output
        result = self.run_export_script(
            [main_deps, engine_deps, logger_deps], verbose=True)
        self.assertSuccessful(result)

        # Verify content organization
        content = result.stdout

        # Should have system includes at top
        self.assertIn("#include <iostream>", content)
        self.assertIn("#include <string>", content)

        # Headers should appear before sources
        logger_h_pos = content.find("class Logger")
        content.find("class Engine")
        main_cpp_pos = content.find("Starting application")

        self.assertLess(
            logger_h_pos,
            main_cpp_pos,
            "Headers should appear before source content")

        # Include guards should be removed
        self.assertNotIn("#pragma once", content)
        self.assertNotIn("#ifndef LOGGER_H", content)

        # Local includes should be removed
        self.assertNotIn('#include "core/engine.h"', content)
        self.assertNotIn('#include "utils/logger.h"', content)


class TestIntegrationScenarios(ExporterTestCase):
    """Test integration with real-world scenarios."""

    def test_plugin_system_export(self):
        """Test exporting a plugin-based system (like the example project)."""
        # Plugin interface
        plugin_h = """#pragma once

class Plugin {
public:
    virtual ~Plugin() = default;
    virtual void execute() = 0;
    virtual const char* getName() const = 0;
};"""

        # Plugin registry
        registry_h = """#pragma once
#include "plugin.h"
#include <vector>
#include <memory>

class PluginRegistry {
public:
    void registerPlugin(std::unique_ptr<Plugin> plugin);
    void executeAll();

private:
    std::vector<std::unique_ptr<Plugin>> plugins;
};"""

        registry_cpp = """#include "plugin_registry.h"
#include <iostream>

void PluginRegistry::registerPlugin(std::unique_ptr<Plugin> plugin) {
    plugins.push_back(std::move(plugin));
}

void PluginRegistry::executeAll() {
    for (auto& plugin : plugins) {
        std::cout << "Executing: " << plugin->getName() << std::endl;
        plugin->execute();
    }
}"""

        # Concrete plugins
        plugin_a_cpp = """#include "plugin.h"
#include <iostream>

class PluginA : public Plugin {
public:
    void execute() override {
        std::cout << "PluginA executed" << std::endl;
    }

    const char* getName() const override {
        return "PluginA";
    }
};"""

        main_cpp = """#include "plugin_registry.h"
#include <memory>

int main() {
    PluginRegistry registry;
    // Note: Simplified for testing
    return 0;
}"""

        # Create dependency files
        main_deps = self.create_dependency_file(
            "main.o", "main.cpp", [
                "plugin_registry.h", "plugin.h"])
        registry_deps = self.create_dependency_file(
            "plugin_registry.o", "plugin_registry.cpp", [
                "plugin_registry.h", "plugin.h"])
        plugin_a_deps = self.create_dependency_file(
            "plugin_a.o", "plugin_a.cpp", ["plugin.h"])

        # Create files
        self.create_temp_file("plugin.h", plugin_h)
        self.create_temp_file("plugin_registry.h", registry_h)
        self.create_temp_file("plugin_registry.cpp", registry_cpp)
        self.create_temp_file("plugin_a.cpp", plugin_a_cpp)
        self.create_temp_file("main.cpp", main_cpp)

        result = self.run_export_script(
            [main_deps, registry_deps, plugin_a_deps])
        self.assertSuccessful(result)

        content = result.stdout

        # Should contain all class definitions
        self.assertIn("class Plugin", content)
        self.assertIn("class PluginRegistry", content)
        self.assertIn("class PluginA", content)

        # Should preserve inheritance
        self.assertIn("public Plugin", content)

        # Should handle includes properly
        self.assertIn("#include <vector>", content)
        self.assertIn("#include <memory>", content)

    def test_library_amalgamation(self):
        """Test creating a single-header library."""
        # Library header
        mylib_h = """#ifndef MYLIB_H
#define MYLIB_H

#include <string>

namespace MyLib {
    class Calculator {
    public:
        int add(int a, int b);
        int multiply(int a, int b);
        std::string getVersion();
    };
}

#endif // MYLIB_H"""

        # Library implementation
        mylib_cpp = """#include "mylib.h"

namespace MyLib {
    int Calculator::add(int a, int b) {
        return a + b;
    }

    int Calculator::multiply(int a, int b) {
        return a * b;
    }

    std::string Calculator::getVersion() {
        return "1.0.0";
    }
}"""

        # Create dependency file
        deps_file = self.create_dependency_file(
            "mylib.o", "mylib.cpp", ["mylib.h"])

        # Create files
        self.create_temp_file("mylib.h", mylib_h)
        self.create_temp_file("mylib.cpp", mylib_cpp)

        # Export to single header
        output_file = os.path.join(self.temp_dir, "mylib_single.hpp")
        result = self.run_export_script(
            [deps_file],
            output_file=output_file,
            add_separators=True)

        self.assertSuccessful(result)

        # Read the amalgamated library
        with open(output_file, 'r') as f:
            content = f.read()

        # Should be a complete single-header library
        self.assertIn("#include <string>", content)
        self.assertIn("namespace MyLib", content)
        self.assertIn("class Calculator", content)
        self.assertIn("return a + b", content)  # Implementation

        # Include guards should be removed
        self.assertNotIn("#ifndef MYLIB_H", content)
        self.assertNotIn("#endif // MYLIB_H", content)


if __name__ == '__main__':
    unittest.main()
