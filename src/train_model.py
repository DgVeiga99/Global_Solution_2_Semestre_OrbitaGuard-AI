import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from config import (
    RAW_DATA_FILE,
    PROCESSED_DATA_FILE,
    RISK_MODEL_FILE,
    ANOMALY_MODEL_FILE,
    SCALER_FILE,
)


FEATURES = [
    "temperatura",
    "umidade",
    "pressao",
    "vento",
    "chuva",
    "luminosidade",
    "indice_vegetacao",
]


def carregar_dados():
    """
    Carrega o dataset gerado.
    """

    df = pd.read_csv(RAW_DATA_FILE)

    # Remover linhas inválidas, caso existam
    df = df.dropna(subset=FEATURES + ["risco_label"])

    return df


def treinar_classificador_risco(df):
    """
    Treina o modelo supervisionado para classificação de risco ambiental.
    """

    X = df[FEATURES]
    y = df["risco_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    modelo = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        random_state=42,
        class_weight="balanced"
    )

    modelo.fit(X_train_scaled, y_train)

    y_pred = modelo.predict(X_test_scaled)

    print("\n==============================")
    print("RESULTADO DO CLASSIFICADOR")
    print("==============================")
    print(f"Acurácia: {accuracy_score(y_test, y_pred):.4f}")

    print("\nMatriz de confusão:")
    print(confusion_matrix(y_test, y_pred))

    print("\nRelatório de classificação:")
    print(classification_report(y_test, y_pred))

    return modelo, scaler


def treinar_detector_anomalias(df, scaler):
    """
    Treina o modelo não supervisionado para detecção de anomalias.
    """

    X = df[FEATURES]
    X_scaled = scaler.transform(X)

    detector = IsolationForest(
        n_estimators=200,
        contamination=0.08,
        random_state=42
    )

    detector.fit(X_scaled)

    pred_anomalia = detector.predict(X_scaled)

    # No Isolation Forest:
    #  1 = normal
    # -1 = anomalia
    df["anomalia"] = pred_anomalia
    df["anomalia"] = df["anomalia"].map({1: 0, -1: 1})

    print("\n==============================")
    print("RESULTADO DO DETECTOR DE ANOMALIAS")
    print("==============================")
    print(df["anomalia"].value_counts())

    return detector, df


def salvar_artefatos(modelo_risco, detector_anomalia, scaler, df):
    """
    Salva modelos treinados, scaler e dataset processado.
    """

    joblib.dump(modelo_risco, RISK_MODEL_FILE)
    joblib.dump(detector_anomalia, ANOMALY_MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    df.to_csv(PROCESSED_DATA_FILE, index=False, encoding="utf-8")

    print("\n==============================")
    print("ARTEFATOS SALVOS")
    print("==============================")
    print(f"Modelo de risco: {RISK_MODEL_FILE}")
    print(f"Modelo de anomalia: {ANOMALY_MODEL_FILE}")
    print(f"Scaler: {SCALER_FILE}")
    print(f"Dataset processado: {PROCESSED_DATA_FILE}")


def main():
    df = carregar_dados()

    modelo_risco, scaler = treinar_classificador_risco(df)

    detector_anomalia, df_processado = treinar_detector_anomalias(df, scaler)

    salvar_artefatos(modelo_risco, detector_anomalia, scaler, df_processado)


if __name__ == "__main__":
    main()