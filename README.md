# Local Audio RAG Assistant (Llama 3.2 + Whisper)

Un sistema de **Generación Aumentada por Recuperación (RAG)** ejecutado 100% en local. Este proyecto permite transcribir archivos de audio (reuniones, clases, podcasts) y conversar con ellos utilizando Inteligencia Artificial, garantizando **privacidad total** y cero coste de API.

> **Arquitectura:** Audio ➔ Whisper (ETL) ➔ Embeddings (LanceDB) ➔ Ollama (Llama 3.2)

---

## Requisitos Previos

Para ejecutar este proyecto necesitas tener instalado en tu sistema:

* **Python 3.10+**
* **[Ollama](https://ollama.com/):** Motor de inferencia local.
* **[FFmpeg](https://ffmpeg.org/):** Necesario para el procesamiento de audio.
* **[AnythingLLM Desktop](https://useanything.com/):** Interfaz para gestión de RAG y base de datos vectorial.

## Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/6Edgar9/local-audio-rag.git
cd local-audio-rag

```

2. **Crear entorno virtual (Opcional pero recomendado):**
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate

```

3. **Instalar dependencias:**
```bash
pip install openai-whisper ollama

```

## Guía de Uso

### FASE 1: Preparación del Entorno

1. **Iniciar el Motor (Ollama):**
Asegúrate de que el servidor está escuchando en el puerto por defecto.
```bash
ollama serve

```

2. **Descargar/Verificar Modelo:**
Usamos `llama3.2` (3B) por ser eficiente para CPU/GPU integrada.
```bash
ollama run llama3.2
# Para verificar que está listo:
ollama list

```

3. **Verificar FFmpeg:**
Fundamental para que Whisper funcione.
```bash
ffmpeg -version

```


### FASE 2: Extracción de Datos (ETL)

Puedes usar el comando directo de Whisper, pero se recomienda usar el script `transcribir_pro.py` incluido en este repo para procesar múltiples archivos y añadir **marcas de tiempo**.

**Opción A: Script Automatizado (Recomendado)**
Coloca tus archivos `.mp3` en la carpeta raíz y ejecuta:

```bash
py transcribir_pro.py

```

*Esto generará archivos `.txt` en la carpeta `/base_conocimiento` con timestamps.*

Una alternativa menos potente es:

```bash
py transcribir.py

```
*Se recomienda usar el primer script*

**Opción B: Comando Manual**

```bash
whisper "nombre_audio.mp3" --model small --language es --output_format txt --initial_prompt "Una conversación"

```

### FASE 3: Configuración de la Suite (AnythingLLM)

1. **Configuración del Proveedor (Setup Inicial):**
* Ve a **Settings** (tuerca) ➔ **AI Providers** ➔ **LLM**.
* **Provider:** Ollama.
* **URL:** `http://127.0.0.1:11434`.
* **Model:** `llama3.2:latest`.
* **Max Tokens:** 4096 (Recomendado para 16GB RAM).


2. **Base de Datos Vectorial:**
* Ve a **Vector Database** y selecciona **LanceDB** (Local).


3. **Ingesta de Datos ("Entrenamiento"):**
* Crea un nuevo **Workspace** (ej: `Proyecto_Inicial`).
* Sube los archivos `.txt` generados en la Fase 2.
* Haz clic en **"Move to Workspace"**.
* Haz clic en **"Save and Embed"**.
* *Espera a que finalice el proceso de vectorización.*

### FASE 4: Interacción (Chat)

Ahora puedes interrogar a tus audios.

**Ejemplos de Prompts:**

* *"Resume los puntos clave de la reunión basándote en el audio."*
* *"¿Qué dijo la Persona A sobre el presupuesto? Cita el minuto exacto."*
* *"Identifica conclusiones técnicas sobre la arquitectura del sistema."*

### Alternativa*

Para la ejecución del chat y Prompts sobre los .txt de audios también puedes ejecutar el script:

```bash
py chat_audio.py

```
*Te permite conversar con la IA sobre los archivos desde la terminal busca todos los archivos .txt y los carga en la RAM*

## Interfaz Web (Quipu AI)

Este proyecto incluye una interfaz gráfica moderna construida con Streamlit.

**Características:**
* 💬 **Chat Interactivo:** Con historial y respuestas en tiempo real.
* 🧠 **Memoria Selectiva:** Elige qué documentos activar/desactivar en la barra lateral.
* 📺 **YouTube Loader:** Descarga y transcribe videos automáticamente.
* 🗣️ **Respuesta de Voz:** TTS Neural con acentos regionales (Colombia, Perú, México, España).

**Ejecución:**
```bash
streamlit run web_app_master.py
```

### Estructura del Proyecto
Asegúrate de que tu carpeta se vea así antes de subir el último commit a GitHub:

```text
📂 local-audio-rag/
│
├── 📂 base_conocimiento/      # (Tus .txt)
├── 📂 temp_uploads/           # (Temporales)
│
├── web_app_master.py          # Aplicación principal
├── requirements.txt           # Lista de dependencias
├── README.md
├── transcribir_pro.py
├── transcribir.py
├── chat_audio.py
└── .gitignore


```

## Notas Técnicas

* **Hardware:** Probado en Intel i7 (12ª Gen) + 16GB RAM + Intel Iris Xe.
* **Modelos:** Se utiliza `whisper-small` para transcripción y `llama3.2-3b` para inferencia, optimizados para ejecutarse sin GPU dedicada.
* **Privacidad:** Todos los datos se procesan localmente (On-Premise). Nada se envía a la nube.

---

#### Edrem
#### Dios, la Patria y Assembly