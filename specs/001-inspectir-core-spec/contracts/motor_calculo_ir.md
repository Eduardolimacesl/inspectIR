# Contract — MotorCalculoIR (domain service)

Serviço de domínio puro (stdlib apenas). Constantes carregadas de `tax_rules_schema.json`.

## processar_calculos (existente)
```
processar_calculos(notas_auditadas: List[NotaAuditada]) -> Dict[str, Any]
```
**Entrada**: lista de `NotaAuditada`.
**Saída**:
```json
{
  "total_saude": 5420.50,
  "total_educacao_dedutivel": 3561.50,
  "detalhes_educacao_individuais": {
    "ENZO ROCHA LIMA": {"gasto_real": 4200.00, "gasto_dedutivel": 3561.50, "estourou_teto": true}
  },
  "total_deducoes_gerais": 8982.00,
  "restituicao_estimada": 2470.05
}
```
**Invariantes**: saúde sem teto; educação com `min(gasto, TETO_EDUCACAO_INDIVIDUAL)` por
beneficiário; notas `dedutivel == false` ignoradas.

## analisar_pgbl (US2) ✅ Implementado
```
analisar_pgbl(rbt: float, pgbl_atual: float) -> Dict[str, Any]
```
**Saída**:
```json
{"limite_pgbl": 12000.0, "aporte_complementar": 8000.0, "economia_estimada": 2200.0, "limite_atingido": false}
```
**Invariantes**: `limite_pgbl = rbt * LIMITE_PGBL_PERCENTUAL`; `aporte_complementar` nunca negativo;
`economia_estimada = aporte_complementar * ALIQUEOTA_PADRAO`.

## recomendar_modelo (US2) ✅ Implementado
```
recomendar_modelo(rbt: float, total_deducoes: float) -> Dict[str, Any]
```
**Saída**:
```json
{"modelo_recomendado": "Completo", "desconto_simplificado": 16754.34, "total_deducoes": 20000.0, "vantagem": 3245.66}
```
**Invariantes**: `desconto_simplificado = min(rbt * 0.20, TETO_DESCONTO_SIMPLIFICADO)`;
`Completo` sse `total_deducoes > desconto_simplificado`.

## Erros
- Entradas numéricas negativas → `ValueError` descritivo.
- Constante ausente no schema → fallback documentado em `carregar_especificacao_sdd` (mas o
  schema é o caminho esperado; `test_spec.py` garante presença).
