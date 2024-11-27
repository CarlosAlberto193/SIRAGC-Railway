from django.db import models

class DocumentoEstado(models.Model):
    nombre = models.CharField(max_length=255)
    numero_control = models.CharField(max_length=50)
    correo = models.EmailField()
    mensaje = models.TextField()
    estado_envio = models.CharField(max_length=50, choices=[('enviado', 'Enviado'), ('pendiente', 'Pendiente')])

    def __str__(self):
        return f"{self.nombre} ({self.numero_control}) - {self.estado_envio}"