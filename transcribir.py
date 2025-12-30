import whisper
import os

model = whisper.load_model("small")

# Busca todos los mp3 en la carpeta
for archivo in os.listdir():
    if archivo.endswith(".mp3"):
        print(f"Transcribiendo {archivo}...")
        result = model.transcribe(archivo, language="es")
        
        # Guardar en txt
        nombre_txt = archivo.replace(".mp3", ".txt")
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(f"--- METADATA ---\nArchivo: {archivo}\n---\n\n")
            f.write(result["text"])
            
        print(f"Listo: {nombre_txt}")