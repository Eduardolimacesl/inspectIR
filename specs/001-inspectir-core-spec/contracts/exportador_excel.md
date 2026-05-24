# Contract — Exportação Excel (US4)

## ExportadorExcelLocal.exportar (infrastructure) ✅ Implementado
```
exportar(notas_auditadas: List[NotaAuditada], caminho_xlsx: str) -> str
```
- **Saída**: caminho do `.xlsx` gerado (via `openpyxl`). Diretório criado se inexistente.
- **Layout**: cabeçalho na linha 1; uma linha por nota.

| Coluna | Fonte | Formato |
|--------|-------|---------|
| CNPJ | `nota.cnpj.formatado` | `XX.XXX.XXX/XXXX-XX` |
| Prestador | `nota.emitente` | texto |
| Beneficiário | `beneficiario.nome` | texto |
| Valor | `nota.valor` | número (2 casas) |
| Categoria | `categoria.value` | `Saude`/`Educacao`/`Nao Dedutivel` |
| Data | `nota.data` | `dd/mm/aaaa` |

- **Invariantes**: CNPJ sempre formatado (US4 cenário 2); arquivo abrível por Excel/LibreOffice
  sem erros (SC-007).

## ExportarPlanilhaUseCase.executar (application) ✅ Implementado
```
executar(caminho_auditoria: str, caminho_xlsx: str) -> str
```
- Lê `auditoria_final.json`, reconstrói objetos de domínio, delega ao `ExportadorExcelLocal`.
- **Privacy-First**: escreve exclusivamente em caminho local sob controle do usuário.
- **Erro**: auditoria inexistente/vazia → mensagem amigável (nada a exportar).
