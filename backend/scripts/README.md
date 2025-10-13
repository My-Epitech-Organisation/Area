# Django Code Quality Scripts (Ruff-Powered)

## 📋 Contents

- `lint-check.sh` - Lightning-fast code verification (Ruff + Bandit)
- `lint-fix.sh` - Instant auto-correction with Ruff
- `README.md` - This documentation

## 🚀 Installation

### 1. Install development dependencies

```bash
# From the backend/ folder
pip install -r requirements-dev.txt
```

### 2. Verify configuration

All tools are configured via `pyproject.toml` in the backend folder.

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

## ⚡ Tools Used

### 🚀 **Ruff** - The Ultra-Fast Python Linter & Formatter

**Ruff replaces multiple tools in one:**
- ✅ **Formatting**
- ✅ **Import sorting**
- ✅ **Linting**
- ✅ **700+ rules** built-in

**Performance:** ~0.6 seconds vs 19+ seconds with old tools!

### 🔒 **Bandit** - Security Analysis

- Advanced security issue detection
- Complements Ruff's security rules (S*)

## ⚙️ Configuration

### Automatic Exclusions

Ruff automatically ignores:

- `migrations/` - Django-generated files
- `__pycache__/` - Python cache
- `venv/` - Virtual environment
- `.mypy_cache/` - mypy cache
- `reports/` - Generated reports

### Main Settings (pyproject.toml)

- **Line length**: 88 characters
- **Python version**: 3.13
- **Rules**: E, W, F, B, C4, SIM, DJ, I, S
- **Django-specific ignores**: S104 (binding), S106 (test passwords), F401 (admin imports)

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

⚡ Checking code with Ruff (linting + formatting + imports)...
All checks passed!
✅ Ruff linting: PASSED

🎨 Checking code formatting with Ruff...
✅ Ruff formatting: PASSED

🔒 Checking security with bandit...
✅ Security check: PASSED

========================================
🎉 All checks passed! Your code is clean.
```

### Verification with errors

```bash
❌ Ruff linting: FAILED
Run './scripts/lint-fix.sh' to auto-fix your code

❌ Ruff formatting: FAILED
Run './scripts/lint-fix.sh' to auto-format your code

⚠️  Some issues require manual fixing
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
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        },
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

Install the **Ruff extension** by Astral Software.

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

- [Ruff Documentation](https://docs.astral.sh/ruff/) - Main tool
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/) - All available rules
- [Bandit Documentation](https://bandit.readthedocs.io/) - Security analysis

## 🤝 Contributing

When adding new Django modules:

1. Add module to `known_first_party` in `pyproject.toml` (Ruff isort section)
2. Test with `./scripts/lint-check.sh module_name/`
3. Adjust per-file ignores in `pyproject.toml` if necessary
