# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ProjectBlueprint is a Python project template generator that creates new projects from pre-configured templates. It provides multiple project templates (FastAPI, Django, database, pre-commit hook, Python package, web scraper) with standardized configurations, pre-commit hooks, and uv dependency management.

## Core Architecture

### Template Generation Flow

The project generation process follows this sequence:

1. **User Input** (`_generate.py:main()`) - Prompts for project name and description
2. **Template Selection** (`_generate_scripts/pick_template.py`) - User selects from available templates in `_templates/`
3. **Modification Generation** (`_generate_scripts/generate_modifications.py`) - Creates substitution dictionary with:
   - `project_name` - Original CamelCase name
   - `project_name_low` - snake_case version
   - `script_name` - kebab-case version
   - `description` - User-provided description
   - `year` - Current year for LICENSE
4. **File Copying** (`_generate_scripts/copy.py`) - Recursively copies files from:
   - Selected template directory
   - Root directory (shared files)
   - Performs template variable substitution on modified files
5. **Project Restructuring** (`_generate_scripts/create_project_folder.py`) - Moves `src/` to `{project_name_low}/`

### Template Variable Substitution

Files in the `modified` tuple undergo string interpolation using Python's `string.Template`:
- `pyproject.toml` - Project metadata and dependencies
- `.pre-commit-config.yaml` - Replaces `$project_name_low` in import reorder args
- `Dockerfile`, `LICENSE`, `README.md`, `__main__.py` - Project-specific content

**Template Syntax**: Uses `$variable` or `${variable}` (not `{variable}`)

**Available Variables**:
- `$project_name` - Original CamelCase name
- `$project_name_low` - snake_case version
- `$script_name` - kebab-case version
- `$project_script_name` - Dotted path format
- `$description` - User-provided description
- `$year` - Current year for LICENSE

**Additional substitutions** injected by `copy.py`:
- `$pydantic_extra` - Pydantic with mypy extras (`"pydantic[mypy]>=2.11.3"`)
- `$anti_magic_formatting` - Black and reorder-python-imports commands
- `$config_parser` - Git dependency reference (`"config-parser @ git+https://github.com/Tesla2000/ConfigParser"`)
- `$utility_functions` - Git dependency reference (`"utility-functions @ git+https://github.com/Tesla2000/UtilityFunctions"`)

### Available Templates

Each template in `_templates/` contains a complete project structure:

- **default** - Basic Python project with uv, pre-commit, pydantic, toml
- **fast_api** - FastAPI server with pytest, gunicorn, client/service structure
- **django** - Django web application
- **database** - Database integration with docker-compose
- **pre_commit_hook** - Custom pre-commit hook package with `.pre-commit-hooks.yaml`
- **python_package** - Minimal package for PyPI with GitHub Actions version bumping
- **web_scraper** - Web scraping project with langchain

## Development Commands

### Initial Setup

```bash
make setup
```

Runs the complete setup sequence:
1. `uv sync` - Install dependencies with uv
2. `git init` - Initialize git repository
3. `pre-commit install --hook-type pre-commit --hook-type pre-push` - Install pre-commit hooks
4. `pre-commit autoupdate` - Update hook versions
5. `git add . && git commit -m "initial commit"` - Initial commit

### Individual Setup Steps

```bash
# Install dependencies only
make uv

# Install pre-commit hooks only
make precommit_install

# Initialize git only
make git_init

# Create initial commit only
make git_add
```

### Generating a New Project

```bash
python _generate.py
```

Interactive prompts:
1. Project name (creates directory at `/home/m-j-panie/work/{project_name}`)
2. Project description (or reuses from `answers.json` if previous run failed)
3. Template selection (0-6 corresponding to template index)

On failure, saves answers to `answers.json` for retry and removes partial project directory.

### Working with uv in Generated Projects

After generating a project, you can use these uv commands:

```bash
# Install all dependencies
uv sync

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Add an optional dependency group
uv add --optional test pytest

# Remove a dependency
uv remove package-name

# Update dependencies
uv lock --upgrade

# Run a command in the virtual environment
uv run python script.py

# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### Pre-commit Hooks

The `.pre-commit-config.yaml` configures strict code formatting:

```bash
# Run hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

Active hooks (in order):
1. **black** - Code formatting (79 char line length, preview mode)
2. **reorder-python-imports** - Import sorting with `from __future__ import annotations`
3. **autoflake** - Remove unused imports
4. **static_marker** - Mark static methods
5. **import_rules_enforcer** - Enforce import conventions
6. **flake8** - Linting (ignores E203, W503, E501, E704)

Commented-out hooks (available but disabled):
- TupleNamer (pre-push)
- FunctionSplitter (pre-push)

## Code Style Conventions

- **Line length**: 79 characters (enforced by black)
- **Python version**: 3.11+ (default template), 3.10+ (django template), 3.9+ (python_package template)
- **Import order**: Enforced by reorder-python-imports with `from __future__ import annotations` at top
- **Type hints**: Pydantic models preferred for configuration
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Dependency management**: Uses uv with standard PEP 621 `[project]` table in pyproject.toml

## Important Implementation Notes

- All templates use **uv** for dependency management with standard PEP 621 pyproject.toml format
- Template variables use dollar sign syntax: `$project_name`, `$description`, etc. (Python's `string.Template`)
- The `copy()` function recursively processes directories, using `Template.safe_substitute()` on files in the `modified` tuple
- Project name transformations:
  - `CamelCase` → `snake_case` (regex in `generate_modifications.py:_to_snake()`)
  - Used for package names and directory structure
- pyproject.toml format:
  - Uses `[project]` table instead of `[tool.poetry]`
  - Dependencies use PEP 440 version specifiers (>=) instead of Poetry caret (^)
  - Build backend is `hatchling` instead of `poetry-core`
  - Optional dependencies use `[project.optional-dependencies]` (e.g., test, deployment groups in FastAPI template)
  - Scripts use `[project.scripts]` instead of `[tool.poetry.scripts]`
  - Git dependencies use PEP 440 format: `"pkg @ git+https://..."`
- The FastAPI template includes separate `clients/`, `services/`, `utils/`, `tests/` directories
- The python_package template includes GitHub Actions workflow for automatic version bumping on main branch merges using sed/awk instead of poetry version