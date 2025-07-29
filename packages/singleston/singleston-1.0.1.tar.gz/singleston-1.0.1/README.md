# 🔗 Singleston

A powerful source file amalgamator that converts multi-file projects into a single, self-contained source file. Currently supports C and C++ projects, using compiler-generated dependency files to intelligently resolve includes and create properly ordered, unified source code.

Perfect for creating single-header libraries, distributing code, simplifying builds, or reducing compilation complexity.

## ✨ Features

- 🔍 **Smart Dependency Resolution**: Uses compiler-generated `.d` files for accurate dependency tracking
- 📁 **C/C++ Support**: Handles both C and C++ files with any header extension (`.h`, `.hh`, `.hpp`, etc.)
- 🔄 **Intelligent Include Processing**: 
  - Preserves system includes (`#include <system>`)
  - Removes local includes for files being amalgamated
  - Deduplicates includes while preserving order of first appearance
- 🛡️ **Include Guard Removal**: Automatically detects and removes both `#pragma once` and traditional include guards
- 📊 **Topological Sorting**: Ensures proper file processing order based on dependency relationships
- 🎯 **First Appearance Priority**: Processes files in order of first appearance across dependency files

### 🎁 Advanced Features

- 🔧 **Flexible Output Options**: Write to file (`-o`) or stdout by default
- 📝 **File Boundary Markers**: Optional separators (`--add-separators`) for debugging
- 🔍 **Verbose Mode**: Detailed processing information (`-v, --verbose`) for troubleshooting
- 🔗 **Symlink Support**: Optional symlink following (`--follow-symlinks`) for complex project structures
- 🚨 **Comprehensive Error Handling**: Colored error messages with detailed diagnostics
- ⚡ **High Performance**: Efficient processing even for large codebases

### 🛠️ Build Integration

- 🔌 **Makefile Integration**: Works seamlessly with existing build systems
- 📦 **Batch Processing**: Handle multiple dependency files in a single command
- 🔄 **Automated Workflow**: Integrate into CI/CD pipelines for automated amalgamation
- 🎯 **Zero Configuration**: Works out of the box with standard gcc/clang `-MMD` output

## 📦 Prerequisites

- **Python 3.8+**: Required for running the amalgamator
- **C/C++ Compiler**: clang or gcc with `-MMD` flag support for dependency generation
- **Make**: For using the provided build system (optional)

## 🚀 Quick Start

### 1. Generate Dependency Files
First, compile your project with dependency generation enabled:

```bash
# Using the example project
cd examples/simple_plugins
make

# Or manually with clang/gcc
clang++ -MMD -c src/main.cpp -o src/main.o
clang++ -MMD -c src/utils.cpp -o src/utils.o
```

### 2. Run Singleston
```bash
# Using the installed console command
singleston examples/simple_plugins/srcs/*.d -o amalgamated.cpp

# Or using the script directly
./scripts/singleston.py examples/simple_plugins/srcs/*.d -o amalgamated.cpp

# With verbose output and file separators
singleston examples/simple_plugins/srcs/*.d -o amalgamated.cpp --verbose --add-separators
```

### 3. Compile the Result
```bash
# Compile the amalgamated file
clang++ -O2 amalgamated.cpp -o final_executable
```

## 🚀 Installation

### From PyPI
```bash
pip install singleston
```

### From Source
```bash
git clone https://github.com/ChuOkupai/singleston
cd singleston
pip install -e .
```

## 🔧 Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/ChuOkupai/singleston
cd singleston

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Building and Publishing
```bash
# Build distribution packages
make build
# or
python -m build

# Upload to TestPyPI (for testing)
make upload-test

# Upload to PyPI (for release)
make upload
```

## 🛠️ Usage

### Synopsis
```
singleston [-o OUTPUT_FILE] [-v|--verbose] [--add-separators] [--follow-symlinks] DEPS_FILE [DEPS_FILE...]
```

### Options
- `-o OUTPUT_FILE`: Output file path (default: stdout)
- `-v, --verbose`: Enable verbose output for debugging
- `-h, --help`: Show help message and exit
- `--add-separators`: Add file boundary markers in output
- `--follow-symlinks`: Follow symbolic links in include paths

### Arguments
- `DEPS_FILE`: One or more compiler-generated dependency files (`.d` format from gcc/clang `-MMD`)

### Examples

```bash
# Basic usage with the console command
singleston examples/simple_plugins/srcs/*.d -o export.cpp

# Using the script directly
./scripts/singleston.py examples/simple_plugins/srcs/*.d -o export.cpp

# Complex project with verbose output
singleston src/*.d lib/*.d -o amalgamated.cpp --verbose

# Debug mode with file separators
singleston examples/simple_plugins/srcs/*.d --add-separators --verbose

# Handle symlinked includes
singleston examples/simple_plugins/srcs/*.d -o output.cpp --follow-symlinks
```

## 🎯 Example Project

The repository includes a complete example project in `examples/simple_plugins/`:

```bash
# Build the example project
cd examples/simple_plugins
make

# Amalgamate the project (using console command)
cd ../..
singleston examples/simple_plugins/srcs/*.d -o example_export.cpp --verbose

# Or from within the project directory
cd examples/simple_plugins
singleston srcs/*.d -o example_export.cpp --verbose

# Verify the amalgamated file compiles
clang++ -O2 example_export.cpp -o example_executable
./example_executable
```

## 🎯 Use Cases

### 📚 Single-Header Libraries
Convert multi-file C++ libraries into single-header distributions

### 🚀 Performance Optimization
Reduce compilation times by eliminating include overhead

### 📦 Code Distribution
Package entire projects into single files for easy sharing

### 🛠️ Build System Integration
Integrate into existing build systems and CI/CD pipelines

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python -m unittest discover tests/

# Run with coverage
make coverage
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `error: dependency file not found`
```bash
# Solution: Ensure you've compiled with -MMD first
cd examples/simple_plugins && make
```

**Issue**: `error: cannot read dependency file (permission denied)`
```bash
# Solution: Check file permissions
chmod 644 examples/simple_plugins/srcs/*.d
```

**Issue**: Missing system includes in output
```bash
# Solution: Use verbose mode to debug include processing
./scripts/singleston.py examples/simple_plugins/srcs/*.d --verbose
```

## 🤝 Contributing

Contributions are welcome! We're especially interested in:

- **Language support**: Help add support for Python, Java, Rust, Go, and other languages
- **Feature improvements**: Better dependency analysis, optimization features
- **Bug fixes**: Help improve reliability and edge case handling

### Development Notes

- **Code Style**: This project uses `.editorconfig` for consistent formatting
- **AI Generated**: Much of the codebase contains AI-generated code - feel free to improve and refactor
- **Testing**: Please include tests for new features

### Development Setup
```bash
# Clone the repository
git clone https://github.com/ChuOkupai/singleston
cd singleston

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
make test

# Check code quality
make lint
```

## 🌍 Community & Contributing

**More languages needed!** While singleston currently supports C and C++ projects, we encourage the community to contribute support for additional programming languages. Whether it's Python, Java, Rust, or any other language - your contributions are welcome!

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
