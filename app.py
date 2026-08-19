import streamlit as st
import tempfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
# Linha de segurança para o erro do ANTIALIAS:
Image.ANTIALIAS = Image.Resampling.LANCZOS

st.set_page_config(page_title="Cortes Inteligentes", layout="wide")
# ... (resto do seu código continua igual)

import streamlit as st
import tempfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Cortes Inteligentes", layout="wide")

st.title("✂️ Gerador de Cortes (9:16)")

video_file = st.sidebar.file_uploader("Vídeo principal", type=["mp4"])
bg_image_file = st.sidebar.file_uploader("Imagem de fundo", type=["jpg", "png"])
min_dur = st.sidebar.slider("Duração Mínima (s)", 20, 90, 20)
max_dur = st.sidebar.slider("Duração Máxima (s)", 20, 90, 60)

def process_video_cuts(video_path, bg_path, min_d, max_d):
    video = VideoFileClip(video_path)
    output_files = []
    duration = video.duration
    
    # Criar segmentos de tempo
    segments = []
    current = 0.0
    while current < duration:
        d = min(max_d, duration - current)
        if d < min_d and segments:
            segments[-1] = (segments[-1][0], duration)
            break
        segments.append((current, current + d))
        current += d

    for start, end in segments:
        # Pega o subclip
        subclip = video.subclip(start, end)
        
        # Redimensiona para largura de 1080px
        # Usamos apply_to_mask=True para evitar erros com o frame
        subclip = subclip.resize(width=1080)
        
        # Fundo 9:16
        if bg_path:
            bg = ImageClip(bg_path).resize(newsize=(1080, 1920))
            bg = bg.set_duration(subclip.duration)
            final_clip = CompositeVideoClip([bg, subclip.set_position("center")])
        else:
            final_clip = subclip
        
        out_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        final_clip.write_videofile(out_filename, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None)
        output_files.append(out_filename)
        
    return output_files

if video_file and st.button("🚀 Processar"):
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    bg_path = None
    if bg_image_file:
        bg_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        bg_tfile.write(bg_image_file.read())
        bg_path = bg_tfile.name
        
    with st.spinner("Processando..."):
        try:
            clips = process_video_cuts(tfile.name, bg_path, min_dur, max_dur)
            st.session_state['clips'] = clips
            st.success("Cortes prontos!")
        except Exception as e:
            st.error(f"Erro: {e}")

if 'clips' in st.session_state:
    for idx, c in enumerate(st.session_state['clips']):
        st.video(c)
        with open(c, "rb") as f:
            st.download_button(f"Baixar Corte {idx+1}", f, f"corte_{idx+1}.mp4")
                          
