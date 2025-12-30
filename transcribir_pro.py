import whisper
import os
import datetime
import warnings

# Filtramos la advertencia de FP16 (ya sabemos que usas CPU)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# 'small' es el mejor balance. Si va muy lento, cambia a 'base'.
MODELO = "base" 
CARPETA_SALIDA = "base_conocimiento"

def obtener_duracion_formateada(segundos):
    return str(datetime.timedelta(seconds=int(segundos)))

def transcribir_batch():
    print(f"--- 1. INICIALIZANDO MOTOR WHISPER ({MODELO}) ---")
    print("Cargando modelo en memoria RAM (esto puede tardar unos segundos)...")
    
    try:
        model = whisper.load_model(MODELO)
    except Exception as e:
        print(f"Error cargando el modelo: {e}")
        return
    if not os.path.exists(CARPETA_SALIDA):
        os.makedirs(CARPETA_SALIDA)
    extensiones_validas = (".mp3", ".wav", ".m4a")
    archivos = [f for f in os.listdir() if f.lower().endswith(extensiones_validas)]
    
    if not archivos:
        print(f"No encontré archivos de audio ({extensiones_validas}) en esta carpeta.")
        return

    print(f"--- 2. SE ENCONTRARON {len(archivos)} ARCHIVOS ---")

    for i, audio_file in enumerate(archivos, 1):
        print(f"\n[{i}/{len(archivos)}] Procesando: {audio_file} ...")
        print("    -> Transcribiendo (Paciencia, usando CPU i7)...")
        
        start_time = datetime.datetime.now()

        result = model.transcribe(audio_file, language="es", verbose=False)

        cuerpo_texto = ""
        for segment in result["segments"]:
            tiempo = obtener_duracion_formateada(segment["start"])
            texto_segmento = segment["text"].strip()
            cuerpo_texto += f"[{tiempo}] {texto_segmento}\n"

        end_time = datetime.datetime.now()
        duracion_proceso = end_time - start_time
        
        nombre_txt = os.path.splitext(audio_file)[0] + ".txt"
        ruta_txt = os.path.join(CARPETA_SALIDA, nombre_txt)
        
        contenido_final = f"""---
METADATA
Archivo Origen: {audio_file}
Fecha Procesamiento: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
Duración del Proceso: {duracion_proceso}
Modelo Usado: {MODELO}
Nota Técnica: Las marcas de tiempo [mm:ss] indican el momento en el audio.
---

CONTENIDO TRANSCRITO:
{cuerpo_texto}
"""
        
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(contenido_final)
            
        print(f"    ✅ Completado en {duracion_proceso}. Guardado en: {ruta_txt}")

    print("\n--- ¡PROCESO FINALIZADO CON ÉXITO! ---")
    print(f"Revisa la carpeta '{CARPETA_SALIDA}' para ver tus archivos.")

if __name__ == "__main__":
    transcribir_batch()