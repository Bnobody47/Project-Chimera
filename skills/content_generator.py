"""
skill_content_generator — Produce text + media drafts with persona and consistency lock.
Contract: specs/technical.md, skills/README.md
Inputs: agent_id, goal, channel, style_overrides?, assets?
Outputs: {text, media_urls?, confidence_score, reasoning_trace, requires_hitl}
"""

# Stub: Not yet implemented. Tests define the contract.


def generate_content(
    agent_id: str,
    goal: str,
    channel: str,
    style_overrides: dict | None = None,
    assets: list[str] | None = None,
) -> dict:
    """Return {text, media_urls?, confidence_score, reasoning_trace, requires_hitl}. Stub raises."""
    raise NotImplementedError("skill_content_generator not implemented")
