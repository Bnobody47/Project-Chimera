"""
TDD: Asserts that the trend data structure matches the API contract.
Contract: specs/technical.md, skills/README.md — skill_trend_fetcher outputs
[{topic, score, sources[], suggested_tasks[]}]
These tests SHOULD fail until the implementation fulfills the contract.
"""

import pytest

# Import will fail until skill module exists; once stubbed, call will raise or return wrong shape
from skills.trend_fetcher import fetch_trends


def test_trend_fetcher_returns_list():
    """Trend fetcher must return a list of trend objects."""
    result = fetch_trends(
        agent_id="agent-001",
        niches=["fashion", "lifestyle"],
        relevance_threshold=0.75,
        lookback_hours=24,
    )
    assert isinstance(result, list), "fetch_trends must return a list"


def test_trend_item_has_required_fields():
    """Each trend item must have: topic, score, sources, suggested_tasks."""
    result = fetch_trends(
        agent_id="agent-001",
        niches=["fashion"],
        relevance_threshold=0.75,
        lookback_hours=4,
    )
    required = {"topic", "score", "sources", "suggested_tasks"}
    for i, item in enumerate(result):
        assert isinstance(item, dict), f"Item {i} must be a dict"
        missing = required - set(item.keys())
        assert not missing, f"Item {i} missing keys: {missing}"


def test_trend_item_field_types():
    """Validate field types: topic str, score float, sources list, suggested_tasks list."""
    result = fetch_trends(
        agent_id="agent-001",
        niches=["tech"],
        relevance_threshold=0.7,
        lookback_hours=12,
    )
    for i, item in enumerate(result):
        assert isinstance(item.get("topic"), str), f"Item {i}: topic must be str"
        assert isinstance(item.get("score"), (int, float)), f"Item {i}: score must be numeric"
        assert isinstance(item.get("sources"), list), f"Item {i}: sources must be list"
        assert isinstance(item.get("suggested_tasks"), list), f"Item {i}: suggested_tasks must be list"


def test_trend_score_in_valid_range():
    """Score must be in [0.0, 1.0]."""
    result = fetch_trends(
        agent_id="agent-001",
        niches=["lifestyle"],
        relevance_threshold=0.75,
        lookback_hours=24,
    )
    for i, item in enumerate(result):
        score = item.get("score")
        assert 0.0 <= score <= 1.0, f"Item {i}: score {score} must be in [0, 1]"
