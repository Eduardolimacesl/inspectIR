# -*- coding: utf-8 -*-
import unittest
import os
import json
from unittest.mock import MagicMock, patch
from application.use_cases import ExtrairNotasUseCase, AuditarNotasUseCase, DeepTaxAdvisorUseCase
from domain.models import MotorCalculoIR, Beneficiario, CategoriaFiscal, NotaAuditada
from infrastructure.services import EscritorLeitorNotasLocal

class TestEndToEndPipeline(unittest.TestCase):
    CAMINHO_E2E_BRUTAS = "inspectir/data/e2e_brutas.json"
    CAMINHO_E2E_AUDITADAS = "inspectir/data/e2e_auditoria.json"
    def tearDown(self):
        for caminho in [self.CAMINHO_E2E_BRUTAS, self.CAMINHO_E2E_AUDITADAS]:
            if os.path.exists(caminho): os.remove(caminho)
    @patch("google.genai.Client")
    def test_fluxo_completo_utilizador_ponta_a_ponta(self, mock_client_class):
        notas_brutas = ExtrairNotasUseCase.executar("11122233344", "01/01/2025", "31/12/2025", True, self.CAMINHO_E2E_BRUTAS)
        self.assertTrue(len(notas_brutas) > 0)
