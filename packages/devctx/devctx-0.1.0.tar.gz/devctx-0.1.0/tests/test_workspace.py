"""Tests for basic workspace creation (Phase 5)."""

import json
from types import SimpleNamespace
from unittest.mock import patch, call

import pytest

from devctx.workspace import create_workspace


class DummyGitHubClient:
    """Light-weight stub of :class:`gt.github_client.GitHubClient`."""

    def __init__(self, branch_exists: bool = True):
        # store behaviour for check_branch_exists
        self._branch_exists = branch_exists

    # Methods used by `create_workspace`
    def check_branch_exists(self, org_name, repo_name, branch_name):
        if callable(self._branch_exists):
            return self._branch_exists(org_name, repo_name, branch_name)
        return self._branch_exists

    def get_repository_default_branch(self, org_name, repo_name):
        return "main"

    def get_clone_url(self, org_name, repo_name, use_ssh=None):
        return f"https://example.com/{org_name}/{repo_name}.git"
    
    def should_use_ssh(self):
        return False  # Default to HTTPS for tests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_completed_process():
    return SimpleNamespace(returncode=0, stdout="", stderr="")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_workspace_success(tmp_path):
    """Successfully creates workspace, writes manifest, respects branch logic."""
    workspace_dir = tmp_path / "ws"

    # Branch exists for repo1, not for repo2 – triggers fallback logic.
    def branch_exists(org, repo, branch):
        return repo == "repo1"

    gh_client = DummyGitHubClient(branch_exists)

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch(
            "devctx.workspace.subprocess.run", return_value=_mock_completed_process()
        ) as mock_run:
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1", "repo2"],
                folder=str(workspace_dir),
                branch="develop",
            )

    # Workspace path returned and directory exists
    assert result_path == workspace_dir.resolve()
    assert workspace_dir.exists()

    # `git clone` invoked twice (once per repo)
    clone_calls = [call for call in mock_run.call_args_list if "clone" in call.args[0]]
    assert len(clone_calls) == 2

    # Manifest written with correct branch info
    manifest_file = workspace_dir / "workspace.json"
    assert manifest_file.exists()
    manifest = json.loads(manifest_file.read_text())

    assert manifest["organization"] == "test-org"
    assert manifest["repositories"] == ["repo1", "repo2"]
    # Branch info respects existence fallback
    assert manifest["branch_info"]["repo1"] == "develop"
    assert manifest["branch_info"]["repo2"] == "main"


def test_create_workspace_partial_failure(tmp_path):
    """If a clone fails, it is excluded from manifest but workspace still created."""
    workspace_dir = tmp_path / "ws2"
    gh_client = DummyGitHubClient(branch_exists=True)

    # Use CalledProcessError to mimic git failure precisely
    from subprocess import CalledProcessError, CompletedProcess

    def side_effect(cmd, check, stdout, stderr, text):
        for token in cmd:
            if "repo2" in token:
                raise CalledProcessError(returncode=1, cmd=cmd, output="", stderr="fatal error")
        return CompletedProcess(cmd, 0, stdout="", stderr="")

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch("devctx.workspace.subprocess.run", side_effect=side_effect):
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1", "repo2"],
                folder=str(workspace_dir),
            )

    # Directory exists even after failure
    assert result_path == workspace_dir.resolve()
    assert workspace_dir.exists()

    manifest = json.loads((workspace_dir / "workspace.json").read_text())

    # Only successful repo listed
    assert manifest["repositories"] == ["repo1"]
    assert "repo2" not in manifest["repositories"]


def test_create_workspace_with_branch_checkout(tmp_path):
    """Test Phase 6.1: Branch checkout functionality."""
    workspace_dir = tmp_path / "ws_branch"
    gh_client = DummyGitHubClient(branch_exists=True)

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch(
            "devctx.workspace.subprocess.run", return_value=_mock_completed_process()
        ) as mock_run:
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1"],
                folder=str(workspace_dir),
                branch="feature-branch",
            )

    # Check that git clone was called with the correct branch
    clone_calls = [call for call in mock_run.call_args_list if "clone" in call.args[0]]
    assert len(clone_calls) == 1
    clone_args = clone_calls[0].args[0]
    assert "--branch" in clone_args
    assert "feature-branch" in clone_args

    # Manifest should record the correct branch
    manifest = json.loads((workspace_dir / "workspace.json").read_text())
    assert manifest["branch_info"]["repo1"] == "feature-branch"


def test_create_workspace_with_branch_fallback(tmp_path):
    """Test Phase 6.1: Branch fallback when branch doesn't exist."""
    workspace_dir = tmp_path / "ws_fallback"
    gh_client = DummyGitHubClient(branch_exists=False)

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch(
            "devctx.workspace.subprocess.run", return_value=_mock_completed_process()
        ) as mock_run:
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1"],
                folder=str(workspace_dir),
                branch="non-existent-branch",
            )

    # Check that git clone was called with the default branch
    clone_calls = [call for call in mock_run.call_args_list if "clone" in call.args[0]]
    assert len(clone_calls) == 1
    clone_args = clone_calls[0].args[0]
    assert "--branch" in clone_args
    assert "main" in clone_args  # Should fall back to default branch
    assert "non-existent-branch" not in clone_args

    # Manifest should record the fallback branch
    manifest = json.loads((workspace_dir / "workspace.json").read_text())
    assert manifest["branch_info"]["repo1"] == "main"


def test_create_workspace_with_branch_creation(tmp_path):
    """Test Phase 6.2: Branch creation functionality."""
    workspace_dir = tmp_path / "ws_create"
    gh_client = DummyGitHubClient(branch_exists=True)

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch(
            "devctx.workspace.subprocess.run", return_value=_mock_completed_process()
        ) as mock_run:
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1"],
                folder=str(workspace_dir),
                create_branch="feature/new-branch",
            )

    # Check that git clone was called normally
    clone_calls = [call for call in mock_run.call_args_list if "clone" in call.args[0]]
    assert len(clone_calls) == 1

    # Check that git checkout -b was called to create the new branch
    checkout_calls = [call for call in mock_run.call_args_list if "checkout" in call.args[0]]
    assert len(checkout_calls) == 1
    checkout_args = checkout_calls[0].args[0]
    assert "checkout" in checkout_args
    assert "-b" in checkout_args
    assert "feature/new-branch" in checkout_args

    # Manifest should record the created branch
    manifest = json.loads((workspace_dir / "workspace.json").read_text())
    assert manifest["branch_info"]["repo1"] == "feature/new-branch"


def test_create_workspace_with_branch_and_create_branch(tmp_path):
    """Test combining branch checkout and branch creation."""
    workspace_dir = tmp_path / "ws_both"
    gh_client = DummyGitHubClient(branch_exists=True)

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch(
            "devctx.workspace.subprocess.run", return_value=_mock_completed_process()
        ) as mock_run:
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1"],
                folder=str(workspace_dir),
                branch="develop",
                create_branch="feature/from-develop",
            )

    # Check that git clone was called with the base branch
    clone_calls = [call for call in mock_run.call_args_list if "clone" in call.args[0]]
    assert len(clone_calls) == 1
    clone_args = clone_calls[0].args[0]
    assert "--branch" in clone_args
    assert "develop" in clone_args

    # Check that git checkout -b was called to create the new branch
    checkout_calls = [call for call in mock_run.call_args_list if "checkout" in call.args[0]]
    assert len(checkout_calls) == 1
    checkout_args = checkout_calls[0].args[0]
    assert "checkout" in checkout_args
    assert "-b" in checkout_args
    assert "feature/from-develop" in checkout_args

    # Manifest should record the created branch (final state)
    manifest = json.loads((workspace_dir / "workspace.json").read_text())
    assert manifest["branch_info"]["repo1"] == "feature/from-develop"


def test_create_workspace_branch_creation_failure(tmp_path):
    """Test Phase 6.2: Handle branch creation failures gracefully."""
    workspace_dir = tmp_path / "ws_fail"
    gh_client = DummyGitHubClient(branch_exists=True)

    from subprocess import CalledProcessError, CompletedProcess

    def side_effect(cmd, check, stdout, stderr, text):
        if "checkout" in cmd and "-b" in cmd:
            # Branch creation fails
            raise CalledProcessError(returncode=1, cmd=cmd, output="", stderr="branch already exists")
        return CompletedProcess(cmd, 0, stdout="", stderr="")

    with patch("devctx.workspace._check_git_available", return_value=True):
        with patch("devctx.workspace.subprocess.run", side_effect=side_effect):
            result_path = create_workspace(
                github_client=gh_client,
                org_name="test-org",
                repo_names=["repo1"],
                folder=str(workspace_dir),
                create_branch="existing-branch",
            )

    # Workspace should still be created despite branch creation failure
    assert result_path == workspace_dir.resolve()
    assert workspace_dir.exists()

    # Manifest should record the original branch (not the failed create branch)
    manifest = json.loads((workspace_dir / "workspace.json").read_text())
    assert manifest["branch_info"]["repo1"] == "default"  # Falls back to default state 