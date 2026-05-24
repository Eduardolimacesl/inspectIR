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

    def test_verificar_constantes_pgbl_e_simplificado_presentes_e_consistentes(self):
        constantes = self.especificacao["tax_constants"]
        self.assertIn("LIMITE_PGBL_PERCENTUAL", constantes)
        self.assertIn("TETO_DESCONTO_SIMPLIFICADO", constantes)
        self.assertEqual(MotorCalculoIR.LIMITE_PGBL_PERCENTUAL, constantes["LIMITE_PGBL_PERCENTUAL"])
        self.assertEqual(MotorCalculoIR.TETO_DESCONTO_SIMPLIFICADO, constantes["TETO_DESCONTO_SIMPLIFICADO"])
