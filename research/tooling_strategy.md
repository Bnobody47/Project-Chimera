Project Chimera — Tooling & Skills Strategy
===========================================

Purpose: separate Developer MCP tools (for us) from Runtime Skills (for agents), and document the stack to minimize ambiguity.

Developer MCP Tools (for building/ops)
--------------------------------------
- git-mcp: version control commands with auditability.
- filesystem-mcp: safe file edits/reads through MCP.
- test-runner MCP (or shell wrapper): run `make test` inside Docker.
- sqlite/pg MCP server: quick schema prototyping and contract tests.
- sense/telemetry: Tenx MCP Sense stays connected for traceability.

Runtime MCP Servers (agent capabilities)
----------------------------------------
- Social: twitter/threads/instagram MCP servers exposing `post_content`, `reply_content`, `read_mentions`.
- Memory: weaviate MCP (`search_memory`, `upsert_memory`), redis resource wrappers for short-term context.
- Media: ideogram or midjourney MCP (`generate_image` with `character_reference_id`), runway/luma MCP for video tiers.
- Commerce: coinbase-agentkit MCP (`wallet_get_balance`, `wallet_transfer`, `deploy_token`) with budget guard.
- News/Trends: custom `news://latest` resource server for trend ingestion.
- Diagnostics: health-check MCP server for swarm node status.

Skills (runtime packages invoked by agents)
-------------------------------------------
- Skill = packaged capability (code + schema) the agent can call; not MCP transport.
- Define IO contracts in `skills/README.md`; implement later.

Operational Conventions
-----------------------
- All external calls routed via MCP; dev tooling separated from runtime skills.
- Rate limits and dry-run toggles enforced at MCP server layer.
- Keep per-tenant configuration in Postgres; never hardcode keys.
- Budget policies enforced by CFO Judge decorator; agents default to testnet/staging.

Next Steps
----------
- Stand up stub MCP servers (twitter mock, news mock, sqlite reference).
- Add Makefile targets to run MCP servers locally for tests.
- Maintain this file as new tools/skills are added.
