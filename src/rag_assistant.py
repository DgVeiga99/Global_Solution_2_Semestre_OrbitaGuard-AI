import re
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
BASE_CONHECIMENTO_FILE = DOCS_DIR / "base_conhecimento_rag.txt"


# ============================================================
# FUNÇÕES DE PRÉ-PROCESSAMENTO
# ============================================================

def carregar_base_conhecimento():
    """
    Carrega a base de conhecimento local utilizada pelo assistente RAG.
    """

    if not BASE_CONHECIMENTO_FILE.exists():
        return []

    texto = BASE_CONHECIMENTO_FILE.read_text(encoding="utf-8")

    blocos = re.split(r"\n\s*\n", texto)

    documentos = []

    for bloco in blocos:
        bloco_limpo = bloco.strip()

        if bloco_limpo:
            documentos.append(bloco_limpo)

    return documentos


def normalizar_texto(texto):
    """
    Normaliza o texto para comparação simples:
    - converte para minúsculas;
    - remove caracteres especiais;
    - separa palavras.
    """

    texto = texto.lower()
    texto = re.sub(r"[^a-záàâãéèêíïóôõöúçñ0-9\s]", " ", texto)
    palavras = texto.split()

    stopwords = {
        "a", "o", "as", "os", "um", "uma", "uns", "umas",
        "de", "da", "do", "das", "dos",
        "em", "no", "na", "nos", "nas",
        "por", "para", "com", "sem", "sobre",
        "e", "ou", "que", "se", "ao", "à",
        "é", "são", "foi", "ser", "como",
        "qual", "quais", "porque", "porquê",
        "me", "explique", "explicar"
    }

    palavras_filtradas = [p for p in palavras if p not in stopwords and len(p) > 2]

    return palavras_filtradas


def calcular_similaridade(pergunta, documento):
    """
    Calcula uma pontuação simples de similaridade entre a pergunta
    e um bloco da base de conhecimento.
    """

    palavras_pergunta = normalizar_texto(pergunta)
    palavras_documento = normalizar_texto(documento)

    if not palavras_pergunta or not palavras_documento:
        return 0

    contador_pergunta = Counter(palavras_pergunta)
    contador_documento = Counter(palavras_documento)

    pontuacao = 0

    for palavra, freq in contador_pergunta.items():
        if palavra in contador_documento:
            pontuacao += freq * contador_documento[palavra]

    return pontuacao


def recuperar_contexto(pergunta, top_k=3):
    """
    Recupera os trechos mais relevantes da base de conhecimento
    para responder à pergunta.
    """

    documentos = carregar_base_conhecimento()

    if not documentos:
        return []

    documentos_pontuados = []

    for doc in documentos:
        score = calcular_similaridade(pergunta, doc)
        documentos_pontuados.append((score, doc))

    documentos_pontuados.sort(key=lambda item: item[0], reverse=True)

    relevantes = [doc for score, doc in documentos_pontuados if score > 0]

    return relevantes[:top_k]


# ============================================================
# FUNÇÕES DE GERAÇÃO DE RESPOSTA
# ============================================================

def montar_contexto_resultado(resultado_atual=None):
    """
    Monta um resumo do resultado atual do sistema para ser usado
    pelo assistente na resposta.
    """

    if not resultado_atual:
        return "Nenhum resultado atual foi informado."

    risco = resultado_atual.get("risco", "Não informado")
    risco_modelo = resultado_atual.get("risco_modelo", "Não informado")
    risco_regra = resultado_atual.get("risco_regra", "Não informado")
    anomalia = resultado_atual.get("anomalia", "Não informado")
    confianca = resultado_atual.get("confianca_percentual", "Não informado")

    contexto = (
        f"Resultado atual do sistema: risco final = {risco}; "
        f"risco pelo modelo = {risco_modelo}; "
        f"risco por regra = {risco_regra}; "
        f"anomalia = {anomalia}; "
        f"confiança do modelo = {confianca}%."
    )

    return contexto


def montar_contexto_leitura(leitura_atual=None):
    """
    Monta um resumo das variáveis ambientais atuais.
    """

    if not leitura_atual:
        return "Nenhuma leitura ambiental atual foi informada."

    contexto = (
        f"Leitura ambiental atual: temperatura = {leitura_atual.get('temperatura')} °C; "
        f"umidade = {leitura_atual.get('umidade')}%; "
        f"pressão = {leitura_atual.get('pressao')} hPa; "
        f"vento = {leitura_atual.get('vento')} km/h; "
        f"chuva = {leitura_atual.get('chuva')} mm; "
        f"luminosidade = {leitura_atual.get('luminosidade')}; "
        f"índice de vegetação = {leitura_atual.get('indice_vegetacao')}."
    )

    return contexto


def gerar_resposta_assistente(pergunta, resultado_atual=None, leitura_atual=None):
    """
    Gera uma resposta técnica com base em:
    - pergunta do usuário;
    - contexto recuperado da base de conhecimento;
    - resultado atual da análise;
    - leitura ambiental atual.
    """

    pergunta = pergunta.strip()

    if not pergunta:
        return {
            "resposta": "Digite uma pergunta para que o assistente possa analisar o contexto.",
            "contextos_recuperados": []
        }

    contextos = recuperar_contexto(pergunta, top_k=3)

    contexto_resultado = montar_contexto_resultado(resultado_atual)
    contexto_leitura = montar_contexto_leitura(leitura_atual)

    if not contextos:
        resposta = (
            "Não encontrei um trecho diretamente relacionado na base de conhecimento local. "
            "Mesmo assim, com base no estado atual do sistema, é possível observar o seguinte:\n\n"
            f"{contexto_resultado}\n\n"
            f"{contexto_leitura}\n\n"
            "Recomenda-se verificar as variáveis ambientais, o risco final, a presença de anomalias "
            "e a recomendação operacional gerada pelo sistema."
        )

        return {
            "resposta": resposta,
            "contextos_recuperados": []
        }

    contexto_textual = "\n\n".join(contextos)

    resposta = (
        "Com base na base de conhecimento local do OrbitaGuard AI e no resultado atual do sistema:\n\n"
        f"{contexto_resultado}\n\n"
        f"{contexto_leitura}\n\n"
        "Análise técnica:\n"
        f"{contexto_textual}\n\n"
        "Síntese operacional:\n"
        "A decisão deve considerar a combinação entre os dados ambientais medidos, "
        "a classificação do modelo de Machine Learning, a camada de regras críticas "
        "e o detector de anomalias. Quando o risco final é elevado ou existe anomalia, "
        "a recomendação é validar os sensores, acompanhar a tendência das próximas leituras "
        "e priorizar medidas preventivas."
    )

    return {
        "resposta": resposta,
        "contextos_recuperados": contextos
    }


# ============================================================
# TESTE LOCAL
# ============================================================

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

    resultado_teste = {
        "risco": "Crítico",
        "risco_modelo": "Atenção",
        "risco_regra": "Crítico",
        "anomalia": True,
        "confianca_percentual": 80.8
    }

    pergunta = "Por que o risco está crítico?"

    resposta = gerar_resposta_assistente(
        pergunta=pergunta,
        resultado_atual=resultado_teste,
        leitura_atual=leitura_teste
    )

    print("\nPergunta:")
    print(pergunta)

    print("\nResposta:")
    print(resposta["resposta"])

    print("\nContextos recuperados:")
    for contexto in resposta["contextos_recuperados"]:
        print("-" * 80)
        print(contexto)


if __name__ == "__main__":
    main()