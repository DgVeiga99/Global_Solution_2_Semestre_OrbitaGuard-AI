from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import sys
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))


from predict_risk import prever_risco, gerar_recomendacao
from log_manager import salvar_leitura_historico


# ============================================================
# CONFIGURAÇÃO DA API
# ============================================================

app = FastAPI(
    title="OrbitaGuard AI API",
    description="API para classificação de risco ambiental com IA, regras críticas, detecção de anomalias e histórico de leituras.",
    version="1.2.0"
)


# ============================================================
# MODELO DE ENTRADA
# ============================================================

class SensorData(BaseModel):
    temperatura: float
    umidade: float
    pressao: float
    vento: float
    chuva: float
    luminosidade: float
    indice_vegetacao: float
    latitude: float | None = None
    longitude: float | None = None


# ============================================================
# ROTAS DA API
# ============================================================

@app.get("/")
def home():
    return {
        "projeto": "OrbitaGuard AI",
        "status": "API online",
        "versao": "1.2.0",
        "descricao": "Sistema inteligente para monitoramento ambiental com dados espaciais, sensores, Machine Learning, regras críticas, detecção de anomalias e histórico."
    }


@app.post("/predict")
def predict(data: SensorData):
    leitura = {
        "temperatura": data.temperatura,
        "umidade": data.umidade,
        "pressao": data.pressao,
        "vento": data.vento,
        "chuva": data.chuva,
        "luminosidade": data.luminosidade,
        "indice_vegetacao": data.indice_vegetacao,
    }

    resultado = prever_risco(leitura)
    recomendacao = gerar_recomendacao(resultado)

    historico_salvo = False
    erro_historico = None

    try:
        salvar_leitura_historico(
            leitura=leitura,
            resultado=resultado,
            recomendacao=recomendacao,
            latitude=data.latitude,
            longitude=data.longitude
        )
        historico_salvo = True

    except Exception as erro:
        historico_salvo = False
        erro_historico = str(erro)

    return {
        "timestamp": datetime.now().isoformat(),
        "localizacao": {
            "latitude": data.latitude,
            "longitude": data.longitude
        },
        "entrada": leitura,
        "resultado": {
            "risco_codigo": resultado.get("risco_codigo"),
            "risco": resultado.get("risco"),

            "risco_modelo_codigo": resultado.get("risco_modelo_codigo"),
            "risco_modelo": resultado.get("risco_modelo"),

            "risco_regra_codigo": resultado.get("risco_regra_codigo"),
            "risco_regra": resultado.get("risco_regra"),

            "anomalia": resultado.get("anomalia"),
            "confianca_percentual": resultado.get("confianca_percentual"),
            "recomendacao": recomendacao
        },
        "historico": {
            "salvo": historico_salvo,
            "erro": erro_historico
        }
    }