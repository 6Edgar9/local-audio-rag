# 1. Usamos una imagen base de Python ligera (Linux Debian)
FROM python:3.11-slim

# 2. Evita que Python genere archivos .pyc y fuerza salida en consola inmediata
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Instalamos FFmpeg y Git (necesarios para Whisper y yt-dlp)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Establecemos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 5. Copiamos primero los requerimientos (para aprovechar caché de Docker)
COPY requirements.txt .

# 6. Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiamos el resto del código del proyecto
COPY . .

# 8. Exponemos el puerto de Streamlit
EXPOSE 8501

# 9. Comando de arranque
CMD ["streamlit", "run", "web_app_master.py", "--server.address=0.0.0.0"]