# ADR-0001: Hierarchical Swarm Architecture (Planner-Worker-Judge)

**Status**: Accepted  
**Date**: 2026-02-05  
**Deciders**: Architecture Team

## Context

Project Chimera requires autonomous agents that can plan, execute, and validate actions at scale. We need an architecture that supports:
- High parallelism (1000+ concurrent agents)
- Quality assurance and governance
- Error recovery and self-healing
- Human-in-the-loop escalation

## Decision

Adopt the **Hierarchical Swarm** pattern (FastRender-inspired) with three specialized roles:

1. **Planner**: Decomposes goals into Task DAGs, monitors global state, dynamic re-planning
2. **Worker**: Stateless executors that pull tasks, call MCP tools, return artifacts
3. **Judge**: Quality gatekeeper, applies confidence tiers, OCC validation, HITL routing

## Consequences

**Positive**:
- High throughput via parallel Workers
- Fault isolation (Worker failures don't cascade)
- Specialized validation (Judge enforces governance)
- Scalable (horizontal Worker pool)

**Negative**:
- More moving parts (3 services vs monolithic)
- OCC complexity (state versioning required)
- Network overhead (Planner → Worker → Judge handoffs)

**Alternatives Considered**:
- Sequential Chain: Simpler but limited parallelism, brittle
- Monolithic Agent: Single LLM call, but no governance, hard to scale

## References

- `research_architecture_strategy.md` - Detailed rationale
- `specs/technical.md` - Architecture section
- FastRender browser project (inspiration)
