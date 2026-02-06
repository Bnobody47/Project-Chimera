---
description: Meta-specification for how agents should generate, evolve, and manage Cursor rules.
---

# Rule Creation & Evolution Specification

## Purpose

This spec defines how Cursor rules (`.cursor/rules/*.mdc`) should be created, categorized, evolved, and mapped back to project specifications. Rules encode agent intent and guide autonomous development.

## Rule Categories

### 1. Core Project Rules (`chimera-core.mdc`)
- **Purpose**: Universal principles that apply to all code changes
- **Scope**: Always active (`alwaysApply: true`)
- **Content**: Prime Directive, MCP-first, spec alignment, traceability
- **Evolution**: Updated only when core philosophy changes (requires ADR)

### 2. Domain-Specific Rules (`*.mdc` per domain)
- **Purpose**: Rules for specific areas (e.g., `security.mdc`, `testing.mdc`, `mcp-integration.mdc`)
- **Scope**: File-pattern based (`globs: "**/*security*.py"`)
- **Content**: Domain-specific constraints, patterns, anti-patterns
- **Evolution**: Updated when domain specs change

### 3. Feature Rules (temporary)
- **Purpose**: Rules for active feature development
- **Scope**: Feature branch or `SPECIFY_FEATURE` env var
- **Content**: Feature-specific constraints, temporary patterns
- **Evolution**: Deleted after feature merge

## Rule Generation Process

### When to Create a Rule

Create a new rule when:
1. **Repeated pattern**: Same guidance needed in 3+ conversations
2. **Spec ambiguity**: Spec doesn't cover a common edge case
3. **Anti-pattern prevention**: Need to prevent a specific mistake
4. **Domain boundary**: Clear separation needed (e.g., security vs. performance)

### Rule Template

```markdown
---
description: Brief description of what this rule enforces
globs: "**/*.py"  # Optional: file pattern
alwaysApply: false  # Set true for universal rules
---

# Rule Title

## Context
Why this rule exists (link to spec section or ADR).

## Constraints
- Constraint 1: Specific guidance
- Constraint 2: Another pattern

## Examples

### ✅ GOOD
```python
# Example of correct pattern
```

### ❌ BAD
```python
# Example of anti-pattern
```

## References
- `specs/technical.md#section` - Related spec
- `docs/adr/000X-decision.md` - Related ADR
```

## Rule Evolution Strategy

### Versioning
- Rules are version-controlled (Git)
- Major changes require:
  1. Update rule file
  2. Add entry to `CHANGELOG.md` (if exists)
  3. Link to spec/ADR that motivated change

### Deprecation
- Mark deprecated rules with `[DEPRECATED]` in description
- Keep for 2 release cycles, then delete
- Migrate content to new rule or spec if still relevant

### Conflict Resolution
- If rules conflict, `chimera-core.mdc` takes precedence
- Domain rules override feature rules
- Document conflicts in rule comments

## Mapping Rules to Specs

Every rule must reference:
- **Source Spec**: Which spec section motivated this rule
- **ADR Link**: If rule encodes an architectural decision
- **Test Link**: Which tests validate rule compliance

Example mapping:
```markdown
## References
- Source: `specs/technical.md#mcp-first-integration`
- ADR: `docs/adr/0002-mcp-first-integration.md`
- Tests: `tests/test_skills_interface.py#test_*_mcp_tool`
```

## Agent Behavior

When an agent needs to create/update a rule:

1. **Check existing rules**: Search `.cursor/rules/` for similar guidance
2. **Reference specs**: Ensure rule aligns with `specs/` and `.specify/memory/constitution.md`
3. **Write rule**: Use template, include examples, link to specs
4. **Test impact**: Verify rule doesn't break existing workflows
5. **Document**: Add rule to README.md or CONTRIBUTING.md if universal

## Rule Validation

Rules should be:
- **Concise**: < 50 lines per rule
- **Actionable**: Clear do/don't guidance
- **Testable**: Can write tests that validate rule compliance
- **Traceable**: Links back to specs/ADRs

## Maintenance

- **Quarterly review**: Audit rules for relevance, merge duplicates
- **On spec change**: Update related rules or mark deprecated
- **On ADR creation**: Create/update rules that encode the decision
