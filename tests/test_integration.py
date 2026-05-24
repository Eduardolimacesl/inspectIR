# -*- coding: utf-8 -*-
import unittest
import os
import json
from unittest.mock import MagicMock, patch
from datetime import datetime
from domain.models import NotaFiscal, CNPJ, NotaAuditada, Beneficiario, CategoriaFiscal
from infrastructure.services import EscritorLeitorNotasLocal
from application.use_cases import AuditarNotasUseCase, DeepTaxAdvisorUseCase

class TestIntegrationPipeline(unittest.TestCase):
    CAMINHO_TEST_BRUTAS = "inspectir/data/test_brutas.json"
    CAMINHO_TEST_SAIDA = "inspectir/data/test_auditoria.json"
    def setUp(self):
        os.makedirs("inspectir/data", exist_ok=True)
        self.nota_mock = {"id": "NF-INTEG-01", "emitente": "CLINICA INTEGRADA", "cnpj": "12345678000199", "valor": 1500.00, "descricao": "CONSULTA CARDIOLOGISTA", "data": "10/05/2025"}
        EscritorLeitorNotasLocal.salvar_brutas([self.nota_mock], self.CAMINHO_TEST_BRUTAS)
    def tearDown(self):
        for caminho in [self.CAMINHO_TEST_BRUTAS, self.CAMINHO_TEST_SAIDA]:
            if os.path.exists(caminho): os.remove(caminho)
    def test_pipeline_de_auditoria_gravacao_e_leitura_local(self):
        adaptador_mock = MagicMock()
        nota_fiscal_dominio = NotaFiscal("NF-INTEG-01", "CLINICA INTEGRADA", CNPJ("12345678000199"), 1500.00, "CONSULTA", datetime.strptime("10/05/2025", "%d/%m/%Y"))
        adaptador_mock.analisar_em_lote.return_value = [NotaAuditada(nota_fiscal_dominio, True, CategoriaFiscal.SAUDE, Beneficiario("Titular", True), "Ok")]
        use_case = AuditarNotasUseCase(adaptador_mock)
        resultado = use_case.executar(self.CAMINHO_TEST_BRUTAS, self.CAMINHO_TEST_SAIDA)
        self.assertEqual(len(resultado), 1)
