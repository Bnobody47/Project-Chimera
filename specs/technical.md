---
description: Technical architecture, schemas, and interfaces.
---

# Technical Specification

## Architecture
- Pattern: Hierarchical Swarm (Planner → Worker → Judge) with optional sub-planners; OCC at Judge commit.
- Transport: Redis queues (`task_queue`, `review_queue`); Planner polls perception signals and goals.
- External I/O: MCP only; stdio/SSE transports to MCP servers (twitter, ideogram/midjourney, runway/luma, coinbase, weaviate, sqlite exemplar).
- Tenancy: Hub-and-spoke; orchestrator maintains tenant-scoped configs and ensures isolation of memories/wallets.
- Observability: Telemetry via Tenx MCP Sense; audit log of all MCP tool calls to Postgres + on-chain ledger for commerce.

## Data Models (contracts)
- Task (queue payload): `{task_id, task_type, priority, context{goal_description, persona_constraints[], required_resources[]}, assigned_worker_id, created_at, status}`
- Result (review payload): `{task_id, worker_id, status, artifact_ref, confidence_score, reasoning_trace, state_version}`
- AgentPersona: parsed from `SOUL.md` (frontmatter: `id`, `name`, `voice_traits[]`, `directives[]`; body: `backstory`).
- WalletPolicy: `{agent_id, max_daily_usdc, max_tx_usdc, allowed_assets[], reviewer_required:boolean}`
- AuditEvent: `{event_id, actor_id, action, payload, timestamp, state_version}`
- VideoMetadata (NoSQL): `{video_id, owner_agent_id, metrics{minute_buckets, hour_buckets}, tags[], canonical_attrs{title,duration,language}}`

## APIs / MCP Tool Contracts (examples)
- `post_content`: `{platform: enum[twitter,instagram,threads], text_content: string, media_urls?: string[], disclosure_level?: enum[automated,assisted,none]}`
- `reply_content`: `{platform, in_reply_to_id: string, text_content: string}`
- `generate_image`: `{prompt: string, character_reference_id: string, style?: string}`
- `generate_video`: `{storyboard: string, tier: enum[daily,hero], ref_images?: string[]}`
- `search_memory` (Weaviate): `{agent_id: string, query: string, k: int}`
- `wallet_get_balance`: `{agent_id}`
- `wallet_transfer`: `{agent_id, to_address, amount_usdc, asset?: string}`
- `trend_resource_read`: `news://latest` style resource returning list of headlines/urls.

## Context Assembly
- Inputs: `agent_id`, `input_query`.
- Steps: load persona from SOUL.md; fetch short-term context (Redis, last hour); fetch long-term memories (Weaviate top-k); build structured prompt sections: "Who You Are", "What You Remember", "Current Input", "Constraints".

## HITL & Governance
- Confidence tiers: >0.90 auto, 0.70–0.90 async HITL, <0.70 reject/retry; sensitive topics always HITL.
- CFO Judge: wraps commerce tools with `budget_check` decorator; enforces `max_daily_usdc` and `max_tx_usdc`; uses Redis counter + Postgres source of truth.
- Disclosure: set platform flags (e.g., `is_generated`) on publish; honesty directive for identity questions.

## Error Handling
- Retries with jitter for tool/resource timeouts.
- Circuit-breaker at MCP server layer on repeated failures.
- OCC conflict => requeue for Planner with updated `state_version`.
- Missing keys/secrets => fail fast and alert.

## Performance Targets
- High-priority interaction latency ≤10s end-to-end (excluding HITL).
- Horizontal scale to 1k concurrent agents; stateless Planner/Judge services; Worker pool autoscaling.

## Testing Strategy (pre-implementation)
- Unit tests for schemas (Task/Result/Persona parsing).
- Contract tests for MCP tool payloads (validate JSON schema).
- OCC simulation test to ensure conflict rejection.
- HITL routing test: confidence tiers and sensitive-topic override.
- Budget governance test: ensures overspend blocked and counter updated.

## Deployment & DevEx
- Dockerfile encapsulates runtime; Makefile targets: `setup`, `test`, `spec-check` (optional).
- CI: GitHub Actions runs Dockerized tests on push.
- Env: Python (uv recommended), redis-py, pydantic, weaviate-client, coinbase-agentkit, mcp SDK.
