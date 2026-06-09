from pathlib import Path

# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretórios principais
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"

# Arquivos de dados
RAW_DATA_FILE = DATA_RAW_DIR / "dados_ambientais_orbitais.csv"
PROCESSED_DATA_FILE = DATA_PROCESSED_DIR / "dados_ambientais_processados.csv"

# Modelos treinados
RISK_MODEL_FILE = MODELS_DIR / "risk_classifier.pkl"
ANOMALY_MODEL_FILE = MODELS_DIR / "anomaly_detector.pkl"
SCALER_FILE = MODELS_DIR / "scaler.pkl"

# Garantir que as pastas existam
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)