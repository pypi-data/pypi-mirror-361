# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-07-09

### Added
- Multi-version Python build testing script (`test_build_multiversion.py`)
- Comprehensive build testing across Python 3.9, 3.10, 3.11, and 3.12
- Enhanced Makefile with `test-multi` target for multi-version testing

### Changed
- **BREAKING**: Dropped support for Python 3.8
- Updated minimum Python requirement to 3.9+ in `pyproject.toml`
- Updated GitHub Actions workflow to test Python 3.9-3.12 only
- Enhanced CI pipeline with package build testing
- Improved code quality with flake8 compliance

### Fixed
- Fixed syntax errors in test files (`test_dependency_parser.py`, `test_include_guard_removal.py`)
- Corrected unterminated f-string literals that caused test failures on older Python versions
- Removed unused imports (`typing.Optional`) for cleaner code
- Fixed duplicate imports in try/except blocks
- Corrected f-string placeholders without variables

## [1.0.1] - 2025-07-09

### Fixed
- Improved string formatting in error messages and verbose output
- Simplified f-string expressions for better readability
- Cleaned up multi-line string formatting in dependency resolution
- Enhanced code formatting consistency

## [1.0.0] - 2025-07-09

### Added
- Initial release of Singleston source file amalgamator
- Smart dependency resolution using compiler-generated `.d` files
- Support for C and C++ projects with any header extension
- Intelligent include processing:
  - Preserves system includes (`#include <system>`)
  - Removes local includes for amalgamated files
  - Deduplicates includes while preserving order
- Include guard removal for both `#pragma once` and traditional guards
- Topological sorting for proper dependency ordering
- First appearance priority for file processing
- Command-line interface with the following features:
  - Output to file (`-o`) or stdout
  - Verbose mode (`-v`, `--verbose`) for debugging
  - File boundary markers (`--add-separators`) for debugging
  - Symlink support (`--follow-symlinks`) for complex structures
- Comprehensive error handling with colored diagnostics
- Complete example project demonstrating usage
- Extensive test suite with 72+ test cases
- Build system integration with Makefile support
- PyPI package distribution
- Documentation with usage examples and troubleshooting guide

### Technical Features
- Zero configuration setup - works with standard gcc/clang `-MMD` output
- High performance processing for large codebases
- UTF-8 encoding support
- Cross-platform compatibility (Windows, macOS, Linux)
- Comprehensive path handling (absolute, relative, symlinks)
- Batch processing of multiple dependency files

### Development
- Python 3.8+ support
- Setuptools-based packaging
- Development environment with virtual environment support
- Code quality tools (flake8, unittest)
- CI/CD ready with automated testing
- MIT License

### Documentation
- Complete README with feature overview
- Quick start guide with examples
- Detailed usage instructions
- Troubleshooting section
- Contributing guidelines
- API documentation in docstrings

[Unreleased]: https://github.com/ChuOkupai/singleston/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/ChuOkupai/singleston/releases/tag/v1.0.2
[1.0.1]: https://github.com/ChuOkupai/singleston/releases/tag/v1.0.1
[1.0.0]: https://github.com/ChuOkupai/singleston/releases/tag/v1.0.0
