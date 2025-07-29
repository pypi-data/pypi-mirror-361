from __future__ import annotations

"""Workspace management for GT CLI (Phase 5)."""

from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)

from devctx.github_client import GitHubClient

console = Console()


class WorkspaceError(Exception):
    """Custom exception for workspace related failures."""


# Public API -----------------------------------------------------------------

def create_workspace(
    github_client: GitHubClient,
    org_name: str,
    repo_names: List[str],
    *,
    folder: Optional[str] = None,
    branch: Optional[str] = None,
    create_branch: Optional[str] = None,
) -> Path:
    """Create a workspace directory and clone repositories into it.

    This is the **basic clone functionality** described in Phase 5.1 of the
    implementation plan. It is intentionally opinionated and keeps error
    handling simple for now – future phases can add retries, rollbacks, etc.

    Args:
        github_client: Authenticated :class:`~gt.github_client.GitHubClient`.
        org_name: GitHub organization name.
        repo_names: List of repository names to clone.
        folder: Optional workspace folder name. If *None*, a name will be
            generated automatically (``"{org}-workspace-YYYYMMDD-HHMMSS"``).
        branch: If provided, attempt to clone this branch for **all** repos.
            When the branch does not exist, fall back to each repo's default
            branch.
        create_branch: If provided, create and check out this new branch in all
            cloned repositories **after** cloning.

    Returns:
        Path to the created workspace directory.

    Raises:
        WorkspaceError: On unrecoverable failures, such as when the workspace
            folder already exists or *git* is not available.
    """
    # ------------------------------------------------------------------
    # 1. Determine workspace directory
    # ------------------------------------------------------------------
    if folder:
        workspace_dir = Path(folder).expanduser().resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        workspace_dir = Path(f"{org_name}-workspace-{timestamp}").resolve()

    if workspace_dir.exists():
        raise WorkspaceError(
            f"Workspace directory '{workspace_dir}' already exists. Choose a "
            "different --folder name or remove the existing directory."
        )

    try:
        workspace_dir.mkdir(parents=True, exist_ok=False)
    except Exception as exc:
        raise WorkspaceError(f"Failed to create workspace directory: {exc}") from exc

    console.print(f"[green]✓ Created workspace directory:[/green] {workspace_dir}")

    # ------------------------------------------------------------------
    # 2. Clone repositories
    # ------------------------------------------------------------------
    branch_info: Dict[str, str] = {}
    failed_repos: List[str] = []

    git_available = _check_git_available()
    if not git_available:
        raise WorkspaceError("'git' command not found. Please install Git.")

    # Auto-detect SSH vs HTTPS preference
    use_ssh = github_client.should_use_ssh()
    clone_method = "SSH" if use_ssh else "HTTPS"
    console.print(f"[dim]Using {clone_method} for cloning (auto-detected)[/dim]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Cloning repositories...", total=len(repo_names))

        for repo_name in repo_names:
            # Decide which branch we will end up with for this repo
            chosen_branch: Optional[str] = branch
            if branch and not github_client.check_branch_exists(org_name, repo_name, branch):
                chosen_branch = github_client.get_repository_default_branch(org_name, repo_name)

            clone_url = github_client.get_clone_url(org_name, repo_name)
            target_dir = workspace_dir / repo_name

            cmd: List[str] = [
                "git",
                "clone",
                "--depth",
                "1",  # shallow clone for speed; can be made configurable later
            ]
            if chosen_branch:
                cmd += ["--branch", chosen_branch]
            cmd += [clone_url, str(target_dir)]

            try:
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                console.print(
                    f"[green]✓ Cloned {repo_name}[/green] "
                    f"(branch: {chosen_branch or 'default'})"
                )
                branch_info[repo_name] = chosen_branch or "default"

                # Optionally create/check-out a new branch
                if create_branch:
                    subprocess.run(
                        [
                            "git",
                            "-C",
                            str(target_dir),
                            "checkout",
                            "-b",
                            create_branch,
                        ],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    branch_info[repo_name] = create_branch
            except subprocess.CalledProcessError as exc:
                failed_repos.append(repo_name)
                console.print(
                    f"[red]✗ Failed to clone {repo_name}: {exc.stderr.strip()}[/red]"
                )
            finally:
                progress.update(task, advance=1)

    # ------------------------------------------------------------------
    # 3. Write workspace manifest
    # ------------------------------------------------------------------
    manifest_path = workspace_dir / "workspace.json"
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "organization": org_name,
        "repositories": [r for r in repo_names if r not in failed_repos],
        "branch_info": branch_info,
    }

    try:
        with open(manifest_path, "w", encoding="utf-8") as fp:
            json.dump(manifest, fp, indent=2)
        console.print(f"[green]✓ Wrote workspace manifest:[/green] {manifest_path}")
    except Exception as exc:
        console.print(f"[red]Failed to write workspace manifest: {exc}[/red]")

    # ------------------------------------------------------------------
    # 4. Final summary
    # ------------------------------------------------------------------
    if failed_repos:
        console.print(
            f"[yellow]Finished with errors. Failed repositories: {', '.join(failed_repos)}[/yellow]"
        )
    else:
        console.print("[bold green]Workspace creation complete![/bold green]")

    return workspace_dir


# Helpers --------------------------------------------------------------------

def _check_git_available() -> bool:
    """Return *True* if the *git* executable is available in $PATH."""
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


__all__ = [
    "create_workspace",
    "WorkspaceError",
] 