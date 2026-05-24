# Contract — AdaptadorGeminiFiscal & DeepTaxAdvisor (infrastructure / application)

## AdaptadorGeminiFiscal.analisar_em_lote (existente)
```
analisar_em_lote(notas: List[NotaFiscal]) -> List[NotaAuditada]
```
- **Modelo**: `gemini-2.5-flash-preview-09-2025`, `response_mime_type="application/json"`,
  `temperature=0.1`.
- **Entrada serializada** (por nota): `{id, emitente, cnpj, valor, descricao, data(dd/mm/aaaa)}`.
- **Saída JSON esperada do LLM**:
```json
{"auditoria_fiscal": [
  {"id": "NF-2025-001", "dedutivel": true, "categoria": "Saude",
   "beneficiario_provavel": "Titular", "beneficiario_cpf": "",
   "justificativa_legal": "..."}
]}
```
- **Resiliência**: 4 tentativas, backoff exponencial base 2s (2→4→8s). Após 4 falhas →
  `RuntimeError("Erro na conexão Gemini: ...")`.
- **Mapeamento**: cada item casado por `id` à `NotaFiscal` de origem; itens sem match são
  ignorados; `eh_titular = (beneficiario_provavel.lower() == "titular")`.
- **Pré-condição**: `api_key` configurada (env `GEMINI_API_KEY` ou sidebar), senão `ValueError`.

## DeepTaxAdvisorUseCase.executar (US2) ✅ Refatorado
```
executar(api_key, renda_anual_bruta, previdencia_pgbl, dependentes_qtd, notas_auditadas) -> str
```
- **Mudança planejada**: a aritmética de PGBL e recomendação de modelo passa a vir de
  `MotorCalculoIR.analisar_pgbl` / `recomendar_modelo` (domínio, determinístico). O LLM recebe
  esses números prontos e gera **somente** o relatório narrativo em Markdown (`temperature=0.15`).
- **Saída**: string Markdown (parecer estratégico). Nenhum número fiscal é "inventado" pelo LLM.
- **Pré-condição**: `api_key` obrigatória (`ValueError` se ausente).
