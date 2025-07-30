# Contributing to Mind Metrics

Thank you for your interest in contributing to Mind Metrics! This document provides guidelines for contributing to the project.

## Development Workflow

We use a **GitFlow-inspired** branching strategy with the following conventions:

### Branch Strategy

- **`main`**: Production-ready code, protected branch
- **`develop`**: Integration branch for features (optional)
- **`feature/*`**: Feature development branches
- **`bugfix/*`**: Bug fix branches
- **`hotfix/*`**: Critical fixes for production

### Branch Naming Convention

- `feature/issue-number-short-description`
- `bugfix/issue-number-bug-description`
- `hotfix/critical-issue-description`

Examples:
- `feature/3-data-loading-module`
- `bugfix/7-cli-argument-parsing`
- `hotfix/memory-leak-visualization`

## Issue → Merge Request Workflow

### 1. Create an Issue

Before starting work:
1. Check existing issues to avoid duplication
2. Create a new issue with:
   - Clear title and description
   - Acceptance criteria
   - Labels (bug, feature, enhancement, documentation)
   - Assignee
   - Milestone (if applicable)

### 2. Create Feature Branch

```bash
# Checkout main and pull latest changes
git checkout main
git pull origin main

# Create and checkout feature branch
git checkout -b feature/issue-number-description
```

### 3. Development Process

1. **Make atomic commits** with meaningful messages
2. **Follow commit message convention** (see below)
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Ensure code quality** (linting, type checking)

### 4. Create Merge Request

1. Push your branch to GitLab
2. Create a Merge Request with:
   - Clear title referencing the issue
   - Description linking to the issue (`Closes #issue-number`)
   - Screenshots/examples if applicable
   - Request reviews from team members

### 5. Review Process

- **All merge requests require at least 1 approval**
- Address review comments promptly
- Update tests and documentation as requested
- Ensure CI pipeline passes

### 6. Merge to Main

- Use **"Merge commit"** strategy
- Delete feature branch after merge
- Create version tag for main branch commits

## Commit Message Convention

We follow the **Conventional Commits** specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(data): add support for Excel file loading

Implement pandas-based Excel file reader with support for .xlsx and .xls formats.
Includes data validation and error handling for malformed files.

Closes #3
```

```
fix(cli): resolve argument parsing issue with --source flag

The --source argument was not properly handling URLs with query parameters.
Updated click option configuration to accept full URLs.

Fixes #7
```

```
docs: update README with installation instructions

Add comprehensive installation guide including pip and source installation methods.
Include examples for common use cases.
```

## Code Standards

### Python Code Style

- **PEP 8** compliance (enforced by `ruff`)
- **Type hints** for all functions and methods
- **Docstrings** for all public functions, classes, and modules
- **Maximum line length**: 88 characters (Black standard)

### Code Quality Tools

We use the following tools (run automatically in CI):

```bash
# Code formatting
uv run black mind_metrics/ tests/

# Linting
uv run ruff check mind_metrics/ tests/

# Type checking
uv run mypy mind_metrics/

# Import sorting
uv run isort mind_metrics/ tests/
```

### Testing Requirements

- **Minimum 80% code coverage**
- **Unit tests** for all functions and methods
- **Integration tests** for CLI commands
- **Test data** should be minimal and not include real personal data

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Type hints**: All function parameters and return values
- **Comments**: Explain complex logic, not obvious code
- **README**: Keep updated with new features

## Setting Up Development Environment

### Prerequisites

- Python 3.9 or higher
- `uv` package manager
- Git

### Setup Steps

```bash
# Clone repository
git clone https://gitlab.com/your-team/mind-metrics.git
cd mind-metrics

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Verify setup
uv run pytest
```

### IDE Configuration

#### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- GitLens

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

#### PyCharm

Configure:
- Interpreter: `.venv/bin/python`
- Code style: Black
- Linter: Ruff
- Test runner: pytest

## Testing Guidelines

### Test Structure

```
tests/
│   ├── conftest.py
│   ├── integration/
│   │   ├── test_cli.py
│   │   └── test_end_to_end.py
│   └── unit/
│       ├── test_burnout_analyzer.py
│       ├── test_data_cleaner.py
│       ├── test_data_loader.py
│       └── test_validation.py
```

### Writing Tests

```python
import pytest
from mind_metrics.data.loader import DataLoader

class TestDataLoader:
    """Test suite for DataLoader class."""
    
    def test_load_csv_file_success(self, sample_csv_path):
        """Test successful CSV loading."""
        loader = DataLoader()
        data = loader.load(sample_csv_path)
        
        assert data is not None
        assert len(data) > 0
        assert 'EmployeeID' in data.columns
    
    def test_load_invalid_file_raises_error(self):
        """Test that invalid file raises appropriate error."""
        loader = DataLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_file.csv")
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_data_loader.py

# Run tests with specific marker
uv run pytest -m "not slow"
```

## Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

### Version Tagging

Tags are created automatically for main branch commits:

- Development versions: `v0.1.0`, `v0.2.0`, ...
- Release candidates: `v1.0.0-rc1`, `v1.0.0-rc2`
- Stable releases: `v1.0.0`, `v1.1.0`, `v2.0.0`

## Review Guidelines

### For Authors

- **Self-review** your code before requesting review
- **Provide context** in the MR description
- **Keep MRs focused** on a single issue/feature
- **Respond promptly** to review feedback

### For Reviewers

- **Be constructive** and respectful
- **Focus on** code quality, design, and maintainability
- **Ask questions** rather than making demands
- **Approve promptly** when requirements are met

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No obvious bugs or issues
- [ ] Performance considerations addressed
- [ ] Security implications considered

## Communication Channels

- **GitLab Issues**: Feature requests, bug reports, discussions
- **Merge Requests**: Code reviews, technical discussions
- **Team Meetings**: Weekly sync-ups, planning sessions
- **Slack/Discord**: Quick questions, daily communication

## Team Responsibilities

### Lead Developer (Person A)
- Project architecture decisions
- Code reviews and final approvals
- CI/CD pipeline maintenance
- Release management

### Developer B
- Data processing and visualization features
- Performance optimization
- Algorithm implementation
- Documentation

### Developer C
- Testing and quality assurance
- CLI interface development
- Bug fixes and maintenance
- User experience improvements

## Getting Help

- **Documentation**: Check project docs first
- **Issues**: Search existing issues for solutions
- **Team Members**: Tag appropriate team members in issues
- **Community**: Reach out via established communication channels

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation
- Annual contributor highlights

Thank you for contributing to Mind Metrics! 🚀