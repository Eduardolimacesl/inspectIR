# Phase 1 — Data Model: InspectIR Core

Entidades e value objects do domínio. Estado atual + adições planejadas (US2/US4).
Fonte das constantes: `specs/tax_rules_schema.json` (carregadas no import de `domain/models.py`).

## Value Objects

### CNPJ (frozen)
- `valor: str` — normalizado para 14 dígitos numéricos no `__post_init__`.
- **Validação**: exatamente 14 dígitos; falha rápida com `ValueError` caso contrário.
- **Derivado**: `formatado` → `XX.XXX.XXX/XXXX-XX`.

### Beneficiario (frozen)
- `nome: str`
- `eh_titular: bool = False`
- `cpf: str = ""` — normalizado para dígitos no `__post_init__`.
- **Identidade**: `chave_identidade` = `cpf` quando presente, senão `nome` (fallback). O agrupamento
  do teto de educação usa a chave de identidade — homônimos com CPFs distintos contam separadamente
  (FR-011). ✅ Implementado.

### CPF (frozen)
- `valor: str` — normalizado para 11 dígitos numéricos no `__post_init__`; `ValueError` se inválido.
- **Derivado**: `formatado` → `XXX.XXX.XXX-XX`.

### CategoriaFiscal (enum)
- `SAUDE = "Saude"`, `EDUCACAO = "Educacao"`, `NAO_DEDUTIVEL = "Nao Dedutivel"`.

## Entities

### NotaFiscal (frozen)
| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | str | identificador único da nota |
| `emitente` | str | razão social do prestador |
| `cnpj` | CNPJ | value object validado |
| `valor` | float | ≥ 0 (schema `minimum: 0`) |
| `descricao` | str | texto bruto do serviço |
| `data` | datetime | parse de `dd/mm/aaaa` na leitura |

### NotaAuditada (frozen)
| Campo | Tipo | Regras |
|-------|------|--------|
| `nota` | NotaFiscal | nota de origem |
| `dedutivel` | bool | resultado da auditoria IA |
| `categoria` | CategoriaFiscal | classificação IA |
| `beneficiario` | Beneficiario | quem usufrui da despesa |
| `justificativa_legal` | str | fundamentação textual da IA |

## Domain Service — MotorCalculoIR

### Constantes (de `tax_rules_schema.json`)
| Constante | Valor atual | Status |
|-----------|-------------|--------|
| `TETO_EDUCACAO_INDIVIDUAL` | 3561.50 | ✅ |
| `ALIQUEOTA_PADRAO_RESTITUICAO` | 0.275 | ✅ |
| `LIMITE_PGBL_PERCENTUAL` | 0.12 | ✅ adicionado (US2) |
| `TETO_DESCONTO_SIMPLIFICADO` | 16754.34 | ✅ adicionado (US2) |

### `processar_calculos(notas_auditadas) -> dict` (existente)
- Soma saúde sem teto.
- Educação: agrupa por beneficiário e aplica `min(gasto, TETO_EDUCACAO_INDIVIDUAL)` por pessoa.
- Retorna `total_saude`, `total_educacao_dedutivel`, `detalhes_educacao_individuais`
  (`gasto_real`, `gasto_dedutivel`, `estourou_teto`), `total_deducoes_gerais`,
  `restituicao_estimada` (= base × alíquota).

### `analisar_pgbl(rbt, pgbl_atual) -> dict` (NOVO — US2)
- `limite_pgbl = rbt * LIMITE_PGBL_PERCENTUAL`
- `aporte_complementar = max(0, limite_pgbl - pgbl_atual)`
- `economia_estimada = aporte_complementar * ALIQUEOTA_PADRAO`
- `limite_atingido = pgbl_atual >= limite_pgbl`
- **Cenários**: US2.1 (RBT 100k, PGBL 4k → aporte 8k, economia 2.200), US2.4 (limite atingido).

### `recomendar_modelo(rbt, total_deducoes) -> dict` (NOVO — US2)
- `desconto_simplificado = min(rbt * 0.20, TETO_DESCONTO_SIMPLIFICADO)`
- `modelo = "Completo" se total_deducoes > desconto_simplificado senão "Simplificado"`
- Retorna `modelo_recomendado`, `desconto_simplificado`, `total_deducoes`, `vantagem` (delta).
- **Cenários**: US2.2 (deduções altas → Completo), US2.3 (deduções baixas → Simplificado).

## Persistência (formato em disco)

### `notas_brutas.json` — lista de objetos `NotaFiscal` serializados (data `dd/mm/aaaa`).
### `auditoria_final.json` — `{ "auditoria_fiscal": [ { id, emitente, cnpj, valor, dedutivel,
categoria, beneficiario_provavel, beneficiario_cpf, justificativa_legal } ] }`.
### `auth_state.json` — estado de sessão Playwright (NÃO versionado).
### `*.xlsx` — saída de exportação (US4), gerada sob demanda.

## Conformidade de Schema
`tests/test_spec.py` valida `NotaFiscal`/`NotaAuditada` e a presença/consistência das constantes
contra `specs/tax_rules_schema.json` (gate SDD do Princípio II).
