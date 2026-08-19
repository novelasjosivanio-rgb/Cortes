import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

st.set_page_config(
    page_title="Gerador de Cortes Inteligentes",
    page_icon="✂️",
    layout="wide"
)

st.title("✂️ Gerador de Cortes Inteligentes para Vídeos")
st.markdown("Transforme vídeos longos em cortes dinâmicos com suporte a imagem de fundo.")

# --- BARRA LATERAL: CONFIGURAÇÕES E UPLOADS ---
st.sidebar.header("📁 1. Arquivos de Mídia")
video_file = st.sidebar.file_uploader("Envie o vídeo principal", type=["mp4", "mov", "avi"])
bg_image_file = st.sidebar.file_uploader("Envie a imagem de fundo (Opcional)", type=["png", "jpg", "jpeg"])

st.sidebar.header("⚙️ 2. Regras dos Cortes")
min_dur = st.sidebar.slider("Duração Mínima (segundos)", 20, 45, 20)
max_dur = st.sidebar.slider("Duração Máxima (segundos)", 46, 90, 60)

def generate_time_segments(duration, min_d, max_d):
    """Gera blocos de tempo baseados na duração total do vídeo."""
    segments = []
    current = 0.0
    while current < duration:
        # Define o tamanho do corte entre o mínimo e o máximo escolhido
        d = min(max_d, duration - current)
        if d < min_d and segments:
            # Se o pedaço final ficar muito pequeno, junta com o último anterior
            last_start, _ = segments[-1]
            segments[-1] = (last_start, duration)
            break
        segments.append((current, current + d))
        current += d
    return segments

def process_video_cuts(video_path, bg_path, segments):
    """Corta o vídeo usando o MoviePy e aplica a imagem de fundo se fornecida."""
    video = VideoFileClip(video_path)
    output_files = []
    
    for idx, (start, end) in enumerate(segments):
        subclip = video.subclip(start, end)
        
        # Se houver imagem de fundo, centraliza o vídeo
        if bg_path:
            bg_clip = ImageClip(bg_path).set_duration(subclip.duration)
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
        with st.spinner("Gerando cortes inteligentes... Aguarde."):
            try:
                clip_temp = VideoFileClip(video_path)
                video_duration = clip_temp.duration
                clip_temp.close()
                
                # Gera os segmentos respeitando os limites configurados
                segments = generate_time_segments(video_duration, min_dur, max_dur)
                
                if not segments:
                    st.warning("O vídeo é muito curto para os parâmetros selecionados.")
                else:
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
