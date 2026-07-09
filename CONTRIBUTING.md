<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="200"/>
  
  # Contributing to Project APE
  
  **Developer Contribution Guidelines**
</div>

---

Thank you for your interest in contributing! This guide will help you get started.

## Quick Start for Contributors

### Prerequisites

- Python 3.10+ ([Download](https://www.python.org/downloads/))
- Chrome browser
- Git
- Google account (Drive + NotebookLM access)

### Setup

1. **Fork and clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Project-APE-dev.git
   cd Project-APE-dev
   git remote add upstream https://github.com/original/Project-APE-dev.git
   ```

2. **Launch GUI (sets up environment automatically):**
   ```bash
   python3 launch-project-ape.py
   ```

3. **Authenticate services (one-time):**
   - Follow web setup wizard at http://localhost:8765/configure
   - Or manually:
     ```bash
     source ~/.project-ape-venv/bin/activate
     notebooklm login
     python3 setup-oauth-drive-improved.py
     ```

---

## The Golden Rule

**Always test changes using the GUI launcher:**

```bash
python3 launch-project-ape.py
```

Even as a developer, use the GUI launcher to test—it validates the complete user experience.

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/amazing-feature
```

### 2. Make Changes

Edit files in your preferred editor.

### 3. Test via GUI

```bash
# Launch dashboard
python3 launch-project-ape.py

# Test your changes at http://localhost:8765
# - Configuration wizard (if you changed config)
# - Workflow execution (if you changed pipeline)
# - Dashboard UI (if you changed templates)
```

### 4. Verify Outputs

```bash
# Check logs
tail -f logs/test_client.log

# Check generated files
ls -la docs_generated/test_client/

# Check status
cat .multi_process_status/test_client.json
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add amazing feature"
```

### 6. Push and Create PR

```bash
git push origin feature/amazing-feature
```

Then open a Pull Request on GitHub.

---

## Code Structure

```
project-ape/
├── core/                     # Pipeline components
│   ├── client_pipeline.py    # Main workflow executor
│   ├── drive_manager.py      # Google Drive integration
│   ├── notebook_manager.py   # NotebookLM API wrapper
│   └── ...
├── dashboard/                # Web interface
│   ├── server.py             # Flask server
│   ├── templates/            # HTML templates
│   └── static/               # CSS/JS/images
├── launch-project-ape.py     # **Primary entry point**
├── main.py                   # Multi-process orchestrator
└── Docs/                     # User documentation
```

**Key Entry Points:**
- `launch-project-ape.py` - GUI launcher (users start here)
- `main.py` - Multi-process orchestrator
- `dashboard/server.py` - Flask web server
- `core/client_pipeline.py` - Client workflow executor

---

## Adding Features

### Backend (Python/Flask)

**Add API endpoint in `dashboard/server.py`:**

```python
@app.route('/api/your-feature', methods=['POST'])
def your_feature():
    """Your feature description."""
    try:
        data = request.json
        result = do_something(data)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Frontend (HTML/JavaScript)

**Add page in `dashboard/templates/your-page.html`:**

```html
<!DOCTYPE html>
<html>
<head><title>Your Feature</title></head>
<body>
    <div id="content"></div>
    <button id="actionBtn">Do Something</button>
    <script>
        document.getElementById('actionBtn').addEventListener('click', async () => {
            const response = await fetch('/api/your-feature', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({param: 'value'})
            });
            const data = await response.json();
            alert(data.message);
        });
    </script>
</body>
</html>
```

**Register route in `dashboard/server.py`:**

```python
@app.route('/your-page')
def your_page():
    return render_template('your-page.html')
```

### Core Pipeline Module

**Add custom analyzer in `core/custom_analyzer.py`:**

```python
import logging

logger = logging.getLogger(__name__)

class CustomAnalyzer:
    def __init__(self, client_id: str, config):
        self.client_id = client_id
        self.config = config
    
    def analyze(self, notebook_id: str) -> dict:
        logger.info(f"[{self.client_id}] Running custom analysis...")
        return {'metric': 0.85}
```

---

## Testing Checklist

Before submitting PR:

- [ ] GUI launcher works without errors
- [ ] Dashboard loads correctly
- [ ] Test workflow completes (fast mode is sufficient)
- [ ] Logs show no unexpected errors
- [ ] Generated outputs are correct
- [ ] Documentation updated (if adding features)
- [ ] Code follows style guide (see below)

---

## Code Standards

### Python (PEP 8)

```python
from typing import Dict, List, Optional

class ClientProcessor:
    """Process client workflows."""
    
    def __init__(self, client_id: str, mode: str = "fast"):
        self.client_id = client_id
        self.mode = mode
    
    def process(self, force_refresh: bool = False) -> Dict[str, any]:
        """Execute pipeline for this client."""
        pass
```

**Formatting:**
- Use 4 spaces (no tabs)
- Max line length: 100 characters
- snake_case for functions/variables
- PascalCase for classes
- Type hints for function signatures

**Linting:**
```bash
pip install black flake8
black core/ dashboard/
flake8 core/ dashboard/ --max-line-length=100
```

### JavaScript (ES6+)

```javascript
// Use const/let, avoid var
const fetchStatus = async () => {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Failed:', error);
    }
};

// No jQuery - use vanilla JavaScript
```

### Shell Scripts (Bash)

```bash
#!/bin/bash
set -euo pipefail

CLIENT_ID="${1:-}"
MODE="${2:-fast}"

if [[ -z "${CLIENT_ID}" ]]; then
    echo "Error: CLIENT_ID required" >&2
    exit 1
fi
```

---

## Documentation Standards

### Python Docstrings (Google Style)

```python
def process_client(client_id: str, mode: str, refresh: bool = False) -> dict:
    """
    Process a single client through the pipeline.
    
    Args:
        client_id: Unique client identifier
        mode: Execution mode ('fast' or 'deep')
        refresh: Force Drive cache refresh
    
    Returns:
        Dict with 'success', 'quality_score', 'notebook_id'
    
    Raises:
        AuthenticationError: If NotebookLM credentials invalid
    
    Example:
        >>> result = process_client('acme', 'fast')
        >>> print(result['quality_score'])
        8
    """
    pass
```

### Markdown

- Use ATX-style headers (`#`, `##`, `###`)
- Include code blocks with language identifiers
- Add examples for new features
- Keep line length reasonable (< 120 chars)

---

## Pull Request Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing Performed

- [ ] Tested via GUI launcher
- [ ] Workflow completed successfully
- [ ] Dashboard displays correctly
- [ ] Documentation updated

## Screenshots

(Add screenshots for UI changes)
```

---

## Getting Help

- **Documentation**: Check [Docs/](Docs/) first
- **Issues**: Search [GitHub Issues](https://github.com/yourusername/Project-APE-dev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Project-APE-dev/discussions)

---

## License

By contributing, you agree your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Project APE!**

<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE" width="100"/>
</div>
