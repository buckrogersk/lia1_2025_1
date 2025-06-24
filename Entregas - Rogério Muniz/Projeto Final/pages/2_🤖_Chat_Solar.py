# Conteúdo completo e corrigido para o arquivo: pages/2_🤖_Chat_Solar.py

import streamlit as st
from llama_cpp import Llama
import os

# ---------- CONFIGURAÇÃO DA PÁGINA ----------
st.set_page_config(page_title="Chat Solar", page_icon="🤖", layout="centered")
st.title("🤖 Chat Solar")
st.info("Tire suas dúvidas sobre energia solar com nosso assistente virtual!")

# ---------- FUNÇÃO DE CARREGAMENTO DO MODELO ----------
@st.cache_resource
def carregar_modelo_ia():
    nome_do_arquivo_modelo = "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    if os.path.exists(nome_do_arquivo_modelo):
        try:
            llm = Llama(
                model_path=nome_do_arquivo_modelo,
                n_ctx=4096,
                n_gpu_layers=0,
                n_batch=256,
                verbose=False
            )
            return llm
        except Exception as e:
            st.error(f"❌ Erro ao carregar o modelo: {e}")
            return None
    else:
        st.error(f"❌ Arquivo do modelo '{nome_do_arquivo_modelo}' NÃO ENCONTRADO.")
        return None

llm = carregar_modelo_ia()

# ---------- LÓGICA DO CHATBOT COM CONTEXTO E CONHECIMENTO ESPECIALIZADO ----------

# 1. INICIALIZAÇÃO INTELIGENTE DO CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

     # Verifica se uma proposta foi gerada para iniciar com a mensagem proativa
    if st.session_state.get("proposta_gerada", False):
        resultados = st.session_state.resultados
        nome_cliente = resultados.get('nome_cliente', 'usuário')
        payback_anos = resultados.get('payback_anos', 'N/A')

        # Mensagem proativa e personalizada
        mensagem_proativa = (
            f"Olá, {nome_cliente}! Bem-vindo(a) ao nosso chat. "
            f"Vi que você acabou de gerar uma simulação para seu projeto em {resultados.get('cidade_cliente', '')} "
            f"e o resultado do payback foi de {payback_anos} anos, o que é um ótimo indicador! "
            f"Você tem alguma dúvida específica sobre esses resultados ou sobre energia solar em geral?"
        )
        st.session_state.messages.append({"role": "assistant", "content": mensagem_proativa})
    else:
        # Mensagem padrão se o usuário veio direto para o chat
        st.session_state.messages.append({"role": "assistant", "content": "Olá! Sou seu assistente solar. Como posso ajudar com suas dúvidas sobre energia fotovoltaica no Brasil?"})
        
# --- Base de Conhecimento Injetada ---
informacao_lei_14300 = """
- **Custo de Disponibilidade:** Todo consumidor deve pagar uma taxa mínima para estar conectado à rede, mesmo que não consuma nada. Esse valor varia, mas cobre custos de infraestrutura.
- **Tarifação do Fio B (Lei 14.300):** Para novas conexões (após jan/2023), a energia que você injeta na rede não compensa 100% da energia que você consome. Uma parte dela é usada para pagar pelo uso da infraestrutura da rede (o "Fio B"). Isso significa que, na prática, sua conta de luz não será zerada, mas sim drasticamente reduzida. Você ainda pagará uma pequena quantia referente a essa tarifação e ao custo de disponibilidade.
"""
concessionarias = {
    "GO": "Equatorial Goiás", "SP": "Enel SP / CPFL / Elektro", "RJ": "Light / Enel RJ", "MG": "CEMIG",
    "PR": "Copel", "SC": "CELESC", "RS": "CEEE / RGE", "DF": "CEB", "MT": "Energisa", "MS": "Energisa",
    # Adicione outros estados e concessionárias conforme necessário
}

# 1. CONSTRUÇÃO DO PROMPT DO SISTEMA
prompt_sistema_base = (
    "Você é um assistente virtual chamado 'Chat Solar', especialista em energia solar fotovoltaica no Brasil. "
    "Suas respostas devem ser claras, objetivas e amigáveis. "
    "Responda apenas a perguntas relacionadas a energia solar. "
    "Se o usuário perguntar sobre outro assunto, recuse educadamente e diga que seu conhecimento é focado em energia solar."
    "As respostas devem ser verdadeiras, não invente informações e nem dados, caso o usuário peça algum dado que não saiba, diga ao usuário entrar em contato com um dos nossos especialistas."
    "A proposta não é totalmente certa, por isso enfatize sempre que os valores são estimativas e podem variar, recomende o cliente entrar em contato com um dos nossos especialistas. "
    "Lembre-se de que você esta falando como um vendedor, sua missão é ajudar o usuário a entender melhor a energia solar e incentivá-lo a entrar em contato com um especialista para obter uma proposta personalizada."
)

prompt_sistema_com_conhecimento = prompt_sistema_base + "\n\n[INFORMAÇÕES TÉCNICAS E LEGAIS IMPORTANTES PARA USAR NAS RESPOSTAS]\n" + informacao_lei_14300

if st.session_state.get("proposta_gerada", False):
    resultados = st.session_state.resultados
    cidade_estado = resultados.get('cidade_cliente', '')

    # Extrai a sigla do estado (ex: 'Goiânia - GO' -> 'GO')
    sigla_estado = ""
    if " - " in cidade_estado:
        sigla_estado = cidade_estado.split(" - ")[-1].upper()

    nome_concessionaria = concessionarias.get(sigla_estado, "a concessionária local")
    
    contexto_do_projeto = (
        "\n\n[INSTRUÇÃO ADICIONAL]\n"
        "O usuário já realizou uma simulação de projeto. Use os dados do contexto abaixo para responder a perguntas sobre 'meu projeto', 'minha proposta', etc. "
        "Não é necessário apresentar os dados novamente, a menos que o usuário peça especificamente."
        "\n\n[CONTEXTO DO PROJETO DO USUÁRIO]\n"
        f"- Nome do Cliente: {resultados.get('nome_cliente', 'N/A')}\n"
        f"- Cidade: {resultados.get('cidade_cliente', 'N/A')}\n"
        f"- Potência do Sistema: {resultados.get('potencia_kWp', 'N/A')} kWp\n"
        f"- Custo Estimado: {resultados.get('preco_formatado', 'N/A')}\n"
        f"- Economia Mensal Estimada: {resultados.get('economia_formatada', 'N/A')}\n"
        f"- Retorno do Investimento: {resultados.get('payback_anos', 'N/A')} anos"
    )
    prompt_final_sistema = prompt_sistema_com_conhecimento + contexto_do_projeto
else:
    prompt_final_sistema = prompt_sistema_com_conhecimento

# 2. LÓGICA DO CHAT (Resto do código)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu assistente solar. Como posso ajudar com suas dúvidas sobre energia fotovoltaica no Brasil?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt_usuario := st.chat_input("Qual sua dúvida?"):
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Consultando base de conhecimento..."):
            conversa_formatada = "".join([f"<|start_header_id|>{msg['role']}<|end_header_id|>\n\n{msg['content']}<|eot_id|>" for msg in st.session_state.messages])
            prompt_final_para_ia = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{prompt_final_sistema}<|eot_id|>"
                f"{conversa_formatada}"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )

            if llm:
                try:
                    output = llm(prompt_final_para_ia, max_tokens=512, temperature=0.4, stop=["<|eot_id|>", "<|end_of_text|>", "<|user|>"], echo=False)
                    resposta_ia = output["choices"][0]["text"].strip()
                    message_placeholder.markdown(resposta_ia)
                    st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar a resposta: {e}")
            else:
                message_placeholder.markdown("Desculpe, meu cérebro de IA não está funcionando no momento.")