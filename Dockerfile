# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    poppler-utils \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*  # Limpiar la caché de apt para reducir el tamaño de la imagen

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt primero (para aprovechar la cache de Docker)
COPY requirements.txt .

# Actualiza pip antes de instalar dependencias
RUN pip install --upgrade pip setuptools wheel

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de tu proyecto
COPY . .

# Establece la variable de entorno PYTHONUNBUFFERED para evitar problemas con la salida en los logs
ENV PYTHONUNBUFFERED 1

# Expone el puerto que tu aplicación usará (8000 para Django)
EXPOSE 8000

# Comando para ejecutar tu aplicación Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
