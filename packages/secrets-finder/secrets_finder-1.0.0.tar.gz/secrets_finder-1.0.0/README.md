# Secrets Finder

A lightweight tool to detect hardcoded secrets and PII in source code using pattern-based detection.

## Features
- Detects API keys, tokens, passwords, emails, credit cards, and more
- Customizable detection patterns
- Multiple output formats (console, JSON, HTML, PDF)
- Multi-threaded scanning for performance
- Git integration with diff-based scanning

## Installation

```bash
pip install secrets-finder
```

## Quick Start

```bash
# Scan current directory
secrets-finder scan .

# Scan specific directory
secrets-finder scan /path/to/repo

# Scan only changed files (git diff)
secrets-finder scan . --diff-only

# Output as JSON
secrets-finder scan . --output json

# See all options
secrets-finder --help
```

## Configuration

Create `.secret-scanner.yaml` in your project root:

```yaml
patterns:
  - name: "Custom API Key"
    regex: "my_api_key_[a-zA-Z0-9]{32}"
    severity: "high"

exclude:
  - "*.log"
  - "node_modules/"
  - "vendor/"

max_file_size: 10485760  # 10MB
max_workers: 8
```

## Usage Examples

```bash
# Scan specific file types
secrets-finder scan . --files "*.py,*.js"

# Generate HTML report
secrets-finder scan . --output html

# Multi-threaded scan
secrets-finder scan . --max-workers 8 --verbose

# Install pre-commit hook
secrets-finder install-hook
```

## License

MIT License