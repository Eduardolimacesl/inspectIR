<!--
SYNC IMPACT REPORT
==================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: none (first fill — all placeholders resolved)
Added sections:
  - Core Principles (I–V)
  - Technology Constraints
  - Development Workflow
  - Governance
Removed sections: none
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ — Constitution Check gates defined
  - .specify/templates/spec-template.md ✅ — aligns with SDD and domain purity constraints
  - .specify/templates/tasks-template.md ✅ — task types reflect TDD + SDD disciplines
Deferred TODOs: none
-->

# InspectIR Constitution

## Core Principles

### I. Domain Purity (NON-NEGOTIABLE)

The `domain/` layer MUST contain zero dependencies on infrastructure, frameworks, or
external services. All fiscal rules, value objects (`CNPJ`, `Beneficiario`), entities
(`NotaFiscal`, `NotaAuditada`), and the `MotorCalculoIR` domain service MUST be
implementable and testable with no imports beyond the Python standard library.

- No ORM, no HTTP client, no Streamlit, no Gemini SDK inside `domain/`
- Domain objects instantiated directly in unit tests without any mock infrastructure
- Violations are a hard gate: PRs touching `domain/` that introduce external imports
  are blocked until refactored

### II. Spec-Driven Development — SDD (NON-NEGOTIABLE)

`specs/tax_rules_schema.json` is the Single Source of Truth (SSOT) for all fiscal
constants. No numeric tax value (teto, alíquota, limit) MUST ever be hardcoded in
Python source files.

- `domain/models.py` MUST load constants from the schema at import time
- `tests/test_spec.py` MUST validate schema conformance on every CI run
- Updating a legal limit means editing only `specs/tax_rules_schema.json`; domain
  picks it up automatically — zero drift by design

### III. Privacy-First / Zero-Knowledge

User credentials, API keys, raw NF-e payloads, and audit results MUST reside
exclusively in the local filesystem (`inspectir/data/`). No financial data is
transmitted to any cloud service except the Gemini API call payload (which is
transient and contains only NF-e metadata, not credentials).

- `auth_state.json` and `auditoria_final.json` MUST NOT be committed to git
- `.gitignore` MUST cover `inspectir/data/` and any `*.json` credential files
- No telemetry, analytics, or logging that persists financial data externally

### IV. Test-First (TDD)

All new behavior MUST have a test written before implementation. The test pyramid is:

1. `test_unit.py` — pure domain logic, no I/O, no mocks needed
2. `test_integration.py` — use-case pipeline with `MagicMock` for LLM adapter
3. `test_spec.py` — schema conformance (SDD gate)
4. `test_e2e.py` — end-to-end pipeline
5. `test_live_gemini.py` — smoke tests (opt-in, requires real `GEMINI_API_KEY`)

Red-Green-Refactor is the only accepted implementation cycle. Tests MUST pass before
any feature branch is merged. `--ignore=tests/test_live_gemini.py` is acceptable in
CI; all other test files are mandatory.

### V. Harness-First Development

New features MUST be testable without live network access. Before implementing any
integration, a simulation path (`simulado=True` flag or equivalent `MagicMock` path)
MUST exist so the full pipeline can be exercised offline.

- `extractor.py` and `ExtrairNotasUseCase` expose `simulado=True` — this pattern is
  REQUIRED for all new external-facing use cases
- Playwright scripts MUST persist `auth_state.json` to avoid interactive login on
  repeated runs; browser automation without state persistence is a violation

## Technology Constraints

- **Runtime**: Python 3.12 (NOT 3.14 — lacks `_ctypes`, breaks `pandas`/`streamlit`)
- **LLM**: `gemini-2.5-flash-preview-09-2025` with `response_mime_type="application/json"`;
  exponential backoff (4 retries, base 2s); temperature ≤ 0.15 for deterministic audit
- **UI**: Streamlit — presentation layer only; no business logic inside `app.py`
- **Scraping**: Playwright with `headless=False` for manual-login portals;
  cookie persistence via `auth_state.json`
- **Schema format**: JSON Schema for all domain contracts (`tax_rules_schema.json`)
- **Cloud infra**: None required — product MUST run fully on localhost

## Development Workflow

1. Feature branch from `main` via `/speckit-git-feature` (naming: `NNN-short-name`)
2. Spec written via `/speckit-specify` before any code
3. Clarifications resolved via `/speckit-clarify`
4. Plan generated via `/speckit-plan` before implementation starts
5. Tasks generated via `/speckit-tasks`, implemented via `/speckit-implement`
6. All tests pass (`python3 -m pytest tests/ -v --ignore=tests/test_live_gemini.py`)
7. PR merged to `main`; branch deleted

**Legal constant updates** (e.g., new `TETO_EDUCACAO_INDIVIDUAL` published by Receita
Federal): edit only `specs/tax_rules_schema.json`, run `test_spec.py`, no code changes.

## Governance

This constitution supersedes all other project documentation in case of conflict.
Amendments MUST follow semantic versioning:

- **MAJOR**: Removal or redefinition of a NON-NEGOTIABLE principle
- **MINOR**: New principle or technology constraint added
- **PATCH**: Wording clarification, typo fix, example update

All amendments MUST update the version line below and the SYNC IMPACT REPORT comment
at the top of this file. PRs/reviews MUST verify constitution compliance before merge.

Use `docs/claude.md` as the runtime harness and agent guidance reference.

**Version**: 1.0.0 | **Ratified**: 2026-05-24 | **Last Amended**: 2026-05-24
