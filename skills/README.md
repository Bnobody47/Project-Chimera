# Project Chimera Skills (Runtime Packages)

Definition: A Skill is a reusable capability module the agent can invoke (often wrapping MCP tools/resources with business logic). Each Skill declares clear IO contracts; implementations can be stubs initially.

## skill_trend_fetcher
- Purpose: Poll news/social resources, score relevance, emit Trend Alerts.
- Inputs: `{agent_id, niches[], relevance_threshold: float, lookback_hours: int}`
- Process: Reads MCP resources (`news://latest`, `twitter://mentions`), runs semantic filter (LLM-lite), clusters topics over time window.
- Outputs: `[{topic, score, sources[], suggested_tasks[]}]`
- Notes: Should be side-effect free; only creates Planner tasks when score >= threshold.

## skill_content_generator
- Purpose: Produce text + media drafts with persona and consistency lock.
- Inputs: `{agent_id, goal, channel: enum[twitter,instagram,threads], style_overrides?, assets?}`
- Process: Assembles persona/memory context; generates copy; calls MCP media tools with `character_reference_id`; returns draft package.
- Outputs: `{text, media_urls?, confidence_score, reasoning_trace, requires_hitl: bool}`
- Notes: Judge validates media likeness; disclosure flag included in publish payload.

## skill_commerce_manager
- Purpose: Safe on-chain actions under CFO policy.
- Inputs: `{agent_id, action: enum[transfer, check_balance, deploy_token], to_address?, amount_usdc?, asset?, memo?}`
- Process: Runs `budget_check` (Redis + Postgres policy), calls coinbase-agentkit MCP, logs AuditEvent.
- Outputs: `{status: enum[approved,blocked], tx_hash?, error?}`
- Notes: Defaults to testnet/sim; blocks if keys/policies missing or limits exceeded.

## Conventions
- Skills are pure modules; external calls only through MCP tools/resources.
- All outputs include `reasoning_trace` and `state_version` when relevant for OCC/Judge steps.
- Validation and HITL routing happen after Skill execution via Judges.
