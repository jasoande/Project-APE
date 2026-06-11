# Contributing to Project APE

Thank you for your interest in contributing to Project APE! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Project-APE.git
   cd Project-APE
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/jasoande/Project-APE.git
   ```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 18+ (for NotebookLM CLI)
- LibreOffice (for document conversion)
- Google account (for NotebookLM)

### Installation

1. **Install Node.js** (if not already installed):
   ```bash
   # RHEL/Fedora
   curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
   sudo dnf install -y nodejs
   
   # macOS
   brew install node git
   ```

2. **Install NotebookLM CLI globally**:
   ```bash
   npm install -g notebooklm
   notebooklm --version
   ```

3. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Upgrade pip and install dependencies**:
   ```bash
   python3 -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Authenticate with NotebookLM**:
   ```bash
   notebooklm login
   ```

6. **Configure test clients**:
   - Copy `vars.py` to `vars_local.py` (gitignored)
   - Update with your test client data
   - Or use the example clients provided

## Making Changes

### Branch Naming
Use descriptive branch names:
- `feature/add-email-notifications`
- `fix/pdf-conversion-error`
- `docs/update-readme`

### Commit Messages
Follow conventional commit format:
```
type(scope): brief description

Longer description if needed

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build process or auxiliary tool changes

Examples:
```
feat(dashboard): add quality score visualization
fix(pdf): handle corrupted image files gracefully
docs(readme): update installation instructions for RHEL/Fedora
```

## Testing

### Manual Testing
1. **Single client test**:
   ```bash
   python3 main.py --mode fast --clients example_client_1
   ```

2. **Full pipeline test**:
   ```bash
   python3 main.py --mode fast
   ```

3. **Check logs**:
   ```bash
   tail -f logs/example_client_1.log
   ```

4. **Verify dashboard**:
   - Open http://localhost:8765
   - Verify real-time updates
   - Check quality scores

### Code Quality
Before submitting:
- **Syntax check**: `python3 -m py_compile yourfile.py`
- **Import check**: `python3 -c "import yourmodule"`
- **Run through pipeline**: Test with at least one client

## Submitting Changes

### Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push changes**:
   ```bash
   git push origin your-branch-name
   ```

3. **Create Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference any related issues
   - Screenshots for UI changes
   - Test results

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Changes tested locally with sample client
- [ ] Documentation updated (README, ARCHITECTURE, etc.)
- [ ] No hardcoded credentials or personal data
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with main

## Coding Standards

### Python Style
- **PEP 8** compliant
- **Type hints** for function signatures where helpful
- **Docstrings** for all public functions/classes
- **Max line length**: 100 characters

### Example Function:
```python
def process_client(client_id: str, mode: str = "fast") -> bool:
    """
    Process a single client through the pipeline.
    
    Args:
        client_id: Client identifier (e.g., 'acme_corp')
        mode: Execution mode ('fast' or 'deep')
    
    Returns:
        True if successful, False otherwise
    """
    # Implementation here
    pass
```

### File Organization
```
Project-APE/
├── core/               # Core pipeline logic
├── dashboard/          # Web dashboard
├── docs/              # Extended documentation
├── *.txt              # Prompt templates
├── main.py            # Entry point
├── vars.py            # Configuration template
└── README.md          # Primary documentation
```

### Logging
Use consistent logging levels:
- `logger.debug()` - Detailed diagnostic info
- `logger.info()` - General progress updates
- `logger.warning()` - Warnings (degraded but functional)
- `logger.error()` - Errors (requires attention)

Format: `logger.info(f"[{client_id}] Processing started")`

### Error Handling
```python
try:
    # Risky operation
    result = process_data()
except SpecificException as e:
    logger.error(f"[{client_id}] Failed to process: {e}")
    # Graceful fallback or re-raise
    return False
```

## Areas for Contribution

### High Priority
- **Error recovery**: Improve retry logic and error messages
- **Performance**: Optimize PDF consolidation for large files
- **Testing**: Add automated test suite
- **Documentation**: Expand user guides and troubleshooting

### Feature Ideas
- Email notifications on completion
- Custom prompt template system
- Multi-language support
- Cloud deployment (Docker, K8s)
- Analytics dashboard
- Quality score improvements
- Batch processing enhancements

### Bug Reports
When filing bugs, include:
- Project APE version
- Python version
- Operating system
- Complete error message/stack trace
- Steps to reproduce
- Relevant log files

## Questions?

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Jason Anderson (project owner)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Project APE!**
