# Harness de Execução e Mapeamento do InspectIR — Claude & Agent Guide

Este guia serve como manual de referência técnica, instrumentação e *Harness* (ambiente de testes/execução isolado) do **InspectIR**. Ele foi projetado para auxiliar agentes de Inteligência Artificial e desenvolvedores a mapear e interagir programaticamente com o ecossistema da aplicação sem quebrar os limites (*boundaries*) do domínio.

---

## 1. O Conceito de Harness no InspectIR

O **Harness** é um mecanismo de isolamento que permite executar, testar e simular todo o fluxo de processamento de notas fiscais e planejamento tributário sem dependências de infraestrutura física de rede (portais de prefeituras ou credenciais ativas da API do Gemini).

Ele é sustentado por três pilares de simulação e controle de estado:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INSPECTIR HARNESS                             │
├──────────────────────────────┬──────────────────────────────────────────┤
│ 1. Injeção de Dados (Mock)   │ Módulo `extractor.py` com flag           │
│                              │ `simulado=True` (Gera base de faturas)   │
├──────────────────────────────┼──────────────────────────────────────────┤
│ 2. Contrato Estrito (Spec)   │ Validação via `tax_rules_schema.json`    │
│                              │ (Segurança contra desvios de Schema)     │
├──────────────────────────────┼──────────────────────────────────────────┤
│ 3. Isolamento de Rede (Mocks)│ Testes de integração com `MagicMock`     │
│                              │ contornando requisições de API de IA     │
└──────────────────────────────┴──────────────────────────────────────────┘
```

Este ecossistema permite que uma IA ou pipeline de CI/CD faça testes de regressão de ponta a ponta avaliando regras matemáticas complexas em milissegundos.

---

## 2. Mapeamento Arquitetural (Ports & Adapters)

O software adota uma arquitetura inspirada em **Domain-Driven Design (DDD)** estruturada em camadas concêntricas. Segue o mapa de responsabilidade de cada arquivo:

### 2.1 Camada de Especificação (Spec Layer)
* **`specs/tax_rules_schema.json`**: A **Fonte Única de Verdade (SSOT)** do sistema. Contém constantes de negócios (tetos de educação, alíquota básica de restituição) e a estrutura formal (JSON Schema) que valida o contrato de dados de entrada e saída.

### 2.2 Camada de Domínio Puro (Domain Layer)
* **`domain/models.py`**:
    * *Value Objects*: `CNPJ` (valida e formata 14 dígitos), `Beneficiario`.
    * *Entidades*: `NotaFiscal` (fatura bruta original), `NotaAuditada` (fatura classificada pela IA com justificativa legal).
    * *Serviço de Domínio*: `MotorCalculoIR` (classe matemática pura que calcula limites, aplica tetos por beneficiário e projeta o retorno estimado).

### 2.3 Camada de Aplicação (Application Layer)
* **`application/use_cases.py`**:
    * `ExtrairNotasUseCase`: Coordena a busca física ou simulada de notas de despesas.
    * `AuditarNotasUseCase`: Orquestra o carregamento de notas brutos locais, delegação para a infraestrutura de IA e persistência estruturada do parecer.
    * `DeepTaxAdvisorUseCase`: Caso de uso estratégico que monta o prompt contextualizado e consome o Gemini com ferramentas de busca ativa para planejamento de previdência (PGBL) e otimização.

### 2.4 Camada de Infraestrutura (Infrastructure Layer)
* **`infrastructure/services.py`**:
    * `EscritorLeitorNotasLocal`: Serialização em disco dos formatos de entrada e saída.
    * `AdaptadorGeminiFiscal`: Implementação concreta do cliente Gemini com tratamento de erros por recuo exponencial (*backoff*).
* **`extractor.py`**: Webscraper dinâmico baseado em Playwright com persistência de cookies (`auth_state.json`) para bypass de CAPTCHA municipal.

---

## 3. Guia de Sandbox e Operações do Harness (Para Agentes de IA)

Caso você (Claude ou outro agente) precise atualizar regras de negócio ou debugar um comportamento tributário no sistema, siga os protocolos abaixo para garantir a segurança operacional.

### Protocolo A: Atualização de Limites Governamentais
Nunca altere constantes matemáticas diretamente nos arquivos de domínio (`domain/models.py`) ou na interface (`app.py`).
1. Abra o arquivo de especificação `specs/tax_rules_schema.json`.
2. Modifique o valor desejado em `tax_constants` (ex: atualizar o `TETO_EDUCACAO_INDIVIDUAL` se o governo alterar o limite anual).
3. Execute a suíte de testes de especificação para garantir que o domínio assimilou a regra:
   ```bash
   python -m unittest tests/test_spec.py
   ```

### Protocolo B: Simulação de Novas Notas para Testes
Para injetar uma nova nota fiscal na esteira de validação sem rodar o navegador ou gastar tokens de IA:
1. Abra `extractor.py` e adicione a nova estrutura de notas na lista interna dentro da condição `if simulado:`.
2. Rode o extrator para gerar o arquivo de dados brutos atualizado:
   ```bash
   python extractor.py
   ```
3. Execute o teste de integração para certificar-se de que o ecossistema está processando e salvando a fita de auditoria sem corromper o arquivo final:
   ```bash
   python -m unittest tests/test_integration.py
   ```

### Protocolo C: Executando Validação Completa de Sanidade
Antes de qualquer deploy ou push de código, execute os testes para validar o comportamento em lote:
```bash
# Executa os testes de regras e de especificação formais
python -m unittest discover -s tests
```

---

## 4. Rastreamento e Diagnóstico de Erros

O Harness expõe diagnósticos rápidos para detecção de problemas na esteira de execução:

1.  **Erro de Schema de CNPJ:** O domínio lança uma exceção `ValueError` imediata caso o CNPJ informado na nota brutas não contenha 14 dígitos numéricos após limpeza.
2.  **Erro de Conectividade Gemini:** O adaptador realiza 4 tentativas automáticas de requisição. Caso todas falhem, a infraestrutura lança um `RuntimeError` capturado de forma amigável pela interface web do Streamlit.
3.  **Divergência de Contratos (Contract Drift):** Se a IA retornar uma resposta com chaves diferentes das mapeadas no JSON Schema (`tax_rules_schema.json`), o motor falhará no parsing do JSON, acusando inconsistência estrutural imediatamente no log.
