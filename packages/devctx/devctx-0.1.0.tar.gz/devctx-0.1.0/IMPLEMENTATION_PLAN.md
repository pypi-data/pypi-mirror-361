# GT CLI Implementation Plan

## Overview
Building a CLI tool for creating temporary monorepos with multiple GitHub repositories.

## Phase 1: Foundation (Checkpoint: Basic CLI runs) ✅

### 1.1 Project Setup
- [x] Create project structure
  ```
  gt/
  ├── pyproject.toml
  ├── README.md
  ├── gt/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── config.py
  │   └── __main__.py
  ```
- [x] Set up pyproject.toml with dependencies and entry points:
  - click>=8.1.0
  - rich>=13.0.0
  - pydantic>=2.0.0
  - PyGithub>=2.1.0
  - rapidfuzz>=3.0.0
- [x] Configure entry point: `gt = "gt.cli:main"`
- [x] Create __main__.py for package execution
- [x] Add version info to __init__.py

### 1.2 Basic CLI Structure
- [x] Implement basic Click command in cli.py
- [x] Add --version flag
- [x] Add --help with rich formatting
- [x] **Checkpoint 1**: Run `gt --help` and see formatted help

## Phase 2: Configuration Management ✅

### 2.1 Config Model
- [x] Define Pydantic model for configuration:
  ```python
  class Config:
      default_org: Optional[str]
      repo_cache_duration_days: int = 30
      repo_cache: Dict[str, RepoCache]
  ```
- [x] Implement config file location (~/.config/gt/config.json)
- [x] Create config loader with defaults
- [x] Create config saver

### 2.2 Config Command
- [x] Implement `gt config` subcommand
- [x] Show current configuration with rich table
- [x] **Checkpoint 2**: Run `gt config` and see/modify configuration

## Phase 3: GitHub Integration ✅

### 3.1 GitHub Client
- [x] Create github_client.py module
- [x] Implement authentication using GITHUB_TOKEN env var
- [x] Add method to list organization repositories
- [x] Implement caching logic (check cache age, update if needed)
- [x] Handle pagination for orgs with many repos

### 3.2 Cache Management
- [x] Implement cache validation (check if older than configured duration)
- [x] Add --refresh-cache flag to force update
- [x] Store last_updated timestamp with cache
- [x] **Checkpoint 3**: Successfully cache and retrieve repo list

## Phase 4: Fuzzy Matching

### 4.1 Fuzzy Matcher
- [x] Create fuzzy.py module
- [x] Implement repo name validation using rapidfuzz
- [x] Create interactive prompt for ambiguous matches using rich
- [x] Handle exact matches (skip prompt)
- [x] Set reasonable threshold for auto-acceptance (e.g., >90% match)

### 4.2 Interactive Resolution
- [x] Build rich table for showing matches
- [x] Implement selection prompt
- [x] Handle multiple typos in one command
- [x] **Checkpoint 4**: Test with intentional typos like "workflws" → "workflows"

## Phase 5: Core Workspace Creation

### 5.1 Basic Clone Functionality
- [x] Create workspace.py module
- [x] Implement workspace directory creation
- [x] Add basic git clone functionality
- [x] Create workspace.json manifest:
  ```json
  {
    "created_at": "2024-01-15T10:30:00Z",
    "organization": "IndicoDataSolutions",
    "repositories": ["indicore", "workflows"],
    "branch_info": {"indicore": "main", "workflows": "main"}
  }
  ```

### 5.2 Progress Display
- [x] Implement rich progress bar for cloning
- [x] Show status for each repo (✓/✗)
- [x] Display clone errors but continue with other repos
- [x] **Checkpoint 5**: Run `gt create indicore workflows -f test-workspace`

## Phase 6: Branch Management ✅

### 6.1 Branch Checkout
- [x] Implement --branch/-b flag functionality
- [x] Check if branch exists before cloning
- [x] Fall back to default branch if specified branch doesn't exist
- [x] Update workspace.json with actual branches used

### 6.2 Branch Creation
- [x] Implement --create-branch/-c flag
- [x] Create new branch from repo's default branch
- [x] Handle branch creation failures gracefully
- [x] **Checkpoint 6**: Test both branch checkout and creation

## Phase 7: Polish and Error Handling

### 7.1 Error Handling
- [x] Add proper error messages for:
  - [x] Missing GITHUB_TOKEN
  - [x] Invalid organization
  - [x] Network failures
  - [x] Git clone failures
  - [x] Permission issues

### 7.2 UI Polish
- [x] Add rich panels for important messages
- [x] Use consistent colors (green=success, red=error, yellow=warning)
- [x] Add spinners for long operations
- [x] Show summary at the end with workspace path

### 7.3 Validation
- [x] Validate folder doesn't already exist (or prompt to overwrite)
- [x] Check disk space before cloning
- [x] Validate GitHub token has necessary permissions
- [x] **Checkpoint 7**: Full end-to-end test with various edge cases

## Phase 8: Final Features

### 8.1 Quality of Life
- [x] Support both SSH and HTTPS clone URLs (auto-detect based on git config)

### 8.2 Documentation & Packaging
- [x] Write comprehensive README.md with installation instructions:
  - [x] Installation via pipx: `pipx install gentex`
  - [x] Installation via uv: `uv tool install gentex`
  - [x] Development installation: `pipx install -e .`
- [x] Add examples for common use cases
- [x] Document configuration options
- [x] Add troubleshooting section
- [x] Ensure proper versioning and releases

## Testing Checkpoints Summary

1. ✅ **Basic CLI**: `gt --help` shows formatted help
2. ✅ **Config**: `gt config` shows and allows modification of settings
3. **GitHub**: Successfully caches repository list from GitHub
4. **Fuzzy**: `gt create workflws -f test` prompts for "workflows"
5. **Clone**: `gt create indicore workflows -f test-workspace` creates workspace
6. **Branches**: `gt create indicore -f feature -b develop` and `--create-branch feature/new`
7. **Full Test**: Complete workflow with error cases
8. ✅ **Packaging**: `pipx install -e .` and `uv tool install -e .` both work

## Success Criteria
- [ ] Can create a workspace with multiple repos in under 30 seconds
- [ ] Gracefully handles typos with helpful suggestions
- [ ] Clear error messages for common problems
- [ ] Minimal configuration required for repeated use
- [x] Beautiful, informative output using rich
- [x] Comprehensive documentation with examples and troubleshooting
- [x] Multiple installation methods (pipx, uv, development)
- [x] Clear configuration options and usage examples 