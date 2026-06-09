import pandas as pd
import joblib

from config import RISK_MODEL_FILE, ANOMALY_MODEL_FILE, SCALER_FILE


FEATURES = [
    "temperatura",
    "umidade",
    "pressao",
    "vento",
    "chuva",
    "luminosidade",
    "indice_vegetacao",
]


RISK_LABELS = {
    0: "Normal",
    1: "Atenção",
    2: "Alto Risco",
    3: "Crítico",
}


def carregar_modelos():
    """
    Carrega os modelos treinados salvos na pasta models.
    """

    modelo_risco = joblib.load(RISK_MODEL_FILE)
    modelo_anomalia = joblib.load(ANOMALY_MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)

    return modelo_risco, modelo_anomalia, scaler


def classificar_risco_por_regras(dados):
    """
    Camada determinística de segurança ambiental.

    Essa função aplica regras físicas simples para evitar que o modelo
    subestime cenários claramente críticos.
    """

    temperatura = dados["temperatura"]
    umidade = dados["umidade"]
    pressao = dados["pressao"]
    vento = dados["vento"]
    chuva = dados["chuva"]
    luminosidade = dados["luminosidade"]
    indice_vegetacao = dados["indice_vegetacao"]

    risco_regra = 0  # Normal

    # Risco crítico de seca severa, queimada ou estresse ambiental extremo
    if temperatura > 38 and umidade < 25 and indice_vegetacao < 0.25:
        risco_regra = max(risco_regra, 3)

    # Alto risco de seca, queimada ou estresse ambiental
    elif temperatura > 34 and umidade < 35 and indice_vegetacao < 0.35:
        risco_regra = max(risco_regra, 2)

    # Luminosidade muito alta combinada com baixa vegetação e baixa umidade
    if luminosidade > 850 and indice_vegetacao < 0.30 and umidade < 35:
        risco_regra = max(risco_regra, 2)

    # Risco crítico de tempestade severa
    if pressao < 990 and vento > 65 and chuva > 40:
        risco_regra = max(risco_regra, 3)

    # Alto risco de tempestade
    elif pressao < 1000 and vento > 45 and chuva > 20:
        risco_regra = max(risco_regra, 2)

    # Condições intermediárias de atenção
    if temperatura > 31 or umidade < 40 or vento > 35 or chuva > 15:
        risco_regra = max(risco_regra, 1)

    return risco_regra


def prever_risco(dados):
    """
    Recebe um dicionário com dados ambientais e retorna:
    - risco final;
    - risco previsto pelo modelo;
    - risco definido pelas regras;
    - anomalia;
    - confiança percentual.
    """

    modelo_risco, modelo_anomalia, scaler = carregar_modelos()

    df = pd.DataFrame([dados])

    X = df[FEATURES]
    X_scaled = scaler.transform(X)

    # Predição pelo modelo supervisionado
    risco_modelo = int(modelo_risco.predict(X_scaled)[0])

    # Predição por regras determinísticas de segurança ambiental
    risco_regra = classificar_risco_por_regras(dados)

    # Estratégia conservadora:
    # o risco final será sempre o maior entre modelo e regras
    risco_num = max(risco_modelo, risco_regra)
    risco_texto = RISK_LABELS.get(risco_num, "Desconhecido")

    # Detecção de anomalia
    anomalia_pred = int(modelo_anomalia.predict(X_scaled)[0])
    anomalia = True if anomalia_pred == -1 else False

    # Confiança do modelo supervisionado
    confianca = None

    if hasattr(modelo_risco, "predict_proba"):
        proba = modelo_risco.predict_proba(X_scaled)[0]
        confianca = round(float(max(proba)) * 100, 2)

    resultado = {
        "risco_codigo": risco_num,
        "risco": risco_texto,
        "risco_modelo_codigo": risco_modelo,
        "risco_modelo": RISK_LABELS.get(risco_modelo, "Desconhecido"),
        "risco_regra_codigo": risco_regra,
        "risco_regra": RISK_LABELS.get(risco_regra, "Desconhecido"),
        "anomalia": anomalia,
        "confianca_percentual": confianca,
        "dados_entrada": dados,
    }

    return resultado


def gerar_recomendacao(resultado):
    """
    Gera uma recomendação inicial baseada no risco final.
    Futuramente essa lógica será ampliada com IA Generativa/RAG.
    """

    risco = resultado["risco"]
    anomalia = resultado["anomalia"]

    if risco == "Normal" and not anomalia:
        return "Condição ambiental dentro do padrão. Manter monitoramento contínuo."

    if risco == "Normal" and anomalia:
        return "Anomalia detectada, mesmo com risco classificado como normal. Recomenda-se validar sensores e acompanhar novas leituras."

    if risco == "Atenção":
        return "Condição de atenção detectada. Recomenda-se acompanhar a evolução dos sensores e verificar tendência dos dados."

    if risco == "Alto Risco":
        return "Alto risco ambiental detectado. Recomenda-se emitir alerta preventivo, validar dados locais e monitorar a região com maior frequência."

    if risco == "Crítico":
        return "Condição crítica detectada. Recomenda-se acionar plano de resposta, monitorar a região em tempo real e priorizar medidas preventivas."

    return "Sem recomendação disponível."


def main():
    leitura_teste = {
        "temperatura": 39.5,
        "umidade": 18.0,
        "pressao": 998.0,
        "vento": 28.0,
        "chuva": 0.5,
        "luminosidade": 940.0,
        "indice_vegetacao": 0.18,
    }

    resultado = prever_risco(leitura_teste)
    recomendacao = gerar_recomendacao(resultado)

    print("\n==============================")
    print("PREDIÇÃO DE RISCO AMBIENTAL")
    print("==============================")
    print(f"Risco final: {resultado['risco']}")
    print(f"Código do risco final: {resultado['risco_codigo']}")
    print(f"Risco pelo modelo: {resultado['risco_modelo']}")
    print(f"Código do risco pelo modelo: {resultado['risco_modelo_codigo']}")
    print(f"Risco por regra: {resultado['risco_regra']}")
    print(f"Código do risco por regra: {resultado['risco_regra_codigo']}")
    print(f"Anomalia: {resultado['anomalia']}")
    print(f"Confiança do modelo: {resultado['confianca_percentual']}%")
    print(f"Recomendação: {recomendacao}")


if __name__ == "__main__":
    main()