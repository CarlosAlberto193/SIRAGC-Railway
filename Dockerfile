# Usa una imagen oficial de Python
FROM python:3.11-slim

# Instala las dependencias del sistema
RUN apt-get update && apt-get install -y \
    poppler-utils \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt y actualiza pip
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu proyecto
COPY . .

# Configuración para evitar problemas de salida en logs
ENV PYTHONUNBUFFERED 1

# Expone el puerto de la aplicación
EXPOSE 8000

# Comando para iniciar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
