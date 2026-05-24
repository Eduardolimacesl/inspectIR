# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

> **Note:** Use `python3` (3.12). The `.venv` was created with Python 3.14 which lacks `_ctypes` — `pandas` and `streamlit` fail there.

```bash
# Run app
python3 -m streamlit run app.py

# Run all tests (from project root)
python3 -m pytest tests/ -v --ignore=tests/test_live_gemini.py

# Run single test file
python3 -m pytest tests/test_unit.py -v

# Run single test
python3 -m pytest tests/test_unit.py::TestDomainRules::test_motor_calculo_ir_saude_sem_limites -v

# Install deps
python3 -m pip install -r requirements.txt --break-system-packages

# Install Playwright browsers (one-time)
python3 -m playwright install chromium
```

Set `GEMINI_API_KEY` env var or enter it in the sidebar at runtime. Tests that hit live Gemini (in `test_live_gemini.py`) also require this key.

## Architecture

DDD + Hexagonal (Ports & Adapters). Domain is fully isolated from infrastructure.

```
domain/models.py        — Pure domain: NotaFiscal, NotaAuditada, CNPJ (value object),
                          Beneficiario, CategoriaFiscal (enum), MotorCalculoIR (service)
application/use_cases.py — Orchestration: ExtrairNotasUseCase, AuditarNotasUseCase,
                          DeepTaxAdvisorUseCase
infrastructure/services.py — Adapters: AdaptadorGeminiFiscal (LLM), EscritorLeitorNotasLocal (file I/O)
extractor.py            — Playwright scraper for SEFIN portal (headless=False for manual login)
app.py                  — Streamlit UI (presentation layer only)
specs/tax_rules_schema.json — SSOT for tax constants (TETO_EDUCACAO_INDIVIDUAL, ALIQUEOTA_PADRAO)
```

**Data flow:** `app.py` → use cases → `AdaptadorGeminiFiscal.analisar_em_lote()` → `EscritorLeitorNotasLocal` (writes to `inspectir/data/`). Dashboard reads from `inspectir/data/auditoria_final.json`.

**Key constraint:** Tax constants (`TETO_EDUCACAO_INDIVIDUAL = 3561.50`, `ALIQUEOTA_PADRAO = 0.275`) come from `specs/tax_rules_schema.json`, not hardcoded — `domain/models.py` loads them at import time. Update the spec file, not the Python constants.

**Gemini integration:** `AdaptadorGeminiFiscal` uses `gemini-2.5-flash-preview-09-2025` with `response_mime_type="application/json"` for structured audit output. Uses exponential backoff (4 retries, starting 2s). `DeepTaxAdvisorUseCase` uses the same model for the tax advisory report (markdown output, temperature=0.15).

**Simulated mode:** `ExtrairNotasUseCase` and `extractor.py` both have a `simulado=True` flag that returns hardcoded fixture notes — use this for development/testing without hitting the SEFIN portal.

**Playwright auth persistence:** Browser session state saved to `inspectir/data/auth_state.json`. On subsequent runs, if this file exists, the scraper reuses it (avoids re-login). After manual login, the page waits for `**/dashboard**` URL (120s timeout) then saves state.

## Test structure

- `test_unit.py` — pure domain logic (no I/O, no mocks needed)
- `test_integration.py` — file I/O + use case pipeline with `MagicMock` for LLM adapter
- `test_spec.py` — validates conformance with `specs/tax_rules_schema.json`
- `test_e2e.py` — end-to-end pipeline
- `test_live_gemini.py` — smoke tests requiring real `GEMINI_API_KEY` and network

<!-- SPECKIT START -->

## Speckit — SDD Workflow

This project uses [Speckit](https://speckit.dev) for spec-driven development. Skills are in `.claude/skills/`. Artifacts live inside the active feature branch under `.specify/`.

**Active plan**: `specs/001-inspectir-core-spec/plan.md` (branch `001-inspectir-core-spec`).

### Full cycle (order matters)

| Step | Skill | Purpose |
|------|-------|---------|
| 0 | `/speckit-constitution` | Define project principles (one-time setup) |
| 1 | `/speckit-specify <feature>` | Create `spec.md` from natural language description |
| 2 | `/speckit-clarify` | Fill gaps in spec — asks up to 5 targeted questions, encodes answers back |
| 3 | `/speckit-plan` | Generate `plan.md` — design decisions, architecture notes |
| 4 | `/speckit-analyze` | Cross-check spec/plan/tasks for consistency before coding |
| 5 | `/speckit-tasks` | Generate dependency-ordered `tasks.md` |
| 6 | `/speckit-implement` | Execute tasks from `tasks.md` |
| 7 | `/speckit-checklist` | Generate review checklist post-implementation |
| 8 | `/speckit-taskstoissues` | Sync tasks to GitHub issues (optional) |

### Git hooks (auto-configured in `.specify/extensions.yml`)

Speckit auto-commits before/after each phase. Hooks run via `speckit.git.*` commands — no manual git needed during the cycle.

### Shortcuts

- Full cycle in one command: `/speckit` (runs specify → plan → tasks → implement)
- New feature branch: `/speckit-git-feature`
- Init git repo: `/speckit-git-initialize`

<!-- SPECKIT END -->
