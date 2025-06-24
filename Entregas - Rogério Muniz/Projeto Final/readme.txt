#  Simulador Solar Inteligente

O Simulador Solar Inteligente é uma aplicação web completa e interativa, construída com Streamlit, que oferece uma análise preliminar completa para a instalação de um sistema de energia solar residencial. O fluxo de trabalho guia o usuário desde o upload de sua conta de energia até a geração de uma análise de viabilidade detalhada e uma conversa com um chatbot especialista para tirar dúvidas.

Este projeto demonstra a integração de múltiplas tecnologias, incluindo Processamento de Linguagem Natural (LLM), Reconhecimento Óptico de Caracteres (OCR), geoprocessamento e análise de dados para criar uma ferramenta de ponta a ponta.

---

##  Principais Funcionalidades

-   **Extração Automática de Dados:** Lê informações (endereço, consumo) diretamente de arquivos PDF ou imagens de contas de energia usando OCR (`Pytesseract`) e `PDFPlumber`.
-   **Geolocalização e Mapeamento Interativo:** Converte o endereço extraído em coordenadas geográficas e exibe um mapa de satélite de alta resolução (Google/Esri), onde o usuário pode desenhar a área exata do seu telhado.
-   **Cálculo Preciso de Potencial:** Com base na área desenhada, calcula a potência do sistema (kWp), o custo estimado da instalação, a economia mensal na conta de luz e o tempo de retorno do investimento (payback).
-   **Apresentação Profissional de Dados:** Exibe os resultados financeiros em um layout moderno com métricas e gráficos comparativos (Antes vs. Depois, Economia Acumulada).
-   **Arquitetura Multi-Página:** O aplicativo é organizado em duas páginas: um Simulador e um Chatbot, com um estado de sessão persistente que compartilha informações entre elas.
-   **Chatbot Especialista e Contextual:** Uma segunda página oferece um chatbot conversacional, alimentado por um LLM local, que tem acesso aos resultados da simulação do usuário e pode responder a perguntas específicas sobre o projeto ou dúvidas gerais sobre energia solar no Brasil.
-   **100% Local:** Todo o processamento de IA é feito localmente, sem depender de APIs externas pagas, utilizando a biblioteca `llama-cpp-python` para rodar modelos GGUF em CPU.

---

##  Tecnologias Utilizadas

-   **Aplicação Web:** Streamlit
-   **Processamento de Documentos:** Pytesseract, PDFPlumber, Pillow (PIL)
-   **Análise Geoespacial:** Folium, streamlit-folium, Shapely, PyProj
-   **Inteligência Artificial (LLM):** `llama-cpp-python`, Modelo Llama 3 8B / Phi-3 Mini (GGUF)
-   **Análise de Dados e Requisições:** Pandas, Requests, Regex (re)

---

##  Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar o projeto no seu computador Windows.

### 1. Pré-requisitos

Certifique-se de que você tem os seguintes softwares instalados:

-   **Python 3.9+:** [Download Python](https://www.python.org/downloads/)
-   **Git:** Essencial para o processo de instalação de algumas bibliotecas. [Download Git](https://git-scm.com/download/win)
-   **Microsoft C++ Build Tools:** Necessário para compilar a `llama-cpp-python`. Instale o "Visual Studio Installer" e marque a carga de trabalho "Desenvolvimento para desktop com C++".
-   **Tesseract-OCR:** O motor de OCR precisa ser instalado no sistema. [Download Tesseract para Windows](https://github.com/UB-Mannheim/tesseract/wiki) (Lembre-se de adicionar o caminho da instalação ao PATH do Windows).

### 2. Configuração do Projeto

1.  **Clone ou baixe este repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```


3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    *Se a instalação do `llama-cpp-python` falhar, use o comando que resolvemos juntos:*
    ```bash
    $env:CMAKE_ARGS="-DLLAMA_CUBLAS=OFF"
    pip install llama-cpp-python
    ```

### 3. Configuração dos Modelos e APIs

1.  **Baixe o Modelo LLM:** Faça o download do arquivo `.gguf` (ex: `Meta-Llama-3-8B-Instruct.Q4_K_M.gguf`) e coloque-o na pasta raiz do projeto.

2.  **Crie o Arquivo de Segredos:** Na pasta raiz, crie uma subpasta `.streamlit` e, dentro dela, um arquivo chamado `secrets.toml`. Adicione suas chaves de API:
    ```toml
    # Conteúdo para .streamlit/secrets.toml
    opencage_api_key = "SUA_CHAVE_API_OPENCAGE"
    maptiler_api_key = "SUA_CHAVE_API_MAPTILER"
    ```

### 4. Executando a Aplicação

Com tudo configurado, execute o seguinte comando no seu terminal:

```bash
streamlit run 1_☀️_Simulador_Solar.py