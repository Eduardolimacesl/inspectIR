# 🛡️ InspectIR — Inteligência Fiscal Avançada

> **Assistente pessoal de auditoria fiscal com IA** para maximizar a restituição do IRPF de forma automatizada, precisa e com privacidade total dos dados.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?logo=google)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 O Problema

Declarar o Imposto de Renda de forma otimizada no Brasil exige planejamento fiscal que esbarra na descentralização dos portais públicos. O contribuinte enfrenta:

- **Dispersão de notas fiscais** entre portais estaduais (SEFIN) e municipais, causando perdas de deduções elegíveis.
- **Erros manuais** no preenchimento de campos essenciais (CNPJ de prestadores, valores de reembolso) no programa da Receita Federal.
- **Classificação ambígua** de despesas (Saúde vs. Educação) e dificuldade em calcular o benefício real do PGBL.
- **Falta de clareza matemática** para determinar o ponto de virada entre o Modelo Simplificado e o Modelo Completo.

## 🎯 O que é o InspectIR

O **InspectIR** automatiza toda a cadeia de inteligência fiscal em quatro etapas:

1. **Extração automatizada** de NF-e, NFC-e e NFS-e via Playwright (com suporte a login manual e persistência de sessão).
2. **Auditoria por IA** com o modelo Gemini, classificando despesas em Saúde, Educação ou Não Dedutível com justificativa legal.
3. **Motor de cálculo do IRPF** com aplicação dos limites legais (ex.: teto de educação de R$ 3.561,50/pessoa) e estimativa de restituição.
4. **Deep Tax Advisor** — consultoria estratégica personalizando a análise com base em renda bruta, PGBL e número de dependentes.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🔍 Extração via Playwright | Scraping headless do portal SEFIN com persistência de autenticação |
| 🤖 Auditoria por IA | Classificação determinística com Gemini 2.5 Flash (baixa temperatura) |
| 📊 Painel de Despesas | Visão consolidada de saúde, educação e restituição estimada |
| 🧠 Deep Tax Advisor | Parecer estratégico: Simplificado vs. Completo + otimização de PGBL |
| 📋 Notas Auditadas | Tabela completa com justificativas legais por nota |
| 📤 Exportação Excel | Planilha pronta para preenchimento da declaração |
| 🔒 Zero-Knowledge | Todos os dados ficam apenas no armazenamento local do usuário |

---

## 🏗️ Arquitetura

O projeto segue **DDD + Arquitetura Hexagonal (Ports & Adapters)**. O núcleo de regras fiscais está totalmente isolado da infraestrutura e da interface.

```
inspectIR/
├── specs/
│   └── tax_rules_schema.json   # SSOT — constantes fiscais (tetos, alíquotas)
├── domain/
│   └── models.py               # Entidades: NotaFiscal, NotaAuditada, CNPJ
│                               # Serviço: MotorCalculoIR
├── application/
│   └── use_cases.py            # Casos de uso: Extrair, Auditar, DeepTaxAdvisor
├── infrastructure/
│   └── services.py             # Adaptadores: Gemini (LLM) + I/O local
├── tests/                      # Suíte TDD/SDD completa
├── extractor.py                # Playwright scraper (portal SEFIN)
├── app.py                      # Interface Streamlit (camada de apresentação)
└── requirements.txt
```

### Fluxo de Dados

```
app.py (UI Streamlit)
    │
    ├─► ExtrairNotasUseCase ─► Playwright Scraper ─► notas_brutas.json
    │
    └─► AuditarNotasUseCase ─► AdaptadorGeminiFiscal (LLM)
                                        │
                                        └─► MotorCalculoIR (Domínio Puro)
                                                    │
                                                    └─► auditoria_final.json
```

> **Princípio-chave:** As constantes fiscais (`TETO_EDUCACAO_INDIVIDUAL`, `ALIQUEOTA_PADRAO`) residem exclusivamente em `specs/tax_rules_schema.json`. Nunca são hardcoded — qualquer atualização legal basta editar o spec, e todas as camadas refletem automaticamente.

---

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.11+
- Uma [chave de API do Google Gemini](https://ai.google.dev/)

### 1. Clone o repositório

```bash
git clone https://github.com/Eduardolimacesl/inspectIR.git
cd inspectIR
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Instale os navegadores do Playwright (uma vez)

```bash
playwright install chromium
```

### 5. Configure a chave de API

```bash
export GEMINI_API_KEY="sua-chave-aqui"
```

> Alternativamente, insira a chave diretamente na barra lateral da interface ao iniciar o app.

### 6. Execute a aplicação

```bash
streamlit run app.py
```

---

## 🧪 Testes

A suíte de testes segue a abordagem **TDD + SDD (Spec-Driven Development)**:

```bash
# Todos os testes
python -m pytest tests/

# Apenas testes unitários (sem I/O, sem mocks)
python -m pytest tests/test_unit.py -v

# Testes de conformidade com a especificação fiscal
python -m pytest tests/test_spec.py -v

# Smoke tests com Gemini real (requer GEMINI_API_KEY)
python -m pytest tests/test_live_gemini.py -v
```

| Arquivo | Escopo |
|---|---|
| `test_unit.py` | Regras de domínio puro (sem I/O) |
| `test_integration.py` | Pipeline completo com MagicMock para o LLM |
| `test_spec.py` | Conformidade com `tax_rules_schema.json` |
| `test_e2e.py` | End-to-end completo |
| `test_live_gemini.py` | Conectividade real com a API Gemini |

---

## 🔧 Modo Simulado

Para desenvolvimento e testes sem acessar o portal SEFIN, ative o **Extrator Simulado** na barra lateral do app (ou via flag `simulado=True` no código). Ele retorna notas fiscais de fixture predefinidas.

---

## 🛡️ Privacidade (Zero-Knowledge)

- **Nenhum dado é enviado para servidores externos**, exceto o conteúdo das notas fiscais para a API Gemini durante a auditoria.
- Credenciais do governo, chaves de API e notas fiscais brutas são salvas **exclusivamente no disco local**.
- O estado de autenticação do Playwright é persistido em `inspectir/data/auth_state.json` para evitar re-login.

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona minha feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

<div align="center">
  Feito com ☕ e IA para simplificar o IRPF brasileiro.
</div>
