# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Any
from domain.models import NotaAuditada, MotorCalculoIR
from infrastructure.services import EscritorLeitorNotasLocal, AdaptadorGeminiFiscal
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
            return mansa_dados if 'mansa_dados' in locals() else massa_dados
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
    def executar(api_key: str, renda_anual_bruta: float, previdencia_pgbl: float, dependentes_qtd: int, notas_auditadas: List[Dict[str, Any]]) -> str:
        if not api_key: raise ValueError("Chave de API do Gemini é obrigatória.")
        client = genai.Client(api_key=api_key)
        saude_encontrada = [n for n in notas_auditadas if n["dedutivel"] and n["categoria"] == "Saude"]
        educacao_encontrada = [n for n in notas_auditadas if n["dedutivel"] and n["categoria"] == "Educacao"]
        rejeitadas = [n for n in notas_auditadas if not n["dedutivel"]]
        resumo_financeiro_notas = {
            "total_saude": sum(n["valor"] for n in saude_encontrada),
            "total_educacao": sum(n["valor"] for n in educacao_encontrada),
            "quantidade_notas_rejeitadas": len(rejeitadas),
            "itens_rejeitados_exemplo": [n["descricao"][:60] for n in rejeitadas[:3]]
        }
        prompt = f"Você é um CFP no Brasil. Analise o perfil fiscal e forneça um relatório em Markdown: Renda R$ {renda_anual_bruta}, PGBL R$ {previdencia_pgbl}, Dependentes: {dependentes_qtd}, Notas: {json.dumps(resumo_financeiro_notas)}"
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.15)
        )
        return response.text
