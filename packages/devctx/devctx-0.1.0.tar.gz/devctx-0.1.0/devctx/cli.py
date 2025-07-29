"""DevCtx CLI - Main command-line interface."""

import click
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from devctx import __version__
from devctx.config import load_config, display_config, update_default_org
from devctx.github_client import create_github_client
from devctx.fuzzy import resolve_names
from devctx.workspace import create_workspace as perform_clone

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="devctx")
def cli():
    """DevCtx - Create temporary monorepos from GitHub repositories."""
    pass


@cli.command(name="create")
@click.argument("repos", nargs=-1, required=True)
@click.option(
    "--org", "-o", 
    help="GitHub organization name"
)
@click.option(
    "--folder", "-f",
    help="Workspace folder name"
)
@click.option(
    "--branch", "-b",
    help="Branch to checkout for all repositories"
)
@click.option(
    "--create-branch", "-c",
    help="Create a new branch in all repositories"
)
@click.option(
    "--refresh-cache",
    is_flag=True,
    help="Force refresh of repository cache"
)
def create_workspace(repos, org, folder, branch, create_branch, refresh_cache):
    """
    Create a temporary monorepo workspace.
    
    \b
    Examples:
      devctx create indicore workflows --org IndicoDataSolutions --folder my-workspace
      devctx create indicore workflows -o IndicoDataSolutions -f feature-branch -b develop
      devctx create indicore workflows cyclone -f new-feature --create-branch feature/awesome-thing
    """
    repo_list = list(repos)
    
    # Load config for default organization
    config = load_config()
    if not org and config.default_org:
        org = config.default_org
        console.print(f"[dim]Using default organization: {org}[/dim]")
    
    if not org:
        console.print("[red]Error: No organization specified. Use --org or set a default organization with 'devctx config --set-org ORG_NAME'[/red]")
        return
    
    try:
        # Create GitHub client
        github_client = create_github_client()
        
        # Get organization repositories list (this will cache them)
        org_repos = github_client.get_organization_repos(org, force_refresh=refresh_cache)

        # Resolve any typos using fuzzy matching
        resolved_repos = resolve_names(repo_list, org_repos)

        # Validate resolved repository names actually exist
        console.print(f"[blue]Validating repositories in {org}...[/blue]")
        valid_repos = github_client.validate_repositories(org, resolved_repos)

        # Determine workspace folder name if not provided
        if not folder:
            folder = f"{org}-workspace-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            console.print(f"[dim]No folder specified – using '{folder}'[/dim]")

        # Display summary
        console.print(f"[green]✓ Organization:[/green] {org}")
        console.print(f"[green]✓ Repositories:[/green] {', '.join(valid_repos)}")
        console.print(f"[green]✓ Folder:[/green] {folder}")
        
        if branch:
            console.print(f"[green]✓ Branch:[/green] {branch}")
            # Check if branch exists in repositories
            console.print("[blue]Checking branch availability...[/blue]")
            for repo in valid_repos:
                if github_client.check_branch_exists(org, repo, branch):
                    console.print(f"  ✓ {repo}: branch '{branch}' exists")
                else:
                    default_branch = github_client.get_repository_default_branch(org, repo)
                    console.print(f"  ⚠ {repo}: branch '{branch}' not found, will use '{default_branch}'")
        
        if create_branch:
            console.print(f"[green]✓ Create Branch:[/green] {create_branch}")
        
        # Show cached repositories count
        console.print(f"[dim]Organization has {len(org_repos)} total repositories[/dim]")
        
        # ------------------------------------------------------------------
        # Phase 5 – Basic clone functionality
        # ------------------------------------------------------------------
        console.print("\n[bold]Cloning repositories...[/bold]")

        workspace_path = perform_clone(
            github_client,
            org,
            valid_repos,
            folder=folder,
            branch=branch,
            create_branch=create_branch,
        )

        console.print(f"\n[bold green]Workspace ready:[/bold green] {workspace_path}")
        
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        if "GITHUB_TOKEN" in str(e):
            console.print("[yellow]Tip: Set your GitHub token with: export GITHUB_TOKEN=your_token_here[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


@cli.command()
@click.option(
    "--set-org", 
    help="Set the default organization"
)
def config(set_org):
    """Manage DevCtx configuration settings."""
    config_obj = load_config()
    
    if set_org:
        update_default_org(set_org)
        config_obj = load_config()  # Reload to show updated config
    
    display_config(config_obj)


@cli.command()
@click.argument("organization")
@click.option(
    "--refresh-cache",
    is_flag=True,
    help="Force refresh of repository cache"
)
def list_repos(organization, refresh_cache):
    """List repositories for a GitHub organization."""
    try:
        github_client = create_github_client()
        repos = github_client.get_organization_repos(organization, force_refresh=refresh_cache)
        
        console.print(f"\n[bold]Repositories in {organization}:[/bold]")
        for i, repo in enumerate(repos, 1):
            console.print(f"  {i:3d}. {repo}")
        
        console.print(f"\n[dim]Total: {len(repos)} repositories[/dim]")
        
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        if "GITHUB_TOKEN" in str(e):
            console.print("[yellow]Tip: Set your GitHub token with: export GITHUB_TOKEN=your_token_here[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    cli() 