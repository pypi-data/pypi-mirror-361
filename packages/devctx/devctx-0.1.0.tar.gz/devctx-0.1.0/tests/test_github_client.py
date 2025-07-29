"""Tests for GitHub client functionality."""

import os
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from devctx.github_client import GitHubClient, create_github_client
from devctx.config import RepoCache


class TestGitHubClient:
    """Test GitHub client functionality."""
    
    def test_github_client_requires_token(self):
        """Test that GitHub client requires authentication token."""
        # Clear any existing token
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                GitHubClient()
    
    def test_github_client_invalid_token(self):
        """Test that invalid token raises appropriate error."""
        with patch("devctx.github_client.Github") as mock_github:
            from unittest.mock import PropertyMock
            mock_user = Mock()
            type(mock_user).login = PropertyMock(side_effect=Exception("Bad credentials"))
            mock_github.return_value.get_user.return_value = mock_user
            
            with pytest.raises(ValueError, match="Failed to authenticate with GitHub"):
                GitHubClient("invalid_token")
    
    @patch("devctx.github_client.Github")
    def test_github_client_initialization(self, mock_github):
        """Test successful GitHub client initialization."""
        # Mock successful authentication
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        client = GitHubClient("valid_token")
        assert client.token == "valid_token"
        assert client.github is not None
    
    @patch("devctx.github_client.Github")
    def test_should_use_ssh_with_known_hosts(self, mock_github):
        """Test SSH detection when github.com is in known_hosts."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        client = GitHubClient("valid_token")
        
        # Mock successful ssh-keygen -F github.com
        with patch("devctx.github_client.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            assert client.should_use_ssh() is True
    
    @patch("devctx.github_client.Github")
    def test_should_use_ssh_with_git_config(self, mock_github):
        """Test SSH detection when git config has SSH URL preference."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        client = GitHubClient("valid_token")
        
        # Mock ssh-keygen fails but git config succeeds
        with patch("devctx.github_client.subprocess.run") as mock_run:
            def side_effect(cmd, **kwargs):
                if "ssh-keygen" in cmd:
                    return Mock(returncode=1)
                elif "git" in cmd and "config" in cmd:
                    return Mock(returncode=0, stdout="https://github.com/")
                return Mock(returncode=1)
            
            mock_run.side_effect = side_effect
            assert client.should_use_ssh() is True
    
    @patch("devctx.github_client.Github")
    def test_should_use_ssh_defaults_to_https(self, mock_github):
        """Test SSH detection defaults to HTTPS when no SSH setup found."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        client = GitHubClient("valid_token")
        
        # Mock both ssh-keygen and git config failing
        with patch("devctx.github_client.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1)
            assert client.should_use_ssh() is False
    
    @patch("devctx.github_client.Github")
    def test_should_use_ssh_handles_exceptions(self, mock_github):
        """Test SSH detection handles exceptions gracefully."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        client = GitHubClient("valid_token")
        
        # Mock subprocess.run raising exception
        with patch("devctx.github_client.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Command not found")
            assert client.should_use_ssh() is False
    
    @patch("devctx.github_client.Github")
    def test_get_clone_url_auto_detect_ssh(self, mock_github):
        """Test get_clone_url with auto-detection of SSH."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        # Mock org and repo
        mock_org = Mock()
        mock_repo = Mock()
        mock_repo.ssh_url = "git@github.com:test-org/test-repo.git"
        mock_repo.clone_url = "https://github.com/test-org/test-repo.git"
        mock_org.get_repo.return_value = mock_repo
        mock_github.return_value.get_organization.return_value = mock_org
        
        client = GitHubClient("valid_token")
        
        # Test auto-detection chooses SSH
        with patch.object(client, 'should_use_ssh', return_value=True):
            url = client.get_clone_url("test-org", "test-repo")
            assert url == "git@github.com:test-org/test-repo.git"
        
        # Test auto-detection chooses HTTPS
        with patch.object(client, 'should_use_ssh', return_value=False):
            url = client.get_clone_url("test-org", "test-repo")
            assert url == "https://github.com/test-org/test-repo.git"
    
    @patch("devctx.github_client.Github")
    def test_get_clone_url_explicit_ssh_override(self, mock_github):
        """Test get_clone_url with explicit SSH override."""
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        # Mock org and repo
        mock_org = Mock()
        mock_repo = Mock()
        mock_repo.ssh_url = "git@github.com:test-org/test-repo.git"
        mock_repo.clone_url = "https://github.com/test-org/test-repo.git"
        mock_org.get_repo.return_value = mock_repo
        mock_github.return_value.get_organization.return_value = mock_org
        
        client = GitHubClient("valid_token")
        
        # Test explicit SSH=True overrides auto-detection
        with patch.object(client, 'should_use_ssh', return_value=False):
            url = client.get_clone_url("test-org", "test-repo", use_ssh=True)
            assert url == "git@github.com:test-org/test-repo.git"
        
        # Test explicit SSH=False overrides auto-detection
        with patch.object(client, 'should_use_ssh', return_value=True):
            url = client.get_clone_url("test-org", "test-repo", use_ssh=False)
            assert url == "https://github.com/test-org/test-repo.git"
    
    @patch("devctx.github_client.load_config")
    @patch("devctx.github_client.save_config")
    @patch("devctx.github_client.Github")
    def test_get_organization_repos_with_cache(self, mock_github, mock_save, mock_load):
        """Test getting organization repos with valid cache."""
        # Mock config with valid cache
        mock_config = Mock()
        mock_config.repo_cache = {
            "test-org": RepoCache(
                repos=["repo1", "repo2"],
                last_updated=datetime.now()  # Recent cache
            )
        }
        mock_config.repo_cache_duration_days = 30
        mock_load.return_value = mock_config
        
        # Mock GitHub client
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        client = GitHubClient("valid_token")
        repos = client.get_organization_repos("test-org")
        
        # Should use cache, not call GitHub API
        assert repos == ["repo1", "repo2"]
        mock_github.return_value.get_organization.assert_not_called()
    
    @patch("devctx.github_client.load_config")
    @patch("devctx.github_client.save_config")
    @patch("devctx.github_client.Github")
    def test_get_organization_repos_expired_cache(self, mock_github, mock_save, mock_load):
        """Test getting organization repos with expired cache."""
        # Mock config with expired cache
        mock_config = Mock()
        mock_config.repo_cache = {
            "test-org": RepoCache(
                repos=["old-repo"],
                last_updated=datetime.now() - timedelta(days=35)  # Expired cache
            )
        }
        mock_config.repo_cache_duration_days = 30
        mock_load.return_value = mock_config
        
        # Mock GitHub API response
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        mock_org = Mock()
        mock_org.public_repos = 1
        mock_org.total_private_repos = 1
        
        mock_repo = Mock()
        mock_repo.name = "new-repo"
        mock_org.get_repos.return_value = [mock_repo]
        
        mock_github.return_value.get_organization.return_value = mock_org
        
        client = GitHubClient("valid_token")
        repos = client.get_organization_repos("test-org")
        
        # Should fetch from API and update cache
        assert repos == ["new-repo"]
        mock_github.return_value.get_organization.assert_called_once_with("test-org")
        mock_save.assert_called_once()
    
    @patch("devctx.github_client.Github")
    def test_validate_repositories_success(self, mock_github):
        """Test successful repository validation."""
        # Mock GitHub client
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        mock_org = Mock()
        mock_repo = Mock()
        mock_repo.name = "valid-repo"
        mock_org.get_repo.return_value = mock_repo
        mock_github.return_value.get_organization.return_value = mock_org
        
        client = GitHubClient("valid_token")
        result = client.validate_repositories("test-org", ["valid-repo"])
        
        assert result == ["valid-repo"]
    
    @patch("devctx.github_client.Github")
    def test_validate_repositories_not_found(self, mock_github):
        """Test repository validation with non-existent repo."""
        # Mock GitHub client
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github.return_value.get_user.return_value = mock_user
        
        mock_org = Mock()
        from github.GithubException import GithubException
        mock_org.get_repo.side_effect = GithubException(404, "Not Found")
        mock_github.return_value.get_organization.return_value = mock_org
        
        client = GitHubClient("valid_token")
        
        with pytest.raises(ValueError, match="Repository\\(ies\\) not found"):
            client.validate_repositories("test-org", ["invalid-repo"])
    
    def test_create_github_client_success(self):
        """Test successful GitHub client creation."""
        with patch("devctx.github_client.GitHubClient") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            result = create_github_client("token")
            
            assert result == mock_instance
            mock_client.assert_called_once_with("token")
    
    def test_create_github_client_failure(self):
        """Test GitHub client creation failure."""
        with patch("devctx.github_client.GitHubClient") as mock_client:
            mock_client.side_effect = Exception("Test error")
            
            with pytest.raises(ValueError, match="Failed to create GitHub client"):
                create_github_client("token") 