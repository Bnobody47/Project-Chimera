# Project Chimera — standardised commands
# Spec: specs/technical.md (Deployment & DevEx)

.PHONY: setup test spec-check lint docker-test

setup:
	pip install -e ".[dev]" 2>/dev/null || pip install pytest pydantic -e .
	@echo "Setup complete. Run 'make test' to execute tests."

test:
	pytest tests/ -v --tb=short

spec-check:
	@echo "=== Spec alignment check ==="
	@test -f specs/_meta.md && echo "  [OK] specs/_meta.md" || (echo "  [FAIL] specs/_meta.md missing"; exit 1)
	@test -f specs/functional.md && echo "  [OK] specs/functional.md" || (echo "  [FAIL] specs/functional.md missing"; exit 1)
	@test -f specs/technical.md && echo "  [OK] specs/technical.md" || (echo "  [FAIL] specs/technical.md missing"; exit 1)
	@test -d skills && echo "  [OK] skills/" || (echo "  [FAIL] skills/ missing"; exit 1)
	@test -d tests && echo "  [OK] tests/" || (echo "  [FAIL] tests/ missing"; exit 1)
	@echo "  Spec check passed."

lint:
	ruff check . 2>/dev/null || echo "Run: pip install ruff && ruff check ."

docker-test:
	docker build -t project-chimera:test .
	docker run --rm project-chimera:test make test
