# Project Chimera Constitution

## Core Principles

### I. Spec-Driven Development (Non‑Negotiable)
- All implementation work starts from ratified specs in `specs/` and the SRS.
- New behavior must first be expressed as requirements and contracts (JSON schemas, ERDs, HITL rules) before code is written.
- Ambiguity is treated as a defect; clarify via Spec Kit (`/speckit.clarify`, `/speckit.specify`, `/speckit.plan`) before implementation.

### II. MCP-First Integration
- The agent core never calls third‑party APIs directly; all external I/O flows through MCP servers and tools.
- Social platforms, vector stores, news feeds, and commerce are accessed only via MCP, so reasoning logic stays decoupled from vendors.

### III. Hierarchical Swarm & HITL Governance
- Planner → Worker → Judge (FastRender pattern) is the default architecture for all agent features.
- Judges enforce confidence tiers, sensitive‑topic routing, OCC, and CFO budget checks; humans remain the ultimate escalation path.
- Any change to Planner/Worker/Judge behavior must preserve these governance guarantees.

### IV. Test-First & Quality Gates
- Tests in `tests/` define the API and data contracts (e.g., skills interfaces, trend structures) before implementations exist.
- It is acceptable and expected for tests to fail until the feature is built; removing or weakening tests requires spec updates.
- CI (GitHub Actions) and Docker are the canonical execution paths for tests and spec checks.

### V. Security, Traceability & Observability
- Secrets (API keys, wallet material) never live in the repo; use environment variables or secret managers.
- Engineers and agents must explain their plan and cite relevant specs/ and research docs before substantial changes.
- Telemetry (Tenx MCP Sense, logs, audit events) is required for debugging and post‑hoc analysis.

## Additional Constraints & Standards
- Tech stack: Python, Redis, Postgres, NoSQL store, Weaviate, Coinbase AgentKit, MCP servers as defined in `specs/technical.md`.
- Multi‑tenancy and data isolation are mandatory for all new capabilities.
- Swarm and commerce features must respect cost/budget constraints and regulatory transparency (AI disclosure, auditability).

## Development Workflow & Reviews
- Use Spec Kit commands (`/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`) to structure work.
- Every significant change:
  - References the relevant spec sections and SRS paragraphs.
  - Updates tests and/or contracts alongside implementation.
  - Runs `make test` (locally or via Docker) before merging.
- Code review and AI review (e.g., CodeRabbit) must check for spec alignment, security, and adherence to this constitution.

## Governance
- This constitution supersedes ad‑hoc practices; exceptions must be documented in specs and justified.
- Amendments require:
  - A spec update describing the motivation and impact.
  - Agreement on migration or deprecation paths.
  - Version bump in this file with dates and rationale.

**Version**: 1.0.0 | **Ratified**: 2026‑02‑05 | **Last Amended**: 2026‑02‑05
