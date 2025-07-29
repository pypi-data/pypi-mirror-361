"""GitHub API client for GT CLI."""

import os
import subprocess
from datetime import datetime
from typing import List, Optional

from github import Github, Auth
from github.GithubException import GithubException, RateLimitExceededException, BadCredentialsException
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from devctx.config import Config, RepoCache, load_config, save_config, is_cache_expired

console = Console()


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with authentication."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass token directly."
            )
        
        try:
            auth = Auth.Token(self.token)
            self.github = Github(auth=auth)
            # Test authentication
            self.github.get_user().login
        except BadCredentialsException:
            raise ValueError("Invalid GitHub token provided")
        except Exception as e:
            raise ValueError(f"Failed to authenticate with GitHub: {e}")
    
    def should_use_ssh(self) -> bool:
        """
        Auto-detect whether to use SSH or HTTPS based on git configuration.
        
        This checks git config for SSH key setup and URL preferences.
        Returns True if SSH should be used, False for HTTPS.
        """
        try:
            # Check if user has configured SSH keys by looking for github.com SSH host keys
            ssh_result = subprocess.run(
                ["ssh-keygen", "-F", "github.com"],
                capture_output=True,
                text=True
            )
            
            # If github.com is in known_hosts, likely using SSH
            if ssh_result.returncode == 0:
                return True
                
            # Check git config for GitHub URL preferences
            try:
                config_result = subprocess.run(
                    ["git", "config", "--get", "url.git@github.com:.insteadOf"],
                    capture_output=True,
                    text=True
                )
                # If user has configured SSH URLs as default, use SSH
                if config_result.returncode == 0 and "https://github.com/" in config_result.stdout:
                    return True
            except Exception:
                pass
            
            # Default to HTTPS for broader compatibility
            return False
            
        except Exception:
            # If we can't determine, default to HTTPS
            return False
    
    def get_organization_repos(self, org_name: str, force_refresh: bool = False) -> List[str]:
        """
        Get list of repository names for an organization.
        
        Args:
            org_name: GitHub organization name
            force_refresh: Force refresh of cache, ignoring cache duration
            
        Returns:
            List of repository names
        """
        config = load_config()
        
        # Check if we have cached data and if it's still valid
        if not force_refresh and org_name in config.repo_cache:
            cache_data = config.repo_cache[org_name]
            if not is_cache_expired(cache_data, config.repo_cache_duration_days):
                console.print(f"[dim]Using cached repository list for {org_name}[/dim]")
                return cache_data.repos
        
        # Fetch fresh data from GitHub
        console.print(f"[yellow]Fetching repository list for {org_name}...[/yellow]")
        
        try:
            org = self.github.get_organization(org_name)
            repos = []
            
            # Use rich progress bar for large organizations
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                # Get total count for progress bar
                total_repos = org.public_repos + org.total_private_repos
                task = progress.add_task(f"Loading {org_name} repositories...", total=total_repos)
                
                # Handle pagination - GitHub API returns 30 repos per page by default
                for repo in org.get_repos():
                    repos.append(repo.name)
                    progress.update(task, advance=1)
                # Ensure the progress bar completes (handles API count mismatch)
                progress.update(task, total=len(repos), completed=len(repos))
            
            # Update cache
            cache_data = RepoCache(
                repos=sorted(repos),  # Sort for consistent ordering
                last_updated=datetime.now()
            )
            config.repo_cache[org_name] = cache_data
            save_config(config)
            
            console.print(f"[green]✓ Found {len(repos)} repositories in {org_name}[/green]")
            return repos
            
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Organization '{org_name}' not found or not accessible")
            elif e.status == 403:
                raise ValueError(f"Access denied to organization '{org_name}'. Check permissions.")
            else:
                raise ValueError(f"GitHub API error: {e}")
        except RateLimitExceededException:
            raise ValueError(
                "GitHub API rate limit exceeded. Please wait and try again later, "
                "or use a token with higher rate limits."
            )
        except Exception as e:
            raise ValueError(f"Failed to fetch repositories: {e}")
    
    def validate_repositories(self, org_name: str, repo_names: List[str]) -> List[str]:
        """
        Validate that repositories exist in the organization.
        
        Args:
            org_name: GitHub organization name
            repo_names: List of repository names to validate
            
        Returns:
            List of valid repository names
            
        Raises:
            ValueError: If any repository doesn't exist
        """
        try:
            org = self.github.get_organization(org_name)
            valid_repos = []
            invalid_repos = []
            
            for repo_name in repo_names:
                try:
                    repo = org.get_repo(repo_name)
                    valid_repos.append(repo.name)
                except GithubException as e:
                    if e.status == 404:
                        invalid_repos.append(repo_name)
                    else:
                        raise
            
            if invalid_repos:
                raise ValueError(
                    f"Repository(ies) not found in {org_name}: {', '.join(invalid_repos)}"
                )
            
            return valid_repos
            
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Organization '{org_name}' not found or not accessible")
            else:
                raise ValueError(f"GitHub API error: {e}")
    
    def get_repository_default_branch(self, org_name: str, repo_name: str) -> str:
        """
        Get the default branch for a repository.
        
        Args:
            org_name: GitHub organization name
            repo_name: Repository name
            
        Returns:
            Default branch name
        """
        try:
            org = self.github.get_organization(org_name)
            repo = org.get_repo(repo_name)
            return repo.default_branch
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository '{repo_name}' not found in {org_name}")
            else:
                raise ValueError(f"GitHub API error: {e}")
    
    def check_branch_exists(self, org_name: str, repo_name: str, branch_name: str) -> bool:
        """
        Check if a branch exists in a repository.
        
        Args:
            org_name: GitHub organization name
            repo_name: Repository name
            branch_name: Branch name to check
            
        Returns:
            True if branch exists, False otherwise
        """
        try:
            org = self.github.get_organization(org_name)
            repo = org.get_repo(repo_name)
            try:
                repo.get_branch(branch_name)
                return True
            except GithubException as e:
                if e.status == 404:
                    return False
                else:
                    raise
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository '{repo_name}' not found in {org_name}")
            else:
                raise ValueError(f"GitHub API error: {e}")
    
    def get_clone_url(self, org_name: str, repo_name: str, use_ssh: Optional[bool] = None) -> str:
        """
        Get the clone URL for a repository.
        
        Args:
            org_name: GitHub organization name
            repo_name: Repository name  
            use_ssh: Whether to use SSH URL instead of HTTPS. If None, auto-detects based on git config.
            
        Returns:
            Repository clone URL
        """
        try:
            org = self.github.get_organization(org_name)
            repo = org.get_repo(repo_name)
            
            # Auto-detect SSH preference if not specified
            if use_ssh is None:
                use_ssh = self.should_use_ssh()
                
            return repo.ssh_url if use_ssh else repo.clone_url
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository '{repo_name}' not found in {org_name}")
            else:
                raise ValueError(f"GitHub API error: {e}")


def create_github_client(token: Optional[str] = None) -> GitHubClient:
    """
    Create a GitHub client with proper error handling.
    
    Args:
        token: GitHub token (optional, will use GITHUB_TOKEN env var if not provided)
        
    Returns:
        GitHubClient instance
        
    Raises:
        ValueError: If authentication fails
    """
    try:
        return GitHubClient(token)
    except ValueError:
        # Re-raise with helpful message
        raise
    except Exception as e:
        raise ValueError(f"Failed to create GitHub client: {e}") 