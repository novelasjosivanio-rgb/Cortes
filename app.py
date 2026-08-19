import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

st.set_page_config(
    page_title="Gerador de Cortes Inteligentes",
    page_icon="✂️",
    layout="wide"
)

st.title("✂️ Gerador de Cortes Inteligentes para Vídeos")
st.markdown("Transforme vídeos longos em cortes dinâmicos, respeitando as pausas da fala e com suporte a imagem de fundo.")

# --- BARRA LATERAL: CONFIGURAÇÕES E UPLOADS ---
st.sidebar.header("📁 1. Arquivos de Mídia")
video_file = st.sidebar.file_uploader("Envie o vídeo principal", type=["mp4", "mov", "avi"])
bg_image_file = st.sidebar.file_uploader("Envie a imagem de fundo (Opcional)", type=["png", "jpg", "jpeg"])

st.sidebar.header("⚙️ 2. Regras dos Cortes")
min_dur = st.sidebar.slider("Duração Mínima (segundos)", 20, 45, 20)
max_dur = st.sidebar.slider("Duração Máxima (segundos)", 46, 90, 60)

def detect_smart_segments(audio_path, min_duration_sec, max_duration_sec):
    """Analisa o áudio para encontrar blocos de fala válidos entre min e max segundos."""
    audio = AudioSegment.from_file(audio_path)
    
    # Detecta trechos com som (fala) - silêncio abaixo de -40dB por mais de 500ms
    # Retorna lista de tuplas em milissegundos [(start, end), ...]
    nonsilent_ranges = detect_nonsilent(
        audio, 
        min_silence_len=500, 
        silence_thresh=audio.dBFS-14, 
        seek_step=100
    )
    
    segments = []
    current_start = None
    current_duration = 0
    
    for start_ms, end_ms in nonsilent_ranges:
        duration_ms = end_ms - (current_start if current_start is not None else start_ms)
        duration_sec = duration_ms / 1000.0
        
        if current_start is None:
            current_start = start_ms
            
        if duration_sec >= min_duration_sec:
            # Se atingiu o tamanho ideal, fecha o bloco
            end_time = min(end_ms, current_start + (max_duration_sec * 1000))
            segments.append((current_start / 1000.0, end_time / 1000.0))
            current_start = None # Reseta para o próximo bloco
        elif duration_sec > (max_duration_sec * 1000):
            # Força corte se passar do limite máximo
            segments.append((current_start / 1000.0, (current_start + max_duration_sec * 1000) / 1000.0))
            current_start = None
            
    return segments

def process_video_cuts(video_path, bg_path, segments):
    """Corta o vídeo usando o MoviePy e aplica a imagem de fundo se fornecida."""
    video = VideoFileClip(video_path)
    output_files = []
    
    for idx, (start, end) in enumerate(segments):
        # Garante limites do vídeo
        if start >= video.duration:
            continue
        end = min(end, video.duration)
        
        subclip = video.subclip(start, end)
        
        # Se houver imagem de fundo, redimensiona o vídeo e centraliza sobre a imagem
        if bg_path:
            bg_clip = ImageClip(bg_path).set_duration(subclip.duration)
            # Redimensiona o vídeo original para caber na tela mantendo proporção (ex: formato vertical/shorts)
            subclip = subclip.resize(width=int(bg_clip.w * 0.8))
            subclip = subclip.set_position("center")
            
            final_clip = CompositeVideoClip([bg_clip, subclip])
        else:
            final_clip = subclip
            
        out_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        final_clip.write_videofile(
            out_filename, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast", 
            logger=None
        )
        output_files.append(out_filename)
        
    return output_files

# --- PROCESSAMENTO PRINCIPAL ---
if video_file is not None:
    # Salva arquivos temporariamente
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    video_path = tfile.name

    bg_path = None
    if bg_image_file is not None:
        bg_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        bg_tfile.write(bg_image_file.read())
        bg_path = bg_tfile.name

    st.success("Vídeo carregado e pronto para análise!")

    if st.button("🚀 Processar Cortes Inteligentes"):
        with st.spinner("Analisando áudio, evitando pausas ruins e gerando cortes... Aguarde."):
            try:
                # Extrai o áudio para análise de silêncio
                temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
                VideoFileClip(video_path).audio.write_audiofile(temp_audio, logger=None)
                
                # Gera os segmentos baseados nas regras de fala (entre min_dur e max_dur)
                segments = detect_smart_segments(temp_audio, min_dur, max_dur)
                
                if not segments:
                    st.warning("Não foi possível encontrar blocos de fala ideais com os parâmetros atuais. Tente ajustar a duração mínima.")
                else:
                    # Cria os arquivos de vídeo reais
                    generated_clips = process_video_cuts(video_path, bg_path, segments)
                    st.session_state['clips'] = generated_clips
                    st.success(f"Sucesso! {len(generated_clips)} cortes gerados.")
            except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {e}")

# --- TELA DE DEMONSTRAÇÃO E DOWNLOADS ---
if 'clips' in st.session_state and st.session_state['clips']:
    st.markdown("---")
    st.header("📺 Tela de Demonstração e Downloads dos Cortes")
    st.markdown("Assista aos cortes gerados abaixo e faça o download dos seus favoritos:")

    for idx, clip_path in enumerate(st.session_state['clips']):
        with st.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"Corte Inteligente #{idx + 1}")
                st.video(clip_path)
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                with open(clip_path, "rb") as file:
                    st.download_button(
                        label=f"📥 Baixar Corte #{idx + 1}",
                        data=file,
                        file_name=f"corte_{idx + 1}.mp4",
                        mime="video/mp4",
                        key=f"dl_btn_{idx}"
                    )
            st.markdown("---")
