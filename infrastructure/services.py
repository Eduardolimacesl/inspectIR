# -*- coding: utf-8 -*-
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
from google import genai
from google.genai import types
from openpyxl import Workbook
from domain.models import NotaFiscal, CNPJ, NotaAuditada, Beneficiario, CategoriaFiscal

class EscritorLeitorNotasLocal:
    @staticmethod
    def salvar_brutas(notas: List[Dict[str, Any]], caminho: str):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(notas, f, indent=4, ensure_ascii=False)
    @staticmethod
    def carregar_brutas(caminho: str) -> List[NotaFiscal]:
        if not os.path.exists(caminho):
            return []
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        lista_notas = []
        for item in dados:
            lista_notas.append(
                NotaFiscal(
                    id=item["id"],
                    emitente=item["emitente"],
                    cnpj=CNPJ(item["cnpj"]),
                    valor=float(item["valor"]),
                    descricao=item["descricao"],
                    data=datetime.strptime(item["data"], "%d/%m/%Y")
                )
            )
        return lista_notas
    @staticmethod
    def salvar_auditoria(notas_auditadas: List[NotaAuditada], caminho: str):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        estrutura = {
            "auditoria_fiscal": [
                {
                    "id": n.nota.id,
                    "emitente": n.nota.emitente,
                    "cnpj": n.nota.cnpj.valor,
                    "valor": n.nota.valor,
                    "dedutivel": n.dedutivel,
                    "categoria": n.categoria.value,
                    "beneficiario_provavel": n.beneficiario.nome,
                    "beneficiario_cpf": n.beneficiario.cpf,
                    "justificativa_legal": n.justificativa_legal
                }
                for n in notas_auditadas
            ]
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estrutura, f, indent=4, ensure_ascii=False)

class AdaptadorGeminiFiscal:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    def analisar_em_lote(self, notas: List[NotaFiscal]) -> List[NotaAuditada]:
        if not self.api_key:
            raise ValueError("Chave de API do Gemini não configurada.")
        client = genai.Client(api_key=self.api_key)
        dados_entrada = [
            {"id": n.id, "emitente": n.emitente, "cnpj": n.cnpj.valor, "valor": n.valor, "descricao": n.descricao, "data": n.data.strftime("%d/%m/%Y")}
            for n in notas
        ]
        prompt = f"Você é um auditor fiscal eletrônico sênior da Receita Federal. Analise as notas fiscais e responda estritamente em formato JSON estruturado com a chave 'auditoria_fiscal'. Para cada nota inclua os campos: id, dedutivel (bool), categoria ('Saude'|'Educacao'|'Nao Dedutivel'), beneficiario_provavel (nome, ou 'Titular'), beneficiario_cpf (somente dígitos do CPF se identificável na descrição, senão string vazia) e justificativa_legal:\\n{json.dumps(dados_entrada)}"
        tentativas = 4
        delay = 2
        for t in range(tentativas):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash-preview-09-2025',
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
                )
                resposta_limpa = response.text.strip()
                if resposta_limpa.startswith("```json"):
                    resposta_limpa = resposta_limpa[7:]
                if resposta_limpa.endswith("```"):
                    resposta_limpa = resposta_limpa[:-3]
                dados_resposta = json.loads(resposta_limpa.strip())
                resultado: List[NotaAuditada] = []
                mapa_notas = {n.id: n for n in notas}
                for item in dados_resposta["auditoria_fiscal"]:
                    nota_origem = mapa_notas.get(item["id"])
                    if not nota_origem: continue
                    resultado.append(
                        NotaAuditada(
                            nota=nota_origem,
                            dedutivel=item["dedutivel"],
                            categoria=CategoriaFiscal(item["categoria"]),
                            beneficiario=Beneficiario(
                                item["beneficiario_provavel"],
                                item["beneficiario_provavel"].lower() == "titular",
                                item.get("beneficiario_cpf", "")
                            ),
                            justificativa_legal=item["justificativa_legal"]
                        )
                    )
                return resultado
            except Exception as ex:
                if t == tentativas - 1:
                    raise RuntimeError(f"Erro na conexão Gemini: {ex}")
                time.sleep(delay)
                delay *= 2
        return []

class ExportadorExcelLocal:
    COLUNAS = ["CNPJ", "Prestador", "Beneficiário", "Valor", "Categoria", "Data"]
    @classmethod
    def exportar(cls, notas_auditadas: List[NotaAuditada], caminho: str) -> str:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.title = "Auditoria IRPF"
        ws.append(cls.COLUNAS)
        for n in notas_auditadas:
            ws.append([
                n.nota.cnpj.formatado,
                n.nota.emitente,
                n.beneficiario.nome,
                round(n.nota.valor, 2),
                n.categoria.value,
                n.nota.data.strftime("%d/%m/%Y")
            ])
        wb.save(caminho)
        return caminho
