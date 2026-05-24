# -*- coding: utf-8 -*-
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any

CAMINHO_SPEC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specs", "tax_rules_schema.json")

CONSTANTES_PADRAO = {
    "tax_constants": {
        "TETO_EDUCACAO_INDIVIDUAL": 3561.50,
        "ALIQUEOTA_PADRAO_RESTITUICAO": 0.275,
        "LIMITE_PGBL_PERCENTUAL": 0.12,
        "TETO_DESCONTO_SIMPLIFICADO": 16754.34
    }
}

def carregar_especificacao_sdd() -> Dict[str, Any]:
    if not os.path.exists(CAMINHO_SPEC):
        return CONSTANTES_PADRAO
    try:
        with open(CAMINHO_SPEC, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return CONSTANTES_PADRAO

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
class CPF:
    valor: str
    def __post_init__(self):
        numeros = "".join(filter(str.isdigit, self.valor))
        if len(numeros) != 11:
            raise ValueError("CPF inválido. O contrato exige exatamente 11 dígitos numéricos.")
        object.__setattr__(self, "valor", numeros)
    @property
    def formatado(self) -> str:
        v = self.valor
        return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"

@dataclass(frozen=True)
class Beneficiario:
    nome: str
    eh_titular: bool = False
    cpf: str = ""
    def __post_init__(self):
        numeros = "".join(filter(str.isdigit, self.cpf))
        object.__setattr__(self, "cpf", numeros)
    @property
    def chave_identidade(self) -> str:
        return self.cpf if self.cpf else self.nome

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
    LIMITE_PGBL_PERCENTUAL = CONSTANTES_FISCAIS.get("LIMITE_PGBL_PERCENTUAL", 0.12)
    TETO_DESCONTO_SIMPLIFICADO = CONSTANTES_FISCAIS.get("TETO_DESCONTO_SIMPLIFICADO", 16754.34)

    @classmethod
    def processar_calculos(cls, notas_auditadas: List[NotaAuditada]) -> Dict[str, Any]:
        total_saude = 0.0
        gastos_educacao_por_pessoa: Dict[str, float] = {}
        rotulo_por_chave: Dict[str, Dict[str, str]] = {}
        for n in notas_auditadas:
            if not n.dedutivel:
                continue
            if n.categoria == CategoriaFiscal.SAUDE:
                total_saude += n.nota.valor
            elif n.categoria == CategoriaFiscal.EDUCACAO:
                chave = n.beneficiario.chave_identidade
                gastos_educacao_por_pessoa[chave] = gastos_educacao_por_pessoa.get(chave, 0.0) + n.nota.valor
                rotulo_por_chave[chave] = {"nome": n.beneficiario.nome, "cpf": n.beneficiario.cpf}
        total_educacao_dedutivel = 0.0
        detalhe_educacao: Dict[str, Dict[str, Any]] = {}
        for chave, gasto_bruto in gastos_educacao_por_pessoa.items():
            gasto_aproveitado = min(gasto_bruto, cls.TETO_EDUCACAO_INDIVIDUAL)
            total_educacao_dedutivel += gasto_aproveitado
            detalhe_educacao[chave] = {
                "nome": rotulo_por_chave[chave]["nome"],
                "cpf": rotulo_por_chave[chave]["cpf"],
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

    @classmethod
    def analisar_pgbl(cls, renda_bruta_tributavel: float, pgbl_atual: float) -> Dict[str, Any]:
        if renda_bruta_tributavel < 0 or pgbl_atual < 0:
            raise ValueError("Renda e contribuição PGBL não podem ser negativas.")
        limite_pgbl = renda_bruta_tributavel * cls.LIMITE_PGBL_PERCENTUAL
        aporte_complementar = max(0.0, limite_pgbl - pgbl_atual)
        economia_estimada = aporte_complementar * cls.ALIQUEOTA_PADRAO
        return {
            "limite_pgbl": limite_pgbl,
            "aporte_complementar": aporte_complementar,
            "economia_estimada": economia_estimada,
            "limite_atingido": pgbl_atual >= limite_pgbl
        }

    @classmethod
    def recomendar_modelo(cls, renda_bruta_tributavel: float, total_deducoes: float) -> Dict[str, Any]:
        if renda_bruta_tributavel < 0 or total_deducoes < 0:
            raise ValueError("Renda e deduções não podem ser negativas.")
        desconto_simplificado = min(renda_bruta_tributavel * 0.20, cls.TETO_DESCONTO_SIMPLIFICADO)
        modelo = "Completo" if total_deducoes > desconto_simplificado else "Simplificado"
        return {
            "modelo_recomendado": modelo,
            "desconto_simplificado": desconto_simplificado,
            "total_deducoes": total_deducoes,
            "vantagem": abs(total_deducoes - desconto_simplificado)
        }
