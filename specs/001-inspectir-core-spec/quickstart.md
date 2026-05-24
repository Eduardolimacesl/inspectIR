# Quickstart — InspectIR Core

## Pré-requisitos
- Python 3.12 (mínimo 3.11; **não** 3.14 — falta `_ctypes`, quebra `pandas`/`streamlit`).
- `GEMINI_API_KEY` em variável de ambiente ou inserida na sidebar.

## Instalação
```bash
python3 -m pip install -r requirements.txt --break-system-packages
python3 -m playwright install chromium   # uma vez, só para extração real
```

## Rodar a aplicação
```bash
python3 -m streamlit run app.py
```
UI com 4 tabs: Painel de Despesas, Notas Auditadas, Consultoria & Planejamento IA, Processar & Configurar.

## Fluxo offline (Harness — sem rede, sem portal)
1. Marque **"Usar Extrator Simulado"** na sidebar (já vem ativo).
2. Aba **Processar** → "Iniciar Coleta & Auditoria" gera `inspectir/data/notas_brutas.json` e,
   com a auditoria IA, `inspectir/data/auditoria_final.json`.
3. **Painel** mostra Saúde, Educação e restituição estimada; **Notas** lista as auditadas.
4. **Consultoria IA** (US2): informe Renda Bruta e PGBL → parecer estratégico
   (cálculos determinísticos do domínio + narrativa do LLM).
5. **Exportar Excel** (US4): gera `.xlsx` a partir de `auditoria_final.json`.

## Testes
```bash
# suíte (sem smoke de rede)
python3 -m pytest tests/ -v --ignore=tests/test_live_gemini.py

# domínio puro (CNPJ, MotorCalculoIR, PGBL, recomendação de modelo)
python3 -m pytest tests/test_unit.py -v

# conformidade com o schema (gate SDD)
python3 -m pytest tests/test_spec.py -v
```

## Critérios de pronto (do spec)
- SC-002: pipeline simulado completo < 30s.
- SC-003/SC-004: recomendação de modelo e cálculo PGBL corretos em 100% dos cenários de teste.
- SC-005: nenhuma escrita fora de `inspectir/data/`.
- SC-006: alterar constante em `tax_rules_schema.json` propaga sem mexer em Python.
- SC-007: `.xlsx` abre em Excel/LibreOffice com todas as colunas exigidas.
