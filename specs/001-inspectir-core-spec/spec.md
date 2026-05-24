# Feature Specification: InspectIR — Assistente Pessoal de Auditoria Fiscal IRPF

**Feature Branch**: `001-inspectir-core-spec`

**Created**: 2026-05-24

**Status**: Draft

**Input**: Formalização do sistema InspectIR a partir dos documentos existentes em `docs/`

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Auditoria Automática de Notas Fiscais (Priority: P1)

O contribuinte carrega ou solicita a extração de suas NF-e/NFC-e/NFS-e do ano-calendário.
O sistema classifica cada nota como Saúde (sem teto) ou Educação (teto por beneficiário),
calcula o total dedutível e estima o impacto na restituição de IRPF com base na alíquota
de 27,5%.

**Why this priority**: É o núcleo de valor do produto. Sem classificação e cálculo corretos,
todas as funcionalidades derivadas perdem sentido.

**Independent Test**: Dado um conjunto de notas fiscais de saúde e educação misturadas,
o sistema deve entregar um relatório de auditoria com deduções totais corretas — testável
isoladamente sem portal ou declaração real.

**Acceptance Scenarios**:

1. **Given** notas de saúde (consultas, hospitais, clínicas), **When** o motor auditoria processa, **Then** todas são classificadas como `SAUDE` sem aplicação de teto limitador.
2. **Given** três notas de educação para dependentes distintos (cada uma > R$3.561,50), **When** o motor processa, **Then** cada beneficiário tem teto aplicado individualmente (cap R$3.561,50/pessoa).
3. **Given** nota com CNPJ inválido (< 14 dígitos), **When** submetida ao motor, **Then** sistema rejeita com erro descritivo antes de processar.
4. **Given** falha temporária de API Gemini, **When** a requisição falha, **Then** sistema retenta até 4 vezes com backoff exponencial; após 4 falhas levanta erro amigável na interface.

---

### User Story 2 — Deep Tax Advisor: Planejamento Fiscal Estratégico (Priority: P2)

O contribuinte informa sua Renda Bruta Tributável anual e o valor atual de contribuição
PGBL. O sistema calcula: (a) o limite dedutível de PGBL (12% da RBT), (b) o aporte
complementar recomendado para atingir o teto, (c) a economia líquida de imposto estimada,
e (d) recomenda o modelo de declaração mais vantajoso (Simplificado vs. Completo).

**Why this priority**: Agrega valor de planejamento proativo, diferenciando o produto de
simples organizadores de NFs; impacto financeiro direto e mensurável para o usuário.

**Independent Test**: Dado RBT de R$100.000,00 e PGBL atual de R$6.000,00, o advisor
deve recomendar aporte adicional de R$6.000,00, economia estimada de R$1.650,00, e
verificar se Modelo Completo é vantajoso — sem necessitar de notas fiscais reais.

**Acceptance Scenarios**:

1. **Given** RBT = R$100.000 e PGBL atual = R$4.000, **When** advisor processa, **Then** recomenda aporte adicional = R$8.000, economia estimada = R$2.200 (8000 × 0,275).
2. **Given** total de deduções > min(RBT × 20%, R$16.754,34), **When** advisor compara modelos, **Then** recomenda Modelo Completo com justificativa matemática.
3. **Given** total de deduções < desconto simplificado aplicável, **When** advisor compara, **Then** recomenda Modelo Simplificado.
4. **Given** PGBL atual ≥ 12% de RBT, **When** advisor processa, **Then** informa que limite já atingido sem recomendar aportes adicionais.

---

### User Story 3 — Extração Automatizada de Notas do Portal SEFIN (Priority: P3)

O contribuinte aciona a extração automática de NFs do portal da prefeitura (SEFIN) via
automação de navegador. O sistema realiza login (com suporte a login manual na primeira
execução), navega pelo portal, captura as notas e persiste o resultado localmente.

**Why this priority**: Automatiza a etapa mais trabalhosa para o usuário; remove a
necessidade de exportação manual de CSVs e planilhas de portais governamentais.

**Independent Test**: Modo simulado (`simulado=True`) deve produzir notas fixtures
idênticas às do portal, permitindo teste completo do pipeline downstream sem acesso de rede.

**Acceptance Scenarios**:

1. **Given** primeira execução (sem `auth_state.json`), **When** extrator é acionado, **Then** abre navegador para login manual e aguarda redirecionamento ao dashboard (timeout 120s).
2. **Given** execução subsequente com `auth_state.json` válido, **When** extrator é acionado, **Then** reutiliza sessão sem abrir tela de login.
3. **Given** modo simulado ativo, **When** extrator é chamado, **Then** retorna conjunto de notas fixture sem tráfego de rede; pipeline completo executa em < 5s.
4. **Given** sessão expirada, **When** portal retorna erro de autenticação, **Then** sistema invalida `auth_state.json` e solicita novo login manual.

---

### User Story 4 — Exportação de Planilha para Declaração (Priority: P4)

Após auditoria concluída, o contribuinte exporta os dados em formato Excel, estruturado
para preenchimento direto no programa declarador da Receita Federal.

**Why this priority**: Fecha o ciclo de valor — sem exportação, o usuário ainda precisa
transcrever manualmente os dados auditados para a declaração.

**Independent Test**: Dado `auditoria_final.json` existente, a exportação deve gerar
`.xlsx` com colunas corretas (CNPJ prestador, beneficiário, valor dedutível, categoria)
sem dependência de portal ou IA.

**Acceptance Scenarios**:

1. **Given** auditoria finalizada com 10 notas, **When** usuário exporta, **Then** arquivo `.xlsx` gerado com uma linha por nota e colunas: CNPJ, prestador, beneficiário, valor, categoria, data.
2. **Given** nota com CNPJ formatado com pontos/barras/traços, **When** exportada, **Then** CNPJ aparece no formato padrão (XX.XXX.XXX/XXXX-XX) na planilha.

---

### Edge Cases

- O que acontece quando o portal SEFIN altera sua estrutura HTML e os seletores Playwright param de funcionar?
- Como o sistema trata notas com valor R$0,00 (cortesias, ajustes)?
- O que ocorre quando dois beneficiários têm o mesmo nome mas CPFs distintos?
- Como o sistema reage se `tax_rules_schema.json` estiver malformado (JSON inválido)?
- O que acontece se o usuário cancelar o login manual antes do timeout de 120s?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema MUST capturar NFs do portal SEFIN via automação de navegador com persistência de sessão entre execuções.
- **FR-002**: Sistema MUST classificar cada NF como `SAUDE` ou `EDUCACAO` com justificativa textual via LLM com temperatura ≤ 0,15.
- **FR-003**: Motor MUST aplicar teto de dedução de educação individualmente por beneficiário (valor configurado em `specs/tax_rules_schema.json`).
- **FR-004**: Motor MUST calcular dedução total de saúde sem aplicar nenhum teto limitador legal.
- **FR-005**: Sistema MUST calcular limite PGBL (12% RBT), aporte complementar recomendado e economia estimada ao receber RBT e contribuição atual.
- **FR-006**: Sistema MUST comparar Modelo Simplificado vs. Modelo Completo e recomendar o mais vantajoso com base matemática.
- **FR-007**: Sistema MUST exportar resultado da auditoria em arquivo Excel com campos exigidos pela Receita Federal.
- **FR-008**: Sistema MUST persistir notas brutas e auditoria final exclusivamente em disco local (`inspectir/data/`); nenhum dado financeiro enviado a serviços externos além da chamada transiente ao LLM.
- **FR-009**: Toda constante fiscal (teto educação, alíquota base, limite simplificado) MUST ser carregada de `specs/tax_rules_schema.json` em runtime — proibido hardcode em código Python.
- **FR-010**: Sistema MUST operar em modo simulado sem acesso de rede, retornando dados fixture para desenvolvimento e testes.

### Key Entities

- **NotaFiscal**: Fatura bruta capturada; campos: CNPJ prestador, beneficiário, valor, data, tipo serviço (descrição bruta).
- **NotaAuditada**: NF classificada pela IA; campos adicionais: categoria fiscal (`SAUDE`|`EDUCACAO`), valor dedutível calculado, justificativa legal textual.
- **Beneficiario**: Value object identificado por CPF; agrupa notas para aplicação individual do teto de educação.
- **CNPJ**: Value object com validação de 14 dígitos numéricos; falha rápida se inválido.
- **MotorCalculoIR**: Serviço de domínio puro; recebe lista de `NotaAuditada` + parâmetros PGBL, produz relatório de deduções e recomendação de modelo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das despesas de saúde classificadas corretamente sem teto; 100% das despesas de educação com teto por beneficiário aplicado — verificável via `test_unit.py` e `test_spec.py`.
- **SC-002**: Pipeline completo (extração simulada → auditoria → relatório) executa do início ao fim em < 30 segundos em modo simulado.
- **SC-003**: Recomendação de modelo (Simplificado vs. Completo) matematicamente correta para 100% dos cenários cobertos pelos testes de domínio.
- **SC-004**: Cálculo PGBL correto (limite, aporte complementar, economia) para qualquer combinação de RBT e contribuição atual — validado por testes unitários.
- **SC-005**: Zero dados financeiros do usuário persistidos em serviços externos; verificável por inspeção de código (nenhuma escrita fora de `inspectir/data/`).
- **SC-006**: Atualização de constante fiscal em `tax_rules_schema.json` propagada automaticamente sem alteração de código Python — validada por `test_spec.py`.
- **SC-007**: Arquivo Excel exportado contém todas as colunas exigidas e pode ser aberto por Microsoft Excel / LibreOffice Calc sem erros de formato.

---

## Assumptions

- Usuário possui Python 3.12 instalado no ambiente local (não 3.14 — ausência de `_ctypes` quebra dependências).
- `GEMINI_API_KEY` configurado como variável de ambiente ou inserido manualmente na sidebar da interface.
- Portal SEFIN utilizado é o da SEFAZ-CE ("Sua Nota Tem Valor"); suporte a outros portais estaduais/municipais está fora do escopo desta especificação.
- Reembolsos de planos de saúde são responsabilidade do usuário informar manualmente (dedução de reembolso automática está no roadmap futuro, não neste escopo).
- Um único contribuinte por instância da aplicação (CPF único); suporte a múltiplos contribuintes está fora do escopo.
- Planilha Excel exportada serve como referência de preenchimento — importação direta no programa da Receita Federal não é automatizada neste escopo.
- Infraestrutura de nuvem (deploy remoto, autenticação multi-usuário) está fora do escopo; o produto roda exclusivamente localhost.
