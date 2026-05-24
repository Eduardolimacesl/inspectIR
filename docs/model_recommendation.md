# Escolha do Modelo de IA e Pesquisa Fundamentada — InspectIR

O **InspectIR** utiliza uma abordagem híbrida inteligente para garantir a máxima eficácia, otimização e precisão nas suas análises de dedução e auditoria de notas fiscais.

## 1. Divisão Estratégica de Papéis entre Modelos

Para obter o máximo desempenho sem comprometer os custos ou a latência da aplicação, o sistema é estruturado para separar o pipeline de processamento em duas vertentes:

```
                  ┌─────────────────────────────────────────┐
                  │          notas_brutas.json              │
                  └────────────────────┬────────────────────┘
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
        ┌─────────────────────────┐         ┌─────────────────────────┐
        │  Mapeamento de Notas    │         │   Planejamento e IA     │
        │        (Lote)           │         │      (Consultoria)      │
        ├─────────────────────────┤         ├─────────────────────────┤
        │ Gemini 2.5 Flash        │         │ Gemini 2.5 Pro / Flash  │
        │ - Rápido e estruturado  │         │ - Raciocínio complexo   │
        │ - Saída em JSON estrito │         │ - Google Search Ativo   │
        └─────────────────────────┘         └─────────────────────────┘
```

## 2. O Valor Indispensável do Google Search Grounding

A legislação do Imposto de Renda no Brasil é frequentemente alterada por Instruções Normativas (IN) publicadas pela Receita Federal, decisões do Supremo Tribunal Federal (STF) sobre a tributação de pensões ou leis estaduais de incentivo fiscal.

A ativação do **Google Search Grounding** na funcionalidade **Deep Tax Advisor** garante que:
* A IA realize uma consulta em tempo real na internet para validar as regras do ano-calendário correto (2025 para o Exercício de 2026), mitigando alucinações baseadas em dados históricos desatualizados.
* O sistema fundamente as recomendações fiscais fornecendo links diretos e fontes para portais de notícias tributárias fidedignas ou Diários Oficiais.
* O planejamento fiscal emita alertas preventivos caso novas decisões ou normativos judiciais permitam a inclusão ou exclusão de novos tipos de despesas de saúde.

## 3. Recomendações de Prompting para Obter a Máxima Restituição
Para obter os melhores resultados possíveis das simulações de IA do Deep Advisor, as diretivas de prompting fornecidas ao Gemini exigem rigorosamente que o modelo se comporte como um planejador de patrimônio certificado (CFP). 

Isto inclui realizar cruzamentos lógicos de notas fiscais, simulações matemáticas do efeito PGBL contra a renda tributável e a recomendação clara do modelo de entrega ideal baseado no ponto de equilíbrio das despesas declaradas.
