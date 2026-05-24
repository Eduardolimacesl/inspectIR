# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from domain.models import CNPJ, CPF, NotaFiscal, NotaAuditada, Beneficiario, CategoriaFiscal, MotorCalculoIR

def _nota_educacao(id_, valor, nome, cpf):
    nf = NotaFiscal(id_, "Escola", CNPJ("12345678000199"), valor, "Mensalidade", datetime.now())
    return NotaAuditada(nf, True, CategoriaFiscal.EDUCACAO, Beneficiario(nome, False, cpf), "Ok")

class TestDomainRules(unittest.TestCase):
    def test_cnpj_valido_deve_formatar_corretamente(self):
        cnpj = CNPJ("12.345.678/0001-99")
        self.assertEqual(cnpj.valor, "12345678000199")
        self.assertEqual(cnpj.formatado, "12.345.678/0001-99")

    def test_cnpj_invalido_deve_lancar_erro(self):
        with self.assertRaises(ValueError):
            CNPJ("123")

    def test_cpf_valido_deve_formatar_corretamente(self):
        cpf = CPF("123.456.789-09")
        self.assertEqual(cpf.valor, "12345678909")
        self.assertEqual(cpf.formatado, "123.456.789-09")

    def test_cpf_invalido_deve_lancar_erro(self):
        with self.assertRaises(ValueError):
            CPF("123")

    def test_motor_calculo_ir_saude_sem_limites(self):
        nota = NotaFiscal("1", "Hosp", CNPJ("12345678000199"), 10000.00, "Cirurgia", datetime.now())
        auditada = NotaAuditada(nota, True, CategoriaFiscal.SAUDE, Beneficiario("Titular", True), "Ok")
        calculo = MotorCalculoIR.processar_calculos([auditada])
        self.assertEqual(calculo["total_saude"], 10000.00)
        self.assertEqual(calculo["restituicao_estimada"], 2750.00)

    def test_educacao_teto_por_cpf_homonimos_sao_pessoas_distintas(self):
        # Dois beneficiários com o MESMO nome, CPFs distintos, cada um acima do teto.
        teto = MotorCalculoIR.TETO_EDUCACAO_INDIVIDUAL
        notas = [
            _nota_educacao("E1", 5000.00, "Joao Silva", "11111111111"),
            _nota_educacao("E2", 5000.00, "Joao Silva", "22222222222"),
        ]
        calculo = MotorCalculoIR.processar_calculos(notas)
        # Teto aplicado individualmente por CPF → 2 × teto.
        self.assertAlmostEqual(calculo["total_educacao_dedutivel"], teto * 2)
        self.assertEqual(len(calculo["detalhes_educacao_individuais"]), 2)

    def test_educacao_mesmo_cpf_soma_antes_do_teto(self):
        teto = MotorCalculoIR.TETO_EDUCACAO_INDIVIDUAL
        notas = [
            _nota_educacao("E1", 2000.00, "Maria", "33333333333"),
            _nota_educacao("E2", 2000.00, "Maria", "33333333333"),
        ]
        calculo = MotorCalculoIR.processar_calculos(notas)
        self.assertEqual(len(calculo["detalhes_educacao_individuais"]), 1)
        self.assertAlmostEqual(calculo["total_educacao_dedutivel"], teto)

    def test_nota_valor_zero_nao_afeta_deducoes(self):
        nota = NotaFiscal("Z", "Cortesia", CNPJ("12345678000199"), 0.0, "Ajuste", datetime.now())
        auditada = NotaAuditada(nota, True, CategoriaFiscal.SAUDE, Beneficiario("Titular", True), "Ok")
        calculo = MotorCalculoIR.processar_calculos([auditada])
        self.assertEqual(calculo["total_saude"], 0.0)
        self.assertEqual(calculo["restituicao_estimada"], 0.0)

    def test_analisar_pgbl_aporte_e_economia(self):
        r = MotorCalculoIR.analisar_pgbl(100000.0, 4000.0)
        self.assertAlmostEqual(r["limite_pgbl"], 12000.0)
        self.assertAlmostEqual(r["aporte_complementar"], 8000.0)
        self.assertAlmostEqual(r["economia_estimada"], 2200.0)
        self.assertFalse(r["limite_atingido"])

    def test_analisar_pgbl_limite_atingido(self):
        r = MotorCalculoIR.analisar_pgbl(100000.0, 12000.0)
        self.assertTrue(r["limite_atingido"])
        self.assertEqual(r["aporte_complementar"], 0.0)

    def test_recomendar_modelo_completo_quando_deducoes_altas(self):
        r = MotorCalculoIR.recomendar_modelo(100000.0, 20000.0)
        self.assertEqual(r["modelo_recomendado"], "Completo")

    def test_recomendar_modelo_simplificado_quando_deducoes_baixas(self):
        r = MotorCalculoIR.recomendar_modelo(100000.0, 5000.0)
        self.assertEqual(r["modelo_recomendado"], "Simplificado")
