# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="../../../assets/logo-fiap.png" 
       alt="FIAP - Faculdade de Informática e Administração Paulista" 
       width="40%">
</a>
</p>

<br>

# OrbitaGuard AI — Plataforma Inteligente de Monitoramento Ambiental com Dados Espaciais, Sensores e Inteligência Artificial

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/diego-veiga-5b884317b">Diego Nunes Veiga</a>

## 👩‍🏫 Professores:

### Coordenador(a)
- André Godoi Chiovato


## 📜 Descrição

O **OrbitaGuard AI** é uma Prova de Conceito (POC/MVP) desenvolvida para a Global Solution da FIAP, com foco no uso de tecnologias avançadas de Inteligência Artificial, dados espaciais, sensores, automação e computação aplicada para impulsionar a nova economia espacial e gerar impacto positivo na Terra.

A proposta do projeto é demonstrar como informações ambientais e geográficas, simulando dados oriundos de satélites, sensores orbitais e estações terrestres, podem ser processadas por uma arquitetura inteligente para apoiar decisões preventivas relacionadas a eventos ambientais extremos. O sistema foi projetado para classificar riscos ambientais, detectar anomalias, registrar histórico de leituras e apresentar os resultados em um dashboard interativo.

O MVP utiliza uma base sintética de dados ambientais/orbitais contendo variáveis como temperatura, umidade, pressão atmosférica, velocidade do vento, volume de chuva, luminosidade, índice de vegetação, latitude e longitude. A partir desses dados, foi treinado um modelo de **Machine Learning** baseado em **Random Forest**, responsável por classificar o risco ambiental em quatro níveis: **Normal**, **Atenção**, **Alto Risco** e **Crítico**.

Além do modelo supervisionado, o sistema também utiliza um algoritmo de **detecção de anomalias com Isolation Forest**, capaz de identificar leituras ambientais fora do padrão esperado. Para aumentar a confiabilidade da decisão, foi implementada uma camada de **regras críticas ambientais**, que atua de forma determinística em situações severas, como risco de seca, queimadas ou tempestades intensas. Assim, o risco final é calculado de forma conservadora, considerando o maior nível de risco entre a previsão estatística do modelo e as regras críticas.

A arquitetura também conta com uma **API desenvolvida em FastAPI**, responsável por receber as leituras ambientais, executar a predição, aplicar as regras, detectar anomalias, gerar recomendações e registrar os resultados em histórico CSV. Para simular uma estação de campo, foi desenvolvido um **simulador Python de ESP32**, que envia leituras automaticamente para a API por meio de requisições HTTP. Também foi preparado um código embarcado em **PlatformIO** para futura execução em uma placa ESP32 física.

A visualização dos dados é feita por um **dashboard em Streamlit**, dividido em módulos: Monitoramento Atual, Histórico de Monitoramento, Assistente Inteligente RAG, Arquitetura do Sistema e Sobre o Projeto. O dashboard permite acompanhar leituras em tempo real, visualizar gráficos, analisar eventos críticos, consultar histórico e obter explicações técnicas por meio de um assistente baseado em **RAG local simplificado**.

Como impacto positivo, o OrbitaGuard AI demonstra como dados espaciais e sensores inteligentes podem ser usados para apoiar alertas preventivos, monitoramento ambiental, mitigação de riscos climáticos e tomada de decisão em regiões vulneráveis. Embora os dados utilizados sejam sintéticos, a arquitetura foi pensada para evoluir futuramente com integração a dados reais de satélites, bancos de dados em nuvem, sensores físicos e sistemas automáticos de alerta.


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>api</b>: Pasta responsável pela API do projeto, desenvolvida com FastAPI. Contém o arquivo `app.py`, que recebe leituras ambientais, executa a predição de risco, aplica regras críticas, detecta anomalias, gera recomendações e salva o histórico de monitoramento.

- <b>dashboard</b>: Pasta destinada ao dashboard interativo desenvolvido com Streamlit. Contém o arquivo `streamlit_app.py`, responsável pela interface visual do sistema, incluindo monitoramento atual, histórico, gráficos, assistente RAG, arquitetura e informações gerais do projeto.

- <b>data</b>: Contém os dados utilizados pelo projeto. A subpasta `raw` armazena a base ambiental/orbital sintética gerada pelo sistema. A subpasta `processed` armazena os dados processados e o histórico de leituras recebidas pela API.

- <b>docs</b>: Pasta destinada à documentação textual do projeto, incluindo base de conhecimento do assistente RAG, registros de arquitetura, prints, diagramas, storyboard, estratégia de IA e materiais de apoio para o relatório final.

- <b>esp32</b>: Pasta destinada ao código embarcado preparado para ESP32 com PlatformIO. Contém o arquivo `platformio.ini` e o código `main.cpp`, que representa a futura estação física de sensoriamento ambiental.

- <b>models</b>: Pasta responsável por armazenar os modelos treinados. Contém o modelo de classificação de risco com Random Forest, o detector de anomalias com Isolation Forest e o scaler utilizado no pré-processamento dos dados.

- <b>src</b>: Todo o código fonte principal desenvolvido em Python. Inclui scripts para geração de dataset, treinamento dos modelos, predição de risco, salvamento de histórico, simulação do ESP32 e assistente RAG local.

- <b>requirements.txt</b>: Arquivo com as bibliotecas necessárias para instalação e execução do projeto.

- <b>.gitignore</b>: Arquivo de configuração para evitar o versionamento de arquivos desnecessários, como ambiente virtual, cache Python e arquivos temporários.

- <b>README.md</b>: Arquivo que serve como guia e explicação geral sobre o projeto.


## 📎 Links e Observações

- <b>Listagem de Links</b>:

  - Relatório: `A preencher após publicação do repositório`
  - Vídeo de apresentação no YouTube: `A preencher após gravação e publicação como não listado`

- <b>Explicação de decisões técnicas</b>:

  - O projeto utiliza dados ambientais/orbitais sintéticos para viabilizar a construção do MVP sem depender de bases externas ou sensores físicos reais.
  - O modelo de classificação foi desenvolvido com Random Forest por ser robusto, interpretável e adequado para dados tabulares.
  - A detecção de anomalias foi implementada com Isolation Forest, permitindo identificar combinações incomuns de variáveis ambientais.
  - A decisão final do sistema combina Machine Learning e regras críticas determinísticas, evitando que situações severas sejam subestimadas pelo modelo estatístico.
  - O ESP32 físico foi representado por um simulador Python, que envia dados para a API no mesmo formato previsto para uma estação real.
  - A persistência foi feita em CSV para simplificar a execução local e facilitar a análise dos registros durante a demonstração.
  - O assistente RAG foi implementado localmente, utilizando uma base de conhecimento textual do próprio projeto, sem dependência de APIs pagas ou serviços externos.

- <b>Observações Gerais</b>:

  - O projeto é uma Prova de Conceito acadêmica e pode ser evoluído futuramente com dados reais de satélites, sensores físicos, banco de dados em nuvem e sistemas automáticos de alerta.
  - Caso a entrega esteja vinculada a uma competição ou avaliação especial da Global Solution, a participação deverá ser confirmada conforme orientação dos docentes.
    

## 🔧 Como executar o código

### Pré-requisitos

Para executar o projeto localmente, recomenda-se utilizar:

- Python 3.10 ou superior
- Visual Studio Code
- Git
- Ambiente virtual Python (`venv`)
- Navegador web atualizado
- PlatformIO instalado no VS Code, caso deseje abrir o código preparado para ESP32

### Bibliotecas utilizadas

As principais bibliotecas utilizadas no projeto são:

- pandas
- numpy
- scikit-learn
- joblib
- matplotlib
- plotly
- streamlit
- fastapi
- uvicorn
- requests

### 1. Clonar o repositório

Após o projeto estar publicado no GitHub, clone o repositório com:

```bash
git clone URL_DO_REPOSITORIO
cd OrbitaGuard_AI
```

Caso o projeto já esteja localmente no computador, basta abrir a pasta no VS Code.

### 2. Criar e ativar o ambiente virtual

No Windows, execute:

```bash
python -m venv .venv
.venv\Scripts\activate
```

No Linux ou macOS, execute:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

Com o ambiente virtual ativo, execute:

```bash
pip install -r requirements.txt
```

### 4. Gerar o dataset sintético

Execute o script responsável por gerar a base ambiental/orbital sintética:

```bash
python src/generate_dataset.py
```

O arquivo será salvo em:

```bash
data/raw/dados_ambientais_orbitais.csv
```

### 5. Treinar os modelos de IA

Execute:

```bash
python src/train_model.py
```

Esse comando gera os arquivos de modelo na pasta `models`:

```bash
models/risk_classifier.pkl
models/anomaly_detector.pkl
models/scaler.pkl
```

Também será gerado um arquivo processado em:

```bash
data/processed/dados_ambientais_processados.csv
```

### 6. Testar a predição local

Para validar a predição diretamente pelo terminal, execute:

```bash
python src/predict_risk.py
```

Esse teste exibe o risco final, risco previsto pelo modelo, risco por regra, anomalia, confiança e recomendação.

### 7. Executar a API FastAPI

Em um terminal, execute:

```bash
uvicorn api.app:app --reload
```

A API ficará disponível em:

```bash
http://127.0.0.1:8000
```

A documentação Swagger pode ser acessada em:

```bash
http://127.0.0.1:8000/docs
```

### 8. Executar o simulador ESP32

Com a API rodando, abra um segundo terminal e execute:

```bash
python src/esp32_simulator.py
```

O simulador enviará leituras ambientais para a API por meio de requisições HTTP POST. As leituras serão processadas e registradas no histórico.

### 9. Executar o dashboard Streamlit

Abra um terceiro terminal e execute:

```bash
streamlit run dashboard/streamlit_app.py
```

O dashboard será aberto no navegador e permitirá acessar os seguintes módulos:

- Monitoramento Atual
- Histórico de Monitoramento
- Assistente Inteligente RAG
- Arquitetura do Sistema
- Sobre o Projeto

### 10. Executar o projeto completo

Para demonstrar o MVP completo, mantenha três terminais abertos:

Terminal 1 — API:

```bash
uvicorn api.app:app --reload
```

Terminal 2 — Simulador ESP32:

```bash
python src/esp32_simulator.py
```

Terminal 3 — Dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

### 11. Código ESP32 com PlatformIO

O código preparado para ESP32 está localizado em:

```bash
esp32/
├── platformio.ini
└── src/
    └── main.cpp
```

Para uso em hardware físico, será necessário ajustar no código embarcado:

- Nome da rede Wi-Fi
- Senha da rede Wi-Fi
- Endereço IP da API FastAPI
- Sensores físicos utilizados


## 🗃 Histórico de lançamentos

* 1.0.0 - 09/06/2026
  * Deploy completo da solução final após testes operacionais e validação completa de todos os sistemas integrados.

---


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/SabrinaOtoni/TEMPLATE-FIAP-GRAD-ON-IA">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
