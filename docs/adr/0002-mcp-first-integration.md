# ADR-0002: MCP-First External Integration

**Status**: Accepted  
**Date**: 2026-02-05  
**Deciders**: Architecture Team

## Context

Agents need to interact with external systems (social platforms, vector DBs, blockchains, media generators). Direct API calls create tight coupling and make the agent core fragile to vendor changes.

## Decision

**All external I/O must go through Model Context Protocol (MCP) servers**. The agent core never calls third-party SDKs directly.

- MCP servers wrap external APIs (Twitter, Weaviate, Coinbase AgentKit, Ideogram, Runway)
- Agents use MCP Tools (executable functions) and Resources (read-only data)
- MCP layer enforces rate limits, dry-run flags, logging

## Consequences

**Positive**:
- Decoupling: Agent logic independent of vendor APIs
- Standardization: All external calls use same MCP interface
- Testability: Mock MCP servers for unit tests
- Governance: Rate limits, logging centralized at MCP layer

**Negative**:
- Additional abstraction layer (slight latency overhead)
- MCP server maintenance required per vendor

**Alternatives Considered**:
- Direct SDK calls: Simpler but fragile, hard to test, vendor lock-in

## References

- `.cursor/mcp.json` - MCP server configuration
- `specs/technical.md` - "APIs / MCP Tool Contracts"
- Model Context Protocol docs: https://modelcontextprotocol.io
