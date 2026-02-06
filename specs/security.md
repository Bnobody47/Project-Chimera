---
description: Security specification: AuthN/AuthZ, rate limits, content moderation, forbidden actions.
---

# Security Specification

## Authentication & Authorization

### Authentication Flow (AuthN)

**JWT Token Issuance**:
- **Endpoint**: `POST /api/v1/auth/login`
- **Request**: `{ email: string, password: string, tenant_id: UUID }`
- **Response**: `{ access_token: JWT, refresh_token: JWT, expires_in: 3600 }`
- **Token Claims**: `{ sub: user_id, tenant_id: UUID, role: enum, iat: timestamp, exp: timestamp }`
- **Storage**: HTTP-only cookies (preferred) or localStorage with XSS protection

**Token Refresh**:
- **Endpoint**: `POST /api/v1/auth/refresh`
- **Request**: `{ refresh_token: JWT }`
- **Response**: `{ access_token: JWT }`
- **Expiry**: Refresh tokens valid 7 days, rotate on use

**Service-to-Service Auth**:
- **Method**: API keys in `X-API-Key` header
- **Scope**: Internal Planner/Worker/Judge services only
- **Rotation**: Keys rotated quarterly, stored in secret manager

### Authorization (AuthZ)

**Role-Based Access Control (RBAC)**:

| Role | Permissions | Endpoints |
|------|-------------|-----------|
| `network_operator` | View agents, create campaigns, view analytics | `/api/v1/agents`, `/api/v1/campaigns`, `/api/v1/analytics/*` |
| `human_reviewer` | View HITL queue, approve/reject content | `/api/v1/judge/hitl-queue`, `/api/v1/judge/hitl-decision` |
| `developer` | Full API access, manage MCP servers | All endpoints except `/api/v1/commerce/wallet/*/transfer` |
| `system` | Internal service calls only | Planner/Worker/Judge endpoints |

**Tenant Isolation**:
- All queries filtered by `tenant_id` from JWT claims
- Cross-tenant access returns `403 Forbidden`
- Database row-level security (RLS) enforces tenant boundaries

**Endpoint Permissions**:

- **GET `/api/v1/agents`**: Requires `network_operator` or `developer`; tenant-scoped
- **POST `/api/v1/agents/{id}/campaigns`**: Requires `network_operator`; tenant-scoped
- **GET `/api/v1/judge/hitl-queue`**: Requires `human_reviewer` or `developer`; tenant-scoped
- **POST `/api/v1/judge/hitl-decision`**: Requires `human_reviewer`; tenant-scoped
- **POST `/api/v1/commerce/wallet/{id}/transfer`**: Requires `developer` + CFO Judge approval; tenant-scoped
- **POST `/api/v1/skills/*`**: Requires `system` (internal) or `developer` (testing)

## Rate Limits

### Per-Endpoint Limits

| Endpoint | Limit | Window | Response |
|----------|-------|--------|----------|
| `POST /api/v1/auth/login` | 5 requests | 15 minutes | `429 Too Many Requests` |
| `GET /api/v1/agents` | 100 requests | 1 minute | `429` + `Retry-After: 60` |
| `POST /api/v1/planner/decompose` | 20 requests | 1 minute | `429` + `Retry-After: 60` |
| `POST /api/v1/worker/submit-result` | 200 requests | 1 minute | `429` + `Retry-After: 30` |
| `GET /api/v1/judge/hitl-queue` | 50 requests | 1 minute | `429` + `Retry-After: 60` |
| `POST /api/v1/commerce/wallet/*/transfer` | 10 requests | 1 hour | `429` + `Retry-After: 3600` |

**Implementation**: Redis-based sliding window counter per `user_id` or `tenant_id`

### Agent-Level Limits

- **Tasks per agent**: Max 1000 pending tasks per agent
- **MCP tool calls**: Max 100 calls/minute per agent (enforced at MCP server layer)
- **Wallet transactions**: Max 10 transactions/day per agent (CFO Judge enforces)

## Content Moderation Pipeline

### Step-by-Step Moderation Flow

1. **Pre-Generation Filter** (Planner):
   - Check goal against forbidden topics list (politics, hate speech, illegal content)
   - If match → reject task creation, log to audit

2. **Post-Generation Filter** (Judge):
   - **Confidence Score**: < 0.70 → auto-reject, < 0.90 → HITL queue
   - **Sensitive Topic Detection**: Keyword + semantic analysis (LLM-lite)
     - Politics, health advice, financial advice, legal claims → mandatory HITL
   - **Character Consistency**: Vision model checks media likeness
   - **Disclosure Check**: Ensures `is_generated` flag set

3. **Human Review** (HITL):
   - Reviewer sees content + confidence score + reasoning trace
   - Actions: Approve, Reject, Request Edit, Escalate to Legal
   - All decisions logged to `audit_events`

4. **Post-Publish Monitoring**:
   - Track engagement metrics for flagged patterns
   - Auto-pause agent if engagement drops < threshold (possible shadowban)

### Forbidden Actions & Content

**Forbidden Actions**:
- Publishing content without `is_generated` disclosure flag
- Executing wallet transactions exceeding `max_daily_usdc` or `max_tx_usdc`
- Accessing cross-tenant data (enforced at DB layer)
- Bypassing HITL for sensitive topics (hardcoded in Judge logic)

**Forbidden Content Topics**:
- Political endorsements or commentary
- Medical/health advice (beyond general wellness)
- Financial investment advice
- Legal claims or guarantees
- Hate speech, harassment, discrimination
- Copyrighted material without license

**Resource Limits**:
- **Agent memory**: Max 10,000 Weaviate vectors per agent
- **Campaign budget**: Max $10,000 USDC per campaign (configurable per tenant)
- **Daily API calls**: Max 50,000 MCP tool calls per tenant/day
- **Storage**: Max 100GB video metadata per tenant

## Security Controls

### Input Validation

- **SQL Injection**: Parameterized queries only, ORM (SQLAlchemy) enforces
- **XSS**: React escapes by default; sanitize user inputs in text fields
- **CSRF**: SameSite cookies + CSRF tokens for state-changing operations
- **Path Traversal**: Validate file paths, restrict to allowed directories

### Secret Management

- **API Keys**: Stored in AWS Secrets Manager / HashiCorp Vault
- **Wallet Private Keys**: Encrypted at rest, injected at runtime only
- **Database Credentials**: Rotated monthly, never logged
- **MCP Server Tokens**: Per-server secrets, scoped to specific tools

### Audit & Compliance

- **All Actions Logged**: `audit_events` table records actor_id, action, payload, timestamp
- **Immutable Logs**: Append-only, retention 7 years (compliance)
- **On-Chain Ledger**: Financial transactions recorded on Base/Ethereum (immutable)
- **Access Logs**: IP addresses, user agents logged for security incidents

### Incident Response

- **Suspicious Activity**: Auto-pause agent if >10 failed transactions in 1 hour
- **Data Breach**: Immediate tenant isolation, rotate all secrets, notify stakeholders
- **Rate Limit Abuse**: Temporary IP ban (1 hour), escalate to permanent if repeated

## Security Testing

- **Penetration Testing**: Quarterly external audit
- **Dependency Scanning**: Dependabot + Snyk for known vulnerabilities
- **SAST**: CodeQL in CI pipeline
- **DAST**: OWASP ZAP scans in staging environment
