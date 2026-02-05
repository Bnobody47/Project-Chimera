# Project Chimera

Spec-driven workspace for the Autonomous Influencer Network (Chimera).

## Repo Layout
- `specs/`: master specifications (`_meta`, functional, technical, openclaw plan).
- `research/`, `research_*.md`: architecture and tooling strategy notes.
- `.cursor/rules/`: persistent Cursor rules (Prime Directive, MCP-first).
- `skills/`: runtime skill modules (trend fetcher, content generator, commerce manager) — stubs + contracts.
- `tests/`: TDD tests defining API contracts; expected to fail until implementations complete.
- `Dockerfile`, `Makefile`: containerized dev/test environment.
- `.github/workflows/main.yml`: CI runs `make test` in Docker on push.
- `.coderabbit.yaml`: AI review policy (spec alignment, security).

## Quick Start
```bash
make setup    # Install deps
make test     # Run tests (TDD: some will fail)
make spec-check   # Verify spec structure
make docker-test  # Run tests inside Docker
```

Telemetry: Tenx feedback analytics MCP configured via `.cursor/mcp.json`.
