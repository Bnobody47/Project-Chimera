---
description: High-level vision, scope, and constraints for Project Chimera.
---

# Project Chimera — Master Specification Meta

## Vision
Build a scalable network of autonomous influencer agents that plan, create, and publish content with MCP-native integrations, HITL safety, and on-chain economic agency.

## Goals
- Ship a reliable Planner/Worker/Judge swarm with OCC and HITL routing.
- Standardize external interactions through MCP tools/resources (no ad-hoc API calls).
- Enable agentic commerce with Coinbase AgentKit under strict budget governance.
- Maintain persona consistency via SOUL.md + hierarchical memory.

## Non-Goals
- Full production media models (use mocked/hosted services for now).
- Full UI polish; only functional dashboard/HITL views are required.
- On-chain deployment of real funds during prototyping (use testnets/simulators).

## Stakeholders
- Network Operators (strategy), Human Reviewers (HITL), Developers/Architects, Compliance/Finance reviewers.

## Scope & Constraints
- Multi-tenant isolation; per-tenant data/firewall boundaries.
- MCP-only external I/O; enforce rate limits and dry-run toggles.
- Regulatory transparency: AI disclosure and sensitive-topic escalation.
- Cost controls: Resource Governor + CFO Judge with daily spend caps.

## Success Criteria
- Specs drive implementation (no coding without alignment to `specs/`).
- Failing tests exist for core contracts before implementation.
- MCP telemetry connected (Tenx Sense) to trace agent/system behavior.
- Dockerized, reproducible dev environment; CI runs tests on push.

## References
- Business and technical requirements: `Project Chimera SRS Document_ Autonomous Influencer Network.pdf`.
- 3-Day Challenge tasks: `Project_Chimera_3Day_Challenge.md.pdf`.
