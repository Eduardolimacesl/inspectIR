# Implementation Plan: InspectIR — Assistente Pessoal de Auditoria Fiscal IRPF

**Branch**: `001-inspectir-core-spec` | **Date**: 2026-05-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-inspectir-core-spec/spec.md`

## Summary

Formalização do núcleo do InspectIR como spec executável sobre a base de código existente
(DDD + Hexagonal). Três das quatro user stories já têm implementação parcial (US1 auditoria,
US3 extração); o plano foca em (a) consolidar a auditoria e o motor de cálculo já existentes
sob contratos testáveis, (b) **mover a lógica determinística de PGBL e recomendação de modelo
(US2) para o domínio** — hoje ela só existe como prompt LLM em `DeepTaxAdvisorUseCase`, o que
conflita com Domain Purity e com a exigência de cálculo verificável por teste — e (c)
implementar a **exportação Excel (US4)**, ainda inexistente apesar de `openpyxl` já estar nas
dependências. Constantes novas (limite PGBL 12%, teto do desconto simplificado R$16.754,34)
entram em `specs/tax_rules_schema.json`, nunca hardcoded.

## Technical Context

**Language/Version**: Python 3.12 (mínimo 3.11; NÃO 3.14 — ausência de `_ctypes` quebra `pandas`/`streamlit`)

**Primary Dependencies**: `google-genai` (LLM), `playwright` (scraper), `streamlit` + `pandas` (UI), `openpyxl` (export Excel), `jsonschema` (validação de spec em testes), `pytest`

**Storage**: Arquivos JSON locais em `inspectir/data/` (`notas_brutas.json`, `auditoria_final.json`, `auth_state.json`); exportação `.xlsx` sob demanda

**Testing**: `pytest` executando `unittest.TestCase` — pirâmide: `test_unit` → `test_integration` → `test_spec` → `test_e2e` → `test_live_gemini` (opt-in)

**Target Platform**: Desktop localhost (Linux/macOS/Windows); navegador Chromium via Playwright para extração

**Project Type**: Single project — aplicação desktop Streamlit com camadas DDD/Hexagonal (`domain` / `application` / `infrastructure` / presentation)

**Performance Goals**: Pipeline completo em modo simulado < 30s (SC-002); pipeline downstream simulado < 5s (US3 cenário 3)

**Constraints**: Offline-capable (modo `simulado=True` obrigatório); privacy-first (nenhuma escrita fora de `inspectir/data/`, nenhum dado financeiro persistido externamente); Domain Purity (zero imports de infra em `domain/`); SDD (constantes fiscais só no schema)

**Scale/Scope**: Único contribuinte por instância (CPF único); 4 user stories; ~5 entidades de domínio; sem infraestrutura de nuvem

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Domain Purity (NON-NEGOTIABLE) | ⚠️ AÇÃO | US1/CNPJ/MotorCalculoIR já puros. **US2 viola hoje**: cálculos de PGBL/modelo estão em `DeepTaxAdvisorUseCase` (application) como prompt LLM. Plano move a aritmética para `MotorCalculoIR` (domínio); LLM fica só com a narrativa/justificativa. |
| II. Spec-Driven Development (NON-NEGOTIABLE) | ⚠️ AÇÃO | Constantes existentes (`TETO_EDUCACAO_INDIVIDUAL`, `ALIQUEOTA_PADRAO_RESTITUICAO`) já no schema. **Adicionar ao schema**: `LIMITE_PGBL_PERCENTUAL = 0.12` e `TETO_DESCONTO_SIMPLIFICADO = 16754.34`. Proibido hardcode. |
| III. Privacy-First / Zero-Knowledge | ✅ PASS | Escritas confinadas a `inspectir/data/`; export `.xlsx` gerado localmente. `.gitignore` deve cobrir `inspectir/data/`. |
| IV. Test-First (TDD) | ✅ PASS | Novos comportamentos (PGBL, recomendação de modelo, export) exigem teste antes da implementação em `test_unit`/`test_integration`. |
| V. Harness-First | ✅ PASS | `simulado=True` já presente em `extractor.py`/`ExtrairNotasUseCase`; export e PGBL são determinísticos e testáveis offline. |

**Resultado do gate**: PASS condicionado às duas ações ⚠️ acima (mover aritmética PGBL para o domínio; adicionar constantes ao schema). Ambas reforçam princípios NON-NEGOTIABLE — não são violações justificadas, são correções planejadas. `Complexity Tracking` permanece vazio.

## Project Structure

### Documentation (this feature)

```text
specs/001-inspectir-core-spec/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── motor_calculo_ir.md
│   ├── adaptador_gemini.md
│   └── exportador_excel.md
├── checklists/
│   └── requirements.md  # (já existente)
└── tasks.md             # Phase 2 output (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
domain/
├── __init__.py
└── models.py            # NotaFiscal, NotaAuditada, CNPJ, Beneficiario,
                         # CategoriaFiscal (enum), MotorCalculoIR (service)
                         # + NOVO: cálculo PGBL e recomendação de modelo

application/
├── __init__.py
└── use_cases.py         # ExtrairNotasUseCase, AuditarNotasUseCase,
                         # DeepTaxAdvisorUseCase (passa a delegar aritmética ao domínio)
                         # + NOVO: ExportarPlanilhaUseCase (US4)

infrastructure/
├── __init__.py
└── services.py          # AdaptadorGeminiFiscal (LLM), EscritorLeitorNotasLocal (I/O)
                         # + NOVO: ExportadorExcelLocal (openpyxl)

extractor.py             # Playwright scraper (headless=False, simulado=True)
app.py                   # Streamlit UI (presentation) — 4 tabs
specs/tax_rules_schema.json  # SSOT de constantes fiscais + JSON Schema

tests/
├── test_unit.py         # domínio puro (CNPJ, MotorCalculoIR, PGBL, modelo)
├── test_integration.py  # pipeline use case + MagicMock LLM + export
├── test_spec.py         # conformidade com tax_rules_schema.json
├── test_e2e.py          # pipeline ponta a ponta
└── test_live_gemini.py  # smoke (opt-in, requer GEMINI_API_KEY)
```

**Structure Decision**: Single project com arquitetura Hexagonal já estabelecida. Sem novos
módulos de topo; as adições (PGBL/modelo no domínio, export no application+infrastructure)
encaixam nas camadas existentes, preservando o isolamento `domain → application → infrastructure`.

## Complexity Tracking

> Nenhuma violação de constituição a justificar. As duas ações ⚠️ do Constitution Check
> aproximam o código dos princípios (não os violam), portanto esta tabela permanece vazia.
