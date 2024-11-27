# Usa una imagen base de Python
FROM python:3.11-slim

# Instalar dependencias del sistema (como poppler para pdf2image)
RUN apt-get update && apt-get install -y poppler-utils

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de dependencias primero
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código
COPY . .

# Define la variable de entorno para evitar el uso de buffers
ENV PYTHONUNBUFFERED 1

# Expón el puerto que Django usará
EXPOSE 8000

# Comando para ejecutar tu aplicación (ajústalo a tu caso)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
