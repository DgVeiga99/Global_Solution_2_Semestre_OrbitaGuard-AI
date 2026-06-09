import time
import requests
from datetime import datetime


API_URL = "http://127.0.0.1:8000/predict"


CENARIOS = [
    {
        "nome": "Normal",
        "temperatura": 25.0,
        "umidade": 65.0,
        "pressao": 1013.0,
        "vento": 12.0,
        "chuva": 2.0,
        "luminosidade": 550.0,
        "indice_vegetacao": 0.65,
        "latitude": -23.71,
        "longitude": -46.41,
    },
    {
        "nome": "Atenção",
        "temperatura": 32.0,
        "umidade": 38.0,
        "pressao": 1008.0,
        "vento": 30.0,
        "chuva": 5.0,
        "luminosidade": 760.0,
        "indice_vegetacao": 0.42,
        "latitude": -23.71,
        "longitude": -46.41,
    },
    {
        "nome": "Seca/Queimada Crítica",
        "temperatura": 39.5,
        "umidade": 18.0,
        "pressao": 998.0,
        "vento": 28.0,
        "chuva": 0.5,
        "luminosidade": 940.0,
        "indice_vegetacao": 0.18,
        "latitude": -23.71,
        "longitude": -46.41,
    },
    {
        "nome": "Tempestade Severa",
        "temperatura": 24.0,
        "umidade": 92.0,
        "pressao": 985.0,
        "vento": 72.0,
        "chuva": 48.0,
        "luminosidade": 180.0,
        "indice_vegetacao": 0.58,
        "latitude": -23.71,
        "longitude": -46.41,
    },
]


def montar_payload(cenario):
    """
    Remove o campo 'nome' antes de enviar para a API,
    mantendo o mesmo formato esperado pelo endpoint /predict.
    """

    payload = cenario.copy()
    payload.pop("nome", None)

    return payload


def enviar_leitura(cenario):
    payload = montar_payload(cenario)

    print("\n==================================================")
    print("OrbitaGuard AI - Simulador de Estação ESP32")
    print("==================================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Cenário: {cenario['nome']}")
    print(f"Payload enviado: {payload}")

    try:
        response = requests.post(API_URL, json=payload, timeout=10)

        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            resposta = response.json()

            resultado = resposta.get("resultado", {})

            print("Resposta da API:")
            print(f"  Risco final: {resultado.get('risco')}")
            print(f"  Risco modelo: {resultado.get('risco_modelo')}")
            print(f"  Risco regra: {resultado.get('risco_regra')}")
            print(f"  Anomalia: {resultado.get('anomalia')}")
            print(f"  Confiança ML: {resultado.get('confianca_percentual')}%")
            print(f"  Recomendação: {resultado.get('recomendacao')}")
        else:
            print("Erro na resposta da API:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("Erro de conexão.")
        print("Verifique se a API está rodando em http://127.0.0.1:8000")

    except requests.exceptions.Timeout:
        print("Tempo limite excedido ao tentar acessar a API.")

    except Exception as erro:
        print(f"Erro inesperado: {erro}")


def main():
    print("Iniciando simulação da estação ESP32...")
    print("Pressione CTRL + C para interromper.")

    indice = 0

    while True:
        cenario = CENARIOS[indice]
        enviar_leitura(cenario)

        indice = (indice + 1) % len(CENARIOS)

        time.sleep(5)


if __name__ == "__main__":
    main()