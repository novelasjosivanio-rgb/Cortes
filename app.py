import streamlit as st
import tempfile
from PIL import Image

# Correção de compatibilidade para o Pillow
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Gerador de Cortes 9:16", layout="wide")
st.title("✂️ Gerador de Cortes (9:16 + Fundo)")

# Barra lateral com os campos necessários
st.sidebar.header("1. Arquivos")
video_file = st.sidebar.file_uploader("Vídeo principal (MP4)", type=["mp4"])
bg_image_file = st.sidebar.file_uploader("Imagem de fundo da galeria", type=["jpg", "png", "jpeg"])

st.sidebar.header("2. Configuração de Cortes")
min_dur = st.sidebar.slider("Duração Mínima (s)", 10, 60, 20)
max_dur = st.sidebar.slider("Duração Máxima (s)", 20, 90, 50)

if video_file and st.button("🚀 Processar Cortes"):
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    
    with st.spinner("Processando vídeo e aplicando o fundo... Aguarde."):
        try:
            video = VideoFileClip(tfile.name)
            # Pega o primeiro trecho com base na duração escolhida
            subclip = video.subclip(0, min(max_dur, video.duration))
            subclip = subclip.resize(width=1080) # Formato do miolo
            
            if bg_image_file:
                bg_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                bg_tfile.write(bg_image_file.read())
                bg = ImageClip(bg_tfile.name).resize(newsize=(1080, 1920)) # Fundo 9:16
                bg = bg.set_duration(subclip.duration)
                final = CompositeVideoClip([bg, subclip.set_position("center")])
            else:
                final = subclip
                
            out_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            final.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("Corte gerado com sucesso!")
            st.video(out_path)
            with open(out_path, "rb") as f:
                st.download_button("📥 Baixar Corte Pronto", f, "corte_916.mp4", mime="video/mp4")
                
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
            
