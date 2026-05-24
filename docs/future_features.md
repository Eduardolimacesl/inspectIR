# Roteiro de Novas Funcionalidades de IA — InspectIR

Este documento apresenta novas propostas de funcionalidades focadas no uso avançado de Inteligência Artificial e no ecossistema de APIs do Gemini para elevar o **InspectIR** ao patamar de uma plataforma de Wealth Management e Blindagem Fiscal pessoal.

---

## 1. Módulo Multimodal de Captura de Recibos (OCR + Gemini Vision)
### Descrição da Funcionalidade
Muitos profissionais de saúde (médicos, dentistas, psicólogos, fisioterapeutas) emitem recibos impressos ou PDFs simples assinados em vez de notas fiscais eletrônicas de serviço (NFS-e). Atualmente, esses gastos ficam de fora da raspagem de dados automáticos dos portais municipais.

### Como a IA é Utilizada
* O usuário faz o upload de uma imagem (JPEG/PNG) ou PDF do recibo físico diretamente no Streamlit.
* A infraestrutura do InspectIR envia a imagem para o **Gemini 2.5 Flash** (usando seus recursos multimodais).
* Através de um prompt estruturado ancorado em nossa especificação (`tax_rules_schema.json`), o Gemini extrai o CPF/CNPJ do prestador, o nome do paciente, a data do atendimento, o valor pago e a assinatura/carimbo do profissional de saúde, devolvendo um JSON perfeitamente formatado para o nosso modelo de domínio.

---

## 2. Simulador de Risco de Malha Fina (Preventive Risk Profiler)
### Descrição da Funcionalidade
O maior medo de quem realiza deduções elevadas de saúde é cair na "Malha Fina" da Receita Federal para comprovação de documentos. Esta funcionalidade visa dar segurança e paz de espírito ao contribuinte antes mesmo de ele enviar a declaração.

### Como a IA é Utilizada
* Com base na Renda Bruta Tributável informada e nas deduções totais compiladas, o Gemini analisa o comportamento estatístico das despesas.
* O modelo executa uma pesquisa web real (**Google Search Grounding**) para identificar os principais gatilhos históricos que levou contribuintes à malha fina nos anos anteriores (ex: variação brusca de gastos de saúde em relação ao ano anterior, proporção de despesa médica superior a $30\%$ da renda bruta, etc.).
* O sistema gera uma pontuação de risco matemática:

$$R_{risco} = f(D_{saude}, R_{anual}, \text{histórico})$$

* A IA sugere medidas de blindagem (ex: "Sua despesa odontológica está acima da média de sua faixa de renda. Certifique-se de anexar e salvar no InspectIR o contrato de prestação de serviços e as radiografias do tratamento para o caso de uma intimação preventiva").

---

## 3. Assistente de Triagem e Leitura de Planos de Saúde (Análise de Reembolso)
### Descrição da Funcionalidade
Quem possui convênio médico frequentemente paga consultas particulares e depois solicita reembolso (parcial ou integral) à operadora de saúde (como Bradesco, SulAmérica ou Unimed). Na declaração de Imposto de Renda, o usuário deve declarar o valor gasto **menos** o valor reembolsado. Calcular isso manualmente é uma tarefa exaustiva e propensa a erros.

### Como a IA é Utilizada
* O usuário faz o upload do arquivo PDF do extrato de reembolsos anuais gerado pelo portal do seu plano de saúde.
* O Gemini lê as tabelas do documento, identifica as datas correspondentes e deduz automaticamente o valor reembolsado do valor bruto das notas fiscais já capturadas no InspectIR.
* O motor de domínio processa o valor líquido dedutível real:

$$D_{real} = V_{bruto\_nota} - V_{reembolsado}$$

---

## 4. Planejamento Mensal Preditivo (Tax Forecast)
### Descrição da Funcionalidade
Em vez de simular o ganho tributário apenas em março/abril (período da entrega da declaração), o InspectIR passa a acompanhar as finanças do usuário de forma contínua durante todo o ano-calendário, oferecendo oportunidades mensais de otimização de fluxo de caixa.

### Como a IA é Utilizada
* O usuário conecta suas notas conforme o ano avança.
* O modelo de IA analisa o padrão de consumo e as projeções de salário e envia "notificações de oportunidades" preventivas, tais como:
    * *"Seu teto de PGBL para este ano é de R$ 12.000,00. Você investiu apenas R$ 4.000,00 até outubro. Recomendamos fazer aportes mensais de R$ 2.000,00 nos próximos meses para garantir um abatimento tributário de R$ 2.200,00 na sua restituição do ano que vem."*
    * *"Você acumulou R$ 3.000,00 em despesas de educação para o Enzo. Faltam apenas R$ 561,50 para bater o teto máximo de aproveitamento fiscal individual dele deste ano."*

---

## 5. Copiloto Conversacional de Consultoria Fiscal Tributária
### Descrição da Funcionalidade
Uma central de atendimento conversacional para responder dúvidas complexas do usuário sobre o que pode ou não ser deduzido, baseando-se em casos reais de sua vida cotidiana.

### Como a IA é Utilizada
* O usuário abre um chat integrado na interface do Streamlit e faz perguntas livres: *"Coloquei lentes de contato dentárias estéticas, posso deduzir no imposto?"* ou *"Paguei a faculdade do meu filho que fez 25 anos em outubro, ele ainda conta como dependente?"*
* O Gemini, utilizando RAG e **Google Search Grounding**, busca na base oficial de Perguntas e Respostas da Receita Federal e na jurisprudência atualizada para trazer uma resposta precisa, com fundamentação jurídica e links para fontes oficiais do governo, orientando o usuário sobre como proceder.
