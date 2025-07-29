# DevCtx - Development Context Creator

A powerful CLI tool for creating temporary monorepos from GitHub repositories with intelligent fuzzy matching and branch management.

## Features

- 🚀 **Fast Setup**: Create workspaces with multiple repositories in seconds
- 🔍 **Intelligent Fuzzy Matching**: Handles typos with helpful suggestions
- 🌿 **Branch Management**: Checkout existing branches or create new ones
- 📝 **Smart Caching**: Remembers repository lists to speed up subsequent runs
- 🎨 **Beautiful Output**: Rich, colorful interface with progress indicators
- ⚙️ **Configurable**: Set default organizations and cache preferences

## Installation

### Option 1: Using pipx (Recommended)

```bash
# Install pipx if you haven't already
pip install pipx

# Install devctx
pipx install devctx

# Verify installation
devctx --help
```

### Option 2: Using uv

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install devctx as a tool
uv tool install devctx

# Verify installation
devctx --help
```

### Option 3: Development Installation

```bash
# Clone the repository
git clone https://github.com/PragmaticMachineLearning/devctx.git
cd devctx

# Install in development mode with pipx
pipx install -e .

# Or with uv
uv tool install -e .
```

## Quick Start

1. **Set up your GitHub token:**
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```

2. **Create your first workspace:**
   ```bash
   devctx create repo1 repo2 --org YourOrg --folder my-workspace
   ```

3. **Set a default organization (optional):**
   ```bash
   devctx config --set-org YourOrg
   ```

## Usage

### Basic Commands

```bash
# Create a workspace with multiple repositories
devctx create indicore workflows --org IndicoDataSolutions --folder my-workspace

# Use short flags for convenience
devctx create indicore workflows -o IndicoDataSolutions -f my-workspace

# Create workspace with specific branch
devctx create indicore workflows -o IndicoDataSolutions -f feature-branch -b develop

# Create workspace and new branch in all repos
devctx create indicore workflows -f new-feature --create-branch feature/awesome-thing

# List repositories in an organization
devctx list-repos IndicoDataSolutions

# View and modify configuration
devctx config
devctx config --set-org IndicoDataSolutions
```

### Common Use Cases

#### 1. Quick Development Setup
```bash
# Set default org once
devctx config --set-org YourOrganization

# Then create workspaces quickly
devctx create frontend backend database -f full-stack-dev
```

#### 2. Feature Development
```bash
# Create workspace on specific branch
devctx create app api -f feature-work -b develop

# Or create new feature branch across all repos
devctx create app api -f new-feature --create-branch feature/user-auth
```

#### 3. Bug Investigation
```bash
# Create workspace for investigating issues
devctx create service1 service2 logs -f bug-investigation -b hotfix
```

#### 4. Code Review
```bash
# Create workspace to review a specific PR branch
devctx create backend frontend -f pr-review -b pr/123-new-feature
```

## Configuration

DevCtx stores configuration in `~/.config/devctx/config.json`. You can manage it using the config command:

```bash
devctx config                    # View current configuration
devctx config --set-org MyOrg   # Set default organization
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `default_org` | `null` | Default GitHub organization to use |
| `repo_cache_duration_days` | `30` | How long to cache repository lists (in days) |
| `repo_cache` | `{}` | Internal cache storage (managed automatically) |

### Configuration File Format

```json
{
  "default_org": "IndicoDataSolutions",
  "repo_cache_duration_days": 30,
  "repo_cache": {
    "IndicoDataSolutions": {
      "repos": ["indicore", "workflows", "cyclone"],
      "last_updated": "2024-01-15T10:30:00Z"
    }
  }
}
```

## Command Reference

### `devctx create`

Create a new workspace with specified repositories.

```bash
devctx create REPO1 REPO2 ... [OPTIONS]
```

**Options:**
- `--org, -o`: GitHub organization name
- `--folder, -f`: Workspace folder name (auto-generated if not provided)
- `--branch, -b`: Branch to checkout in all repositories
- `--create-branch, -c`: Create new branch in all repositories
- `--refresh-cache`: Force refresh of repository cache

**Examples:**
```bash
devctx create app api docs -o myorg -f workspace
devctx create frontend -f ui-work -b develop
devctx create backend -f hotfix --create-branch hotfix/critical-bug
```

### `devctx list-repos`

List all repositories in a GitHub organization.

```bash
devctx list-repos ORGANIZATION [OPTIONS]
```

**Options:**
- `--refresh-cache`: Force refresh of repository cache

**Example:**
```bash
devctx list-repos IndicoDataSolutions --refresh-cache
```

### `devctx config`

View or modify configuration settings.

```bash
devctx config [OPTIONS]
```

**Options:**
- `--set-org ORG`: Set default organization

**Examples:**
```bash
devctx config                           # View current config
devctx config --set-org MyOrganization  # Set default org
```

## Fuzzy Matching

DevCtx includes intelligent fuzzy matching that helps when you make typos:

```bash
# Typo: "workflws" instead of "workflows"
devctx create indicore workflws -f test

# DevCtx will show:
# Multiple matches found for "workflws":
# 1. workflows (score: 89%)
# 2. workflex (score: 45%)
# Select repository [1-2]: 1
```

The fuzzy matching:
- Automatically selects exact matches
- Prompts for confirmation on close matches (>70% similarity)
- Shows multiple options for ambiguous cases
- Handles multiple typos in one command

## Branch Management

DevCtx provides flexible branch management:

### Checkout Existing Branch
```bash
devctx create repo1 repo2 -f workspace -b feature-branch
```

If the branch doesn't exist in a repository, DevCtx will:
1. Show a warning
2. Fall back to the repository's default branch
3. Continue with other repositories

### Create New Branch
```bash
devctx create repo1 repo2 -f workspace --create-branch feature/new-feature
```

DevCtx will:
1. Create the branch from each repository's default branch
2. Handle creation failures gracefully
3. Report success/failure for each repository

## Troubleshooting

### Common Issues

#### 1. "GITHUB_TOKEN not found"
**Problem:** GitHub token not set in environment.

**Solution:**
```bash
export GITHUB_TOKEN=your_token_here
# Add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
```

#### 2. "Permission denied" errors
**Problem:** GitHub token doesn't have necessary permissions.

**Solutions:**
- Ensure token has `repo` scope for private repositories
- Use `public_repo` scope for public repositories only
- Check if you have access to the organization

#### 3. "Repository not found"
**Problem:** Repository doesn't exist or you don't have access.

**Solutions:**
- Verify repository name spelling
- Check organization name
- Ensure your GitHub token has access to the repository
- Use `devctx list-repos ORGANIZATION` to see available repositories

#### 4. "Branch not found"
**Problem:** Specified branch doesn't exist.

**Solutions:**
- DevCtx will automatically fall back to the default branch
- Check branch name spelling
- Verify the branch exists in the repository

#### 5. "Folder already exists"
**Problem:** Workspace folder already exists.

**Solutions:**
- Use a different folder name with `-f other-name`
- Remove existing folder: `rm -rf existing-folder`
- DevCtx will prompt for confirmation before overwriting

#### 6. Git clone failures
**Problem:** Network issues or authentication problems.

**Solutions:**
- Check internet connection
- Verify GitHub token is valid
- Try refreshing cache with `--refresh-cache`
- Check if repositories are private and you have access

### Debug Tips

1. **Use `--refresh-cache`** to force fresh repository data
2. **Check config** with `devctx config` to verify settings
3. **Test with public repos** first to verify setup
4. **Use `devctx list-repos ORG`** to verify repository access

### Getting Help

- Run `devctx --help` for general help
- Run `devctx COMMAND --help` for command-specific help
- Check the [GitHub Issues](https://github.com/PragmaticMachineLearning/devctx/issues) for known problems
- File a bug report if you encounter new issues

## Development

### Setup
```bash
git clone https://github.com/PragmaticMachineLearning/devctx.git
cd devctx

# Install in development mode
pipx install -e .

# Or with uv
uv tool install -e .
```

### Running Tests
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests to ensure everything works
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues or have questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Search [existing issues](https://github.com/PragmaticMachineLearning/devctx/issues)
3. Create a new issue if needed

## Changelog

### 0.1.0
- Initial release
- Basic workspace creation
- Fuzzy matching for repository names
- Branch management
- Configuration system
- Repository caching 