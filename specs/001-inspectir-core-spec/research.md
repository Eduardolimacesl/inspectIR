# Phase 0 — Research: InspectIR Core

Consolidação das decisões técnicas. A maior parte do stack já está definida no código e na
constituição; este documento resolve os pontos abertos das user stories US2 e US4 e ratifica
as escolhas existentes.

## R1 — Onde fica a aritmética de PGBL e recomendação de modelo (US2)?

- **Decision**: A aritmética (limite PGBL = 12% da RBT, aporte complementar, economia =
  base × alíquota, comparação Simplificado × Completo) vive em `MotorCalculoIR` no domínio.
  O LLM (`DeepTaxAdvisorUseCase`) recebe os números já calculados e produz apenas a narrativa
  textual/justificativa em Markdown.
- **Rationale**: Princípio I (Domain Purity) e SC-003/SC-004 exigem cálculo determinístico e
  verificável por teste unitário. Um número gerado por LLM não é reproduzível nem auditável.
- **Alternatives considered**: Manter tudo no prompt LLM (rejeitado: não determinístico, viola
  Domain Purity, impossível de testar com `test_unit`); criar serviço separado fora do domínio
  (rejeitado: a lógica é regra fiscal pura, pertence ao domínio).

## R2 — Constantes fiscais novas para US2

- **Decision**: Adicionar a `specs/tax_rules_schema.json`:
  `LIMITE_PGBL_PERCENTUAL = 0.12` e `TETO_DESCONTO_SIMPLIFICADO = 16754.34`.
  `MotorCalculoIR` carrega ambas no import, como já faz com as demais.
- **Rationale**: Princípio II (SDD) — nenhum valor fiscal hardcoded. O cenário US2.2 referencia
  explicitamente `min(RBT × 20%, R$16.754,34)`; o percentual 12% de PGBL é regra legal.
- **Alternatives considered**: Hardcode em Python (rejeitado: viola NON-NEGOTIABLE II e SC-006).

## R3 — Cálculo do desconto simplificado

- **Decision**: Desconto simplificado = `min(RBT × 0,20, TETO_DESCONTO_SIMPLIFICADO)`.
  Recomenda-se Modelo Completo quando `total_deducoes > desconto_simplificado`, senão Simplificado.
- **Rationale**: Reflete a regra da Receita Federal e os cenários US2.2/US2.3.
- **Alternatives considered**: Comparar restituições absolutas dos dois modelos (equivalente, mas
  a comparação de base dedutível vs. desconto é mais direta e cobre os cenários do spec).

## R4 — Exportação Excel (US4)

- **Decision**: `ExportadorExcelLocal` (infrastructure) usa `openpyxl` para gerar `.xlsx` com uma
  linha por nota e colunas: CNPJ (formato `XX.XXX.XXX/XXXX-XX`), prestador, beneficiário, valor,
  categoria, data. Orquestrado por `ExportarPlanilhaUseCase` lendo `auditoria_final.json`.
- **Rationale**: `openpyxl` já é dependência; CNPJ formatado já disponível via `CNPJ.formatado`.
  Geração local satisfaz Privacy-First (III).
- **Alternatives considered**: `pandas.to_excel` (rejeitado: menos controle de formatação de
  célula/cabeçalho e acopla a camada de export ao pandas além do necessário); CSV (rejeitado:
  US4 exige `.xlsx` abrível por Excel/LibreOffice — SC-007).

## R5 — Resiliência da chamada Gemini

- **Decision**: Manter backoff exponencial (4 tentativas, base 2s, dobrando) em
  `AdaptadorGeminiFiscal`; `temperature ≤ 0,15`; `response_mime_type="application/json"` na
  auditoria. Após 4 falhas, erro amigável propagado à UI.
- **Rationale**: US1 cenário 4 e Technology Constraints da constituição.
- **Alternatives considered**: Retry fixo sem backoff (rejeitado: pressão sobre API em falha
  transiente); sem retry (rejeitado: falha o cenário US1.4).

## R6 — Persistência de sessão do scraper (US3)

- **Decision**: `auth_state.json` em `inspectir/data/`; reutiliza sessão se existir, senão login
  manual com `wait_for_url("**/dashboard**", timeout=120000)` e salva o estado. Sessão expirada
  invalida o arquivo e solicita novo login.
- **Rationale**: Princípio V (Harness-First) e cenários US3.1/US3.2/US3.4.
- **Alternatives considered**: Login programático com credenciais armazenadas (rejeitado: viola
  Privacy-First e fragilidade frente a captcha/2FA do portal).

## Itens NEEDS CLARIFICATION

Nenhum. Todos os pontos do Technical Context estão resolvidos pela base de código existente,
pela constituição e pelas decisões R1–R6.
