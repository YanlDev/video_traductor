#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: DESCARGA DE VIDEO
========================
Descarga videos de YouTube usando yt-dlp
"""

import os
import yt_dlp
import time
import threading
from datetime import datetime

def obtener_info_video(url):
    """Obtiene información básica del video"""
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'titulo': info.get('title', 'Sin título'),
                'duracion': info.get('duration', 0),
                'canal': info.get('uploader', 'Desconocido'),
                'id': info.get('id', 'sin_id'),
                'url': url
            }
            
    except Exception as e:
        print(f"❌ Error obteniendo información del video")
        return None

def mostrar_barra_progreso(porcentaje, mensaje="Descargando"):
    """Muestra barra de progreso personalizada"""
    barra_llena = "█" * int(porcentaje // 5)
    barra_vacia = "░" * (20 - int(porcentaje // 5))
    
    print(f"\r🔄 [{barra_llena}{barra_vacia}] {porcentaje:5.1f}% - {mensaje}", end="", flush=True)

def hook_progreso(d):
    """Hook para capturar progreso de yt-dlp"""
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            porcentaje = (d['downloaded_bytes'] / d['total_bytes']) * 100
        elif 'total_bytes_estimate' in d:
            porcentaje = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
        else:
            return
        
        mostrar_barra_progreso(porcentaje, "Descargando video")
    
    elif d['status'] == 'finished':
        mostrar_barra_progreso(100, "Descarga completada")
        print()  # Nueva línea

def crear_nombre_archivo_seguro(titulo, video_id):
    """Crea nombre de archivo más limpio - VERSIÓN MEJORADA"""
    import re
    
    # Limpiar caracteres problemáticos MÁS AGRESIVAMENTE
    titulo_limpio = re.sub(r'[<>:"/\\|?*\[\]{}()]', '_', titulo)
    titulo_limpio = re.sub(r'[^\w\s-]', '', titulo_limpio)  # Solo alfanuméricos, espacios y guiones
    titulo_limpio = ' '.join(titulo_limpio.split())  # Eliminar espacios múltiples
    titulo_limpio = titulo_limpio.strip()  # Eliminar espacios al inicio/final
    titulo_limpio = titulo_limpio.replace(' ', '_')  # Reemplazar espacios con guiones bajos
    
    # Limitar longitud
    if len(titulo_limpio) > 25:
        titulo_limpio = titulo_limpio[:25]
    
    # Asegurar que no esté vacío
    if not titulo_limpio:
        titulo_limpio = "video"
    
    return f"{titulo_limpio}_{video_id}"

def formatear_duracion(segundos):
    """Convierte segundos a formato MM:SS o HH:MM:SS"""
    if not segundos:
        return "Desconocida"
    
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    
    if horas > 0:
        return f"{int(horas):02d}:{int(minutos):02d}:{int(segs):02d}"
    else:
        return f"{int(minutos):02d}:{int(segs):02d}"

def mostrar_info_video(info):
    """Muestra información del video"""
    print("📊 INFORMACIÓN DEL VIDEO")
    print("-" * 40)
    print(f"🎬 Título: {info['titulo']}")
    print(f"👤 Canal: {info['canal']}")
    print(f"⏱️  Duración: {formatear_duracion(info['duracion'])}")
    print(f"🆔 ID: {info['id']}")
    print()

def mostrar_barra_progreso(porcentaje, mensaje="Descargando"):
    """Muestra barra de progreso personalizada"""
    barra_llena = "█" * int(porcentaje // 5)
    barra_vacia = "░" * (20 - int(porcentaje // 5))
    
    print(f"\r🔄 [{barra_llena}{barra_vacia}] {porcentaje:5.1f}% - {mensaje}", end="", flush=True)

def hook_progreso(d):
    """Hook para capturar progreso de yt-dlp"""
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            porcentaje = (d['downloaded_bytes'] / d['total_bytes']) * 100
        elif 'total_bytes_estimate' in d:
            porcentaje = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
        else:
            return
        
        mostrar_barra_progreso(porcentaje, "Descargando video")
    
    elif d['status'] == 'finished':
        mostrar_barra_progreso(100, "Descarga completada")
        print()  # Nueva línea

def crear_nombre_archivo_seguro(titulo, video_id):
    """Crea nombre de archivo más limpio"""
    import re
    
    # Limpiar caracteres problemáticos más agresivamente
    titulo_limpio = re.sub(r'[<>:"/\\|?*\[\]]', '_', titulo)
    titulo_limpio = re.sub(r'[^\w\s-]', '', titulo_limpio)
    
    # Limitar longitud
    if len(titulo_limpio) > 30:
        titulo_limpio = titulo_limpio[:30]
    
    return f"{titulo_limpio}_{video_id}"

def descargar_video_youtube(url, ruta_proyecto, info_video):
    """Descarga el video de YouTube con barra de progreso personalizada"""
    
    # Carpeta destino (1_original)
    carpeta_destino = os.path.join(ruta_proyecto, "1_original")
    
    # Crear nombre de archivo
    nombre_archivo = crear_nombre_archivo_seguro(info_video['titulo'], info_video['id'])
    
    # Configuración de yt-dlp (SILENCIOSO)
    ydl_opts = {
        'format': 'best[height<=1080][ext=mp4]/best[height<=1080]/best',
        'outtmpl': os.path.join(carpeta_destino, f'{nombre_archivo}.%(ext)s'),
        'noplaylist': True,
        'writeinfojson': False,  # No crear archivos .info.json
        'writesubtitles': False,
        'writeautomaticsub': False,
        'quiet': True,  # ¡IMPORTANTE! Oculta todos los logs
        'no_warnings': True,  # Oculta advertencias
        'progress_hooks': [hook_progreso],  # Usar nuestro hook personalizado
    }
    
    try:
        print("🚀 Iniciando descarga...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Descargar con nuestra barra de progreso
            ydl.download([url])
        
        print(f"✅ Video guardado en el proyecto")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la descarga: {e}")
        return False

def guardar_info_proyecto(ruta_proyecto, info_video):
    """Guarda información del proyecto (silencioso)"""
    archivo_info = os.path.join(ruta_proyecto, "proyecto_info.txt")
    
    try:
        with open(archivo_info, 'w', encoding='utf-8') as f:
            f.write(f"Título: {info_video['titulo']}\n")
            f.write(f"Canal: {info_video['canal']}\n")
            f.write(f"Duración: {formatear_duracion(info_video['duracion'])}\n")
            f.write(f"ID: {info_video['id']}\n")
            f.write(f"URL: {info_video['url']}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return True
    except:
        return False

def procesar_descarga(url):
    """
    Función principal que procesa la descarga completa
    Versión simplificada para el usuario final
    """
    print("📥 INICIANDO DESCARGA")
    print("=" * 30)
    
    # Paso 1: Obtener información del video
    print("🔍 Obteniendo información del video...")
    info_video = obtener_info_video(url)
    if not info_video:
        return False
    
    # Paso 2: Mostrar información básica
    print(f"🎬 Video: {info_video['titulo']}")
    print(f"⏱️  Duración: {formatear_duracion(info_video['duracion'])}")
    print(f"👤 Canal: {info_video['canal']}")
    print()
    
    continuar = input("¿Continuar con la descarga? (s/n): ").lower().strip()
    if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Descarga cancelada")
        return False
    
    # Paso 3: Crear proyecto (silencioso)
    try:
        import main
        ruta_proyecto, nombre_proyecto = main.crear_proyecto(info_video['titulo'], info_video['id'])
        print(f"📁 Proyecto: {nombre_proyecto}")
    except Exception as e:
        print(f"❌ Error creando proyecto: {e}")
        return False
    
    # Paso 4: Descargar video
    print()
    exito_descarga = descargar_video_youtube(url, ruta_proyecto, info_video)
    
    if not exito_descarga:
        return False
    
    # Paso 5: Guardar información del proyecto (silencioso)
    guardar_info_proyecto(ruta_proyecto, info_video)
    
    # Paso 6: Resumen final (simplificado)
    print()
    print("🎉 ¡DESCARGA COMPLETADA!")
    print(f"📁 Ubicación: {nombre_proyecto}")
    print("🔄 Listo para el siguiente paso (extracción de audio)")
    
    return True

def main():
    """Función para ejecutar el módulo independientemente"""
    url = input("🔗 Ingresa URL del video: ")
    procesar_descarga(url)

if __name__ == "__main__":
    main()