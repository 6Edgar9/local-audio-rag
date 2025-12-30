import ollama
import os
import glob

MODELO = "llama3.2"
CARPETA_DATOS = "base_conocimiento"

def cargar_conocimiento():
    """Recorre la carpeta y concatena todos los .txt en una sola variable"""
    texto_total = ""
    archivos = glob.glob(os.path.join(CARPETA_DATOS, "*.txt"))
    
    print(f"--- Cargando 'cerebro' desde {len(archivos)} archivos... ---")
    
    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                texto_total += f"\n--- INICIO ARCHIVO: {os.path.basename(archivo)} ---\n"
                texto_total += f.read()
                texto_total += f"\n--- FIN ARCHIVO ---\n"
                print(f" -> Leído: {os.path.basename(archivo)}")
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
            
    return texto_total

if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)
    print(f"¡Carpeta '{CARPETA_DATOS}' creada! Mete tus .txt ahí y reinicia.")
    exit()

contenido_contexto = cargar_conocimiento()

if not contenido_contexto:
    print("La carpeta está vacía. Añade archivos .txt para empezar.")
    exit()

print(f"\nContexto cargado en RAM ({len(contenido_contexto)} caracteres).")
print("---------------------------------------------------------------")

historial_chat = []

while True:
    pregunta = input("\nTú: ")
    if pregunta.lower() in ["salir", "exit", "chau"]:
        break

    # Prompt Engineering: Le damos rol y contexto
    instrucciones = f"""
    Eres un asistente experto en Ingeniería de Sistemas.
    Responde basándote EXCLUSIVAMENTE en la siguiente Información de Contexto.
    Si la respuesta no está en el contexto, di "No tengo información sobre eso en mis archivos".
    
    INFORMACIÓN DE CONTEXTO (Tus archivos):
    {contenido_contexto}
    
    PREGUNTA DEL USUARIO:
    {pregunta}
    """

    print("    Procesando...", end="", flush=True)
    
    stream = ollama.chat(
        model=MODELO, 
        messages=[{'role': 'user', 'content': instrucciones}],
        stream=True # Efecto "escritura" como ChatGPT
    )
    
    print("\rIA: ", end="")
    for chunk in stream:
        print(chunk['message']['content'], end="", flush=True)
    print("") # Salto de línea final