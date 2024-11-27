from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from django.core.mail import send_mail
from .utils import extraer_datos_pdf
from .models import DocumentoEstado
poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'

def index(request):
    return render(request, "index.html")

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Credenciales incorrectas.')

    return render(request, "login.html")

def registrar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombre
        user.save()

        messages.success(request, 'Usuario registrado exitosamente.')
        return redirect('login')

    return render(request, 'registrar.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('login')

def detectar_firma_area(imagen, coords):
    image = cv2.imread(imagen)

    if image is None:
        print("No se puede cargar la imagen.")
        return False

    xmin, ymin, xmax, ymax = coords
    alto, ancho = image.shape[:2]
    xmin = min(xmin, ancho)
    ymin = min(ymin, alto)
    xmax = min(xmax, ancho)
    ymax = min(ymax, alto)

    print(f"Coordenadas ajustadas: ({xmin}, {ymin}, {xmax}, {ymax})")
    area = image[ymin:ymax, xmin:xmax]
    print(f"Área extraída: {area.shape}")

    if area.shape[0] == 0 or area.shape[1] == 0:
        print("No se pudo extraer el área correctamente.")
        return False

    gray_area = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)
    umbral = 220
    _, threshold_area = cv2.threshold(gray_area, umbral, 255, cv2.THRESH_BINARY)

    print(f"Área en escala de grises: {gray_area.shape}")
    print(f"Área binarizada (con umbral {umbral}): {np.sum(threshold_area == 255)} blancos, {np.sum(threshold_area == 0)} negros")

    total_pixels = threshold_area.size
    white_pixels = np.sum(threshold_area == 255)
    black_pixels = np.sum(threshold_area == 0)
    umbral_negros = 7500

    if black_pixels > umbral_negros:
        print("Firma detectada en el área.")
        return True
    else:
        print("No se detectó firma en el área.")
        return False

@login_required
def analizar_documento(request):
    datos_pdf = {"firmas_completas": False}
    mensaje = ""

    if request.method == "POST":
        accion = request.POST.get('accion')

        if accion == "cargar" and request.FILES.get('documento_pdf'):
            archivo_pdf = request.FILES['documento_pdf']
            ruta = default_storage.save('tmp/' + archivo_pdf.name, archivo_pdf)
            pdf_path = default_storage.path(ruta)
            datos_extraidos = extraer_datos_pdf(pdf_path)
            images = convert_from_path(pdf_path, 300, poppler_path=poppler_path)
            image_path = pdf_path.replace('.pdf', '.png')
            images[0].save(image_path, 'PNG')

            coords_area = (300, 2600, 1600, 2668)  # Coordenadas de la firma
            datos_pdf["firmas_completas"] = detectar_firma_area(image_path, coords_area)

            datos_pdf.update(datos_extraidos)

            # Validar si todos los campos están vacíos (excepto firmas_completas)
            campos_vacios = all(value is None for key, value in datos_pdf.items() if key != "firmas_completas")

            if campos_vacios:
                mensaje = "Documento No Cumple con Estandar de Acuerdo o Defectuoso"
            return render(request, 'analizar_documento.html', {'datos': datos_pdf, 'mensaje': mensaje})

        elif accion == "analizar" and request.FILES.get('documento_pdf'):
            archivo_pdf = request.FILES['documento_pdf']
            ruta = default_storage.save('tmp/' + archivo_pdf.name, archivo_pdf)
            pdf_path = default_storage.path(ruta)
            datos_extraidos = extraer_datos_pdf(pdf_path)
            images = convert_from_path(pdf_path, 300, poppler_path=poppler_path)
            image_path = pdf_path.replace('.pdf', '.png')
            images[0].save(image_path, 'PNG')

            coords_area = (300, 2600, 1600, 2668)  # Coordenadas de la firma
            datos_pdf["firmas_completas"] = detectar_firma_area(image_path, coords_area)

            datos_pdf.update(datos_extraidos)

            campos_incompletos = 0
            razones_error = []
            for key, value in datos_pdf.items():
             if value is None and key != "firmas_completas":
              campos_incompletos += 1
              razones_error.append(f"El campo {key.replace('_', ' ').capitalize()} no fue rellenado.")

            if not datos_pdf["firmas_completas"]:
             razones_error.append("La firma no fue satisfactoriamente rellenada.")

            if all(value is None for key, value in datos_pdf.items() if key != "firmas_completas"):
                mensaje = "Documento No Cumple con Estandar de Acuerdo o Defectuoso"
            elif campos_incompletos == 0 and datos_pdf["firmas_completas"]:
                mensaje = "Documento Correcto"
            elif campos_incompletos >= 3 or not datos_pdf["firmas_completas"]:
                mensaje = "Documento Incorrecto"
                nombre = datos_pdf.get('nombre', 'No disponible')
                numero_control = datos_pdf.get('numero_control', 'No disponible')
                correo = datos_pdf.get('correo', 'No disponible')

                request.session['razones_error'] = razones_error
                request.session['nombre'] = nombre
                request.session['numero_control'] = numero_control
                request.session['correo'] = correo

                return redirect('enviar_correo')

            return render(request, 'analizar_documento.html', {'datos': datos_pdf, 'mensaje': mensaje})

        elif accion == "guardar" and request.POST.get('nombre') and request.POST.get('numero_control') and request.POST.get('correo'):
            nombre = request.POST['nombre']
            numero_control = request.POST['numero_control']
            correo = request.POST['correo']
            mensaje = request.POST.get('mensaje', '')

            DocumentoEstado.objects.create(
                nombre=nombre,
                numero_control=numero_control,
                correo=correo,
                mensaje=mensaje,
                estado_envio='Pendiente',  # Estado de envío como pendiente
            )

            mensaje = "Los datos han sido guardados exitosamente."
            return render(request, 'analizar_documento.html', {'datos': datos_pdf, 'mensaje': mensaje})

    return render(request, 'analizar_documento.html', {'datos': {}, 'mensaje': ''})

@login_required
def enviar_correo(request):
    razones_error = request.session.get('razones_error', [])
    if 'razones_error' in request.session:
        del request.session['razones_error']

    nombre = request.session.get('nombre', 'No disponible')
    numero_control = request.session.get('numero_control', 'No disponible')
    correo = request.session.get('correo', 'No disponible')

    if razones_error:
        mensaje_error = (
            "Por parte del área de Residencias, se le comunica que su acuerdo de colaboración "
            "no puede ser firmado de nuestra parte debido a que falta por corregir los siguientes espacios:"
        )
        mensaje_error += "\n" + "\n".join(f"- {razon.strip()}" for razon in razones_error)
    else:
        mensaje_error = "No se encontraron errores en el documento."

    DocumentoEstado.objects.create(
        nombre=nombre,
        numero_control=numero_control,
        correo=correo,
        mensaje="Documento Incorrecto", 
        estado_envio='Enviado',
    )

    asunto = "Errores detectados en el documento"
    cuerpo = (
        f"Estimado usuario,\n\n{mensaje_error}\n\n"
        "Por favor, realice las correcciones necesarias y vuelva a enviar el documento.\n\n"
        "Atentamente,\nEl equipo de Residencias."
    )

    try:
        send_mail(
            asunto,
            cuerpo,
            'carlos.iniguez193@tectijuana.edu.mx',
            [correo],
            fail_silently=False,
        )
        messages.success(request, "El correo ha sido enviado exitosamente.")
    except Exception as e:
        messages.error(request, f"No se pudo enviar el correo: {e}")

    print("Guardando razones_error en la sesión:", razones_error)
    request.session['razones_error'] = razones_error

    return render(request, 'enviar_correo.html', {
        'correo': correo,
        'mensaje_error': mensaje_error,  # Este es el mensaje que se verá en el formulario
        'razones_error': razones_error,  # Este es el listado de errores que debe mostrar
        'nombre': nombre,
        'numero_control': numero_control
    })

@login_required
def historial_residentes(request):
    numero_control_buscar = request.GET.get('numero_control', '')
    if numero_control_buscar:
        Entradas = DocumentoEstado.objects.filter(numero_control__icontains=numero_control_buscar).order_by('id')
    else:
        Entradas = DocumentoEstado.objects.all().order_by('id')
    
    return render(request, 'historial_residentes.html', {'Entradas': Entradas, 'numero_control_buscar': numero_control_buscar})

def eliminar_instancia(request, id_orden):
    residente = get_object_or_404(DocumentoEstado, id=id_orden)
    residente.delete()
    return redirect('Historial_Residentes')

@login_required
def actualizar_residente(request):
    if request.method == 'POST':
        buscar_id = request.POST.get('buscar_id')
        nombre = request.POST.get('nombre')
        numero_control = request.POST.get('numero_control')
        correo = request.POST.get('correo')
        mensaje = request.POST.get('mensaje')
        estado_envio = request.POST.get('estado_envio')

        documento = get_object_or_404(DocumentoEstado, id=buscar_id)

        documento.nombre = nombre
        documento.numero_control = numero_control
        documento.correo = correo
        documento.mensaje = mensaje
        documento.estado_envio = estado_envio
        documento.save()

        messages.success(request, "Documento actualizado exitosamente.")
        return redirect('Historial_Residentes')
    buscar_id = request.GET.get('buscar_id')
    if buscar_id:
        documento = get_object_or_404(DocumentoEstado, id=buscar_id)
        return render(request, 'actualizar_residente.html', {'documento': documento})

    return redirect('Historial_Residentes')

