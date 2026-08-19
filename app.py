import streamlit as st
import tempfile
import os

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# IMPORTAÇÃO CORRETA DO MOVIEPY
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Gerador de Cortes", layout="wide")
st.title("✂️ Gerador de Cortes (9:16)")

video_file = st.sidebar.file_uploader("Vídeo principal", type=["mp4"])
bg_image_file = st.sidebar.file_uploader("Imagem de fundo", type=["jpg", "png"])
min_dur = st.sidebar.slider("Duração Mínima (s)", 20, 90, 20)
max_dur = st.sidebar.slider("Duração Máxima (s)", 20, 90, 60)

if video_file and st.button("🚀 Processar"):
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    
    with st.spinner("Processando..."):
        try:
            video = VideoFileClip(tfile.name)
            subclip = video.subclip(0, min(max_dur, video.duration))
            subclip = subclip.resize(width=1080)
            
            if bg_image_file:
                bg_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                bg_tfile.write(bg_image_file.read())
                bg = ImageClip(bg_tfile.name).resize(newsize=(1080, 1920))
                bg = bg.set_duration(subclip.duration)
                final = CompositeVideoClip([bg, subclip.set_position("center")])
            else:
                final = subclip
                
            out_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            final.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
            
            st.video(out_path)
            with open(out_path, "rb") as f:
                st.download_button("Baixar Corte", f, "corte.mp4")
                
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
            
