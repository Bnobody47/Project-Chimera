---
description: Functional requirements and user stories for Chimera.
---

# Functional Specification

## User Stories
- As a Network Operator, I define campaign goals and see task/status per agent.
- As a Worker Agent, I pull tasks, call MCP tools/resources, and return artifacts.
- As a Judge, I score confidence, enforce persona/policy, and route to HITL when needed.
- As a Human Reviewer, I approve/reject/annotate pending items quickly.
- As a CFO Judge, I block or approve on-chain transactions within budget caps.
- As a Developer, I add MCP servers (tools/resources) without changing agent logic.

## Core Flows
1) Goal → Plan → Execute → Review → Publish  
   - Planner decomposes goals into Task DAG; pushes to `task_queue`.  
   - Workers execute single tasks, use MCP tools (post_content, generate_image, search_memory, coinbase actions).  
   - Judges validate outputs, apply OCC, route to HITL or commit.

2) HITL Routing  
   - Confidence >0.90 auto-approve; 0.70–0.90 async queue; <0.70 reject/replan.  
   - Sensitive topics always HITL regardless of score.

3) Persona & Memory  
   - Persona defined in `SOUL.md`; loaded via YAML frontmatter + markdown body.  
   - Before inference, assemble context from Redis (short-term) + Weaviate (long-term) + persona.

4) Perception  
   - Poll MCP resources (e.g., twitter://mentions, news://latest).  
   - Semantic filter (LLM-lite) scores relevance; only high-score items create tasks.

5) Creative Engine  
   - Text via LLM; images via ideogram/midjourney MCP; video via runway/luma tiers.  
   - Character Consistency enforced by injecting `character_reference_id` on media requests.  
   - Vision Judge checks likeness before publish.

6) Action System  
   - All social actions through MCP tools; rate limits and dry-run flags enforced at MCP layer.

7) Agentic Commerce  
   - Each agent has non-custodial wallet (Coinbase AgentKit).  
   - CFO Judge checks `get_balance`, budget caps, anomaly patterns before any transaction.

## Acceptance Criteria (MVP)
- Tasks flow Planner→Worker→Judge with OCC versioning and HITL logic.
- MCP-only I/O; no direct platform SDK calls from agent core.
- Persona context assembly uses Redis + Weaviate and injects SOUL.md.
- Media generation requests include consistency token; Judge vision check exists.
- Budget governance decorator blocks overspend; testnets only by default.
- Dashboard surfaces agent state, HITL queue, balances at least in JSON/API mock.

## Edge Cases & Errors
- API timeouts: retry with backoff; self-healing triage agent requeues failures.
- State drift: Judge rejects if `state_version` changed; Planner re-plans.
- Rate limit: MCP server enforces and surfaces `retry_after`.
- Wallet key missing: fail fast, block commerce tasks.
- Memory miss: degrade gracefully using persona + recent context only.

## Dependencies
- Redis (queues, cache), PostgreSQL (config/audit), NoSQL store (hot metrics), Weaviate (vector), MCP servers (twitter, ideogram, runway/luma, coinbase, sqlite exemplar), Tenx MCP Sense telemetry.
