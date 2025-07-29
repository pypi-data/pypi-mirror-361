"""Basic tests for GT configuration management.

These tests focus on the most critical functionality without going overboard.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from devctx.config import Config, RepoCache, load_config, save_config, is_cache_expired


def test_config_defaults():
    """Test that default configuration values are correct."""
    config = Config()
    
    assert config.default_org is None
    assert config.repo_cache_duration_days == 30
    assert config.repo_cache == {}


def test_config_serialization():
    """Test that config can be serialized to/from JSON using Pydantic."""
    # Create a config with some data
    config = Config(
        default_org="TestOrg",
        repo_cache_duration_days=15,
        repo_cache={
            "TestOrg": RepoCache(
                repos=["repo1", "repo2"],
                last_updated=datetime(2024, 1, 1, 12, 0, 0)
            )
        }
    )
    
    # Serialize to JSON using Pydantic
    json_data = config.model_dump_json()
    
    # Deserialize back using Pydantic
    restored_config = Config.model_validate_json(json_data)
    
    assert restored_config.default_org == "TestOrg"
    assert restored_config.repo_cache_duration_days == 15
    assert "TestOrg" in restored_config.repo_cache
    assert restored_config.repo_cache["TestOrg"].repos == ["repo1", "repo2"]
    assert restored_config.repo_cache["TestOrg"].last_updated == datetime(2024, 1, 1, 12, 0, 0)


def test_cache_expiration():
    """Test cache expiration logic."""
    now = datetime.now()
    
    # Fresh cache (not expired)
    fresh_cache = RepoCache(
        repos=["repo1"], 
        last_updated=now - timedelta(days=1)
    )
    assert not is_cache_expired(fresh_cache, 30)
    
    # Old cache (expired)
    old_cache = RepoCache(
        repos=["repo1"], 
        last_updated=now - timedelta(days=31)
    )
    assert is_cache_expired(old_cache, 30)
    
    # Boundary case (exactly at limit)
    boundary_cache = RepoCache(
        repos=["repo1"], 
        last_updated=now - timedelta(days=30)
    )
    assert is_cache_expired(boundary_cache, 30)


def test_config_save_load():
    """Test saving and loading configuration from file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the config directory
        config_dir = Path(temp_dir) / "gt"
        config_file = config_dir / "config.json"
        
        with patch('devctx.config.get_config_dir', return_value=config_dir):
            # Create and save a config
            original_config = Config(
                default_org="SaveLoadTest",
                repo_cache_duration_days=45
            )
            save_config(original_config)
            
            # Verify file was created
            assert config_file.exists()
            
            # Load the config back
            loaded_config = load_config()
            
            assert loaded_config.default_org == "SaveLoadTest"
            assert loaded_config.repo_cache_duration_days == 45
            assert loaded_config.repo_cache == {}


def test_config_load_creates_default():
    """Test that loading config creates default file when none exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "gt"
        config_file = config_dir / "config.json"
        
        with patch('devctx.config.get_config_dir', return_value=config_dir):
            # Load config when no file exists
            config = load_config()
            
            # Should create default config
            assert config.default_org is None
            assert config.repo_cache_duration_days == 30
            assert config.repo_cache == {}
            
            # Should have created the file
            assert config_file.exists()


def test_repo_cache_model():
    """Test RepoCache model functionality."""
    cache = RepoCache(repos=["repo1", "repo2", "repo3"])
    
    assert len(cache.repos) == 3
    assert "repo1" in cache.repos
    assert isinstance(cache.last_updated, datetime)
    
    # Test that last_updated is recent (within last minute)
    now = datetime.now()
    assert (now - cache.last_updated).total_seconds() < 60


if __name__ == "__main__":
    # Simple test runner
    import traceback
    
    test_functions = [
        test_config_defaults,
        test_config_serialization,
        test_cache_expiration,
        test_config_save_load,
        test_config_load_creates_default,
        test_repo_cache_model
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    exit(0 if failed == 0 else 1) 