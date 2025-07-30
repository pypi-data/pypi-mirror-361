.PHONY: help install install-dev test lint format clean build publish

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .

test: ## Run tests
	python -m pytest tests/ -v

lint: ## Run linting
	flake8 odoo_lve/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 odoo_lve/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	black --check odoo_lve/
	mypy odoo_lve/

format: ## Format code with black
	black odoo_lve/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires TWINE_USERNAME and TWINE_PASSWORD)
	twine upload dist/*

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files 