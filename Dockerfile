# Usa una imagen base ligera de Python
FROM python:3.11-slim

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    && apt-get clean

# Define el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt
COPY requirements.txt .

# Actualiza pip e instala dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir numpy>=1.21.2,<1.24.0 && \
    pip install --no-cache-dir opencv-python-headless==4.8.0.76 && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . .

# Configuración de entorno para Django
ENV PYTHONUNBUFFERED 1
ENV ALLOWED_HOSTS="*"
ENV DEBUG=False

# Expone el puerto (requerido por Railway)
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:$PORT"]
