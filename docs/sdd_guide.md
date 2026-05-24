# Guia de Spec-Driven Development (SDD) — InspectIR

Este guia documenta o processo de desenvolvimento orientado por especificação técnica formal adotado no **InspectIR**, com base nos princípios de Source of Truth (SSOT) do `github/spec-kit`.

## 1. O que é o Spec-Driven Development?
Tradicionalmente, os desenvolvedores escrevem código e depois redigem a documentação e os testes. No **InspectIR**, a especificação formal declarada em `inspectir/specs/tax_rules_schema.json` é a **fonte única de verdade**.
O código de domínio consome este JSON para carregar limites e calibrar validações, e a suíte de testes executa asserções diretamente contra os dados estruturados declarados na especificação.

## 2. Vantagens do SDD contra o "Contract Drift"
* **Sincronização de Regras de Negócio:** Se o limite anual de educação for atualizado pela autoridade fiscal, a alteração é efetuada unicamente no arquivo JSON de regras. O motor de cálculo e os testes de integração adaptam-se de forma automática, sem necessidade de alteração de linhas de código de lógica tributária.
* **Consistência de Mocks de IA:** A resposta em JSON estruturado esperada da API do Gemini é governada pelas definições de esquemas contidas no JSON Schema. Desta forma, o comportamento e a validação do payload estão sempre sincronizados.

## 3. Como Manter e Atualizar a Especificação
Ao alterar ou adicionar uma propriedade (por exemplo, ao criar um novo campo de despesa dedutível), siga este fluxo de trabalho:
1. Abra o arquivo `inspectir/specs/tax_rules_schema.json`.
2. Update as propriedades no bloco de definições correspondente.
3. Altere o número da versão declarada na chave `"version"`.
4. Execute o comando de validação de especificações:
   ```bash
   python -m unittest inspectir/tests/test_spec.py
   ```
5. Os testes validarão automaticamente se as entidades do modelo Python e o comportamento do motor fiscal continuam em paridade estrutural direta com o esquema JSON configurado.
