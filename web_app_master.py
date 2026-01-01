import streamlit as st
import ollama
import os
import glob
import asyncio
import edge_tts
import yt_dlp
import whisper
import warnings

# Ignorar advertencias de librerías
warnings.filterwarnings("ignore")

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Quipu AI", page_icon="🧶", layout="wide")

MODELO_LLM = "llama3.2"
MODELO_WHISPER = "small"
CARPETA_CONOCIMIENTO = "base_conocimiento"
CARPETA_TEMP = "temp_uploads"

os.makedirs(CARPETA_CONOCIMIENTO, exist_ok=True)
os.makedirs(CARPETA_TEMP, exist_ok=True)

VOCES_DISPONIBLES = {
    "🇨🇴 Colombia (Gonzalo - Hombre)": "es-CO-GonzaloNeural",
    "🇨🇴 Colombia (Salomé - Mujer)": "es-CO-SalomeNeural",
    "🇵🇪 Perú (Camila - Mujer)": "es-PE-CamilaNeural",
    "🇵🇪 Perú (Alex - Hombre)": "es-PE-AlexNeural",
    "🇲🇽 México (Dalia - Mujer)": "es-MX-DaliaNeural",
    "🇪🇸 España (Alvaro - Hombre)": "es-ES-AlvaroNeural"
}

# --- FUNCIONES BACKEND ---

@st.cache_resource
def cargar_whisper():
    return whisper.load_model(MODELO_WHISPER)

def procesar_audio_a_texto(ruta_audio):
    model = cargar_whisper()
    result = model.transcribe(ruta_audio, language="es")
    nombre_base = os.path.basename(ruta_audio).split('.')[0]
    ruta_txt = os.path.join(CARPETA_CONOCIMIENTO, f"{nombre_base}.txt")
    
    contenido = f"--- METADATA: {nombre_base} ---\n{result['text']}\n"
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta_txt

def descargar_youtube(url):
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(CARPETA_TEMP, '%(title)s.%(ext)s'),
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True, 'no_warnings': True
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

async def generar_audio_async(texto, voz_id):
    output_file = "respuesta_temp.mp3"
    comunicator = edge_tts.Communicate(texto, voz_id)
    await comunicator.save(output_file)
    return output_file

# --- NUEVA LÓGICA DE FILTRADO ---
def obtener_archivos_disponibles():
    """Devuelve la lista limpia de nombres de archivos .txt"""
    archivos = glob.glob(os.path.join(CARPETA_CONOCIMIENTO, "*.txt"))
    return [os.path.basename(f) for f in archivos]

def cargar_contexto_selectivo(nombres_seleccionados):
    """Carga SOLO los archivos que el usuario eligió"""
    texto_total = ""
    if not nombres_seleccionados:
        return ""
        
    for nombre in nombres_seleccionados:
        ruta_completa = os.path.join(CARPETA_CONOCIMIENTO, nombre)
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                texto_total += f"\n--- INICIO DOCUMENTO: {nombre} ---\n"
                texto_total += f.read() + "\n--- FIN DOCUMENTO ---\n"
        except: pass
    return texto_total

# --- INTERFAZ GRÁFICA ---

# 1. SIDEBAR (CONFIGURACIÓN Y FILTROS)
with st.sidebar:
    st.title("🎛️ Centro de Control")
    
    # Selector de Voz
    st.markdown("### 🗣️ Voz de la IA")
    voz_seleccionada_nombre = st.selectbox("Acento:", list(VOCES_DISPONIBLES.keys()))
    voz_id = VOCES_DISPONIBLES[voz_seleccionada_nombre]
    activar_tts = st.toggle("Activar Audio", value=True)
    
    st.divider()
    
    # --- NUEVO: CHECKLIST DE ARCHIVOS ---
    st.markdown("### 🧠 Memoria Selectiva")
    archivos_en_disco = obtener_archivos_disponibles()
    
    if archivos_en_disco:
        # Multiselect actúa como checklist avanzado
        seleccion_archivos = st.multiselect(
            "Selecciona qué audios usar:",
            options=archivos_en_disco,
            default=archivos_en_disco, # Por defecto selecciona todos
            placeholder="Elige tus fuentes..."
        )
        st.caption(f"Usando {len(seleccion_archivos)} de {len(archivos_en_disco)} archivos.")
    else:
        st.warning("No hay conocimientos cargados.")
        seleccion_archivos = []

    st.divider()
    if st.button("🗑️ Borrar Chat"):
        st.session_state.messages = []
        st.rerun()

# 2. PESTAÑAS PRINCIPALES
tab_chat, tab_yt, tab_upload = st.tabs(["💬 Chat", "📺 YouTube", "📁 Archivos"])

# --- PESTAÑA CHAT ---
with tab_chat:
    st.header("💬 Quipu AI: Interfaz de Consulta")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu pregunta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # CARGAR CONTEXTO FILTRADO
            contexto_rag = cargar_contexto_selectivo(seleccion_archivos)
            
            if not contexto_rag and len(archivos_en_disco) > 0:
                full_response = "⚠️ No has seleccionado ningún archivo en la barra lateral. Por favor marca al menos uno para que pueda responderte."
                message_placeholder.markdown(full_response)
            else:
                prompt_final = f"""
                Actúa como 'Quipu', un asistente experto en sistemas.
                Responde basándote EXCLUSIVAMENTE en el siguiente contexto seleccionado por el usuario.
                
                CONTEXTO SELECCIONADO:
                {contexto_rag}
                
                PREGUNTA: {prompt}
                """

                stream = ollama.chat(model=MODELO_LLM, messages=[{'role': 'user', 'content': prompt_final}], stream=True)
                
                for chunk in stream:
                    full_response += chunk['message']['content']
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # AUDIO
                if activar_tts:
                    try:
                        archivo_audio = asyncio.run(generar_audio_async(full_response, voz_id))
                        st.audio(archivo_audio, format="audio/mp3", autoplay=True)
                    except Exception as e:
                        st.error(f"Error de voz: {e}")

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- PESTAÑA YOUTUBE ---
with tab_yt:
    st.header("📺 Ingesta desde YouTube")
    col1, col2 = st.columns([3, 1])
    with col1:
        url_yt = st.text_input("URL del video:")
    with col2:
        btn_yt = st.button("Procesar Video", use_container_width=True)
        
    if btn_yt and url_yt:
        with st.status("Descargando y Transcribiendo...", expanded=True):
            try:
                st.write("📥 Descargando audio...")
                ruta_mp3 = descargar_youtube(url_yt)
                st.write("🤖 Transcribiendo (Whisper)...")
                ruta_txt = procesar_audio_a_texto(ruta_mp3)
                st.success(f"¡Agregado!: {os.path.basename(ruta_txt)}")
                st.rerun() # Recargar para que aparezca en la lista
            except Exception as e:
                st.error(f"Error: {e}")

# --- PESTAÑA UPLOAD ---
with tab_upload:
    st.header("📁 Ingesta Local")
    uploaded_file = st.file_uploader("Arrastra tus audios aquí", type=['mp3', 'wav', 'm4a'])
    
    if uploaded_file and st.button("Procesar Archivo Subido"):
        with st.status("Procesando...", expanded=True):
            ruta_temp = os.path.join(CARPETA_TEMP, uploaded_file.name)
            with open(ruta_temp, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.write("🤖 Transcribiendo...")
            ruta_txt = procesar_audio_a_texto(ruta_temp)
            st.success("¡Indexado correctamente!")
            st.rerun()