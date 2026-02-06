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

## Acceptance Criteria (Formal Syntax)

### Scenario: Planner-Worker-Judge Flow with OCC

**Given** a campaign goal "Promote summer fashion collection" exists for agent `@fashion_ai`  
**When** the Planner decomposes the goal into tasks  
**Then** tasks are created in `task_queue` with `status='pending'`  
**And** each task has `task_id`, `task_type`, `priority`, `context`, `state_version=0`

**Given** a Worker claims a task from `task_queue`  
**When** the Worker executes the task and calls MCP tools (`generate_image`, `post_content`)  
**Then** a Result is created with `status='success'`, `confidence_score`, `reasoning_trace`, `state_version`  
**And** the Result is pushed to `review_queue`

**Given** a Result exists in `review_queue` with `confidence_score=0.85`  
**When** the Judge reviews the Result  
**Then** the Result is routed to HITL queue (`status='requires_hitl'`)  
**And** an HITL item is created with `agent_id`, `content_preview`, `confidence_score`

**Given** a Judge attempts to commit a Result with `state_version=5`  
**When** the global state has `state_version=7` (OCC conflict)  
**Then** the commit is rejected (`409 Conflict`)  
**And** the task is re-queued for Planner re-evaluation

**Performance Threshold**: End-to-end latency (goal → published) ≤ 10 seconds for high-priority tasks (excluding HITL time)

### Scenario: MCP-Only External I/O

**Given** an agent needs to post content to Twitter  
**When** the Worker executes the task  
**Then** the Worker calls `mcp-server-twitter.post_content` tool (not Twitter SDK directly)  
**And** the MCP server enforces rate limits and dry-run flags  
**And** all tool calls are logged to `audit_events`

**Given** an agent needs to fetch trends  
**When** the Planner polls perception resources  
**Then** the Planner reads `mcp://news/latest` resource (not NewsAPI directly)  
**And** semantic filtering scores relevance; only items with `score >= 0.75` create tasks

**Link to Spec**: `specs/technical.md` - "APIs / MCP Tool Contracts"

### Scenario: Persona & Memory Context Assembly

**Given** an agent `@fashion_ai` with `SOUL.md` defining voice traits and backstory  
**When** the Worker assembles context for content generation  
**Then** the system loads persona from `SOUL.md` (YAML frontmatter + markdown body)  
**And** fetches short-term context from Redis (last 1 hour)  
**And** queries Weaviate for top-5 semantically relevant memories  
**And** constructs prompt sections: "Who You Are", "What You Remember", "Current Input", "Constraints"

**Performance Threshold**: Context assembly completes in < 500ms

**Link to Spec**: `specs/technical.md` - "Context Assembly"

### Scenario: Media Generation with Character Consistency

**Given** an agent `@fashion_ai` with `character_reference_id='char_abc123'`  
**When** the Worker calls `generate_image` MCP tool  
**Then** the request includes `character_reference_id='char_abc123'` in payload  
**And** the generated image is validated by Vision Judge  
**And** if likeness check fails, the Result is rejected and task re-queued

**Given** a generated image passes Vision Judge  
**When** the image is published  
**Then** the platform `is_generated` flag is set  
**And** the media URL is stored in `VideoMetadata` collection

**Link to Spec**: `specs/technical.md` - "Creative Engine"

### Scenario: Budget Governance & Agentic Commerce

**Given** an agent `@fashion_ai` with `wallet_policy.max_daily_usdc=50.0`  
**And** the agent has spent `$45.0` today (tracked in Redis `daily_spend` counter)  
**When** a Worker attempts to transfer `$10.0 USDC`  
**Then** the CFO Judge decorator checks `daily_spend + amount > max_daily_usdc`  
**And** the transaction is blocked (`status='blocked'`, `error='Budget exceeded'`)  
**And** an `audit_event` is created with `action='commerce_blocked'`

**Given** an agent attempts a transaction on mainnet  
**When** the environment variable `USE_TESTNET=true`  
**Then** the transaction is routed to Base Sepolia testnet  
**And** a warning is logged: "Mainnet transaction blocked; using testnet"

**Performance Threshold**: Budget check completes in < 100ms

**Link to Spec**: `specs/security.md` - "Resource Limits", `specs/technical.md` - "HITL & Governance"

### Scenario: Dashboard & HITL Queue Visibility

**Given** a Network Operator is authenticated with `role='network_operator'`  
**When** the operator accesses `/dashboard`  
**Then** the API returns agent list, active task count, HITL queue depth  
**And** the frontend displays StatCards and AgentTable  
**And** all data is tenant-scoped (operator's `tenant_id` from JWT)

**Given** a Human Reviewer accesses `/hitl-queue`  
**When** the reviewer approves an item  
**Then** `POST /api/v1/judge/hitl-decision` is called with `decision='approve'`  
**And** the Result status changes to `'success'`  
**And** the task proceeds to publish (if applicable)

**Link to Spec**: `specs/frontend.md` - "Screens & Wireframes", `specs/technical.md` - "Backend API Contract"

## Edge Cases & Errors
- API timeouts: retry with backoff; self-healing triage agent requeues failures.
- State drift: Judge rejects if `state_version` changed; Planner re-plans.
- Rate limit: MCP server enforces and surfaces `retry_after`.
- Wallet key missing: fail fast, block commerce tasks.
- Memory miss: degrade gracefully using persona + recent context only.

## Dependencies
- Redis (queues, cache), PostgreSQL (config/audit), NoSQL store (hot metrics), Weaviate (vector), MCP servers (twitter, ideogram, runway/luma, coinbase, sqlite exemplar), Tenx MCP Sense telemetry.
