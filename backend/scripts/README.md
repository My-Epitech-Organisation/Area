# Django Linting Scripts

This folder contains scripts to maintain code quality in the AREA project Django backend.

## 📋 Contents

- `lint-check.sh` - Code verification script (read-only)
- `lint-fix.sh` - Auto-correction script
- `README.md` - This documentation

## 🚀 Installation

### 1. Install development dependencies

```bash
# From the backend/ folder
pip install -r requirements-dev.txt
```

### 2. Verify configuration

Tools are configured via `.flake8` and `pyproject.toml` in the backend folder.

## 🔧 Usage

### Complete code verification (read-only)

```bash
# Check entire project
./scripts/lint-check.sh

# Check specific module
./scripts/lint-check.sh users/

# Check specific file
./scripts/lint-check.sh users/models.py
```

### Auto-correction

```bash
# Fix entire project
./scripts/lint-fix.sh

# Fix specific module
./scripts/lint-fix.sh automations/

# Fix specific file
./scripts/lint-fix.sh users/views.py
```

## 🔍 Tools Used

### 🎨 Automatic Formatting
- **Black**: Python code formatting (PEP 8)
- **isort**: Import sorting and organization

### 📏 Style Checking
- **flake8**: Style checking and error detection
  - Plugins: `flake8-django`, `flake8-bugbear`, `flake8-comprehensions`

### 🔍 Static Analysis
- **bandit**: Security analysis

## ⚙️ Configuration

### Automatic Exclusions
Tools automatically ignore:
- `migrations/` - Django-generated files
- `__pycache__/` - Python cache
- `venv/` - Virtual environment
- `.mypy_cache/` - mypy cache
- `reports/` - Generated reports

### Main Settings
- **Line length**: 88 characters (Black standard)
- **Python version**: 3.13
- **isort profile**: Black compatible

## 🎯 Return Codes

The `lint-check.sh` script uses binary return codes:

- `0`: Everything compliant ✅
- `1`: Formatting issues (auto-fixable) 🎨
- `2`: Style issues (manual) 📏
- `8`: Security issues (manual) 🔒

Codes can combine (e.g., `3` = formatting + style).

## 📊 Example Output

### Successful verification
```
🔍 Django Backend Code Quality Check
========================================
🐍 Activating virtual environment...
📂 Checking: .

🎨 Checking code formatting with Black...
✅ Black formatting: PASSED

📚 Checking import sorting with isort...
✅ Import sorting: PASSED

📏 Checking code style with flake8...
✅ Code style: PASSED

🔒 Checking security with bandit...
✅ Security check: PASSED

========================================
🎉 All checks passed! Your code is clean.
```

### Verification with errors
```
❌ Black formatting: FAILED
Run './scripts/lint-fix.sh' to auto-format your code

❌ Import sorting: FAILED
Run './scripts/lint-fix.sh' to auto-sort your imports

❌ Code style: FAILED
Please fix the style issues reported above
```

## 🛠️ Troubleshooting

### Error: "Virtual environment not found"
```bash
# Create and configure venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Error: "Development dependencies not found"
The script automatically installs missing dependencies.

### Slow performance on large projects
```bash
# Use specific paths
./scripts/lint-check.sh users/models.py
./scripts/lint-fix.sh automations/
```

## 🚀 IDE Integration

### VS Code
Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.linting.flake8Enabled": true
}
```

### PyCharm
1. File → Settings → Tools → External Tools
2. Add scripts as external tools

## 📝 Recommended Workflow

1. **Before commit**:
   ```bash
   ./scripts/lint-fix.sh
   ./scripts/lint-check.sh
   ```

2. **During development**:
   ```bash
   # Frequent auto-correction
   ./scripts/lint-fix.sh users/
   ```

3. **Before push**:
   ```bash
   # Complete verification
   ./scripts/lint-check.sh
   ```

## 🔄 Updates

To update tools:
```bash
pip install -r requirements-dev.txt --upgrade
```

## 📚 Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [bandit Documentation](https://bandit.readthedocs.io/)

## 🤝 Contributing

When adding new Django modules:
1. Add module to `known_first_party` in `pyproject.toml`
2. Test with `./scripts/lint-check.sh module_name/`
3. Adjust exclusions in `.flake8` if necessary