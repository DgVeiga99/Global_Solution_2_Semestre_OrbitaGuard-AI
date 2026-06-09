import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from predict_risk import prever_risco, gerar_recomendacao
from log_manager import carregar_historico
from rag_assistant import gerar_resposta_assistente


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="OrbitaGuard AI",
    page_icon="🛰️",
    layout="wide"
)


# ============================================================
# CONSTANTES
# ============================================================

RISK_ICONS = {
    "Normal": "🟢",
    "Atenção": "🟡",
    "Alto Risco": "🟠",
    "Crítico": "🔴"
}


RISK_DESCRIPTIONS = {
    "Normal": "Condição ambiental dentro da faixa esperada.",
    "Atenção": "Condição intermediária que exige acompanhamento.",
    "Alto Risco": "Condição ambiental severa com necessidade de alerta preventivo.",
    "Crítico": "Condição extrema que exige resposta imediata."
}


CENARIOS = {
    "Normal": {
        "temperatura": 25.0,
        "umidade": 65.0,
        "pressao": 1013.0,
        "vento": 12.0,
        "chuva": 2.0,
        "luminosidade": 550.0,
        "indice_vegetacao": 0.65,
    },
    "Atenção": {
        "temperatura": 32.0,
        "umidade": 38.0,
        "pressao": 1008.0,
        "vento": 30.0,
        "chuva": 5.0,
        "luminosidade": 760.0,
        "indice_vegetacao": 0.42,
    },
    "Seca/Queimada Crítica": {
        "temperatura": 39.5,
        "umidade": 18.0,
        "pressao": 998.0,
        "vento": 28.0,
        "chuva": 0.5,
        "luminosidade": 940.0,
        "indice_vegetacao": 0.18,
    },
    "Tempestade Severa": {
        "temperatura": 24.0,
        "umidade": 92.0,
        "pressao": 985.0,
        "vento": 72.0,
        "chuva": 48.0,
        "luminosidade": 180.0,
        "indice_vegetacao": 0.58,
    },
    "Anomalia Ambiental": {
        "temperatura": 44.0,
        "umidade": 12.0,
        "pressao": 970.0,
        "vento": 95.0,
        "chuva": 80.0,
        "luminosidade": 1100.0,
        "indice_vegetacao": 0.08,
    },
}


# ============================================================
# ESTILO VISUAL
# ============================================================

def aplicar_estilo_sidebar():
    """
    Aplica pequenos ajustes visuais na barra lateral.
    """

    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                background-color: #f8fafc;
            }

            div[data-testid="stSidebarContent"] {
                padding-top: 1rem;
            }

            .sidebar-title {
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 4px;
            }

            .sidebar-subtitle {
                font-size: 13px;
                color: #64748b;
                margin-bottom: 16px;
            }

            .menu-selected {
                background-color: #e0f2fe;
                border-left: 5px solid #0284c7;
                padding: 10px 12px;
                border-radius: 8px;
                margin-bottom: 7px;
                font-weight: 700;
                color: #0f172a;
            }

            .status-item {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 9px;
                font-size: 14px;
            }

            .status-dot {
                height: 11px;
                width: 11px;
                border-radius: 50%;
                display: inline-block;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FUNÇÕES BASE
# ============================================================

def inicializar_estado():
    """
    Inicializa os dados da última leitura para uso entre as páginas.
    """

    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "monitoramento"

    if "ultima_leitura" not in st.session_state:
        st.session_state["ultima_leitura"] = {
            "temperatura": 39.5,
            "umidade": 18.0,
            "pressao": 998.0,
            "vento": 28.0,
            "chuva": 0.5,
            "luminosidade": 940.0,
            "indice_vegetacao": 0.18,
        }

    if "ultimo_resultado" not in st.session_state:
        st.session_state["ultimo_resultado"] = prever_risco(st.session_state["ultima_leitura"])

    if "ultima_recomendacao" not in st.session_state:
        st.session_state["ultima_recomendacao"] = gerar_recomendacao(st.session_state["ultimo_resultado"])


def montar_leitura(
    temperatura,
    umidade,
    pressao,
    vento,
    chuva,
    luminosidade,
    indice_vegetacao
):
    return {
        "temperatura": temperatura,
        "umidade": umidade,
        "pressao": pressao,
        "vento": vento,
        "chuva": chuva,
        "luminosidade": luminosidade,
        "indice_vegetacao": indice_vegetacao,
    }


def normalizar_coluna_anomalia(df_historico):
    if df_historico.empty or "anomalia" not in df_historico.columns:
        return pd.Series(dtype=bool)

    return df_historico["anomalia"].astype(str).str.lower().isin(["true", "1", "sim"])


# ============================================================
# MENU E STATUS DO MVP
# ============================================================

def exibir_status_mvp():
    """
    Exibe o status visual dos módulos do MVP.
    Verde = ativo
    Vermelho = desativado
    """

    status_modulos = {
        "Machine Learning": True,
        "Detecção de Anomalias": True,
        "API FastAPI": True,
        "Histórico CSV": True,
        "RAG Local": True,
        "Dashboard Streamlit": True,
        "Simulador ESP32": True,
        "ESP32 Físico": False,
        "Deploy em Nuvem": False,
    }

    st.sidebar.markdown("### Status do MVP")

    for modulo, ativo in status_modulos.items():
        cor = "#16a34a" if ativo else "#dc2626"
        texto_status = "Ativo" if ativo else "Desativado"

        st.sidebar.markdown(
            f"""
            <div class="status-item">
                <span class="status-dot" style="background-color: {cor};"></span>
                <span><strong>{modulo}</strong>: {texto_status}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


def botao_menu(nome_pagina, icone, chave_pagina):
    """
    Cria um botão de navegação na sidebar.
    A página selecionada fica destacada visualmente.
    """

    selecionado = st.session_state.get("pagina_atual") == chave_pagina
    label = f"{icone} {nome_pagina}"

    if selecionado:
        st.sidebar.markdown(
            f"""
            <div class="menu-selected">
                {label}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.sidebar.button(label, use_container_width=True):
            st.session_state["pagina_atual"] = chave_pagina
            st.rerun()


def exibir_menu_lateral():
    """
    Exibe menu principal lateral em formato de botões.
    """

    st.sidebar.markdown(
        """
        <div class="sidebar-title">🛰️ OrbitaGuard AI</div>
        <div class="sidebar-subtitle">Monitoramento ambiental inteligente</div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("### Menu")

    botao_menu(
        nome_pagina="Monitoramento Atual",
        icone="📡",
        chave_pagina="monitoramento"
    )

    botao_menu(
        nome_pagina="Histórico de Monitoramento",
        icone="📊",
        chave_pagina="historico"
    )

    botao_menu(
        nome_pagina="Assistente Inteligente RAG",
        icone="🤖",
        chave_pagina="rag"
    )

    botao_menu(
        nome_pagina="Arquitetura do Sistema",
        icone="🏗️",
        chave_pagina="arquitetura"
    )

    botao_menu(
        nome_pagina="Sobre o Projeto",
        icone="🌎",
        chave_pagina="sobre"
    )

    st.sidebar.divider()

    exibir_status_mvp()


# ============================================================
# COMPONENTES VISUAIS
# ============================================================

def exibir_cards(resultado):
    risco = resultado["risco"]
    risco_modelo = resultado["risco_modelo"]
    risco_regra = resultado["risco_regra"]
    anomalia = resultado["anomalia"]
    confianca = resultado["confianca_percentual"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Risco Final", f"{RISK_ICONS.get(risco, '')} {risco}")

    with col2:
        st.metric("Risco pelo Modelo", risco_modelo)

    with col3:
        st.metric("Risco por Regra", risco_regra)

    with col4:
        st.metric(
            "Anomalia",
            "Sim" if anomalia else "Não",
            delta=f"Confiança ML: {confianca}%"
        )


def exibir_grafico_variaveis(leitura):
    df_plot = pd.DataFrame({
        "Variável": [
            "Temperatura (°C)",
            "Umidade (%)",
            "Pressão (hPa)",
            "Vento (km/h)",
            "Chuva (mm)",
            "Luminosidade",
            "Índice Vegetação"
        ],
        "Valor": [
            leitura["temperatura"],
            leitura["umidade"],
            leitura["pressao"],
            leitura["vento"],
            leitura["chuva"],
            leitura["luminosidade"],
            leitura["indice_vegetacao"]
        ]
    })

    fig = px.bar(
        df_plot,
        x="Variável",
        y="Valor",
        title="Leitura Ambiental Atual",
        text="Valor"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=450,
        xaxis_title="Variável Ambiental",
        yaxis_title="Valor Medido"
    )

    st.plotly_chart(fig, use_container_width=True)


def exibir_mapa(latitude, longitude):
    df_map = pd.DataFrame({
        "lat": [latitude],
        "lon": [longitude]
    })

    st.map(
        df_map,
        latitude="lat",
        longitude="lon",
        size=120
    )


def exibir_resumo_tecnico(resultado):
    risco = resultado["risco"]
    risco_modelo = resultado["risco_modelo"]
    risco_regra = resultado["risco_regra"]
    anomalia = resultado["anomalia"]

    st.markdown("## Interpretação do Sistema")

    st.markdown(
        f"""
        O sistema recebeu os dados ambientais informados e executou uma análise híbrida.

        - O modelo de **Machine Learning** classificou o cenário como **{risco_modelo}**.
        - A camada de **regras críticas** classificou o cenário como **{risco_regra}**.
        - O risco final adotado foi **{risco}**, utilizando uma estratégia conservadora.
        - O detector de anomalias retornou: **{"anomalia detectada" if anomalia else "sem anomalia"}**.

        **Descrição do risco final:** {RISK_DESCRIPTIONS.get(risco, "Sem descrição disponível.")}

        Essa abordagem evita que o sistema dependa exclusivamente do modelo estatístico,
        principalmente em situações ambientais severas, nas quais uma resposta preventiva
        é mais importante do que uma classificação otimista.
        """
    )


# ============================================================
# PÁGINA 1 - MONITORAMENTO ATUAL
# ============================================================

def pagina_monitoramento_atual():
    st.title("🛰️ Monitoramento Atual")
    st.subheader("Análise em tempo real de uma estação ambiental simulada")

    st.markdown(
        """
        Nesta tela, o usuário seleciona ou ajusta manualmente os dados ambientais.
        O sistema processa a leitura usando **Machine Learning**, **regras críticas**
        e **detecção de anomalias**.
        """
    )

    st.divider()

    st.sidebar.markdown("## Entrada dos Sensores")
    st.sidebar.markdown("### Localização")

    latitude = st.sidebar.number_input(
        "Latitude",
        value=-23.710000,
        format="%.6f"
    )

    longitude = st.sidebar.number_input(
        "Longitude",
        value=-46.410000,
        format="%.6f"
    )

    st.sidebar.markdown("### Cenário de Demonstração")

    cenario = st.sidebar.selectbox(
        "Selecionar cenário",
        [
            "Personalizado",
            "Normal",
            "Atenção",
            "Seca/Queimada Crítica",
            "Tempestade Severa",
            "Anomalia Ambiental"
        ]
    )

    if cenario != "Personalizado":
        valores = CENARIOS[cenario]
    else:
        valores = st.session_state["ultima_leitura"]

    st.sidebar.markdown("### Variáveis Ambientais")

    temperatura = st.sidebar.slider(
        "Temperatura (°C)",
        0.0,
        50.0,
        float(valores["temperatura"]),
        0.1
    )

    umidade = st.sidebar.slider(
        "Umidade (%)",
        0.0,
        100.0,
        float(valores["umidade"]),
        0.1
    )

    pressao = st.sidebar.slider(
        "Pressão atmosférica (hPa)",
        950.0,
        1050.0,
        float(valores["pressao"]),
        0.1
    )

    vento = st.sidebar.slider(
        "Vento (km/h)",
        0.0,
        130.0,
        float(valores["vento"]),
        0.1
    )

    chuva = st.sidebar.slider(
        "Chuva (mm)",
        0.0,
        120.0,
        float(valores["chuva"]),
        0.1
    )

    luminosidade = st.sidebar.slider(
        "Luminosidade",
        0.0,
        1200.0,
        float(valores["luminosidade"]),
        1.0
    )

    indice_vegetacao = st.sidebar.slider(
        "Índice de Vegetação",
        0.0,
        1.0,
        float(valores["indice_vegetacao"]),
        0.01
    )

    leitura = montar_leitura(
        temperatura=temperatura,
        umidade=umidade,
        pressao=pressao,
        vento=vento,
        chuva=chuva,
        luminosidade=luminosidade,
        indice_vegetacao=indice_vegetacao
    )

    resultado = prever_risco(leitura)
    recomendacao = gerar_recomendacao(resultado)

    st.session_state["ultima_leitura"] = leitura
    st.session_state["ultimo_resultado"] = resultado
    st.session_state["ultima_recomendacao"] = recomendacao

    st.markdown("## Resultado da Análise Inteligente")
    exibir_cards(resultado)

    st.divider()

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown("### Variáveis Monitoradas")
        exibir_grafico_variaveis(leitura)

    with col_b:
        st.markdown("### Local Monitorado")
        exibir_mapa(latitude, longitude)

    st.divider()

    st.markdown("## Diagnóstico Técnico")
    st.info(recomendacao)

    with st.expander("Ver dados completos da predição atual"):
        diagnostico = {
            "timestamp": datetime.now().isoformat(),
            "cenario_selecionado": cenario,
            "latitude": latitude,
            "longitude": longitude,
            "entrada": leitura,
            "resultado": resultado,
            "recomendacao": recomendacao
        }

        st.json(diagnostico)

    st.divider()

    exibir_resumo_tecnico(resultado)


# ============================================================
# PÁGINA 2 - HISTÓRICO DE MONITORAMENTO
# ============================================================

def exibir_metricas_historico(df_historico):
    total_leituras = len(df_historico)

    total_criticos = 0
    total_alto_risco = 0
    total_anomalias = 0
    ultimo_risco = "Sem dados"

    if total_leituras > 0:
        total_criticos = int((df_historico["risco"] == "Crítico").sum())
        total_alto_risco = int((df_historico["risco"] == "Alto Risco").sum())
        total_anomalias = int(normalizar_coluna_anomalia(df_historico).sum())
        ultimo_risco = str(df_historico.iloc[-1]["risco"])

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Leituras registradas", total_leituras)

    with col2:
        st.metric("Eventos críticos", total_criticos)

    with col3:
        st.metric("Alto risco", total_alto_risco)

    with col4:
        st.metric("Anomalias", total_anomalias)

    with col5:
        st.metric("Último risco", ultimo_risco)


def exibir_distribuicao_riscos(df_historico):
    if df_historico.empty or "risco" not in df_historico.columns:
        st.info("Ainda não há dados suficientes para exibir a distribuição de riscos.")
        return

    ordem_risco = ["Normal", "Atenção", "Alto Risco", "Crítico"]

    df_count = (
        df_historico["risco"]
        .value_counts()
        .reindex(ordem_risco, fill_value=0)
        .reset_index()
    )

    df_count.columns = ["Risco", "Quantidade"]

    fig = px.bar(
        df_count,
        x="Risco",
        y="Quantidade",
        text="Quantidade",
        title="Distribuição dos Riscos Registrados"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=350,
        xaxis_title="Classificação de Risco",
        yaxis_title="Quantidade de Eventos"
    )

    st.plotly_chart(fig, use_container_width=True)


def exibir_distribuicao_anomalias(df_historico):
    if df_historico.empty or "anomalia" not in df_historico.columns:
        st.info("Ainda não há dados de anomalias para exibir.")
        return

    serie_anomalia = normalizar_coluna_anomalia(df_historico)

    df_anomalias = pd.DataFrame({
        "Tipo": ["Normal", "Anomalia"],
        "Quantidade": [
            int((~serie_anomalia).sum()),
            int(serie_anomalia.sum())
        ]
    })

    fig_anomalia = px.pie(
        df_anomalias,
        names="Tipo",
        values="Quantidade",
        title="Distribuição de Anomalias"
    )

    fig_anomalia.update_layout(height=350)
    st.plotly_chart(fig_anomalia, use_container_width=True)


def exibir_graficos_historico(df_historico):
    if df_historico.empty:
        st.warning("Ainda não há histórico de leituras salvo. Execute o simulador ESP32 para gerar dados.")
        return

    df = df_historico.copy()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    st.markdown("### Evolução Temporal das Variáveis Ambientais")

    variaveis = [
        "temperatura",
        "umidade",
        "pressao",
        "vento",
        "chuva",
        "luminosidade",
        "indice_vegetacao"
    ]

    variaveis_disponiveis = [v for v in variaveis if v in df.columns]
    variaveis_default = [v for v in ["temperatura", "umidade", "vento"] if v in variaveis_disponiveis]

    variaveis_selecionadas = st.multiselect(
        "Selecionar variáveis para o gráfico histórico",
        variaveis_disponiveis,
        default=variaveis_default
    )

    if variaveis_selecionadas:
        df_melt = df.melt(
            id_vars="timestamp",
            value_vars=variaveis_selecionadas,
            var_name="variável",
            value_name="valor"
        )

        fig = px.line(
            df_melt,
            x="timestamp",
            y="valor",
            color="variável",
            markers=True,
            title="Histórico das Variáveis Ambientais"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Tempo",
            yaxis_title="Valor"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecione pelo menos uma variável para exibir o gráfico histórico.")

    st.markdown("### Evolução do Risco Ambiental")

    if "risco_codigo" in df.columns:
        fig_risco = px.line(
            df,
            x="timestamp",
            y="risco_codigo",
            markers=True,
            title="Histórico do Código de Risco"
        )

        fig_risco.update_layout(
            height=350,
            xaxis_title="Tempo",
            yaxis_title="Código de Risco",
            yaxis=dict(
                tickmode="array",
                tickvals=[0, 1, 2, 3],
                ticktext=["Normal", "Atenção", "Alto Risco", "Crítico"]
            )
        )

        st.plotly_chart(fig_risco, use_container_width=True)


def exibir_eventos_criticos(df_historico):
    if df_historico.empty:
        st.info("Nenhum evento crítico ou anômalo registrado até o momento.")
        return

    df = df_historico.copy()
    serie_anomalia = normalizar_coluna_anomalia(df)

    filtro = (df["risco"].isin(["Crítico", "Alto Risco"])) | serie_anomalia
    df_alertas = df[filtro].copy()

    if df_alertas.empty:
        st.success("Nenhum evento crítico, alto risco ou anômalo foi registrado até o momento.")
        return

    colunas_alertas = [
        "timestamp",
        "temperatura",
        "umidade",
        "pressao",
        "vento",
        "chuva",
        "risco",
        "anomalia",
        "recomendacao"
    ]

    colunas_existentes = [col for col in colunas_alertas if col in df_alertas.columns]

    if "timestamp" in df_alertas.columns:
        df_alertas["timestamp"] = pd.to_datetime(df_alertas["timestamp"], errors="coerce")
        df_alertas = df_alertas.sort_values("timestamp", ascending=False)

    st.dataframe(
        df_alertas[colunas_existentes],
        use_container_width=True
    )


def exibir_tabela_historico(df_historico):
    if df_historico.empty:
        st.info("Nenhum registro encontrado no histórico.")
        return

    colunas_exibir = [
        "timestamp",
        "temperatura",
        "umidade",
        "pressao",
        "vento",
        "chuva",
        "luminosidade",
        "indice_vegetacao",
        "risco",
        "risco_modelo",
        "risco_regra",
        "anomalia",
        "confianca_percentual"
    ]

    colunas_existentes = [col for col in colunas_exibir if col in df_historico.columns]

    df_tabela = df_historico[colunas_existentes].copy()

    if "timestamp" in df_tabela.columns:
        df_tabela["timestamp"] = pd.to_datetime(df_tabela["timestamp"], errors="coerce")
        df_tabela = df_tabela.sort_values("timestamp", ascending=False)

    st.dataframe(df_tabela, use_container_width=True)


def pagina_historico_monitoramento():
    st.title("📊 Histórico de Monitoramento")
    st.subheader("Análise temporal das leituras recebidas pela API")

    df_historico = carregar_historico(limite=200)

    exibir_metricas_historico(df_historico)

    st.divider()

    col_a, col_b = st.columns([1, 1])

    with col_a:
        exibir_distribuicao_riscos(df_historico)

    with col_b:
        exibir_distribuicao_anomalias(df_historico)

    st.divider()

    exibir_graficos_historico(df_historico)

    st.divider()

    st.markdown("### Eventos Críticos, Alto Risco ou Anômalos")
    exibir_eventos_criticos(df_historico)

    st.divider()

    st.markdown("### Últimas Leituras Registradas")
    exibir_tabela_historico(df_historico)


# ============================================================
# PÁGINA 3 - ASSISTENTE RAG
# ============================================================

def pagina_assistente_rag():
    st.title("🤖 Assistente Inteligente RAG")
    st.subheader("Explicação técnica baseada em base de conhecimento local")

    st.markdown(
        """
        Este assistente utiliza uma base de conhecimento local para explicar os resultados
        da análise ambiental. Ele recupera trechos relevantes e gera uma resposta técnica
        considerando a última leitura analisada no módulo de monitoramento.
        """
    )

    leitura = st.session_state["ultima_leitura"]
    resultado = st.session_state["ultimo_resultado"]
    recomendacao = st.session_state["ultima_recomendacao"]

    st.divider()

    st.markdown("## Última análise disponível")
    exibir_cards(resultado)

    with st.expander("Ver última leitura e recomendação"):
        st.markdown("### Última leitura")
        st.json(leitura)

        st.markdown("### Recomendação")
        st.info(recomendacao)

    st.divider()

    perguntas_sugeridas = [
        "Por que o risco está crítico?",
        "Quais ações preventivas devem ser tomadas?",
        "O que significa anomalia ambiental?",
        "Como o sistema combina Machine Learning e regras críticas?",
        "Qual é o impacto positivo dessa solução na Terra?",
        "Como o ESP32 participa da arquitetura?",
        "Como dados espaciais ajudam no monitoramento ambiental?",
        "O que significa risco de seca ou queimada?"
    ]

    pergunta = st.selectbox(
        "Perguntas sugeridas",
        perguntas_sugeridas
    )

    pergunta_livre = st.text_input(
        "Ou digite uma pergunta personalizada",
        value=""
    )

    pergunta_final = pergunta_livre if pergunta_livre.strip() else pergunta

    if st.button("Gerar resposta do assistente", use_container_width=True):
        resposta = gerar_resposta_assistente(
            pergunta=pergunta_final,
            resultado_atual=resultado,
            leitura_atual=leitura
        )

        st.markdown("### Resposta do Assistente")
        st.write(resposta["resposta"])

        with st.expander("Ver contextos recuperados da base de conhecimento"):
            contextos = resposta.get("contextos_recuperados", [])

            if contextos:
                for i, contexto in enumerate(contextos, start=1):
                    st.markdown(f"**Contexto {i}:**")
                    st.write(contexto)
                    st.divider()
            else:
                st.info("Nenhum contexto específico foi recuperado.")


# ============================================================
# PÁGINA 4 - ARQUITETURA
# ============================================================

def pagina_arquitetura():
    st.title("🏗️ Arquitetura do Sistema")
    st.subheader("Visão técnica do fluxo de dados do OrbitaGuard AI")

    st.markdown(
        """
        O OrbitaGuard AI foi construído como uma arquitetura integrada, conectando
        dados ambientais, simulação de sensores, API, modelos de IA, histórico e dashboard.
        """
    )

    st.divider()

    st.markdown("## Fluxo principal")

    st.code(
        """
Simulador ESP32 / Estação de Sensores
        ↓
Requisição HTTP POST
        ↓
API FastAPI
        ↓
Modelo Random Forest
        ↓
Regras Críticas Ambientais
        ↓
Detector de Anomalias Isolation Forest
        ↓
Histórico CSV
        ↓
Dashboard Streamlit
        ↓
Assistente RAG Local
        """,
        language="text"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("## Componentes")

        st.markdown(
            """
            - **ESP32 / Simulador Python:** representa a estação de campo.
            - **FastAPI:** recebe leituras e retorna predição.
            - **Random Forest:** classifica o risco ambiental.
            - **Isolation Forest:** identifica anomalias.
            - **Regras críticas:** reforçam a segurança da decisão.
            - **CSV histórico:** armazena leituras e resultados.
            - **Streamlit:** exibe painel interativo.
            - **RAG local:** explica tecnicamente os resultados.
            """
        )

    with col2:
        st.markdown("## Tecnologias")

        st.markdown(
            """
            - Python
            - Pandas
            - Scikit-learn
            - FastAPI
            - Uvicorn
            - Streamlit
            - Plotly
            - PlatformIO
            - ESP32
            - CSV como persistência local
            """
        )

    st.divider()

    st.markdown("## Estratégia de decisão")

    st.markdown(
        """
        O sistema utiliza uma estratégia conservadora. O risco final é definido pelo maior valor
        entre o risco previsto pelo modelo de Machine Learning e o risco identificado pelas regras
        críticas ambientais.

        Isso evita que situações severas sejam subestimadas pelo modelo estatístico.
        """
    )


# ============================================================
# PÁGINA 5 - SOBRE O PROJETO
# ============================================================

def pagina_sobre_projeto():
    st.title("🌎 Sobre o Projeto")
    st.subheader("OrbitaGuard AI — Monitoramento ambiental inteligente")

    st.markdown(
        """
        O **OrbitaGuard AI** é uma Prova de Conceito desenvolvida para demonstrar como
        Inteligência Artificial, dados espaciais, sensores e computação aplicada podem apoiar
        a nova economia espacial e gerar impacto positivo na Terra.
        """
    )

    st.divider()

    st.markdown("## Objetivo")

    st.markdown(
        """
        Desenvolver uma plataforma inteligente capaz de receber dados ambientais,
        classificar riscos, detectar anomalias, registrar histórico e gerar explicações técnicas
        para apoiar decisões preventivas em cenários de eventos ambientais extremos.
        """
    )

    st.markdown("## Relação com a economia espacial")

    st.markdown(
        """
        A economia espacial envolve o uso de satélites, sensores orbitais, telecomunicações,
        geolocalização, processamento de dados e aplicações inteligentes. Neste MVP, os dados
        ambientais e geográficos simulam informações que poderiam ser obtidas por satélites,
        sensores terrestres e estações distribuídas.
        """
    )

    st.markdown("## Impacto positivo na Terra")

    st.markdown(
        """
        A solução contribui para o monitoramento de riscos ambientais, apoio a alertas
        preventivos, acompanhamento de regiões vulneráveis e transformação de dados em
        informação acionável para governos, empresas, produtores rurais e comunidades.
        """
    )

    st.markdown("## Funcionalidades implementadas")

    st.markdown(
        """
        - Geração de dataset ambiental/orbital sintético.
        - Modelo de Machine Learning para classificação de risco.
        - Detecção de anomalias.
        - Regras críticas ambientais.
        - API FastAPI.
        - Dashboard Streamlit.
        - Histórico de monitoramento.
        - Simulador Python de ESP32.
        - Código ESP32 preparado em PlatformIO.
        - Assistente RAG local.
        """
    )

    st.markdown("## Limitações do MVP")

    st.markdown(
        """
        - Os dados utilizados são sintéticos.
        - O ESP32 físico não foi utilizado nesta etapa, sendo representado por simulador.
        - O RAG é local e simplificado, sem uso de modelo generativo externo.
        - A persistência foi feita em CSV para simplificar a demonstração.
        """
    )

    st.markdown("## Melhorias futuras")

    st.markdown(
        """
        - Integração com dados reais de satélites.
        - Uso de banco de dados relacional ou NoSQL.
        - Implantação da API em nuvem.
        - Integração com ESP32 físico.
        - Uso de embeddings reais para RAG.
        - Envio automático de alertas via e-mail, SMS ou aplicativo.
        """
    )


# ============================================================
# MAIN
# ============================================================

def main():
    aplicar_estilo_sidebar()
    inicializar_estado()
    exibir_menu_lateral()

    pagina = st.session_state["pagina_atual"]

    if pagina == "monitoramento":
        pagina_monitoramento_atual()

    elif pagina == "historico":
        pagina_historico_monitoramento()

    elif pagina == "rag":
        pagina_assistente_rag()

    elif pagina == "arquitetura":
        pagina_arquitetura()

    elif pagina == "sobre":
        pagina_sobre_projeto()


if __name__ == "__main__":
    main()