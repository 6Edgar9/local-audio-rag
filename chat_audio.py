import ollama
import os
import glob
import tts_manager  ### NUEVO: Importamos tu módulo de voz

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

    instrucciones = f"""
    Eres un asistente experto en Ingeniería de Sistemas llamado 'VoluNet AI'.
    Responde basándote EXCLUSIVAMENTE en la siguiente Información de Contexto.
    Si la respuesta no está en el contexto, di "No tengo información sobre eso en mis archivos".
    
    INFORMACIÓN DE CONTEXTO:
    {contenido_contexto}
    
    PREGUNTA DEL USUARIO:
    {pregunta}
    """

    print("    Procesando...", end="", flush=True)
    
    stream = ollama.chat(
        model=MODELO, 
        messages=[{'role': 'user', 'content': instrucciones}],
        stream=True 
    )
    
    print("\rIA: ", end="")
    
    ### NUEVO: Variable acumuladora para guardar el texto completo
    respuesta_completa = "" 
    
    for chunk in stream:
        trozo_texto = chunk['message']['content']
        print(trozo_texto, end="", flush=True) # Imprime en pantalla (Efecto Matrix)
        respuesta_completa += trozo_texto      # Guarda en memoria para el audio
        
    print("") # Salto de línea final
    
    ### NUEVO: Enviamos el texto completo al módulo de voz
    # Validamos que no esté vacío para evitar errores
    if respuesta_completa.strip():
        tts_manager.hablar(respuesta_completa)