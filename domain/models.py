# -*- coding: utf-8 -*-
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any

CAMINHO_SPEC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specs", "tax_rules_schema.json")

def carregar_especificacao_sdd() -> Dict[str, Any]:
    if not os.path.exists(CAMINHO_SPEC):
        return {
            "tax_constants": {
                "TETO_EDUCACAO_INDIVIDUAL": 3561.50,
                "ALIQUEOTA_PADRAO_RESTITUICAO": 0.275
            }
        }
    with open(CAMINHO_SPEC, "r", encoding="utf-8") as f:
        return json.load(f)

SPEC_DADOS = carregar_especificacao_sdd()
CONSTANTES_FISCAIS = SPEC_DADOS.get("tax_constants", {})

class CategoriaFiscal(Enum):
    SAUDE = "Saude"
    EDUCACAO = "Educacao"
    NAO_DEDUTIVEL = "Nao Dedutivel"

@dataclass(frozen=True)
class CNPJ:
    valor: str
    def __post_init__(self):
        numeros = "".join(filter(str.isdigit, self.valor))
        if len(numeros) != 14:
            raise ValueError("CNPJ inválido. O contrato exige exatamente 14 dígitos numéricos.")
        object.__setattr__(self, "valor", numeros)
    @property
    def formatado(self) -> str:
        v = self.valor
        return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"

@dataclass(frozen=True)
class Beneficiario:
    nome: str
    eh_titular: bool = False

@dataclass(frozen=True)
class NotaFiscal:
    id: str
    emitente: str
    cnpj: CNPJ
    valor: float
    descricao: str
    data: datetime

@dataclass(frozen=True)
class NotaAuditada:
    nota: NotaFiscal
    dedutivel: bool
    categoria: CategoriaFiscal
    beneficiario: Beneficiario
    justificativa_legal: str

class MotorCalculoIR:
    TETO_EDUCACAO_INDIVIDUAL = CONSTANTES_FISCAIS.get("TETO_EDUCACAO_INDIVIDUAL", 3561.50)
    ALIQUEOTA_PADRAO = CONSTANTES_FISCAIS.get("ALIQUEOTA_PADRAO_RESTITUICAO", 0.275)

    @classmethod
    def processar_calculos(cls, notas_auditadas: List[NotaAuditada]) -> Dict[str, Any]:
        total_saude = 0.0
        gastos_educacao_por_pessoa: Dict[str, float] = {}
        for n in notas_auditadas:
            if not n.dedutivel:
                continue
            if n.categoria == CategoriaFiscal.SAUDE:
                total_saude += n.nota.valor
            elif n.categoria == CategoriaFiscal.EDUCACAO:
                nome = n.beneficiario.nome
                gastos_educacao_por_pessoa[nome] = gastos_educacao_por_pessoa.get(nome, 0.0) + n.nota.valor
        total_educacao_dedutivel = 0.0
        detalhe_educacao: Dict[str, Dict[str, Any]] = {}
        for pessoa, gasto_bruto in gastos_educacao_por_pessoa.items():
            gasto_aproveitado = min(gasto_bruto, cls.TETO_EDUCACAO_INDIVIDUAL)
            total_educacao_dedutivel += gasto_aproveitado
            detalhe_educacao[pessoa] = {
                "gasto_real": gasto_bruto,
                "gasto_dedutivel": gasto_aproveitado,
                "estourou_teto": gasto_bruto > cls.TETO_EDUCACAO_INDIVIDUAL
            }
        base_deducoes = total_saude + total_educacao_dedutivel
        restituicao_estimada = base_deducoes * cls.ALIQUEOTA_PADRAO
        return {
            "total_saude": total_saude,
            "total_educacao_dedutivel": total_educacao_dedutivel,
            "detalhes_educacao_individuais": detalhe_educacao,
            "total_deducoes_gerais": base_deducoes,
            "restituicao_estimada": restituicao_estimada
        }
