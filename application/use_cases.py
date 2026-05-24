# -*- coding: utf-8 -*-
import json
import os
from typing import List, Dict, Any
from domain.models import NotaAuditada, MotorCalculoIR, CategoriaFiscal, Beneficiario
from infrastructure.services import EscritorLeitorNotasLocal, AdaptadorGeminiFiscal, ExportadorExcelLocal
from google import genai
from google.genai import types

class ExtrairNotasUseCase:
    @staticmethod
    def executar(cpf: str, data_ini: str, data_fim: str, simulado: bool, caminho_saida: str) -> List[Dict[str, Any]]:
        if simulado:
            massa_dados = [
                {"id": "NF-2025-001", "emitente": "HOSPITAL DA LUZ S/A", "cnpj": "12345678000199", "valor": 5420.50, "descricao": "PRESTAÇÃO DE SERVIÇOS MÉDICOS HOSPITALARES DE CIRURGIA GERAL DO TITULAR", "data": "10/02/2025"},
                {"id": "NF-2025-002", "emitente": "COLÉGIO INTEGRAR FORTALEZA LTDA", "cnpj": "98765432000111", "valor": 4200.00, "descricao": "MENSALIDADES ESCOLARES DE ENSINO FUNDAMENTAL - ALUNO: ENZO ROCHA LIMA", "data": "05/06/2025"},
                {"id": "NF-2025-003", "emitente": "DROGARIA PAGUE MENOS", "cnpj": "05333444000120", "valor": 345.90, "descricao": "COMPRAS DIVERSAS - MEDICAMENTOS ISOLADOS E HIGIENE", "data": "12/07/2025"},
                {"id": "NF-2025-004", "emitente": "CLINICA DE ODONTOLOGIA SMILE", "cnpj": "11222333000144", "valor": 850.00, "descricao": "TRATAMENTO DE CANAL REALIZADO EM HELENA ROCHA LIMA", "data": "20/08/2025"},
                {"id": "NF-2025-005", "emitente": "ACADEMIA FIT E SAÚDE LTDA", "cnpj": "22333444000155", "valor": 1200.00, "descricao": "PLANO ANUAL DE GINÁSTICA DO TITULAR", "data": "01/01/2025"}
            ]
            EscritorLeitorNotasLocal.salvar_brutas(massa_dados, caminho_saida)
            return massa_dados
        return []

class AuditarNotasUseCase:
    def __init__(self, adaptador_ia: AdaptadorGeminiFiscal):
        self.adaptador_ia = adaptador_ia
    def executar(self, caminho_brutas: str, caminho_saida_auditoria: str) -> List[NotaAuditada]:
        notas_brutas = EscritorLeitorNotasLocal.carregar_brutas(caminho_brutas)
        if not notas_brutas: return []
        notas_auditadas = self.adaptador_ia.analisar_em_lote(notas_brutas)
        EscritorLeitorNotasLocal.salvar_auditoria(notas_auditadas, caminho_saida_auditoria)
        return notas_auditadas

class DeepTaxAdvisorUseCase:
    @staticmethod
    def calcular_perfil(renda_anual_bruta: float, previdencia_pgbl: float, notas_auditadas: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_saude = sum(n["valor"] for n in notas_auditadas if n["dedutivel"] and n["categoria"] == "Saude")
        educacao_por_pessoa: Dict[str, float] = {}
        for n in notas_auditadas:
            if n["dedutivel"] and n["categoria"] == "Educacao":
                chave = n.get("beneficiario_cpf") or n.get("beneficiario_provavel", "")
                educacao_por_pessoa[chave] = educacao_por_pessoa.get(chave, 0.0) + n["valor"]
        total_educacao = sum(min(v, MotorCalculoIR.TETO_EDUCACAO_INDIVIDUAL) for v in educacao_por_pessoa.values())
        deducoes_notas = total_saude + total_educacao
        pgbl = MotorCalculoIR.analisar_pgbl(renda_anual_bruta, previdencia_pgbl)
        modelo = MotorCalculoIR.recomendar_modelo(renda_anual_bruta, deducoes_notas + previdencia_pgbl)
        return {
            "total_saude": total_saude,
            "total_educacao_dedutivel": total_educacao,
            "deducoes_notas": deducoes_notas,
            "pgbl": pgbl,
            "modelo": modelo
        }

    @staticmethod
    def executar(api_key: str, renda_anual_bruta: float, previdencia_pgbl: float, dependentes_qtd: int, notas_auditadas: List[Dict[str, Any]]) -> str:
        if not api_key: raise ValueError("Chave de API do Gemini é obrigatória.")
        perfil = DeepTaxAdvisorUseCase.calcular_perfil(renda_anual_bruta, previdencia_pgbl, notas_auditadas)
        client = genai.Client(api_key=api_key)
        prompt = (
            "Você é um planejador financeiro (CFP) no Brasil. Os números a seguir já foram "
            "CALCULADOS de forma determinística pelo motor fiscal — NÃO os recalcule, apenas "
            "interprete e gere um parecer estratégico de IRPF em Markdown, recomendando o aporte "
            "PGBL complementar e o modelo de declaração indicado, com justificativa para o "
            f"contribuinte. Renda bruta tributável anual: R$ {renda_anual_bruta:.2f}. "
            f"Dependentes: {dependentes_qtd}. Dados calculados: {json.dumps(perfil, ensure_ascii=False)}"
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.15)
        )
        return response.text

class ExportarPlanilhaUseCase:
    @staticmethod
    def executar(caminho_brutas: str, caminho_auditoria: str, caminho_xlsx: str) -> str:
        if not os.path.exists(caminho_auditoria):
            raise ValueError("Nenhuma auditoria encontrada para exportar.")
        notas_brutas = EscritorLeitorNotasLocal.carregar_brutas(caminho_brutas)
        with open(caminho_auditoria, "r", encoding="utf-8") as f:
            dados = json.load(f).get("auditoria_fiscal", [])
        if not dados:
            raise ValueError("Auditoria vazia — nada a exportar.")
        mapa = {n.id: n for n in notas_brutas}
        auditadas: List[NotaAuditada] = []
        for item in dados:
            origem = mapa.get(item["id"])
            if not origem:
                continue
            auditadas.append(
                NotaAuditada(
                    nota=origem,
                    dedutivel=item["dedutivel"],
                    categoria=CategoriaFiscal(item["categoria"]),
                    beneficiario=Beneficiario(item["beneficiario_provavel"], False, item.get("beneficiario_cpf", "")),
                    justificativa_legal=item["justificativa_legal"]
                )
            )
        return ExportadorExcelLocal.exportar(auditadas, caminho_xlsx)
