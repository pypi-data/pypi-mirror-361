# GT CLI Installation Guide

## Prerequisites

- Python 3.8 or higher
- Git installed and configured
- GitHub token (for API access)

## Installation Options

### Option 1: Using pipx (Recommended)

```bash
# Install pipx if you haven't already
pip install pipx

# Install gt
pipx install gt

# Verify installation
gt --help
```

### Option 2: Using uv

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install gt as a tool
uv tool install gt

# Verify installation
gt --help
```

### Option 3: Development Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gt.git
cd gt

# Install in development mode with pipx
pipx install -e .

# Or with uv
uv tool install -e .
```

## Post-Installation Setup

1. **Set up GitHub token:**
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```
   Add this to your shell profile (.bashrc, .zshrc, etc.)

2. **First run:**
   ```bash
   # Configure default organization
   gt config
   
       # Create your first workspace
    gt repo1 repo2 -f my-workspace
   ```

## Updating

### With pipx:
```bash
pipx upgrade gt
```

### With uv:
```bash
uv tool upgrade gt
```

## Uninstalling

### With pipx:
```bash
pipx uninstall gt
```

### With uv:
```bash
uv tool uninstall gt
```

## Why pipx/uv?

- **Isolated environments**: No conflicts with other Python packages
- **System-wide availability**: `gt` command available everywhere
- **Easy updates**: Simple upgrade commands
- **Clean uninstall**: No leftover files
- **Fast installation**: Especially with uv's speed 