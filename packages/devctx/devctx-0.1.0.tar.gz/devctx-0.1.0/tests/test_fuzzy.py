"""Tests for fuzzy matching helper functions."""

from unittest.mock import patch

from devctx.fuzzy import resolve_names


def test_exact_matches():
    choices = ["indicore", "workflows", "cyclone"]
    names = ["indicore", "workflows"]
    result = resolve_names(names, choices)
    assert result == names


def test_auto_accept_high_score():
    choices = ["workflows"]
    names = ["workflws"]  # missing 'o'
    with patch("devctx.fuzzy.console.print"):
        result = resolve_names(names, choices, auto_accept_threshold=80)
    assert result == ["workflows"]


def test_no_match_returns_original():
    choices = ["indicore"]
    names = ["unknown"]
    # Patch console.print to avoid clutter
    with patch("devctx.fuzzy.console.print"), patch("devctx.fuzzy.Prompt.ask", return_value="0"):
        result = resolve_names(names, choices)
    assert result == ["unknown"] 