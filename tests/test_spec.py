# -*- coding: utf-8 -*-
import unittest
import os
import re
from domain.models import carregar_especificacao_sdd, MotorCalculoIR

class TestSpecDrivenCompliance(unittest.TestCase):
    def setUp(self):
        self.especificacao = carregar_especificacao_sdd()
    def test_verificar_existencia_e_metadados_da_especificacao(self):
        self.assertIsNotNone(self.especificacao)
    def test_verificar_consistencia_de_regras_fiscal_no_motor(self):
        limite_spec = self.especificacao["tax_constants"]["TETO_EDUCACAO_INDIVIDUAL"]
        self.assertEqual(MotorCalculoIR.TETO_EDUCACAO_INDIVIDUAL, limite_spec)
