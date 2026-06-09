import pandas as pd
from datetime import datetime
from pathlib import Path

from config import DATA_PROCESSED_DIR


HISTORICO_FILE = DATA_PROCESSED_DIR / "historico_leituras.csv"


COLUNAS_HISTORICO = [
    "timestamp",
    "latitude",
    "longitude",

    "temperatura",
    "umidade",
    "pressao",
    "vento",
    "chuva",
    "luminosidade",
    "indice_vegetacao",

    "risco_codigo",
    "risco",
    "risco_modelo_codigo",
    "risco_modelo",
    "risco_regra_codigo",
    "risco_regra",

    "anomalia",
    "confianca_percentual",
    "recomendacao"
]


def montar_registro_historico(leitura, resultado, recomendacao, latitude=None, longitude=None):
    """
    Monta um registro único de histórico a partir da leitura recebida,
    do resultado da IA e da recomendação gerada.
    """

    registro = {
        "timestamp": datetime.now().isoformat(),

        "latitude": latitude,
        "longitude": longitude,

        "temperatura": leitura.get("temperatura"),
        "umidade": leitura.get("umidade"),
        "pressao": leitura.get("pressao"),
        "vento": leitura.get("vento"),
        "chuva": leitura.get("chuva"),
        "luminosidade": leitura.get("luminosidade"),
        "indice_vegetacao": leitura.get("indice_vegetacao"),

        "risco_codigo": resultado.get("risco_codigo"),
        "risco": resultado.get("risco"),

        "risco_modelo_codigo": resultado.get("risco_modelo_codigo"),
        "risco_modelo": resultado.get("risco_modelo"),

        "risco_regra_codigo": resultado.get("risco_regra_codigo"),
        "risco_regra": resultado.get("risco_regra"),

        "anomalia": resultado.get("anomalia"),
        "confianca_percentual": resultado.get("confianca_percentual"),
        "recomendacao": recomendacao
    }

    return registro


def salvar_leitura_historico(leitura, resultado, recomendacao, latitude=None, longitude=None):
    """
    Salva uma leitura processada no arquivo CSV de histórico.

    O arquivo é criado automaticamente caso ainda não exista.
    """

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    registro = montar_registro_historico(
        leitura=leitura,
        resultado=resultado,
        recomendacao=recomendacao,
        latitude=latitude,
        longitude=longitude
    )

    df_novo = pd.DataFrame([registro], columns=COLUNAS_HISTORICO)

    arquivo_existe = HISTORICO_FILE.exists()

    df_novo.to_csv(
        HISTORICO_FILE,
        mode="a",
        header=not arquivo_existe,
        index=False,
        encoding="utf-8"
    )

    return registro


def carregar_historico(limite=None):
    """
    Carrega o histórico de leituras salvas.

    Se limite for informado, retorna apenas os últimos registros.
    """

    if not HISTORICO_FILE.exists():
        return pd.DataFrame(columns=COLUNAS_HISTORICO)

    df = pd.read_csv(HISTORICO_FILE)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp")

    if limite is not None:
        df = df.tail(limite)

    return df


def limpar_historico():
    """
    Remove o arquivo de histórico.

    Essa função é útil para testes durante o desenvolvimento.
    """

    if HISTORICO_FILE.exists():
        HISTORICO_FILE.unlink()
        return True

    return False