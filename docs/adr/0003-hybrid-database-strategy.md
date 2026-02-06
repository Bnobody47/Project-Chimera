# ADR-0003: Hybrid SQL + NoSQL Database Strategy

**Status**: Accepted  
**Date**: 2026-02-05  
**Deciders**: Architecture Team

## Context

Chimera needs to store:
- Authoritative config data (agents, campaigns, wallets) requiring ACID guarantees
- High-velocity metrics (video engagement, real-time trends) requiring high write throughput
- Semantic memories (long-term agent knowledge) requiring vector search

## Decision

Use a **hybrid approach**:

- **PostgreSQL**: Authoritative data (tenants, agents, campaigns, tasks, results, audit_events, wallet_policies)
  - ACID transactions, relational integrity, multi-tenant isolation
- **NoSQL (MongoDB/Cassandra)**: High-velocity metrics (video_metadata with time-series buckets)
  - Horizontal scaling, append-mostly writes, fast aggregations
- **Weaviate**: Semantic memory (agent memories, persona embeddings)
  - Vector similarity search, RAG pipeline

## Consequences

**Positive**:
- Right tool for each data type
- PostgreSQL ensures transactional integrity for money/config
- NoSQL handles high-volume metrics without overwhelming SQL
- Weaviate optimized for semantic search

**Negative**:
- Multiple systems to manage
- Data consistency across systems requires careful design
- More complex deployment

**Alternatives Considered**:
- SQL-only: Would struggle with high-velocity metrics, limited vector search
- NoSQL-only: Would lose ACID guarantees for critical config/financial data

## References

- `specs/technical.md` - "Database & Data Management" section
- `research_architecture_strategy.md` - Database strategy rationale
