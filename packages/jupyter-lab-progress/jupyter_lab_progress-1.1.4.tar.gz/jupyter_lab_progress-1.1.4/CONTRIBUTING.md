# Contributing to Jupyter Lab Utils

We welcome contributions to jupyter-lab-utils! This document provides guidelines for contributing to the project.

## Getting Started

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/jupyter-lab-utils.git
   cd jupyter-lab-utils
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the code style guidelines below

3. Write or update tests for your changes

4. Run the test suite:
   ```bash
   pytest
   pytest --cov=jupyter_lab_utils --cov-report=html
   ```

5. Run code quality checks:
   ```bash
   black jupyter_lab_utils tests
   flake8 jupyter_lab_utils tests
   mypy jupyter_lab_utils
   ```

### Code Style Guidelines

- Follow PEP 8
- Use Black for code formatting
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep line length to 88 characters (Black default)

### Testing

- Write tests for all new functionality
- Ensure test coverage remains high (>90%)
- Test files should be in the `tests/` directory
- Use descriptive test names and include docstrings

### Documentation

- Update docstrings for any changed functionality
- Add examples to docstrings where helpful
- Update README.md if adding major features
- Update CHANGELOG.md following the format

## Submitting Changes

### Pull Request Process

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request on GitHub with:
   - Clear title and description
   - Reference to any related issues
   - List of changes made
   - Screenshots if UI changes are involved

3. Ensure all CI checks pass

4. Address any review feedback

### Commit Message Guidelines

- Use clear, descriptive commit messages
- Start with a verb in present tense
- Keep first line under 50 characters
- Use body for detailed explanation if needed

Example:
```
Add validation for embedding dimensions

- Implement check_embedding_shape method
- Add support for numpy arrays and lists
- Include comprehensive error messages
```

## Types of Contributions

### Bug Reports

When filing bug reports, please include:
- Python version and environment details
- Steps to reproduce the issue
- Expected vs. actual behavior
- Error messages or stack traces
- Minimal code example if applicable

### Feature Requests

For feature requests, please provide:
- Clear description of the feature
- Use case and motivation
- Example of how it would be used
- Any alternative solutions considered

### Code Contributions

We welcome:
- Bug fixes
- New validation methods
- New display components
- Performance improvements
- Documentation improvements
- Test coverage improvements

## Code Review Process

- All changes require review by maintainers
- Reviews focus on correctness, performance, and maintainability
- Be responsive to feedback and questions
- Update your PR based on review comments

## Community

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Follow the MongoDB Community Code of Conduct

## Questions?

Feel free to open an issue for:
- Questions about contributing
- Clarifications on requirements
- General discussion about features

Thank you for contributing to jupyter-lab-utils!