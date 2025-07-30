.PHONY: help install install-dev test lint format clean build upload upload-test dist check-dist

help:			## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:		## Install the package
	pip install -e .

install-dev:		## Install in development mode with dev dependencies
	pip install -e ".[dev]"

test:			## Run tests
	python -m pytest tests/ -v

test-coverage:		## Run tests with coverage
	python -m pytest tests/ --cov=nerdman --cov-report=html --cov-report=term

lint:			## Run linting
	flake8 nerdman.py tests/
	mypy nerdman.py

format:			## Format code
	black nerdman.py tests/

clean:			## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

build:			## Build the package
	python -m build

check-dist:		## Check the distribution
	python -m twine check dist/*

upload-test:		## Upload to Test PyPI
	python -m twine upload --repository testpypi dist/*

upload:			## Upload to PyPI
	python -m twine upload dist/*

dist: clean build check-dist	## Build and check distribution

demo:			## Run the demo
	python nerdman.py

cheat:			## Generate HTML cheatsheet
	python nerdman.py cheat

version:		## Show version info
	python nerdman.py version

update:			## Update Nerd Fonts data
	python nerdman.py update
