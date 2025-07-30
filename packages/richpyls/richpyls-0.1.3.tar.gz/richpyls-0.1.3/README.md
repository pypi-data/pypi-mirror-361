# `richpyls` - A Python Implementation of the Unix `ls` Command

[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/lpozo/richpyls/ci.yml?branch=main&label=CI%2FCD&logo=github)](https://github.com/lpozo/richpyls/actions)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

<!-- Commented out until package is published to PyPI
[![Test Coverage](https://img.shields.io/codecov/c/github/lpozo/richpyls?logo=codecov)](https://codecov.io/gh/lpozo/richpyls)
[![PyPI Version](https://img.shields.io/pypi/v/richpyls?logo=pypi)](https://pypi.org/project/richpyls/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/richpyls?logo=pypi)](https://pypi.org/project/richpyls/)
-->

A modern, type-annotated Python implementation of the Unix `ls` command with beautiful Rich formatting,
color-coded file types, and support for long format listings and hidden files.

## Quality Metrics

![Code Size](https://img.shields.io/github/languages/code-size/lpozo/richpyls?style=flat-square)
![Repo Size](https://img.shields.io/github/repo-size/lpozo/richpyls?style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/lpozo/richpyls?style=flat-square)

| Metric | Status |
|--------|--------|
| Test Coverage | ![Coverage Status](https://img.shields.io/badge/coverage-excellent-brightgreen.svg) |
| Type Coverage | [![mypy](https://img.shields.io/badge/mypy-100%25-brightgreen.svg)](https://mypy.readthedocs.io/) |
| Code Quality | [![Ruff](https://img.shields.io/badge/ruff-passing-brightgreen.svg)](https://github.com/astral-sh/ruff) |
| Security Scan | [![Bandit](https://img.shields.io/badge/bandit-passing-brightgreen.svg)](https://github.com/PyCQA/bandit) |
| Documentation | [![Docs](https://img.shields.io/badge/docs-100%25-brightgreen.svg)](README.md) |

## Features

- 🎨 **Rich Visual Output**: Beautiful color-coded file types with emoji icons
- 📁 **Directory Listing**: List files and directories in the current or specified path
- 📄 **Long Format**: Display detailed file information in a professional table format
- 🌳 **Tree View**: Display directories in a tree-like hierarchical format with the `-t` option
- 🔍 **Hidden Files**: Show hidden files (starting with `.`) with the `-a` option using 🫣 emoji
- 📊 **Size Sorting**: Show top N largest files/directories sorted by size with the `-s` option
- 🏃 **Fast Performance**: Built with modern Python using pathlib for efficient path operations
- 🎯 **Type Safety**: Fully type-annotated codebase with mypy validation
- ✅ **Well Tested**: Comprehensive test suite with excellent coverage
- 🐍 **Modern Python**: Uses Python 3.13+ features and best practices

## File Type Icons

The Rich output includes beautiful emoji icons for different file types:

- 🐍 Python files (`.py`, `.pyx`, `.pyi`)
- ⚙️ Configuration files (`.toml`, `.json`, `.yaml`, `.yml`, `.ini`, `.cfg`, `.conf`)
- 📄 Documentation files (`.md`, `.rst`, `.txt`, `.doc`, `.docx`, `.pdf`)
- 📦 Archive files (`.zip`, `.tar`, `.gz`, `.bz2`, `.xz`, `.7z`, `.rar`)
- 🖼️ Image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.ico`)
- 📁 Directories
- ⚡ Executable files
- 🔗 Symbolic links
- 🫣 Hidden files (starting with `.`)

## Installation

### From PyPI (Recommended)

```sh
pip install richpyls
```

Once installed, you can use the `richpyls` command anywhere in your terminal.

### From Source

#### Using `uv` (recommended)

```sh
# Clone the repository
git clone https://github.com/lpozo/richpyls.git
cd richpyls

# Install with uv
uv sync

# Run the application
uv run richpyls
```

#### Using `pip`

```sh
# Clone the repository
git clone https://github.com/lpozo/richpyls.git
cd richpyls

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install in editable mode
pip install -e .

# Run the application
richpyls
```

## Usage

```sh
# List files in current directory
richpyls

# List files in specific directory
richpyls /path/to/directory

# List multiple files/directories
richpyls file1.txt directory1 file2.txt
```

### Command Options

| Option | Description |
|--------|-------------|
| `-l` | Use long listing format (shows permissions, ownership, size, date in Rich table) |
| `-a` | Show all files, including hidden files (starting with `.`) with 🫣 emoji |
| `-t` | Display directories in a tree-like format with Rich styling |
| `-s N` | Show top N files/directories sorted by size (descending) in a Rich table |
| `-la` | Combine long format with showing hidden files |
| `-tl` | Combine tree format with long listing |
| `-ta` | Combine tree format with showing hidden files |
| `-sa` | Combine size sorting with showing hidden files |

### Examples

```sh
# Basic listing with Rich icons and colors
richpyls
📄 README.md
⚙️ pyproject.toml
📁 src
📁 tests
📄 uv.lock

# Show hidden files with special emoji
richpyls -a
🫣 .git
🫣 .gitignore
🫣 .python-version
📁 .venv
📄 README.md
⚙️ pyproject.toml
📁 src
📁 tests
📄 uv.lock

# Tree format (shows directory structure with Rich styling)
richpyls -t
├── 📄 README.md
├── ⚙️ pyproject.toml
├── 📁 src
│   └── 📁 richpyls
│       ├── 🐍 __init__.py
│       └── 🐍 __main__.py
├── 📁 tests
│   ├── 🐍 __init__.py
│   └── 🐍 test_richpyls.py
└── 📄 uv.lock

# Tree format with long listing and Rich table
richpyls -tl src
└── drwxr-xr-x  5 user staff     160B Jul 11 18:34 📁 richpyls
    ├── drwxr-xr-x  4 user staff     128B Jul 11 18:34 📁 __pycache__
    │   ├── -rw-r--r--  1 user staff     622B Jul 11 18:34 📄 __init__.cpython-313.pyc
    │   └── -rw-r--r--  1 user staff   14.8KB Jul 11 18:34 📄 __main__.cpython-313.pyc
    ├── -rw-r--r--  1 user staff     452B Jul 11 18:34 🐍 __init__.py
    └── -rw-r--r--  1 user staff   12.1KB Jul 11 18:34 🐍 __main__.py
```

## Technologies

### Dependencies

- **[Python 3.13+](https://python.org)**: Modern Python with type hints and advanced features
- **[click](https://click.palletsprojects.com/)**: Command-line interface creation toolkit
- **[rich](https://rich.readthedocs.io/)**: Rich text and beautiful formatting for the terminal

### Development Dependencies

- **[pytest](https://pytest.org/)**: Testing framework for comprehensive test coverage
- **[mypy](https://mypy.readthedocs.io/)**: Static type checker for Python
- **[ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[bandit](https://github.com/PyCQA/bandit)**: Security vulnerability scanner
- **[pre-commit](https://pre-commit.com/)**: Git hooks for automated quality checks
- **[uv](https://docs.astral.sh/uv/)**: Fast Python package manager and resolver

### Build & Deployment

![Build Status](https://img.shields.io/github/actions/workflow/status/lpozo/richpyls/ci.yml?branch=main&label=Build&logo=github)
![Tests](https://img.shields.io/github/actions/workflow/status/lpozo/richpyls/ci.yml?branch=main&label=Tests&logo=pytest)

<!-- Commented out until package is published to PyPI
![PyPI Status](https://img.shields.io/pypi/status/richpyls?logo=pypi)
![Wheel](https://img.shields.io/pypi/wheel/richpyls?logo=pypi)
-->

## Development & Contributing

Contributions are welcome! Here's how you can set up the development environment and contribute:

### Setup

1. Fork the repository or clone directly:

    ```sh
    git clone https://github.com/lpozo/richpyls.git
    cd richpyls
    ```

2. Reproduce the development environment:

    ```sh
    uv sync --dev
    ```

3. Set up pre-commit hooks for code quality:

    ```sh
    uv run pre-commit install
    ```

### Running Tests

```sh
# Run all tests
uv run python -m pytest

# Run tests with verbose output
uv run python -m pytest -v

# Run tests with coverage
uv run python -m pytest --cov=richpyls
```

### Type Checking

```sh
# Check types with mypy
uv run mypy src/richpyls/

# Check all Python files
uv run mypy .
```

### Code Quality and Formatting

The project uses automated code quality tools:

```sh
# Format code with ruff
uv run ruff format .

# Lint code with ruff
uv run ruff check . --fix

# Security scan with bandit
uv run bandit -r src/
```

**Pre-commit hooks** automatically run quality checks on every commit.

### Contributing Workflow

1. **Create a feature branch**: `git checkout -b feature/amazing-feature`
2. **Make your changes**: Implement your feature or bug fix
3. **Add tests**: Ensure your changes are well-tested
4. **Run quality checks**:

   ```sh
   uv run python -m pytest          # Run tests
   uv run mypy src/richpyls/        # Type check
   uv run ruff format .             # Format code
   uv run ruff check .              # Lint code
   ```

5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all new code
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

### Project Standards

The project maintains high code quality through:

- **Type annotations**: All functions and variables are type-annotated
- **Comprehensive tests**: Excellent test coverage with edge cases
- **Clean architecture**: Well-organized code with clear separation of concerns
- **Modern Python**: Uses latest Python features and best practices
- **Rich UI**: Beautiful terminal output with colors, icons, and professional formatting

### Build & Publishing

For information about building and publishing the package, see [BUILD_PUBLISHING.md](BUILD_PUBLISHING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

### Leodanis Pozo Ramos

- GitHub: [@lpozo](https://github.com/lpozo)

---

⭐ If you found this project helpful, please give it a star!

## Acknowledgments

- Inspired by the Unix `ls` command
- Built with modern Python best practices
- Thanks to the Python community for excellent tools and libraries
- Special thanks to the [Rich](https://rich.readthedocs.io/) library for beautiful terminal output
- Development assisted by [GitHub Copilot Chat](https://github.com/features/copilot) for enhanced productivity
