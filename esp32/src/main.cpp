#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================================================
// ORBITAGUARD AI - ESTAÇÃO EMBARCADA ESP32
// ============================================================
// Este código representa a versão embarcada da estação ambiental.
// Ele foi estruturado para execução em ESP32 físico via PlatformIO.
//
// Como o projeto pode ser demonstrado sem hardware físico,
// a execução funcional será feita também por um simulador Python,
// mantendo o mesmo formato de payload JSON enviado à API.
// ============================================================


// ============================================================
// CONFIGURAÇÕES DE REDE
// ============================================================

const char* WIFI_SSID = "NOME_DA_REDE";
const char* WIFI_PASSWORD = "SENHA_DA_REDE";

// Trocar pelo IP do computador onde a API FastAPI está rodando.
// Exemplo: http://192.168.0.105:8000/predict
const char* API_URL = "http://192.168.0.105:8000/predict";


// ============================================================
// CONFIGURAÇÕES GERAIS
// ============================================================

const unsigned long INTERVALO_ENVIO_MS = 5000;
unsigned long ultimoEnvio = 0;
int contadorLeitura = 0;


// ============================================================
// ESTRUTURA DE DADOS AMBIENTAIS
// ============================================================

struct LeituraAmbiental {
    float temperatura;
    float umidade;
    float pressao;
    float vento;
    float chuva;
    float luminosidade;
    float indiceVegetacao;
    float latitude;
    float longitude;
};


// ============================================================
// CONEXÃO WI-FI
// ============================================================

void conectarWiFi() {
    Serial.println();
    Serial.println("========================================");
    Serial.println("Conectando ao Wi-Fi");
    Serial.println("========================================");

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int tentativas = 0;

    while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
        delay(500);
        Serial.print(".");
        tentativas++;
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Wi-Fi conectado com sucesso.");
        Serial.print("IP local do ESP32: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("Falha ao conectar ao Wi-Fi.");
    }
}


// ============================================================
// GERAÇÃO DE LEITURA SIMULADA
// ============================================================
// Em uma aplicação física, esta função seria substituída por
// leituras reais de sensores, como:
// - DHT22 para temperatura e umidade;
// - BMP280/BME280 para pressão;
// - LDR para luminosidade;
// - sensor de chuva;
// - GPS ou coordenadas fixas.
// ============================================================

LeituraAmbiental gerarLeituraSimulada() {
    contadorLeitura++;

    LeituraAmbiental leitura;

    leitura.latitude = -23.7100;
    leitura.longitude = -46.4100;

    int cenario = contadorLeitura % 4;

    if (cenario == 0) {
        // Cenário normal
        leitura.temperatura = 25.0;
        leitura.umidade = 65.0;
        leitura.pressao = 1013.0;
        leitura.vento = 12.0;
        leitura.chuva = 2.0;
        leitura.luminosidade = 550.0;
        leitura.indiceVegetacao = 0.65;
    }
    else if (cenario == 1) {
        // Cenário de atenção
        leitura.temperatura = 32.0;
        leitura.umidade = 38.0;
        leitura.pressao = 1008.0;
        leitura.vento = 30.0;
        leitura.chuva = 5.0;
        leitura.luminosidade = 760.0;
        leitura.indiceVegetacao = 0.42;
    }
    else if (cenario == 2) {
        // Cenário crítico de seca/queimada
        leitura.temperatura = 39.5;
        leitura.umidade = 18.0;
        leitura.pressao = 998.0;
        leitura.vento = 28.0;
        leitura.chuva = 0.5;
        leitura.luminosidade = 940.0;
        leitura.indiceVegetacao = 0.18;
    }
    else {
        // Cenário de tempestade severa
        leitura.temperatura = 24.0;
        leitura.umidade = 92.0;
        leitura.pressao = 985.0;
        leitura.vento = 72.0;
        leitura.chuva = 48.0;
        leitura.luminosidade = 180.0;
        leitura.indiceVegetacao = 0.58;
    }

    return leitura;
}


// ============================================================
// MONTAGEM DO JSON
// ============================================================

String montarPayloadJson(const LeituraAmbiental& leitura) {
    StaticJsonDocument<512> doc;

    doc["temperatura"] = leitura.temperatura;
    doc["umidade"] = leitura.umidade;
    doc["pressao"] = leitura.pressao;
    doc["vento"] = leitura.vento;
    doc["chuva"] = leitura.chuva;
    doc["luminosidade"] = leitura.luminosidade;
    doc["indice_vegetacao"] = leitura.indiceVegetacao;
    doc["latitude"] = leitura.latitude;
    doc["longitude"] = leitura.longitude;

    String payload;
    serializeJson(doc, payload);

    return payload;
}


// ============================================================
// ENVIO HTTP PARA A API
// ============================================================

void enviarParaAPI(const String& payload) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi desconectado. Tentando reconectar...");
        conectarWiFi();
        return;
    }

    HTTPClient http;

    Serial.println();
    Serial.println("========================================");
    Serial.println("Enviando leitura para OrbitaGuard API");
    Serial.println("========================================");
    Serial.print("URL: ");
    Serial.println(API_URL);
    Serial.print("Payload: ");
    Serial.println(payload);

    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    int codigoHttp = http.POST(payload);

    Serial.print("Código HTTP: ");
    Serial.println(codigoHttp);

    if (codigoHttp > 0) {
        String resposta = http.getString();

        Serial.println("Resposta da API:");
        Serial.println(resposta);
    } else {
        Serial.println("Falha no envio HTTP.");
        Serial.print("Erro: ");
        Serial.println(http.errorToString(codigoHttp));
    }

    http.end();
}


// ============================================================
// SETUP
// ============================================================

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("========================================");
    Serial.println("OrbitaGuard AI - Estacao ESP32");
    Serial.println("PlatformIO + Arduino Framework");
    Serial.println("========================================");

    conectarWiFi();
}


// ============================================================
// LOOP PRINCIPAL
// ============================================================

void loop() {
    unsigned long agora = millis();

    if (agora - ultimoEnvio >= INTERVALO_ENVIO_MS) {
        ultimoEnvio = agora;

        LeituraAmbiental leitura = gerarLeituraSimulada();
        String payload = montarPayloadJson(leitura);

        enviarParaAPI(payload);
    }
}