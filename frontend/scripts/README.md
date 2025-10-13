# Frontend Linting Scripts

This directory contains scripts for code quality checks and auto-fixes for the React frontend.

## Available Scripts

### `lint-check.sh`

Runs all linting and formatting checks:
- ESLint for TypeScript/JavaScript
- Stylelint for CSS
- Prettier for code formatting

This script will exit with a non-zero code if any issues are found.

### `lint-fix.sh`

Automatically fixes code quality issues:
- Fixes ESLint issues where possible
- Fixes Stylelint issues where possible
- Applies Prettier formatting

## Usage

From the frontend directory:

```bash
# Check code quality
./scripts/lint-check.sh

# Auto-fix issues
./scripts/lint-fix.sh
```

## Integration

These scripts follow the same pattern as the linting scripts in the mobile and backend
parts of the project for consistency across the codebase.