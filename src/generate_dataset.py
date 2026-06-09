import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from config import RAW_DATA_FILE


def classificar_risco(row):
    """
    Classifica o risco ambiental com base em regras simuladas.
    Essas regras representam uma lógica inicial para gerar o dataset rotulado.
    """

    temperatura = row["temperatura"]
    umidade = row["umidade"]
    pressao = row["pressao"]
    vento = row["vento"]
    chuva = row["chuva"]
    luminosidade = row["luminosidade"]
    indice_vegetacao = row["indice_vegetacao"]

    risco = 0  # Normal

    # Risco de seca/queimada
    if temperatura > 34 and umidade < 35 and indice_vegetacao < 0.35:
        risco = max(risco, 2)

    if temperatura > 38 and umidade < 25 and indice_vegetacao < 0.25:
        risco = max(risco, 3)

    # Risco de tempestade
    if pressao < 1000 and vento > 45 and chuva > 20:
        risco = max(risco, 2)

    if pressao < 990 and vento > 65 and chuva > 40:
        risco = max(risco, 3)

    # Condição intermediária
    if temperatura > 31 or umidade < 40 or vento > 35 or chuva > 15:
        risco = max(risco, 1)

    # Luminosidade muito alta associada à baixa vegetação pode indicar estresse ambiental
    if luminosidade > 850 and indice_vegetacao < 0.30 and umidade < 35:
        risco = max(risco, 2)

    return risco


def gerar_dataset(qtd_registros=3000, seed=42):
    """
    Gera um dataset ambiental sintético para o projeto OrbitaGuard AI.
    """

    np.random.seed(seed)

    data_inicial = datetime.now() - timedelta(days=180)

    registros = []

    for i in range(qtd_registros):
        timestamp = data_inicial + timedelta(hours=i)

        # Coordenadas aproximadas em regiões do Brasil
        latitude = np.random.uniform(-30.0, 5.0)
        longitude = np.random.uniform(-60.0, -35.0)

        temperatura = np.random.normal(loc=28, scale=6)
        umidade = np.random.normal(loc=60, scale=20)
        pressao = np.random.normal(loc=1012, scale=12)
        vento = np.random.exponential(scale=18)
        chuva = np.random.exponential(scale=8)
        luminosidade = np.random.normal(loc=650, scale=180)
        indice_vegetacao = np.random.normal(loc=0.55, scale=0.20)

        # Limites físicos aproximados
        temperatura = np.clip(temperatura, 5, 48)
        umidade = np.clip(umidade, 5, 100)
        pressao = np.clip(pressao, 960, 1040)
        vento = np.clip(vento, 0, 120)
        chuva = np.clip(chuva, 0, 100)
        luminosidade = np.clip(luminosidade, 0, 1200)
        indice_vegetacao = np.clip(indice_vegetacao, 0, 1)

        registros.append({
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "temperatura": round(temperatura, 2),
            "umidade": round(umidade, 2),
            "pressao": round(pressao, 2),
            "vento": round(vento, 2),
            "chuva": round(chuva, 2),
            "luminosidade": round(luminosidade, 2),
            "indice_vegetacao": round(indice_vegetacao, 3),
        })

    df = pd.DataFrame(registros)
    df["risco_label"] = df.apply(classificar_risco, axis=1)

    return df


def main():
    df = gerar_dataset()
    df.to_csv(RAW_DATA_FILE, index=False, encoding="utf-8")

    print("Dataset gerado com sucesso!")
    print(f"Arquivo salvo em: {RAW_DATA_FILE}")
    print()
    print(df.head())
    print()
    print("Distribuição das classes:")
    print(df["risco_label"].value_counts().sort_index())


if __name__ == "__main__":
    main()