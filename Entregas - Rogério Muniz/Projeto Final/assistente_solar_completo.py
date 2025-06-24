import streamlit as st
import pytesseract
import pdfplumber
from PIL import Image
import re
import requests
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import shapely.geometry
from shapely.ops import transform
import pyproj
import os
from llama_cpp import Llama
import pandas as pd

# ---------- CONFIGURAÇÃO DA PÁGINA ----------
st.set_page_config(page_title="Simulador Solar", page_icon="☀️", layout="wide", initial_sidebar_state="expanded")

# --- LAYOUT: Título e subtítulo para uma aparência mais profissional ---
st.title("☀️ Simulador Solar Inteligente")
st.markdown("Uma ferramenta completa para simular seu sistema de energia solar, da conta de luz à proposta final.")
st.divider()

# ---------- FUNÇÃO DE CARREGAMENTO DO MODELO (versão limpa) ----------
@st.cache_resource
def carregar_modelo_ia():
    nome_do_arquivo_modelo = "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    if os.path.exists(nome_do_arquivo_modelo):
        try:
            llm = Llama(model_path=nome_do_arquivo_modelo, n_ctx=2048, n_gpu_layers=0, n_batch=256, verbose=False)
            print("Modelo de IA carregado com sucesso na memória.") # Mensagem para o console
            return llm
        except Exception as e:
            st.error(f"❌ Erro crítico ao carregar o modelo de IA: {e}")
            return None
    else:
        st.error(f"❌ Arquivo do modelo '{nome_do_arquivo_modelo}' não encontrado. As funcionalidades de IA estão desativadas.")
        return None

llm = carregar_modelo_ia()

# ---------- INICIALIZAÇÃO DO ESTADO DA SESSÃO ----------
if "proposta_gerada" not in st.session_state:
    st.session_state.proposta_gerada = False
    st.session_state.lat = None
    st.session_state.lng = None
    st.session_state.texto_conta = ""
    st.session_state.resultados = {}

# ---------- LÓGICA DE EXIBIÇÃO ----------

# Se uma proposta JÁ FOI GERADA, mostramos a interface de resultados com ABAS
if st.session_state.proposta_gerada:
    st.success("Simulação concluída!")
    resultados = st.session_state.resultados

    # --- LAYOUT: Resultados organizados em Abas ---
    tab_resumo, tab_proposta = st.tabs(["📊 Resumo da Simulação", "📄 Proposta Detalhada"])

    with tab_resumo:
        st.subheader("Visão Geral e Indicadores Financeiros")
        
        # As métricas numéricas que você queria manter
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="⚡ Potência do Sistema", value=f"{resultados['potencia_kWp']} kWp")
        with col2:
            st.metric(label="💰 Custo Estimado", value=resultados["preco_formatado"])
        with col3:
            st.metric(label="📉 Economia Mensal", value=resultados["economia_formatada"])
        with col4:
            st.metric(label="⏳ Payback Simples", value=f"{resultados['payback_anos']} anos")
        
        st.info(f"💡 Simulação baseada em um consumo de referência de {resultados.get('consumo_referencia', 'N/A')} kWh/mês.")
        
        st.divider() # Adiciona uma linha divisória

        # --- GRÁFICOS DE COMPARAÇÃO ADICIONADOS AQUI ---
        st.subheader("Análise Gráfica")
        
        # Recuperando os valores numéricos para os gráficos
        economia_valor = float(resultados["economia_formatada"].replace("R$ ", "").replace(".", "").replace(",", "."))
        custo_disponibilidade = 70.0 # Valor estimado para o custo mínimo/fio B
        
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.markdown("##### Custo Mensal da Conta de Energia")
            df_custo_mensal = pd.DataFrame({
                "Situação": ["Antes do Solar", "Depois do Solar"],
                "Custo (R$)": [economia_valor, custo_disponibilidade]
            })
            st.bar_chart(df_custo_mensal, x="Situação", y="Custo (R$)")

        with graf_col2:
            st.markdown("##### Economia Acumulada ao Longo do Tempo")
            anos = list(range(1, 11))
            economia_anual = economia_valor * 12
            df_economia_acumulada = pd.DataFrame({
                "Ano": anos,
                "Economia Acumulada (R$)": [economia_anual * ano for ano in anos]
            })
            st.line_chart(df_economia_acumulada, x="Ano", y="Economia Acumulada (R$)")
    
    with tab_proposta:
        st.subheader("Análise de Viabilidade")
        st.markdown(resultados.get("proposta_texto", "Nenhuma proposta gerada."))
        
        # O botão para o chat fica contextualmente dentro da aba da proposta
        if st.button("🤖 Tirar dúvidas sobre esta proposta com o Assistente"):
            st.switch_page("pages/2_🤖_Chat_Solar.py")

    st.divider()
    if st.button("Iniciar Nova Simulação"):
        keys_to_clear = ["proposta_gerada", "resultados", "lat", "lng", "texto_conta"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Se NENHUMA proposta foi gerada ainda, mostramos o formulário de entrada
else:
    # --- LAYOUT: Inputs em colunas dentro de um container ---
    with st.container(border=True):
        st.subheader("1️⃣ Passo 1: Seus Dados e Conta de Energia")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Seu nome completo")
        with col2:
            cidade = st.text_input("Sua cidade e estado (ex: Goiânia - GO)")
        
        if nome and cidade:
            uploaded_file = st.file_uploader("📄 Envie sua conta de energia (PDF ou imagem)", type=["pdf", "png", "jpg", "jpeg"])
            
            if uploaded_file:
                with st.spinner("Processando conta de energia..."):
                    tipo = uploaded_file.type
                    if tipo == "application/pdf":
                        with pdfplumber.open(uploaded_file) as pdf:
                            texto = "\n".join([p.extract_text() or "" for p in pdf.pages])
                    else:
                        imagem = Image.open(uploaded_file)
                        texto = pytesseract.image_to_string(imagem)
                    st.session_state.texto_conta = texto
                    
                    padrao_endereco = re.compile(r"(RUA\s+[^\n,]{3,100}|AVENIDA\s+[^\n,]{3,100}|Rua\s+[^\n,]{3,100}|Avenida\s+[^\n,]{3,100})", re.IGNORECASE)
                    endereco_padrao = padrao_endereco.findall(texto)
                    rua = endereco_padrao[0].strip() if endereco_padrao else ""
                    cep = re.findall(r'\d{5}-?\d{3}', texto)
                    cep_str = cep[0] if cep else ""
                    endereco = f"{rua}, {cidade}, {cep_str}".strip(", ")

                api_key = st.secrets.get("opencage_api_key", "")
                if not api_key:
                    api_key = st.text_input("🔑 Chave da API OpenCage:", type="password")

                if api_key and st.button("📍 Localizar Endereço e Continuar para o Mapa"):
                    with st.spinner("Localizando endereço na API..."):
                        resp = requests.get(f"https://api.opencagedata.com/geocode/v1/json?q={endereco}&key={api_key}&language=pt&countrycode=br")
                        dados = resp.json()
                        if dados and dados['results']:
                            coords = dados['results'][0]['geometry']
                            st.session_state.lat = coords['lat']
                            st.session_state.lng = coords['lng']
                            st.rerun()
                        else:
                            st.error("Endereço não localizado pela API. Verifique os dados.")
    
    st.divider()

    if st.session_state.lat and st.session_state.lng:
        with st.container(border=True):
            st.subheader("2️⃣ Passo 2: Marque a Área do Telhado")
            st.info("Use a ferramenta de polígono no menu esquerdo do mapa para desenhar sobre a área útil do seu telhado. Dê zoom para máxima precisão.")
            
            # --- MUDANÇA PRINCIPAL: O MAPA É CRIADO JÁ COM A ÚNICA CAMADA DESEJADA ---
            # Não há outras camadas ou LayerControl, eliminando qualquer conflito.
            mapa = folium.Map(
                location=[st.session_state.lat, st.session_state.lng],
                zoom_start=19,
                max_zoom=22,
                # Força o uso da camada Google Híbrido como a única base do mapa
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr='Google'
            )
            
            # A ferramenta de desenho é adicionada diretamente ao mapa base
            Draw(export=True).add_to(mapa)
            
            # O st_folium exibe o mapa simplificado
            resultado = st_folium(mapa, key="mapa_solar", width=1600, height=600)

            if resultado and resultado.get("all_drawings") and len(resultado["all_drawings"]) > 0:
                with st.spinner("Calculando e gerando proposta..."):
                    ultimo_desenho = resultado["all_drawings"][-1]
                    forma = ultimo_desenho["geometry"]
                    coords = forma["coordinates"][0]
                    pontos = [(lng, lat) for lng, lat in coords]
                    project = pyproj.Transformer.from_crs(pyproj.CRS("EPSG:4326"), pyproj.CRS("EPSG:3857"), always_xy=True).transform
                    area_m2 = transform(project, shapely.geometry.Polygon(pontos)).area
                    potencia = area_m2 * 0.170
                    consumo_match = re.search(r'consumo.*mês[^0-9]*(\d{2,}[\.,]?\d*)', st.session_state.texto_conta, re.IGNORECASE)
                    consumo = float(consumo_match.group(1).replace(',', '.')) if consumo_match else 400.0
                    tarifa_energia = 0.95
                    economia = consumo * tarifa_energia
                    preco = potencia * 4500
                    payback = preco / (economia * 12) if economia > 0 else float('inf')

                    proposta_texto_final = f"""
                    Olá, **{nome}**,
                    Agradecemos o seu interesse em explorar as vantagens da energia solar para sua propriedade em **{cidade}**. Com base nos dados fornecidos, realizamos uma simulação detalhada do potencial do seu projeto.
                    ### **Resumo da Simulação**
                    A análise indica um sistema com as seguintes características:
                    - **Potência Estimada:** **{potencia:.2f} kWp**
                    - **Investimento Estimado:** **R$ {preco:,.2f}**
                    - **Economia Mensal na Conta de Energia:** **~ R$ {economia:,.2f}**
                    - **Retorno do Investimento (Payback Simples):** **~ {payback:.1f} anos**
                    ### **Vantagens do Seu Projeto**
                    1.  **Redução de Custos:** A economia mensal é o benefício mais imediato, protegendo você contra futuros aumentos na tarifa de energia.
                    2.  **Sustentabilidade:** Você gerará sua própria energia limpa e renovável.
                    3.  **Valorização do Imóvel:** Propriedades com sistemas fotovoltaicos são mais valorizadas no mercado.
                    ### **Próximos Passos**
                    Esta simulação é uma excelente estimativa inicial. O próximo passo recomendado é **contatar um fornecedor qualificado** para agendar uma visita técnica, onde um projeto definitivo e um orçamento preciso serão elaborados.
                    """

                    st.session_state.resultados = {
                        "nome_cliente": nome, "cidade_cliente": cidade, "potencia_kWp": f"{potencia:.2f}",
                        "preco_formatado": f"R$ {preco:,.2f}", "economia_formatada": f"R$ {economia:,.2f}",
                        "payback_anos": f"{payback:.1f}", "consumo_referencia": f"{consumo:.0f}",
                        "proposta_texto": proposta_texto_final
                    }
                    st.session_state.proposta_gerada = True
                    st.rerun()