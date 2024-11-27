from django.contrib import admin
from django.urls import path

from django import views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index', views.index, name='index'),
    path('', views.login, name='login'),
    path('Registrar/', views.registrar_usuario, name='registrar'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('Analizar_Documento/', views.analizar_documento, name='Analizar_Documento'),
    path('Historial_Residentes/', views.historial_residentes, name='Historial_Residentes'),
    path('enviar_correo/', views.enviar_correo, name='enviar_correo'),

    path('Eliminar_Instancia/<str:id_orden>/', views.eliminar_instancia, name='eliminar_instancia'),
    path('ActualizarResidente/', views.actualizar_residente, name='actualizar_residente'),
]