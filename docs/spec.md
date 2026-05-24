# Especificação Matemática e Contratos de Negócio — InspectIR

Este documento descreve as fórmulas matemáticas aplicadas pelo motor de domínio do **InspectIR** para calcular as deduções e simular o planejamento profundo de IRPF.

## 1. Regra das Deduções e Abatimentos de IRPF

O montante total dedutível calculado pelo motor é governado pela seguinte expressão:

$$D_{total} = D_{saude} + \sum_{i=1}^{n} \min(D_{educacao, i}, T_{educacao})$$

Onde:
* $D_{saude}$ representa o somatório das despesas hospitalares, clínicas e consultas legítimas elegíveis (sem teto limitador legal).
* $D_{educacao, i}$ representa as despesas de educação formal declaradas para o indivíduo $i$ (seja o titular ou um dependente específico).
* $T_{educacao}$ é o teto máximo dedutível para educação por indivíduo, estabelecido dinamicamente na especificação central como $R\$\,3.561,50$.

A estimativa do impacto direto na restituição do usuário, baseada na alíquota progressiva padrão de $27,5\%$, é expressa por:

$$R_{estimado} = D_{total} \times 0.275$$

## 2. Planejamento de Previdência Privada (PGBL)

O diferimento fiscal máximo permitido por lei para aplicações em planos de previdência privada do tipo PGBL é limitado a $12\%$ dos rendimentos brutos tributáveis anuais do usuário:

$$L_{limite} = R_{anual} \times 0.12$$

Se o usuário contribui atualmente com uma quantia $C_{atual}$ que seja menor do que o teto permitido ($L_{limite}$), o valor recomendado de aporte adicional para o final do ano-calendário é dado por:

$$I_{restante} = L_{limite} - C_{atual}$$

La economia líquida de imposto gerada pelo aporte complementar deste montante restante é calculada como:

$$E_{economia} = I_{restante} \times 0.275$$

## 3. Modelo Simplificado vs. Modelo Completo

O desconto simplificado padrão substitui todas as deduções legais por um abatimento fixo de $20\%$ sobre a renda tributável, limitado por lei ao teto máximo de $R\$\,16.754,34$.

O sistema avalia que a declaração pelo Modelo Completo é vantajosa para o usuário se, e apenas se:

$$D_{total} > \min(R_{anual} \times 0.20, 16754.34)$$
