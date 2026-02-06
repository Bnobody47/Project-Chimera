# Project Chimera

Spec-driven workspace for the **Project Chimera: Agentic Infrastructure Challenge** — a factory for autonomous influencer agents (Planner → Worker → Judge) built on MCP and Spec Kit.

## Overview
- **Goal**: Provide a repository so well specified and tooled that a swarm of AI agents can safely build final features with minimal conflict.
- **Approach**: Spec-Driven Development (GitHub Spec Kit), MCP-first integrations, TDD, Dockerized tests, and CI/CD with AI governance.

## Repo Layout
- `specs/`: master specifications (`_meta`, `functional`, `technical`, `openclaw_integration`).
- `research/`, `research_*.md`: architecture and tooling strategy notes.
- `.cursor/rules/`: Cursor rules (project context, Prime Directive, traceability, MCP-first).
- `skills/`: runtime skill modules (`trend_fetcher`, `content_generator`, `commerce_manager`) — stubs + IO contracts.
- `tests/`: TDD tests defining API/data contracts; **expected to fail** until implementations are built.
- `.specify/`: GitHub Spec Kit artifacts (constitution, scripts, templates).
- `Dockerfile`, `Makefile`: containerized dev/test environment and standard commands.
- `.github/workflows/main.yml`: CI running `make test` and `make spec-check` on push.
- `.coderabbit.yaml`: AI review policy (spec alignment, security, MCP-first).

## Quick Start
```bash
make setup        # Install deps
make test         # Run tests (TDD: some will fail)
make spec-check   # Verify spec & repo structure
make docker-test  # Run tests inside Docker
```

## Spec Kit Usage
- Installed via `specify-cli` from `github/spec-kit`.
- Initialized with `specify init . --ai cursor-agent --script ps`.
- Constitution: `.specify/memory/constitution.md` encodes Chimera’s principles (spec-first, MCP-first, Planner/Worker/Judge, HITL, TDD, security).

Telemetry: Tenx feedback analytics MCP configured via `.cursor/mcp.json`.
