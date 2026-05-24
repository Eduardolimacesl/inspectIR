# Arquitetura de Software — InspectIR

A arquitetura do **InspectIR** segue os padrões de **Domain-Driven Design (DDD)** e **Arquitetura Hexagonal (Ports & Adapters)**, garantindo que o núcleo das regras de negócio fiscais brasileiras esteja totalmente isolado de bibliotecas externas, frameworks de interface gráfica e serviços de terceiros.

## 1. Estrutura Arquitetural do Projeto

```
inspectir/
├── specs/                     # Fonte Única de Verdade (SSOT)
│   └── tax_rules_schema.json  # Especificação formal e esquemas JSON (SDD)
├── domain/                    # Domínio Puro (Entidades, Value Objects, Serviços de Domínio)
│   ├── __init__.py
│   └── models.py              # Regras fiscais e motor de cálculo do IRPF
├── application/               # Casos de Uso (Orquestração de Fluxos de Trabalho)
│   ├── __init__.py
│   └── use_cases.py           # Casos de uso de extração, auditoria e planejamento
├── infrastructure/            # Adaptadores de Infraestrutura (Acesso de dados e APIs)
│   ├── __init__.py
│   └── services.py            # Adaptador Gemini, Leitores de Arquivos e Scrapers
├── tests/                     # Suíte de Testes Automatizados (TDD / SDD)
│   ├── __init__.py
│   ├── test_unit.py           # Testes unitários de domínio puro
│   ├── test_integration.py    # Testes de integração (mocks de arquivos e APIs)
│   ├── test_spec.py           # Testes de conformidade com a especificação formal
│   └── test_live_gemini.py    # Smoke Tests de conectividade de rede real
├── app.py                     # Camada de Apresentação (Interface Streamlit)
└── requirements.txt           # Arquivo de dependências Python
```

## 2. Fluxo de Dados e Interações de Camadas

```
   ┌────────────────────────────────────────────────────────┐
   │            Camada de Apresentação (app.py)             │
   └───────────┬────────────────────────────────┬───────────┘
               │                                │
               ▼                                ▼
   ┌───────────────────────┐        ┌───────────────────────┐
   │ ExtrairNotasUseCase   │        │ AuditarNotasUseCase   │
   └───────────┬───────────┘        └───────────┬───────────┘
               │                                │
               ▼ (Usa Adaptador)                ▼ (Usa Adaptador)
   ┌───────────────────────┐        ┌───────────────────────┐
   │  Playwright Scraper   │        │  AdaptadorGemini      │
   └───────────────────────┐        └───────────┬───────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │    MotorCalculoIR     │ (Domínio Puro)
                                    └───────────────────────┘
```

## 3. Decisões Tecnológicas e Justificativas
1. **Playwright:** Escolhido por permitir a execução interativa para logins manuais complexos de portais da SEFIN ou do programa "Sua Nota Tem Valor" da SEFAZ-CE, salvando os cookies e estado de autenticação em formato JSON para execuções subsequentes sem intervenção humana.
2. **Abstração de Armazenamento Local:** Leitura e escrita direta em disco através de serialização JSON de notas fiscais estruturadas. Evita-se o uso de bancos de dados externos complexos para proteger a privacidade dos dados financeiros do usuário.
3. **Desacoplamento de API (Gemini Client):** A comunicação com os modelos de linguagem reside na infraestrutura. Se os SDKs da Google forem atualizados, o código de regras de negócio de domínio permanece intacto.
