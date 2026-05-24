---

description: "Task list for InspectIR core spec implementation"
---

# Tasks: InspectIR — Assistente Pessoal de Auditoria Fiscal IRPF

**Input**: Design documents from `/specs/001-inspectir-core-spec/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: INCLUÍDOS — a constituição (Princípio IV, Test-First/TDD) torna os testes obrigatórios. Escreva os testes antes da implementação e garanta que falham primeiro.

**Organization**: Tarefas agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependências pendentes)
- **[Story]**: user story associada (US1–US4)

## Path Conventions

Single project, layout DDD/Hexagonal na raiz: `domain/`, `application/`, `infrastructure/`, `app.py`, `extractor.py`, `specs/`, `tests/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar ambiente e baseline.

- [ ] T001 Verificar Python 3.12 (não 3.14) e instalar dependências: `python3 -m pip install -r requirements.txt --break-system-packages`
- [ ] T002 [P] Instalar navegador Playwright (uma vez, para extração real US3): `python3 -m playwright install chromium`
- [ ] T003 [P] Estabelecer baseline verde executando `python3 -m pytest tests/ -v --ignore=tests/test_live_gemini.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base compartilhada por todas as stories — domínio puro, loader SDD e persistência local.

**⚠️ CRITICAL**: Nenhuma user story começa antes desta fase.

- [ ] T004 Confirmar loader SDD `carregar_especificacao_sdd()` lendo `specs/tax_rules_schema.json` no import em domain/models.py
- [ ] T005 [P] Confirmar value objects/entidades puros (sem imports de infra) em domain/models.py: `CNPJ`, `Beneficiario`, `CategoriaFiscal`, `NotaFiscal`, `NotaAuditada`
- [ ] T006 [P] Confirmar adaptador de persistência local `EscritorLeitorNotasLocal` (salvar/carregar brutas e auditoria em `inspectir/data/`) em infrastructure/services.py

**Checkpoint**: Fundação pronta — user stories podem iniciar.

---

## Phase 3: User Story 1 — Auditoria Automática de Notas Fiscais (Priority: P1) 🎯 MVP

**Goal**: Classificar NFs em Saúde (sem teto) / Educação (teto por beneficiário) e estimar restituição (27,5%).

**Independent Test**: Dado um conjunto misto de notas de saúde e educação, o sistema entrega auditoria com deduções totais corretas — sem portal nem declaração real.

### Tests for User Story 1 ⚠️ (escrever primeiro, devem falhar)

- [ ] T007 [P] [US1] Teste unitário de `CNPJ` (14 dígitos, `formatado`, falha em inválido) em tests/test_unit.py
- [ ] T008 [P] [US1] Teste unitário de `MotorCalculoIR.processar_calculos` (saúde sem teto; educação com teto por beneficiário; nota não dedutível ignorada) em tests/test_unit.py
- [ ] T009 [P] [US1] Teste de integração do pipeline de auditoria com `MagicMock` no adaptador LLM em tests/test_integration.py

### Implementation for User Story 1

- [ ] T010 [US1] Implementar/confirmar `MotorCalculoIR.processar_calculos` em domain/models.py
- [ ] T011 [US1] Implementar/confirmar `AdaptadorGeminiFiscal.analisar_em_lote` (saída JSON, temperatura 0,1, backoff 4× base 2s) em infrastructure/services.py
- [ ] T012 [US1] Implementar/confirmar `AuditarNotasUseCase.executar` (carrega brutas → audita → salva `auditoria_final.json`) em application/use_cases.py
- [ ] T013 [US1] Exibir métricas do painel (Saúde, Educação, Restituição) na aba Painel em app.py
- [ ] T014 [US1] Tratar caminhos de erro: CNPJ inválido (falha rápida) e falha do Gemini após 4 tentativas (erro amigável na UI) em app.py / infrastructure/services.py

**Checkpoint**: US1 totalmente funcional e testável de forma independente (MVP).

---

## Phase 4: User Story 2 — Deep Tax Advisor: Planejamento Fiscal Estratégico (Priority: P2)

**Goal**: Calcular limite PGBL (12% RBT), aporte complementar, economia estimada e recomendar Modelo Simplificado vs. Completo — cálculo determinístico no domínio; LLM apenas narra.

**Independent Test**: RBT R$100.000 e PGBL R$6.000 → aporte adicional R$6.000, economia ~R$1.650, e verificação de modelo — sem notas reais.

### Tests for User Story 2 ⚠️ (escrever primeiro, devem falhar)

- [ ] T015 [P] [US2] Atualizar tests/test_spec.py para exigir `LIMITE_PGBL_PERCENTUAL` e `TETO_DESCONTO_SIMPLIFICADO` no schema
- [ ] T016 [P] [US2] Teste unitário de `MotorCalculoIR.analisar_pgbl` (RBT 100k/PGBL 4k → aporte 8k, economia 2200; PGBL ≥ 12% → limite atingido) em tests/test_unit.py
- [ ] T017 [P] [US2] Teste unitário de `MotorCalculoIR.recomendar_modelo` (deduções > desconto → Completo; deduções < desconto → Simplificado) em tests/test_unit.py

### Implementation for User Story 2

- [ ] T018 [US2] Adicionar `LIMITE_PGBL_PERCENTUAL = 0.12` e `TETO_DESCONTO_SIMPLIFICADO = 16754.34` em specs/tax_rules_schema.json
- [ ] T019 [US2] Carregar as novas constantes em `MotorCalculoIR` (do schema, sem hardcode) em domain/models.py
- [ ] T020 [P] [US2] Implementar `MotorCalculoIR.analisar_pgbl(rbt, pgbl_atual)` em domain/models.py
- [ ] T021 [P] [US2] Implementar `MotorCalculoIR.recomendar_modelo(rbt, total_deducoes)` em domain/models.py
- [ ] T022 [US2] Refatorar `DeepTaxAdvisorUseCase` para usar os cálculos do domínio e passar números prontos ao LLM (apenas narrativa Markdown, temperatura 0,15) em application/use_cases.py
- [ ] T023 [US2] Atualizar aba Consultoria IA para exibir PGBL/modelo + parecer em app.py

**Checkpoint**: US1 e US2 funcionam de forma independente.

---

## Phase 5: User Story 3 — Extração Automatizada de Notas do Portal SEFIN (Priority: P3)

**Goal**: Extrair NFs do portal via Playwright com login manual na primeira execução e persistência de sessão.

**Independent Test**: Modo `simulado=True` produz fixtures idênticas ao portal; pipeline downstream completo em < 5s sem rede.

### Tests for User Story 3 ⚠️ (escrever primeiro, devem falhar)

- [ ] T024 [P] [US3] Teste de integração: caminho `simulado=True` retorna fixtures sem rede e pipeline < 5s em tests/test_integration.py

### Implementation for User Story 3

- [ ] T025 [US3] Confirmar fixtures de `capturar_notas_portal_sefin(simulado=True)` e `ExtrairNotasUseCase` modo simulado em extractor.py / application/use_cases.py
- [ ] T026 [US3] Confirmar persistência/reuso de `auth_state.json` e espera de `**/dashboard**` (timeout 120s) na primeira execução em extractor.py
- [ ] T027 [US3] Tratar sessão expirada: invalidar `auth_state.json` e solicitar novo login manual em extractor.py

**Checkpoint**: US1, US2 e US3 funcionam de forma independente.

---

## Phase 6: User Story 4 — Exportação de Planilha para Declaração (Priority: P4)

**Goal**: Exportar a auditoria em `.xlsx` pronto para conferência na declaração da Receita Federal.

**Independent Test**: Dado `auditoria_final.json`, a exportação gera `.xlsx` com colunas corretas (CNPJ formatado, prestador, beneficiário, valor, categoria, data) sem portal nem IA.

### Tests for User Story 4 ⚠️ (escrever primeiro, devem falhar)

- [ ] T028 [P] [US4] Teste de integração: exportação gera `.xlsx` com todas as colunas exigidas e CNPJ no formato `XX.XXX.XXX/XXXX-XX` em tests/test_integration.py

### Implementation for User Story 4

- [ ] T029 [US4] Implementar `ExportadorExcelLocal.exportar` (openpyxl: cabeçalho + 1 linha/nota) em infrastructure/services.py
- [ ] T030 [US4] Implementar `ExportarPlanilhaUseCase.executar` (lê `auditoria_final.json`, reconstrói domínio, delega ao exportador) em application/use_cases.py
- [ ] T031 [US4] Adicionar botão de exportação/download na UI em app.py

**Checkpoint**: Todas as user stories funcionam de forma independente.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e preocupações transversais.

- [ ] T032 [P] Validar `quickstart.md`: pipeline simulado completo do início ao fim < 30s (SC-002)
- [ ] T033 [P] Atualizar docs/ e CLAUDE.md se o comportamento mudou
- [ ] T034 Garantir que `.gitignore` cobre `inspectir/data/` (auth_state, auditoria) — Privacy-First (SC-005)
- [ ] T035 Execução final verde: `python3 -m pytest tests/ -v --ignore=tests/test_live_gemini.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode iniciar imediatamente
- **Foundational (Phase 2)**: depende do Setup — BLOQUEIA todas as user stories
- **User Stories (Phase 3–6)**: dependem da Foundational; podem then proceder em paralelo ou em ordem de prioridade (P1→P2→P3→P4)
- **Polish (Phase 7)**: depende das stories desejadas concluídas

### User Story Dependencies

- **US1 (P1)**: após Foundational — sem dependências de outras stories
- **US2 (P2)**: após Foundational — independente; reaproveita métricas de deduções de US1 mas é testável isoladamente
- **US3 (P3)**: após Foundational — independente; alimenta as brutas consumidas por US1, mas o modo simulado a torna testável isoladamente
- **US4 (P4)**: após Foundational — consome `auditoria_final.json` (produzido por US1), mas testável a partir de um JSON fixture

### Within Each User Story

- Testes escritos e falhando ANTES da implementação (TDD)
- Schema/constantes antes do domínio que as carrega (US2: T018/T019 antes de T020/T021)
- Modelos/domínio antes de serviços; serviços antes de UI
- Story completa antes de avançar para a próxima prioridade

### Parallel Opportunities

- Setup: T002 e T003 em paralelo
- Foundational: T005 e T006 em paralelo
- Testes marcados [P] dentro de uma story rodam em paralelo
- US2: T020 e T021 em paralelo (métodos distintos, mesmo arquivo — coordenar se editados juntos)
- Com equipe: após a Foundational, US1–US4 podem ser tocadas em paralelo

---

## Parallel Example: User Story 1

```bash
# Testes da US1 juntos (devem falhar primeiro):
Task: "Teste unitário de CNPJ em tests/test_unit.py"
Task: "Teste unitário de MotorCalculoIR.processar_calculos em tests/test_unit.py"
Task: "Teste de integração do pipeline com MagicMock em tests/test_integration.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 Setup
2. Phase 2 Foundational (CRÍTICO — bloqueia tudo)
3. Phase 3 US1
4. **PARAR e VALIDAR**: testar US1 isoladamente
5. Demonstrar (MVP)

### Incremental Delivery

1. Setup + Foundational → fundação pronta
2. US1 → testar → demo (MVP)
3. US2 → testar → demo
4. US3 → testar → demo
5. US4 → testar → demo

---

## Notes

- [P] = arquivos diferentes, sem dependências
- Verificar que os testes falham antes de implementar (TDD — Princípio IV)
- Toda constante fiscal só em `specs/tax_rules_schema.json` (Princípio II); proibido hardcode
- `domain/` sem imports de infraestrutura (Princípio I)
- Nenhuma escrita fora de `inspectir/data/` (Princípio III)
- Commit após cada tarefa ou grupo lógico
