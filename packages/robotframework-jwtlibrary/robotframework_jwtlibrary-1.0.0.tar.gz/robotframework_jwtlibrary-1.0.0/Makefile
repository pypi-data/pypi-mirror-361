.PHONY: help install install-dev test test-unit test-robot lint format clean build docs

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .

test:  ## Run all tests
	pytest tests/unit
	robot --outputdir results tests/robot/acceptance/

test-unit:  ## Run unit tests
	pytest tests/unit --cov=src/JWTLibrary --cov-report=term-missing

test-robot:  ## Run Robot Framework tests
	robot --outputdir results tests/robot/acceptance/

lint:  ## Run linting
	flake8 src tests
	mypy src/JWTLibrary
	black --check src tests
	isort --check-only src tests

format:  ## Format code
	black src tests
	isort src tests

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

docs:  ## Build documentation
	rm -rf docs/
	python3 generate.py

dev-setup:  ## Setup development environment
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/pip install -e .

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
