# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from domain.models import CNPJ, NotaFiscal, NotaAuditada, Beneficiario, CategoriaFiscal, MotorCalculoIR

class TestDomainRules(unittest.TestCase):
    def test_cnpj_valido_deve_formatar_corretamente(self):
        cnpj = CNPJ("12.345.678/0001-99")
        self.assertEqual(cnpj.valor, "12345678000199")
        self.assertEqual(cnpj.formatado, "12.345.678/0001-99")
    def test_cnpj_invalido_deve_lancar_erro(self):
        with self.assertRaises(ValueError):
            CNPJ("123")
    def test_motor_calculo_ir_saude_sem_limites(self):
        nota = NotaFiscal("1", "Hosp", CNPJ("12345678000199"), 10000.00, "Cirurgia", datetime.now())
        auditada = NotaAuditada(nota, True, CategoriaFiscal.SAUDE, Beneficiario("Titular", True), "Ok")
        calculo = MotorCalculoIR.processar_calculos([auditada])
        self.assertEqual(calculo["total_saude"], 10000.00)
        self.assertEqual(calculo["restituicao_estimada"], 2750.00)
