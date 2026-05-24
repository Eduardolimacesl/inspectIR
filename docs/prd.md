# Product Requirement Document (PRD) — InspectIR (Versão Inteligência Avançada)

## 1. Visão Geral do Produto
O **InspectIR** é um assistente pessoal de inteligência fiscal estruturado para automatizar a captura, triagem, auditoria e simulação de otimização de Notas Fiscais Eletrônicas (NF-e, NFC-e e NFS-e) sob o CPF do usuário. O foco principal é identificar de forma automatizada e inteligente todas as despesas dedutíveis para a Declaração de Ajuste Anual do Imposto de Renda Pessoa Física (IRPF 2026, ano-calendário 2025), maximizando o potencial de restituição legal com o recurso de uma auditoria assistida por Inteligência Artificial profunda.

## 2. O Problema
Declarar o Imposto de Renda de forma otimizada no Brasil exige um planejamento fiscal que esbarra na descentralização e complexidade dos portais públicos. O usuário enfrenta desafios como:
* Perda de prazos e esquecimento de notas fiscais elegíveis devido à dispersão entre portais estaduais (produtos) e municipais (serviços).
* Erros manuais no preenchimento de campos essenciais (como CNPJ de prestadores e valores de reembolso) no programa declarador da Receita Federal.
* Dificuldade em classificar despesas ambíguas e em calcular estrategicamente os benefícios de diferimento fiscal, tais como o limite dedutível de planos de previdência privada PGBL (limite legal de $12\%$).
* Falta de clareza matemática para determinar o ponto de virada exato entre o Modelo Simplificado e o Modelo Completo de declaração.

## 3. Objetivos e Metas
* **Centralizar e Automatizar:** Obter e centralizar o histórico de notas fiscais municipais e estaduais de forma estruturada.
* **Auditoria de Domínio Rigorosa:** Classificar de forma inequívoca despesas de Saúde (sem limite) e Educação (sujeitas a limite) através do modelo de linguagem.
* **Deep Tax Planning:** Fornecer aconselhamento financeiro proativo, calculando desvios em relação ao teto de dedução do PGBL e identificando potenciais omissões na base de dados coletada.
* **Garantia de Não-Divergência (SDD):** Garantir que qualquer atualização legal de limites fiscais seja automaticamente refletida em todas as camadas da aplicação através de um único arquivo de especificação declarativo.

## 4. Requisitos Funcionais (RF)
* **RF-001 - Extração via Playwright:** Capturar notas fiscais utilizando automação com navegação persistente para contornar autenticações e barreiras de segurança.
* **RF-002 - Módulo de Auditoria por IA:** Classificar o payload das notas fiscais usando o modelo Gemini com baixa temperatura para garantir determinismo estrutural.
* **RF-003 - Motor de Cálculo de Domínio:** Processar os limites individuais de Educação de R\$ 3.561,50 por CPF e agrupar despesas de forma consolidada.
* **RF-004 - Deep Tax Advisor:** Permitir que o usuário simule cenários de previdência, informe a sua Renda Bruta Tributável e receba recomendações fundamentadas sobre o melhor modelo de entrega (Simplificado vs. Completo).
* **RF-005 - Exportação:** Gerar planilhas do Excel prontas para introdução no preenchimento da declaração.

## 5. Requisitos Não Funcionais (RNF)
* **RNF-001 - Privacidade dos Dados (Zero-Knowledge):** Credenciais governamentais, chaves de API e notas fiscais brutas devem ser salvas apenas no ambiente de armazenamento local do usuário.
* **RNF-002 - Consistência (SDD):** As validações do modelo de dados e as constantes do motor fiscal devem derivar estritamente de uma especificação formal JSON comum.
* **RNF-003 - Portabilidade:** O sistema deve poder ser executado localmente via interface Streamlit sem necessidade de infraestrutura em nuvem.
