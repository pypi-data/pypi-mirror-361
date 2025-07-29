"""Fuzzy matching helpers for repository names using rapidfuzz."""

from typing import List, Sequence, Tuple

from rapidfuzz import process, fuzz
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# Default thresholds
DEFAULT_SUGGEST_LIMIT = 5  # how many suggestions to show
AUTO_ACCEPT_THRESHOLD = 90  # score above which we auto-accept best match


def _get_matches(
    query: str,
    choices: Sequence[str],
    limit: int = DEFAULT_SUGGEST_LIMIT,
) -> List[Tuple[str, int]]:
    """Return (choice, score) pairs sorted by best match first."""
    # rapidfuzz `extract` returns tuples of (choice, score, index)
    raw_matches = process.extract(query, choices, scorer=fuzz.QRatio, limit=limit)
    return [(match[0], int(match[1])) for match in raw_matches]


def resolve_names(
    names: Sequence[str],
    choices: Sequence[str],
    *,
    auto_accept_threshold: int = AUTO_ACCEPT_THRESHOLD,
    suggest_limit: int = DEFAULT_SUGGEST_LIMIT,
) -> List[str]:
    """Resolve possibly misspelled *names* against *choices*.

    1. If a name is an exact match, it is returned unchanged.
    2. If the best match score ≥ *auto_accept_threshold*, it is auto-accepted.
    3. Otherwise, show a rich prompt with up to *suggest_limit* options and
       ask the user to choose.

    Returns list of resolved names (same length as *names*).
    """
    resolved: List[str] = []

    for name in names:
        if name in choices:
            # Exact match – accept as-is
            resolved.append(name)
            continue

        matches = _get_matches(name, choices, limit=suggest_limit)
        if not matches:
            console.print(f"[red]No suggestions found for '{name}'. Keeping as-is.[/red]")
            resolved.append(name)
            continue

        best_match, best_score = matches[0]

        # Auto-accept if score high enough
        if best_score >= auto_accept_threshold:
            console.print(
                f"[yellow]Assuming '{best_match}' for '{name}' (similarity {best_score}%).[/yellow]"
            )
            resolved.append(best_match)
            continue

        # Interactive selection
        table = Table(title=f"Select repository for '{name}'")
        table.add_column("#", justify="right")
        table.add_column("Repository", style="cyan")
        table.add_column("Score", justify="right", style="green")
        for idx, (candidate, score) in enumerate(matches, 1):
            table.add_row(str(idx), candidate, f"{score}")
        table.add_row("0", "[dim]Keep original[/dim]", "")
        console.print(table)

        choice_nums = [str(i) for i in range(0, len(matches) + 1)]
        choice = Prompt.ask("Enter choice", choices=choice_nums, default="0")
        if choice == "0":
            resolved.append(name)
        else:
            resolved.append(matches[int(choice) - 1][0])

    return resolved


__all__ = ["resolve_names"] 