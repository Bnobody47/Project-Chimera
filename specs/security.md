---
description: Dedicated security spec for Project Chimera — AuthN/AuthZ, secrets, rate limits, content safety, agent containment boundaries. Tied to APIs and runtime.
---

# Security Specification

This document directly addresses the security requirement for the Agentic Infrastructure Challenge: AuthN/AuthZ, secrets handling, rate limiting, content safety, and **explicit agent containment boundaries** (forbidden actions, escalation triggers, resource limits) tied to APIs and the runtime environment.

---

## 1. Authentication (AuthN)

### 1.1 Human Users (Dashboard / API)

| Concern | Specification | Runtime / API Tie-In |
|--------|----------------|----------------------|
| **Token type** | JWT (RS256 or HS256) | Issued by `POST /api/v1/auth/login` |
| **Claims** | `sub` (user_id), `tenant_id`, `role`, `iat`, `exp` | Validated on every API request via middleware |
| **Storage** | HTTP-only cookie or Authorization header | Frontend must not store in localStorage if XSS risk |
| **Refresh** | Refresh token, 7-day expiry, rotate on use | `POST /api/v1/auth/refresh` |
| **Login rate limit** | 5 attempts per 15 min per IP | Enforced at API gateway; returns `429` + `Retry-After` |

**API contract**:
- `POST /api/v1/auth/login` → `{ access_token, refresh_token, expires_in }`
- `POST /api/v1/auth/refresh` → `{ access_token }`
- All other API requests require header: `Authorization: Bearer <access_token>`

### 1.2 Service-to-Service (Planner / Worker / Judge)

| Concern | Specification | Runtime Tie-In |
|--------|----------------|----------------|
| **Method** | API key in `X-API-Key` header | Injected at deploy time from secret manager |
| **Scope** | Internal services only; not exposed to user-facing API | Env: `INTERNAL_API_KEY` |
| **Rotation** | Quarterly; old key valid 7 days overlap | Secret manager versioning |

**Runtime**: Keys MUST be read from environment (e.g. `INTERNAL_API_KEY`). No keys in code or config files in repo.

---

## 2. Authorization (AuthZ)

### 2.1 Role-Based Access (RBAC)

| Role | Allowed API Endpoints | Denied |
|------|------------------------|--------|
| `network_operator` | `GET/POST /api/v1/agents`, `GET/POST /api/v1/agents/{id}/campaigns`, `GET /api/v1/analytics/*` | HITL decision, wallet transfer, internal services |
| `human_reviewer` | `GET /api/v1/judge/hitl-queue`, `POST /api/v1/judge/hitl-decision` | Agent creation, campaign creation, wallet, analytics write |
| `developer` | All read/write except `POST /api/v1/commerce/wallet/*/transfer` (requires CFO approval) | Direct wallet transfer without CFO check |
| `system` | Planner/Worker/Judge internal endpoints only | Any user-facing API |

### 2.2 Per-Endpoint Permissions

- **GET `/api/v1/agents`**: `network_operator` or `developer`; response filtered by JWT `tenant_id`.
- **POST `/api/v1/agents/{id}/campaigns`**: `network_operator`; `tenant_id` from JWT must match agent’s tenant.
- **GET `/api/v1/judge/hitl-queue`**: `human_reviewer` or `developer`; tenant-scoped.
- **POST `/api/v1/judge/hitl-decision`**: `human_reviewer` only; `tenant_id` enforced.
- **POST `/api/v1/commerce/wallet/{id}/transfer`**: `developer` only; request still passes through CFO Judge; tenant-scoped.
- **POST `/api/v1/planner/decompose`**, **POST `/api/v1/worker/*`**, **POST `/api/v1/judge/review`**: `system` (internal) or `developer` (testing); require `X-API-Key` when not user JWT.

### 2.3 Tenant Isolation

- Every API handler MUST resolve tenant from JWT (or service context) and filter all DB/Weaviate/Redis queries by `tenant_id`.
- Cross-tenant access returns **403 Forbidden**.
- PostgreSQL RLS (row-level security) MUST be enabled on all tenant-scoped tables.

---

## 3. Secrets Handling

| Secret Type | Where Stored | How Injected | Forbidden |
|-------------|--------------|--------------|-----------|
| DB credentials | AWS Secrets Manager / Vault | Env at runtime: `POSTGRES_*`, `REDIS_*` | Never in code, config, or logs |
| Wallet private keys | Secret manager, per agent | Injected into Worker/CFO runtime only; never logged | Never in DB or API response |
| MCP server tokens (Twitter, Weaviate, etc.) | Secret manager or env | Env: `TWITTER_*`, `WEAVIATE_*`, etc. | Never in `.cursor/mcp.json` values; use `${VAR}` only |
| JWT signing key | Secret manager | Env: `JWT_SECRET` or `JWT_PUBLIC_KEY` | Never in repo |
| Internal API key | Secret manager | Env: `INTERNAL_API_KEY` | Never in repo |

**Runtime rule**: Application MUST fail fast at startup if any required secret env var is missing (no default secrets).

**Code rule**: No `os.environ.get("SECRET", "fallback")` for real secrets; use `os.environ["SECRET"]` or exit.

---

## 4. Rate Limiting

### 4.1 API Rate Limits (per user or tenant)

| Endpoint | Limit | Window | Response |
|----------|-------|--------|----------|
| `POST /api/v1/auth/login` | 5 | 15 min | `429` + `Retry-After: 900` |
| `GET /api/v1/agents` | 100 | 1 min | `429` + `Retry-After: 60` |
| `POST /api/v1/planner/decompose` | 20 | 1 min | `429` + `Retry-After: 60` |
| `POST /api/v1/worker/submit-result` | 200 | 1 min | `429` + `Retry-After: 30` |
| `GET /api/v1/judge/hitl-queue` | 50 | 1 min | `429` + `Retry-After: 60` |
| `POST /api/v1/judge/hitl-decision` | 100 | 1 min | `429` + `Retry-After: 60` |
| `POST /api/v1/commerce/wallet/*/transfer` | 10 | 1 hour | `429` + `Retry-After: 3600` |

**Implementation**: Redis key `ratelimit:{tenant_id}:{endpoint}` with sliding window or fixed window counter.

### 4.2 Runtime / Agent-Level Limits

| Resource | Limit | Enforced Where |
|----------|-------|----------------|
| Pending tasks per agent | 1000 | Planner when pushing to `task_queue` |
| MCP tool calls per agent | 100/min | MCP server layer (or wrapper) |
| Wallet transactions per agent | 10/day | CFO Judge + Redis `daily_tx_count` |
| Weaviate vectors per agent | 10,000 | `upsert_memory` tool / Weaviate schema |
| Campaign budget (USDC) | Configurable per tenant; default max $10,000 | CFO Judge + `wallet_policies` table |

---

## 5. Content Safety

### 5.1 Pre-Generation (Planner)

- Before creating tasks, Planner MUST check campaign goal against **forbidden topics** list.
- If match: do not create task; log to `audit_events` with `action=goal_rejected_forbidden_topic`.
- Forbidden topics: politics, hate speech, illegal content, explicit adult content (list maintained in config/spec).

### 5.2 Post-Generation (Judge)

- **Confidence score**: &lt; 0.70 → auto-reject; 0.70–0.90 → HITL queue; ≥ 0.90 → auto-approve (unless sensitive).
- **Sensitive topic detection** (keyword + semantic): politics, health advice, financial advice, legal claims → **mandatory HITL** regardless of score.
- **Disclosure**: Every published post MUST set platform `is_generated` (or equivalent) to true.
- **Character consistency**: Vision Judge MUST verify media likeness before publish; on failure, reject and re-queue.

### 5.3 Human-in-the-Loop (HITL)

- All HITL decisions (approve/reject/edit/escalate) MUST be logged to `audit_events` with `actor_id` (human), `action`, and payload.
- Escalation to Legal/Compliance is a supported action and MUST be recorded.

### 5.4 Content Moderation Pipeline (Summary)

1. Planner: reject goals matching forbidden topics.  
2. Judge: apply confidence + sensitive-topic rules → auto-approve, HITL, or reject.  
3. HITL: human approves/rejects/edits; optional escalate.  
4. Post-publish: monitor engagement; auto-pause agent if anomaly (e.g. possible shadowban).

---

## 6. Agent Containment Boundaries

### 6.1 Forbidden Actions (Explicit List)

Agents (Planner/Worker/Judge) MUST NOT:

- Publish content without setting the platform’s AI disclosure flag (`is_generated`).
- Execute a wallet transaction that would exceed `wallet_policies.max_daily_usdc` or `max_tx_usdc`.
- Access or query data for another tenant (enforced by `tenant_id` in all queries).
- Bypass HITL for content that triggered sensitive-topic or low-confidence rules.
- Call any external API or service except via the MCP layer (no direct SDK calls from agent code).
- Read or log secrets (API keys, wallet keys, DB URLs).
- Create tasks with goal text longer than 10,000 characters (truncate and log).
- Submit a Result without a valid `state_version` for OCC.

### 6.2 Escalation Triggers (When to Escalate to Human or System)

| Trigger | Action |
|--------|--------|
| Confidence score &lt; 0.90 | Send to HITL queue (or reject if &lt; 0.70). |
| Sensitive topic detected | Always send to HITL; do not auto-approve. |
| CFO Judge: transaction exceeds budget | Reject; log `commerce_blocked`; do not call MCP transfer. |
| CFO Judge: anomaly pattern (e.g. many failed tx) | Reject and create alert for human review. |
| OCC conflict (state_version mismatch) | Reject commit; re-queue task to Planner. |
| MCP tool returns 5xx or timeout repeatedly | Circuit-breaker; pause agent tasks for that tool; alert. |
| &gt; 10 failed wallet transactions in 1 hour for one agent | Auto-pause agent; escalate to operator. |

### 6.3 Resource Limits (Hard Caps)

| Resource | Limit | Enforced In |
|----------|-------|-------------|
| Pending tasks per agent | 1,000 | Planner / `task_queue` |
| MCP tool calls per agent | 100/min | MCP wrapper / runtime |
| Wallet transactions per agent | 10/day | CFO Judge + Redis |
| Weaviate vectors per agent | 10,000 | Weaviate + `upsert_memory` |
| Campaign budget (USDC) | Per `wallet_policies` | CFO Judge |
| Daily MCP calls per tenant | 50,000 | Redis counter at API/MCP layer |
| Video metadata storage per tenant | 100 GB | Storage layer / admin |

### 6.4 Runtime Environment Mapping

- **Planner**: Reads goals from API/DB; writes tasks to Redis `task_queue`. Must enforce task-per-agent cap and forbidden-topic check.  
- **Worker**: Reads tasks from Redis; calls MCP tools only; writes Result to `review_queue`. Must not hold secrets in memory longer than request lifecycle.  
- **Judge**: Reads from `review_queue`; applies confidence + sensitive-topic rules; writes to HITL or commits to state. Must enforce OCC and disclosure.  
- **CFO Judge**: Wraps any wallet transfer; reads `wallet_policies` and Redis daily counters; blocks or allows; logs to `audit_events`.

All of the above MUST run with secrets supplied only via environment (or secret manager); no secrets in config files in the repo.

---

## 7. Audit and Compliance

- **Audit log**: Every sensitive action (login, HITL decision, wallet transfer attempt, goal rejection) MUST create an `audit_events` row (actor_id, action, payload, timestamp, state_version).  
- **Immutability**: Append-only; no updates or deletes.  
- **Retention**: Per data retention policy (e.g. 7 years for financial/compliance).  
- **On-chain**: Approved wallet transactions MUST be recorded on-chain (e.g. Base); ledger is immutable.

---

## 8. Security Testing and CI

- **SAST**: CodeQL (or equivalent) in CI on every push.  
- **Dependency scanning**: Dependabot / Snyk; no high/critical vulnerabilities in main.  
- **Secrets scan**: Pre-commit or CI must scan for accidental secret patterns; fail if found.  
- **AuthZ tests**: Automated tests that verify 403 for cross-tenant and wrong-role access.

---

This security spec is the single source of truth for AuthN/AuthZ, secrets, rate limits, content safety, and agent containment. All APIs and runtime components (Planner, Worker, Judge, CFO Judge, MCP layer) MUST align with it.
