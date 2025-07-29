help:
	@echo "Available targets:"
	@echo "  clean        - Clean up generated files"
	@echo "  check        - Run all checks"
	@echo "  install-dev  - Install development dependencies"
	@echo "  lint         - Run code linting"
	@echo "  test         - Run all unit tests"
	@echo "  coverage     - Run tests with coverage report"
	@echo "  version      - Show current version"
	@echo "  build        - Build distribution packages"
	@echo "  upload       - Upload to PyPI (requires PyPI credentials)"
	@echo "  upload-test  - Upload to TestPyPI"

check: lint test

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

install-dev:
	pip install -r requirements-dev.txt

lint:
	flake8 scripts/ tests/

test:
	python3 -m unittest discover tests/ -v

coverage:
	python3 -m coverage run --source=scripts -m unittest discover tests/ -v
	python3 -m coverage report -m
	python3 -m coverage html

version:
	@python3 -c "import sys; sys.path.insert(0, 'scripts'); from version import __version__; print(f'Singleston v{__version__}')"

build:
	python3 -m build

upload:
	python3 -m twine upload dist/*

upload-test:
	python3 -m twine upload --repository testpypi dist/*

script-version:
	@python3 scripts/singleston.py --version

.PHONY: clean check help install-dev lint test coverage version build upload upload-test script-version
