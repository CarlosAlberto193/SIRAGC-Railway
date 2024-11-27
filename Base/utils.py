import pdfplumber
from django.shortcuts import render
from django.core.files.storage import default_storage
from PIL import Image
import numpy as np
import cv2
import io

def extraer_datos_pdf(ruta_pdf):
    datos = {
        'nombre': None,
        'numero_control': None,
        'carrera': None,
        'semestre': None,
        'domicilio': None,
        'colonia': None,
        'poliza': None,
        'codigo_postal': None,
        'ciudad': None,
        'correo': None,
        'sexo': None,
        'nombre_titular': None,
        'puesto_titular': None,
        'nombre_empresa': None,
        'nombre_corto_empresa' : None,
        'rfc_empresa': None,
        'giro_empresa': None,
        'sector_empresa': None,
        'telefono_empresa': None,
        'domicilio_empresa': None,
        'colonia_empresa': None,
        'ciudad_empresa': None,
        'cp_empresa': None,
        'area_residencia': None,
        'nombre_firma_empresa': None,
        'puesto_firma_empresa': None,
        'email_empresa': None,
        'fecha_inicio': None,
        'fecha_terminacion': None,
        'horario_residente': None,
        'dias_residente': None,
        'fecha_entrega_reporte': None,
        'apoyo_economico': None,
    }

    with pdfplumber.open(ruta_pdf) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tablas = page.extract_tables()

            print(f"--- Página {page_num} ---")
            for tabla_num, tabla in enumerate(tablas, start=1):
                print(f"Tabla {tabla_num}:")
                for fila_num, fila in enumerate(tabla):
                    print(f"  Fila {fila_num}: {fila}")
                print("\n")

            if len(tablas) > 1:
                tabla_2 = tablas[1]
                
                if len(tabla_2) > 0:
                    fila_0 = tabla_2[0]
                    if len(fila_0) > 0:
                        datos['nombre'] = limpiar_caracteres_incorrectos(fila_0[0].split(':')[-1].strip() if fila_0[0] else None)
                    if len(fila_0) > 3:
                        datos['numero_control'] = limpiar_caracteres_incorrectos(fila_0[3].split(':')[-1].strip() if fila_0[3] else None)
                    if len(fila_0) > 5:
                        datos['carrera'] = limpiar_caracteres_incorrectos(fila_0[5].split(':')[-1].strip() if fila_0[5] else None)
                    if len(fila_0) > 7:
                        datos['semestre'] = limpiar_caracteres_incorrectos(fila_0[7].split(':')[-1].strip() if fila_0[7] else None)

                if len(tabla_2) > 1:
                    fila_1 = tabla_2[1]
                    if len(fila_1) > 0:
                        datos['domicilio'] = limpiar_caracteres_incorrectos(fila_1[0].split(':')[-1].strip() if fila_1[0] else None)
                    if len(fila_1) > 3:
                        datos['colonia'] = limpiar_caracteres_incorrectos(fila_1[3].split(':')[-1].strip() if fila_1[3] else None)
                    if len(fila_1) > 5:
                        datos['poliza'] = limpiar_caracteres_incorrectos(fila_1[5].split(':')[-1].strip() if fila_1[5] else None)

                if len(tabla_2) > 2:
                    fila_2 = tabla_2[2]
                    if len(fila_2) > 0:
                        datos['codigo_postal'] = limpiar_caracteres_incorrectos(fila_2[0].split(':')[-1].strip() if fila_2[0] else None)
                    if len(fila_2) > 1:
                        datos['ciudad'] = limpiar_caracteres_incorrectos(fila_2[1].split(':')[-1].strip() if fila_2[1] else None)
                    if len(fila_2) > 2:
                        datos['telefono'] = limpiar_caracteres_incorrectos(fila_2[2].split(':')[-1].strip() if fila_2[2] else None)
                    if len(fila_2) > 4:
                        datos['edad'] = limpiar_caracteres_incorrectos(fila_2[4].split(':')[-1].strip() if fila_2[4] else None)
                    if len(fila_2) > 5:
                        datos['nss'] = limpiar_caracteres_incorrectos(fila_2[5].split(':')[-1].strip() if fila_2[5] else None)

                if len(tabla_2) > 3:
                    fila_3 = tabla_2[3]
                    if len(fila_3) > 0:
                        datos['correo'] = limpiar_caracteres_incorrectos(fila_3[0].split(':')[-1].strip() if fila_3[0] else None)
                    if len(fila_3) > 5:
                        if "X" in fila_3[8]:
                            datos['sexo'] = "Masculino"
                        elif "X" in fila_3[6]:
                            datos['sexo'] = "Femenino"
              
            if len(tablas) > 2:  
                tabla_3 = tablas[2]
                
                if len(tabla_3) > 0:
                    fila_0 = tabla_3[0]
                    if len(fila_0) > 0:
                        datos['nombre_empresa'] = limpiar_caracteres_incorrectos(fila_0[0].split(':')[-1].strip() if fila_0[0] else None)
                    if len(fila_0) > 6:
                        datos['nombre_corto_empresa'] = limpiar_caracteres_incorrectos(fila_0[6].split(':')[-1].strip() if fila_0[6] else None)

                if len(tabla_3) > 1:
                    fila_1 = tabla_3[1]
                    if len(fila_1) > 0:
                        datos['rfc_empresa'] = limpiar_caracteres_incorrectos(fila_1[0].split(':')[-1].strip() if fila_1[0] else None)
                    if len(fila_1) > 2:
                        datos['giro_empresa'] = limpiar_caracteres_incorrectos(fila_1[1].split(':')[-1].strip() if fila_1[1] else None)
                    if len(fila_1) > 5:
                        datos['sector_empresa'] = limpiar_caracteres_incorrectos(fila_1[5].split(':')[-1].strip() if fila_1[5] else None)

                if len(tabla_3) > 2:
                    fila_2 = tabla_3[2]
                    if len(fila_2) > 0:
                        datos['telefono_empresa'] = limpiar_caracteres_incorrectos(fila_2[0].split(':')[-1].strip() if fila_2[0] else None)
                    if len(fila_2) > 3:
                        datos['domicilio_empresa'] = limpiar_caracteres_incorrectos(fila_2[2].split(':')[-1].strip() if fila_2[2] else None)
                    if len(fila_2) > 7:
                        datos['colonia_empresa'] = limpiar_caracteres_incorrectos(fila_2[7].split(':')[-1].strip() if fila_2[7] else None)

                if len(tabla_3) > 3:
                    fila_3 = tabla_3[3]
                    if len(fila_3) > 0:
                        datos['ciudad_empresa'] = limpiar_caracteres_incorrectos(fila_3[0].split(':')[-1].strip() if fila_3[0] else None)
                    if len(fila_3) > 3:
                        datos['cp_empresa'] = limpiar_caracteres_incorrectos(fila_3[3].split(':')[-1].strip() if fila_3[3] else None)
                    if len(fila_3) > 5:
                        datos['area_residencia'] = limpiar_caracteres_incorrectos(fila_3[4].split(':')[-1].strip() if fila_3[4] else None)

                if len(tabla_3) > 4:
                    fila_4 = tabla_3[4]
                    if len(fila_4) > 0:
                        datos['nombre_titular'] = limpiar_caracteres_incorrectos(fila_4[0].split(':')[-1].strip() if fila_4[0] else None)
                    if len(fila_4) > 7:
                        datos['puesto_titular'] = limpiar_caracteres_incorrectos(fila_4[7].split(':')[-1].strip() if fila_4[7] else None) 
                
                if len(tabla_3) > 5:
                    fila_5 = tabla_3[5]
                    if len(fila_5) > 0:
                        datos['nombre_firma_empresa'] = limpiar_caracteres_incorrectos(fila_5[0].split(':')[-1].strip() if fila_5[0] else None)
                    if len(fila_5) > 7:
                        datos['puesto_firma_empresa'] = limpiar_caracteres_incorrectos(fila_5[7].split(':')[-1].strip() if fila_5[7] else None)  
                
                if len(tabla_3) > 6:
                    fila_6 = tabla_3[6]
                    if len(fila_6) > 0:
                        datos['email_empresa'] = limpiar_caracteres_incorrectos(fila_6[0].split(':')[-1].strip() if fila_6[0] else None)


            if len(tablas) > 3:
                tabla_4 = tablas[3]
                
                if len(tabla_4) > 0:
                    fila_0 = tabla_4[0]
                    if len(fila_0) > 0:
                        datos['fecha_inicio'] = limpiar_caracteres_incorrectos(fila_0[0].split(':')[-1].strip() if fila_0[0] else None)
                    if len(fila_0) > 2:
                        datos['fecha_terminacion'] = limpiar_caracteres_incorrectos(fila_0[2].split(':')[-1].strip() if fila_0[2] else None)

                if len(tabla_4) > 1:
                    fila_1 = tabla_4[1]
                    if len(fila_1) > 0:
                        datos['horario_residente'] = limpiar_caracteres_incorrectos(fila_1[0].split(':')[-1].strip() if fila_1[0] else None)
                    if len(fila_1) > 1:
                        datos['dias_residente'] = limpiar_caracteres_incorrectos(fila_1[1].split(':')[-1].strip() if fila_1[1] else None)
                    if len(fila_1) > 2:
                        datos['fecha_entrega_reporte'] = limpiar_caracteres_incorrectos(fila_1[2].split(':')[-1].strip() if fila_1[2] else None)

                if len(tabla_4) > 2:
                    fila_2 = tabla_4[2]
                    if len(fila_2) > 0:
                        datos['apoyo_economico'] = limpiar_caracteres_incorrectos(fila_2[0].split(':')[-1].strip() if fila_2[0] else None)

    return datos

def detectar_firma_area(imagen, coords):
    image = cv2.imread(imagen)

    if image is None:
        print("No se puede cargar la imagen.")
        return False 

    xmin, ymin, xmax, ymax = coords
    area = image[ymin:ymax, xmin:xmax]

    print(f"Ruta de la imagen: {imagen}")
    print(f"Coordenadas de la firma: {coords}")
    print(f"Área extraída: {area.shape}")

    gray_area = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)
    print(f"Área en escala de grises: {gray_area.shape}")

    _, threshold_area = cv2.threshold(gray_area, 240, 255, cv2.THRESH_BINARY)
    print(f"Área binarizada (con umbral 240): {np.sum(threshold_area == 255)} blancos, {np.sum(threshold_area == 0)} negros")

    total_pixels = threshold_area.size
    white_pixels = np.sum(threshold_area == 255)
    black_pixels = np.sum(threshold_area == 0)

    if white_pixels > total_pixels * 0.5 and black_pixels > total_pixels * 0.5:
        return True  # Se detecta una firma
    return False  # No hay firma

def limpiar_caracteres_incorrectos(data):
    if isinstance(data, str):
        return data.replace('\x00', 'ti')
    return data