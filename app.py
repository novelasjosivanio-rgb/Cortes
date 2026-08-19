import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="IA de Cortes Inteligentes", layout="wide")
st.title("🤖 IA Geradora de Cortes (100% Gratuita)")

# Configuração da Chave da API do Gemini (Gratuita)
# O usuário pode colocar a chave diretamente na barra lateral
st.sidebar.header("Configuração da IA")
api_key = st.sidebar.text_input("Cole sua Chave da API do Gemini", type="password")

st.markdown("""
Esta ferramenta utiliza a Inteligência Artificial do Google para analisar vídeos e encontrar os momentos mais impactantes para cortes verticais (9:16).
""")

video_file = st.sidebar.file_uploader("Envie seu vídeo", type=["mp4", "mov", "avi"])

if video_file and api_key:
    genai.configure(api_key=api_key)
    
    # Salvar temporariamente o vídeo enviado
    video_path = "temp_video.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.read())
        
    if st.button("✨ Analisar Vídeo com IA"):
        with st.spinner("A IA está assistindo e analisando o seu vídeo... Isso pode levar alguns minutos."):
            try:
                st.info("Fazendo upload do vídeo para a nuvem da IA...")
                uploaded_file = genai.upload_file(video_path)
                
                # Aguardar o arquivo ficar pronto na API
                while uploaded_file.state.name == "PROCESSING":
                    import time
                    time.sleep(5)
                    uploaded_file = genai.get_file(uploaded_file.name)
                
                st.info("Gerando os melhores cortes com IA...")
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = (
                    "Analise este vídeo e identifique os 3 melhores trechos (momentos mais interessantes, "
                    "engraçados ou de maior impacto) para transformar em cortes verticais curtos (Reels/TikTok). "
                    "Para cada corte, forneça o tempo de início e o tempo de término exatos em segundos, "
                    "junto com uma justificativa curta."
                )
                
                response = model.generate_content([uploaded_file, prompt])
                
                st.success("Análise concluída pela IA!")
                st.markdown("### Sugestões de Cortes da IA:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Ocorreu um erro na IA: {e}")
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
elif not api_key:
    st.warning("⚠️ Por favor, insira sua Chave da API do Gemini na barra lateral para continuar.")
    st.markdown("""
    **Como conseguir uma chave gratuita do Gemini (Google AI Studio):**
    1. Acesse [aistudio.google.com](https://aistudio.google.com/) (gratuito).
    2. Faça login com sua conta Google.
    3. Clique em **"Get API key"** e crie sua chave gratuitamente.
    4. Cole a chave no campo ao lado esquerdo.
    """)
                    
