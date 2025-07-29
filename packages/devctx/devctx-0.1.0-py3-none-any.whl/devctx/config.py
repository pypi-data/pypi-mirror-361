"""Configuration management for GT CLI."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class RepoCache(BaseModel):
    """Cache information for a GitHub organization's repositories."""
    repos: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


class Config(BaseModel):
    """Main configuration model for GT CLI."""
    default_org: Optional[str] = None
    repo_cache_duration_days: int = 30
    repo_cache: Dict[str, RepoCache] = Field(default_factory=dict)


def get_config_dir() -> Path:
    # TODO: make this configurable with an environment variable
    """Get the configuration directory path."""
    config_dir = Path.home() / ".config" / "devctx"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.json"


def load_config() -> Config:
    """Load configuration from file, creating defaults if not found."""
    config_file = get_config_file()
    
    if not config_file.exists():
        # Create default config
        config = Config()
        save_config(config)
        return config
    
    try:
        with open(config_file, 'r') as f:
            json_data = f.read()
        
        # Use Pydantic's built-in JSON parsing with datetime handling
        return Config.model_validate_json(json_data)
    except (ValueError, Exception) as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        console.print("[yellow]Creating fresh config file...[/yellow]")
        config = Config()
        save_config(config)
        return config


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_file = get_config_file()
    
    # Ensure the directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use Pydantic's built-in JSON serialization with datetime handling
        json_data = config.model_dump_json(indent=2)
        with open(config_file, 'w') as f:
            f.write(json_data)
    except Exception as e:
        console.print(f"[red]Error saving config: {e}[/red]")


def display_config(config: Config) -> None:
    """Display current configuration using rich formatting."""
    table = Table(title="GT Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Config File", str(get_config_file()))
    table.add_row("Default Organization", config.default_org or "[dim]Not set[/dim]")
    table.add_row("Cache Duration (days)", str(config.repo_cache_duration_days))
    
    console.print(table)
    
    # Show cached organizations
    if config.repo_cache:
        console.print("\n[bold]Cached Organizations:[/bold]")
        for org_name, cache_data in config.repo_cache.items():
            repo_count = len(cache_data.repos)
            last_updated = cache_data.last_updated.strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"  • {org_name}: {repo_count} repos (updated: {last_updated})")
    else:
        console.print("\n[dim]No cached organizations[/dim]")


def update_default_org(new_org: str) -> None:
    """Update the default organization in config."""
    config = load_config()
    config.default_org = new_org
    save_config(config)
    console.print(f"[green]✓ Default organization set to: {new_org}[/green]")


def is_cache_expired(cache_data: RepoCache, duration_days: int) -> bool:
    """Check if cache data is expired."""
    age = datetime.now() - cache_data.last_updated
    return age.days >= duration_days 