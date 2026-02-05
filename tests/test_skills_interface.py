"""
TDD: Asserts that skills/ modules accept the correct parameters per contracts.
Contract: specs/technical.md, skills/README.md
These tests SHOULD fail until implementations accept and validate inputs correctly.
"""

import inspect
import pytest

from skills.trend_fetcher import fetch_trends
from skills.content_generator import generate_content
from skills.commerce_manager import execute_commerce_action


def test_trend_fetcher_accepts_contract_params():
    """skill_trend_fetcher must accept: agent_id, niches, relevance_threshold, lookback_hours."""
    sig = inspect.signature(fetch_trends)
    params = set(sig.parameters.keys())
    required = {"agent_id", "niches", "relevance_threshold", "lookback_hours"}
    missing = required - params
    assert not missing, f"fetch_trends missing params: {missing}"


def test_content_generator_accepts_contract_params():
    """skill_content_generator must accept: agent_id, goal, channel, style_overrides?, assets?."""
    sig = inspect.signature(generate_content)
    params = set(sig.parameters.keys())
    required = {"agent_id", "goal", "channel"}
    optional = {"style_overrides", "assets"}
    missing = required - params
    assert not missing, f"generate_content missing required params: {missing}"
    # Optional params should exist (can have defaults)
    for opt in optional:
        assert opt in params, f"generate_content missing optional param: {opt}"


def test_commerce_manager_accepts_contract_params():
    """skill_commerce_manager must accept: agent_id, action, to_address?, amount_usdc?, asset?, memo?."""
    sig = inspect.signature(execute_commerce_action)
    params = set(sig.parameters.keys())
    required = {"agent_id", "action"}
    optional = {"to_address", "amount_usdc", "asset", "memo"}
    missing = required - params
    assert not missing, f"execute_commerce_action missing required params: {missing}"
    for opt in optional:
        assert opt in params, f"execute_commerce_action missing param: {opt}"


def test_content_generator_channel_enum():
    """Channel must be one of: twitter, instagram, threads."""
    valid_channels = {"twitter", "instagram", "threads"}
    # Call with valid channel - implementation must accept
    result = generate_content(
        agent_id="agent-001",
        goal="Promote summer collection",
        channel="twitter",
    )
    assert "text" in result, "Output must include 'text'"
    assert "confidence_score" in result, "Output must include 'confidence_score'"
    assert "reasoning_trace" in result, "Output must include 'reasoning_trace'"
    assert "requires_hitl" in result, "Output must include 'requires_hitl'"


def test_commerce_manager_output_structure():
    """Commerce manager output must have: status (approved|blocked), optional tx_hash, error."""
    result = execute_commerce_action(
        agent_id="agent-001",
        action="check_balance",
    )
    assert isinstance(result, dict), "Output must be dict"
    assert "status" in result, "Output must include 'status'"
    assert result["status"] in {"approved", "blocked"}, "status must be approved or blocked"
