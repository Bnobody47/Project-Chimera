# Contributing to Project Chimera

## Workflow

### Spec-First Development

1. **Read the specs**: Before writing code, review `specs/_meta.md`, `specs/functional.md`, `specs/technical.md`, and relevant ADRs in `docs/adr/`.
2. **Use Spec Kit**: For new features, use `/speckit.specify` to create a feature spec, then `/speckit.plan` and `/speckit.tasks`.
3. **Update specs first**: If your change affects behavior, update the relevant spec file before implementation.
4. **Write failing tests**: Add tests in `tests/` that define the contract (they should fail until implementation).
5. **Implement**: Write code to make tests pass, following the spec and `.cursor/rules/chimera-core.mdc`.
6. **Verify**: Run `make test` and `make spec-check` locally before pushing.

### Branching Strategy

- **Feature branches**: `feature/{spec-number}-{description}` (e.g., `feature/001-planner-service`)
- **Bug fixes**: `fix/{issue-number}-{description}`
- **Spec updates**: `specs/{area}-{description}` (e.g., `specs/security-authn`)
- **Infra changes**: `infra/{description}` (e.g., `infra/ci-security-scan`)

Keep commits small and topical. Reference spec sections in commit messages:
```
feat(planner): implement task decomposition per specs/technical.md#planner-service

- Adds POST /api/v1/planner/decompose endpoint
- Creates Task DAG and pushes to task_queue
- Links to specs/functional.md#goal-plan-execute-flow
```

### Pull Request Process

1. **Title**: Clear, descriptive (e.g., "Add Planner service endpoint per spec")
2. **Description**: 
   - Link to relevant spec sections
   - Explain what changed and why
   - List any breaking changes
3. **Checks**: All CI jobs must pass (test, lint, security, spec-check)
4. **Review**: CodeRabbit AI review + at least one human reviewer
5. **Merge**: Squash merge preferred to keep history clean

## Expectations

- **MCP-first**: All external I/O via MCP servers/tools (see `.cursor/mcp.json`)
- **TDD**: Tests define contracts before implementation
- **Security**: No secrets in code; use env vars or secret manager
- **Documentation**: Update README.md, specs/, or ADRs if behavior changes
- **Accessibility**: Frontend changes must meet WCAG AA standards

## Onboarding Checklist

- [ ] Read `README.md` and `specs/_meta.md`
- [ ] Review `.cursor/rules/chimera-core.mdc` (Prime Directive, MCP-first, etc.)
- [ ] Set up local environment: `make setup`
- [ ] Run tests: `make test` (expect some failures - that's TDD)
- [ ] Review ADRs in `docs/adr/` for major decisions
- [ ] Check `.cursor/mcp.json` to understand MCP server setup
- [ ] Read `CONTRIBUTING.md` (this file)

## Questions?

- Open an issue for clarifications
- Check `specs/` for requirements
- Review ADRs for architectural decisions
- Ask in team chat (if applicable)
