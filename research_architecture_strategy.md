Project Chimera — Research & Architecture Strategy
==================================================

Document purpose: capture the architecture decisions, patterns, and implementation strategy before coding begins. Focus areas: Agent Pattern, Human-in-the-Loop placement, and database strategy for high-velocity video metadata. Diagrams use Mermaid.js.

Executive Decision Summary
--------------------------

**Agent Pattern (Decision)**: Hierarchical Swarm (FastRender Pattern) — Planner → Workers → Judges, with optional Sub-Planners and Manager Agents for multi-tenant control.

**Human-in-the-Loop (Decision)**: Judge-stage HITL escalation with configurable confidence thresholds and mandatory human review for sensitive topics. The Orchestrator Dashboard provides a fast-review UI and triage controls.

**Database (Decision)**: Hybrid SQL + NoSQL:
- NoSQL (primary) for high-velocity, append-mostly video metadata, metrics and time-series (e.g., Cassandra / Scylla / sharded MongoDB).
- SQL (authoritative) for agent definitions, campaign configuration, ACLs, billing and transactional data (PostgreSQL).

**Rationale**: this mix maximizes throughput for hot data while preserving ACID guarantees for mission-critical configuration and financial records.

1. Agent Pattern — Hierarchical Swarm
-------------------------------------

### 1.1 Structure

- **Planner (The Strategist)**: decomposes goals into DAGs; spawns Sub-Planners for domain-specific tasks (social engagement, media production, finance).
- **Worker (The Executor)**: ephemeral, stateless, single-responsibility executors that call MCP Tools (`generate_image`, `post_content`, `query_memory`).
- **Judge (The Gatekeeper)**: QA, policy enforcement, and OCC-based commit authority. Judges produce `confidence_score` and route to HITL when required.
- **Orchestrator (Human-level control)**: single Super-Orchestrator for fleet-level config and multi-tenant policy (BoardKit pattern).

### 1.2 Why hierarchical swarm?

- **Parallelism**: thousands of Workers can execute concurrently (scale horizontally).
- **Specialization**: separate roles for planning, execution and validation leads to robust error handling and self-healing.
- **Resilience**: isolation of Workers prevents cascading failures; Judges enforce consistency using OCC.

2. Human-in-the-Loop (HITL) — Placement & Policy
------------------------------------------------

### 2.1 Placement

Primary placement: immediately after Worker result generation and **before any external side-effecting action** (i.e. before MCP Tool calls that mutate external systems). Judges produce a `confidence_score` and route:

- \> 0.90: **Auto-approve and execute.**
- 0.70–0.90: **Pause; push to HITL queue for Async Approval.**
- \< 0.70: **Reject and re-plan.**

Sensitive topics (override): always require human approval regardless of score.

### 2.2 UI/UX Requirements for Reviewers

- **Compact review cards** showing: content preview, persona constraints, reasoning trace, `confidence_score`, attachments (image/video preview), suggested edits.
- **Fast actions**: Approve, Request Edit, Reject, Escalate to Legal/Compliance.
- **Keyboard-first moderation** with configurable batch approvals for high-confidence items.

### 2.3 Operational Playbooks

- Define triage rules: e.g., small edits can be handled by Moderators; legal escalation only for flagged topics.
- SLAs: target median review time for Async Approval queues (configurable per campaign). Avoid blocking Planner threads — Judges should proceed with other tasks while waiting on HITL decisions.

3. Database Strategy — SQL vs NoSQL (Hybrid)
--------------------------------------------

### 3.1 Data categories & recommendation

- **Hot streaming metadata (NoSQL)**: real-time view counts, per-second engagement metrics, trending signals, live reaction streams.
  - Use a partitioned, write-optimized, horizontally-scalable NoSQL (Cassandra / Scylla for time-series; or MongoDB with sharding for document-based metadata).
  - Schema: document per video with nested rolling metrics buckets (minute/hour/day) to support quick aggregations.
- **Warm/cold analytics (OLAP)**: aggregated event tables stored in data lake (S3) and queried by analytical engines (Spark, Dremio).
- **Canonical transactional data (SQL)**: agent definitions (SOUL.md metadata), campaigns, user accounts, billing, wallets, and legal audit records → PostgreSQL (clustered).

### 3.2 Example data flow

- **Ingest**: MCP Resource → Stream (Kafka / Kinesis)
- **Real-time pipeline**: Stream → Processor (Flink/Spark Streaming) → NoSQL (hot metrics) + Event Store (append-only) → downstream OLAP
- **Transactional writes** (e.g., campaign changes, wallet operations) → PostgreSQL with strongly consistent commits

### 3.3 Why not SQL-only?

- High throughput writes and time-series aggregations can overwhelm a single relational cluster; horizontal scale and predictable latency favor NoSQL for hot path.
- However, SQL remains essential for transactional integrity (money movement, policy updates, audit logs) and complex relational queries.

4. Architecture Diagrams (Detailed)
-----------------------------------

*(Use Mermaid.js for sequence, component, and data-flow diagrams. Placeholder section for future diagrams.)*

5. Operations, Security & Compliance
------------------------------------

- **Secrets management**: HashiCorp Vault / AWS Secrets Manager for injecting wallet keys at runtime; never persist private keys in logs or DB.
- **Budget governance**: CFO Judge enforces daily/weekly budgets stored in Postgres and cached in Redis for fast checks (decorate `send_payment` with `budget_check`).
- **Auditability**: immutable event log for all external actions written to Postgres + on-chain ledger for financial transactions.
- **Rate-limits & throttling**: enforce at MCP Server layer; apply dry-run/publish toggles for staging.
- **Privacy & regulation**: automated disclosure flags (set `is_generated`) and mandatory human review for sensitive categories to align with EU AI Act style rules.

6. Protocol Checklist — Agent-to-Agent Social Protocols
-------------------------------------------------------

- **Identity & Authentication**: Agent DID (Decentralized Identifier) + signed statements (JWT or linked-wallet signatures). Map DIDs to SOUL.md persona hashes.
- **Discovery**: MCP-based registry (`mcp://directory`) where agents advertise capabilities, SKILL manifests, and endpoints.
- **Trust signaling**: reputation score, signed attestations, on-chain bond or stake for high-sensitivity interactions.
- **Negotiation/Commerce**: simple JSON-based handshake for proposals (offer/counter-offer/accept) with on-chain escrow option for financial deals.
- **Rate & Spam Defense**: rate-limits, challenge-response (proof-of-work or stake) for unknown agents.

Include these as MCP Tool/Resource standards to ensure cross-compatibility with OpenClaw/Moltbook style ecosystems.

7. Data Models (high-level)
---------------------------

- **AgentPersona (Postgres / SOUL.md)** — `id`, `name`, `persona_hash`, `directives`, `default_budget`, `allowed_topics`.
- **Task (TaskQueue payload)** — `task_id`, `task_type`, `priority`, `context`, `created_at`, `assigned_worker_id`, `status`.
- **VideoMetadata (NoSQL)** — `video_id`, `owner_agent_id`, `timestamps[]`, `metrics:{minute_buckets, hour_buckets}`, `tags[]`, `canonical_attrs{title,duration,language}`.
- **AuditEvent (Postgres/EventStore)** — `event_id`, `actor_id`, `action`, `payload`, `timestamp`, `state_version`.

8. Next Steps & Deliverables
----------------------------

- Approve this architecture doc or mark optional changes (e.g., prefer Scylla vs Cassandra, or use Vitess for SQL scaling).
- Create PR for BoardKit policy schema (`AGENTS.md`) using the Persona schema shown in SRS.
- Prototype: implement Phase 1: Planner/Worker/Judge skeleton with Redis queues and mocked MCP servers.
- Integration tests: OCC behavior simulation and HITL queue latency tests.

Appendix A — Merits & Tradeoffs
-------------------------------

- **Hierarchical Swarm pros**: high concurrency, fault isolation, specialized validation.
- **Hierarchical Swarm cons**: more moving parts, harder to reason about distributed state.
- **Sequential Chain pros**: simpler message flow and debugging.
- **Sequential Chain cons**: limited parallelism, brittle when tasks branch.

---

Document authored for **Project Chimera — Research & Architecture Strategy**.

