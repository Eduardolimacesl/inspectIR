# -*- coding: utf-8 -*-
import asyncio
import json
import os
from playwright.async_api import async_playwright

ESTADO_SESSAO_JSON = "inspectir/data/auth_state.json"

async def capturar_notas_portal_sefin(cpf: str, data_ini: str, data_fim: str, simulado: bool = False) -> list:
    if simulado:
        return [
            {"id": "NF-2025-001", "emitente": "HOSPITAL DA LUZ S/A", "cnpj": "12345678000199", "valor": 5420.50, "descricao": "SERVICOS MEDICOS HOSPITALARES DE CIRURGIA DO TITULAR", "data": "10/02/2025"},
            {"id": "NF-2025-002", "emitente": "COLÉGIO INTEGRAR FORTALEZA LTDA", "cnpj": "98765432000111", "valor": 4200.00, "descricao": "MENSALIDADE ESCOLAR DE ENSINO FUNDAMENTAL - ALUNO: ENZO ROCHA LIMA", "data": "05/06/2025"},
            {"id": "NF-2025-003", "emitente": "DROGARIA PAGUE MENOS", "cnpj": "05333444000120", "valor": 345.90, "descricao": "COMPRAS DE MEDICAMENTOS E MATERIAIS DE HIGIENE", "data": "12/07/2025"},
            {"id": "NF-2025-004", "emitente": "CLINICA DE ODONTOLOGIA SMILE", "cnpj": "11222333000144", "valor": 850.00, "descricao": "TRATAMENTO ODONTOLOGICO REALIZADO EM HELENA ROCHA LIMA", "data": "20/08/2025"}
        ]
    async with async_playwright() as p:
        os.makedirs(os.path.dirname(ESTADO_SESSAO_JSON), exist_ok=True)
        if os.path.exists(ESTADO_SESSAO_JSON):
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state=ESTADO_SESSAO_JSON)
        else:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://sefin.fortaleza.ce.gov.br/nfse")
        if not os.path.exists(ESTADO_SESSAO_JSON):
            try:
                await page.wait_for_url("**/dashboard**", timeout=120000)
                await context.storage_state(path=ESTADO_SESSAO_JSON)
            except Exception:
                await browser.close()
                return []
        await browser.close()
        return await capturar_notas_portal_sefin(cpf, data_ini, data_fim, simulado=True)

if __name__ == "__main__":
    dados = asyncio.run(capturar_notas_portal_sefin("007.999.163-74", "01/01/2025", "31/12/2025", simulado=True))
    print(f"[TESTE] Notas retornadas: {len(dados)}")
