import streamlit as st
import tempfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(page_title="Cortes 9:16", layout="wide")

st.title("✂️ Cortes Inteligentes (9:16 + 4:3)")

# Configurações na barra lateral
video_file = st.sidebar.file_uploader("Vídeo principal", type=["mp4"])
bg_image_file = st.sidebar.file_uploader("Imagem de fundo", type=["jpg", "png"])
min_dur = st.sidebar.slider("Duração Mínima (s)", 20, 90, 20)
max_dur = st.sidebar.slider("Duração Máxima (s)", 20, 90, 60)

def generate_time_segments(duration, min_d, max_d):
    segments = []
    current = 0.0
    while current < duration:
        d = min(max_d, duration - current)
        if d < min_d and segments:
            last_start, _ = segments[-1]
            segments[-1] = (last_start, duration)
            break
        segments.append((current, current + d))
        current += d
    return segments

def process_video_cuts(video_path, bg_path, segments):
    video = VideoFileClip(video_path)
    output_files = []
    
    # Define dimensões para 9:16 (Ex: 1080x1920)
    target_w, target_h = 1080, 1920
    
    for start, end in segments:
        subclip = video.subclip(start, end)
        
        # 1. Redimensionar vídeo para caber 4:3 na largura 1080
        # 1080 / 4 * 3 = 810 de altura
        subclip = subclip.resize(width=1080)
        
        # 2. Criar Fundo 9:16
        if bg_path:
            bg = ImageClip(bg_path).resize(newsize=(target_w, target_h))
            bg = bg.set_duration(subclip.duration)
        else:
            bg = None # Ou pode criar um fundo preto aqui

        # 3. Compor: Fundo + Vídeo centralizado
        clips = [bg] if bg else []
        subclip = subclip.set_position("center")
        clips.append(subclip)
        
        final_clip = CompositeVideoClip(clips, size=(target_w, target_h))
        
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
        segments = generate_time_segments(VideoFileClip(tfile.name).duration, min_dur, max_dur)
        clips = process_video_cuts(tfile.name, bg_path, segments)
        st.session_state['clips'] = clips
        st.success("Cortes prontos!")

if 'clips' in st.session_state:
    for idx, c in enumerate(st.session_state['clips']):
        st.video(c)
        with open(c, "rb") as f:
            st.download_button(f"Baixar Corte {idx+1}", f, f"corte_{idx+1}.mp4")
            
