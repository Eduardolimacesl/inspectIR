# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
import asyncio
from application.use_cases import ExtrairNotasUseCase, AuditarNotasUseCase, DeepTaxAdvisorUseCase
from infrastructure.services import AdaptadorGeminiFiscal, EscritorLeitorNotasLocal
from domain.models import MotorCalculoIR, CategoriaFiscal, NotaAuditada, Beneficiario

st.set_page_config(page_title="InspectIR — Inteligência Fiscal", page_icon="🛡️", layout="wide")

CAMINHO_BRUTAS = "inspectir/data/notas_brutas.json"
CAMINHO_AUDITADAS = "inspectir/data/auditoria_final.json"

st.sidebar.title("Configurações InspectIR")
api_key = st.sidebar.text_input("Chave API Gemini:", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
if api_key: os.environ["GEMINI_API_KEY"] = api_key

cpf = st.sidebar.text_input("CPF:", "111.222.333-44")
periodo_ini = st.sidebar.date_input("De:", pd.to_datetime("2025-01-01"))
periodo_fim = st.sidebar.date_input("Até:", pd.to_datetime("2025-12-31"))
modo_simulado = st.sidebar.checkbox("Usar Extrator Simulado", value=True)

st.title("🛡️ InspectIR — Inteligência Fiscal Avançada")

tab_dashboard, tab_notas, tab_planejador_ia, tab_config = st.tabs([
    "📊 Painel de Despesas", "📋 Notas Fiscais Auditadas", "🧠 Consultoria & Planejamento de IA", "⚙️ Processar & Configurar"
])

dados_disponiveis = os.path.exists(CAMINHO_AUDITADAS)

with tab_dashboard:
    if dados_disponiveis:
        notas_carregadas = EscritorLeitorNotasLocal.carregar_brutas(CAMINHO_BRUTAS)
        with open(CAMINHO_AUDITADAS, "r", encoding="utf-8") as f:
            dados_auditados = json.load(f)["auditoria_fiscal"]
        lista_objetos_dominio = []
        for item in dados_auditados:
            lista_objetos_dominio.append(
                NotaAuditada(
                    nota=next(n for n in notas_carregadas if n.id == item["id"]),
                    dedutivel=item["dedutivel"],
                    categoria=CategoriaFiscal(item["categoria"]),
                    beneficiario=Beneficiario(item["beneficiario_provavel"]),
                    justificativa_legal=item["justificativa_legal"]
                )
            )
        metricas = MotorCalculoIR.processar_calculos(lista_objetos_dominio)
        col1, col2, col3 = st.columns(3)
        col1.metric("🩺 Saúde", f"R$ {metricas['total_saude']:,.2f}")
        col2.metric("🎓 Educação", f"R$ {metricas['total_educacao_dedutivel']:,.2f}")
        col3.metric("💰 Restituição Estimada", f"R$ {metricas['restituicao_estimada']:,.2f}")
    else:
        st.info("Processe as notas fiscais na aba 'Processar & Configurar' primeiro.")

with tab_notas:
    if dados_disponiveis:
        st.dataframe(pd.DataFrame(dados_auditados), use_container_width=True, hide_index=True)

with tab_planejador_ia:
    if not dados_disponiveis:
        st.info("Capture e audite suas notas fiscais antes.")
    else:
        renda_anual = st.number_input("Renda Bruta Anual (R$):", value=120000.00)
        previdencia = st.number_input("Contribuição PGBL (R$):", value=5000.00)
        dependentes = st.number_input("Dependentes:", value=1, min_value=0)
        if st.button("🧠 Gerar Parecer Fiscal Estratégico"):
            if not api_key: st.error("Chave API em falta.")
            else:
                with st.spinner("Analisando..."):
                    relatorio = DeepTaxAdvisorUseCase.executar(api_key, renda_anual, previdencia, dependentes, dados_auditados)
                    st.markdown(relatorio)

with tab_config:
    if st.button("🚀 Iniciar Coleta & Auditoria Completa"):
        if not api_key: st.error("Insira a chave API.")
        else:
            with st.status("Processando..."):
                ExtrairNotasUseCase.executar(cpf, periodo_ini.strftime("%d/%m/%Y"), periodo_fim.strftime("%d/%m/%Y"), modo_simulado, CAMINHO_BRUTAS)
                adaptador = AdaptadorGeminiFiscal(api_key)
                caso_de_uso = AuditarNotasUseCase(adaptador)
                caso_de_uso.executar(CAMINHO_BRUTAS, CAMINHO_AUDITADAS)
            st.success("Concluído!")
            st.rerun()
