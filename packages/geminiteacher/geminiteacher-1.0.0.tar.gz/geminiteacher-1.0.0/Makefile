# ==============================================================================
# GeminiTeacher Makefile
#
# Primary Commands:
#   install       - Set up the development environment.
#   gui           - Launch the user-friendly GUI.
#   check         - Run all code quality checks (linting, type-checking).
#   test          - Run the unit test suite.
#   build         - Build the package for distribution.
#   docs          - Serve the documentation locally for preview.
#   deploy-docs   - Deploy the documentation to GitHub Pages.
#   publish       - Publish the package to PyPI.
# ==============================================================================

.DEFAULT_GOAL := help

# --------------------- Project Setup ---------------------
.PHONY: install
install: ## Install the virtual environment and pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

# --------------------- Application ---------------------
.PHONY: gui
gui: ## Launch the GUI application
	@echo "🚀 Launching GeminiTeacher GUI"
	@uv run geminiteacher-gui

# --------------------- Quality Assurance ---------------------
.PHONY: check
check: ## Run all code quality checks (linting, type-checking, etc.)
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry src

.PHONY: test
test: ## Run the unit test suite with coverage
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest --cov --cov-config=pyproject.toml --cov-report=xml

# --------------------- Build & Publish ---------------------
.PHONY: build
build: clean-build ## Build the package wheel for distribution
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: publish
publish: ## Publish the package to PyPI (requires built wheel)
	@echo "🚀 Publishing to PyPI."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and then publish the package to PyPI

.PHONY: clean-build
clean-build: ## Clean build artifacts from the `dist` directory
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

# --------------------- Documentation ---------------------
.PHONY: docs
docs: ## Build and serve the documentation locally for preview
	@uv run mkdocs serve

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings
	@uv run mkdocs build -s

.PHONY: deploy-docs
deploy-docs: ## Deploy documentation to GitHub Pages
	@echo "🚀 Deploying documentation to GitHub Pages"
	@uv run python -m mkdocs gh-deploy

# --------------------- Help ---------------------
.PHONY: help
help:
	@echo "Available commands:"
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"
