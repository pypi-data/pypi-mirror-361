.PHONY: help install install-dev test test-cov clean lint format sort-imports

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development and test dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  sort-imports - Sort imports (isort)"
	@echo "  clean        - Clean up build artifacts"

# Install production dependencies
install:
	pip install -e .

# Install development dependencies
install-dev:
	pip install -e .[dev]

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ --cov=kini --cov-report=term-missing --cov-report=html

# Run linting
lint:
	flake8 kini tests

# Format code
format:
	black kini tests

# Sort imports
sort-imports:
	isort kini tests

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete