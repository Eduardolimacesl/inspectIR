# -*- coding: utf-8 -*-
import unittest
import os
from domain.models import NotaFiscal, CNPJ
from datetime import datetime
from infrastructure.services import AdaptadorGeminiFiscal

class TestLiveGeminiConnection(unittest.TestCase):
    def setUp(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.nota_teste = NotaFiscal("NF-SMOKE-99", "CLINICA MEDICA EXEMPLO", CNPJ("12345678000199"), 250.00, "CONSULTA", datetime.now())
    def test_conexao_real_com_gemini_api(self):
        if not self.api_key: self.skipTest("Sem chave de API do Gemini para executar.")
        adaptador = AdaptadorGeminiFiscal(self.api_key)
        resultado = adaptador.analisar_em_lote([self.nota_teste])
        self.assertEqual(len(resultado), 1)
