#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRADUCTOR DE VIDEOS AL ESPAÑOL
==============================
Programa completamente automático:
Ingresa URL → Obtén video traducido

Flujo automático:
URL → Descarga → Extrae audio → Separa audio → Transcribe → Traduce → TTS → Video final
"""

import os
import sys
import asyncio
from datetime import datetime

def mostrar_banner():
    """Banner del programa simplificado"""
    print("=" * 60)
    print("🎬 TRADUCTOR AUTOMÁTICO DE VIDEOS AL ESPAÑOL")
    print("=" * 60)
    print("🎯 Ingresa una URL → Proceso completamente automático")
    print("🚀 Descarga → Audio → Separación → Transcripción → Traducción → TTS → Video final")
    print("=" * 60)
    print()

def crear_carpeta_base():
    """Crea carpeta downloads base (silencioso)"""
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

def obtener_siguiente_numero():
    """Obtiene el siguiente número para proyectos"""
    if not os.path.exists("downloads"):
        return 1
    
    carpetas_numeradas = []
    for item in os.listdir("downloads"):
        if os.path.isdir(os.path.join("downloads", item)):
            if item[:3].isdigit():
                try:
                    numero = int(item[:3])
                    carpetas_numeradas.append(numero)
                except:
                    pass
    
    return max(carpetas_numeradas) + 1 if carpetas_numeradas else 1

def crear_proyecto(nombre_video, video_id=""):
    """Crea estructura del proyecto (silencioso)"""
    import re
    
    # Limpiar nombre del video
    nombre_limpio = re.sub(r'[<>:"/\\|?*\[\]{}()]', '_', nombre_video)
    nombre_limpio = re.sub(r'[^\w\s-]', '', nombre_limpio)
    nombre_limpio = ' '.join(nombre_limpio.split())
    nombre_limpio = nombre_limpio.strip()
    nombre_limpio = nombre_limpio.replace(' ', '_')
    nombre_limpio = nombre_limpio[:20]
    
    if not nombre_limpio:
        nombre_limpio = "video"
    
    # Crear nombre del proyecto
    numero = obtener_siguiente_numero()
    nombre_proyecto = f"{numero:03d}_{nombre_limpio}"
    
    # Crear ruta del proyecto
    ruta_proyecto = os.path.join("downloads", nombre_proyecto)
    
    # Crear subcarpetas organizadas
    subcarpetas = [
        "1_original", "2_audio", "audio_separado",
        "3_transcripcion", "4_traduccion", "5_audio_es", "6_final"
    ]
    
    # Crear estructura completa
    try:
        os.makedirs(ruta_proyecto, exist_ok=True)
        
        for subcarpeta in subcarpetas:
            ruta_subcarpeta = os.path.join(ruta_proyecto, subcarpeta)
            os.makedirs(ruta_subcarpeta, exist_ok=True)
        
    except Exception as e:
        print(f"❌ Error creando estructura: {e}")
        raise
    
    return ruta_proyecto, nombre_proyecto

def validar_url_youtube(url):
    """Valida si es una URL de YouTube válida"""
    dominios_validos = [
        'youtube.com',
        'youtu.be', 
        'www.youtube.com',
        'm.youtube.com'
    ]
    
    return any(dominio in url.lower() for dominio in dominios_validos)

async def proceso_automatico(url):
    """
    Proceso completamente automático de 7 pasos:
    1. Descarga video
    2. Extrae audio 
    3. Separa música y voces
    4. Transcribe audio
    5. Traduce al español
    6. Genera audio en español (TTS)
    7. Genera video final
    """
    print("🚀 INICIANDO PROCESO AUTOMÁTICO")
    print("=" * 40)
    
    # PASO 1: DESCARGA
    print("🔄 Paso 1/7: Descargando video...")
    
    try:
        import download_video
        
        # Obtener info del video
        info_video = download_video.obtener_info_video(url)
        if not info_video:
            print("❌ No se pudo obtener información del video")
            return False
        
        print(f"🎬 Video: {info_video['titulo']}")
        print(f"⏱️  Duración: {download_video.formatear_duracion(info_video['duracion'])}")
        print()
        
        # Crear proyecto
        ruta_proyecto, nombre_proyecto = crear_proyecto(info_video['titulo'], info_video['id'])
        print(f"📁 Proyecto: {nombre_proyecto}")
        
        # Descargar
        exito_descarga = download_video.descargar_video_youtube(url, ruta_proyecto, info_video)
        
        if not exito_descarga:
            print("❌ Error en la descarga")
            return False
            
        download_video.guardar_info_proyecto(ruta_proyecto, info_video)
        print("✅ Descarga completada")
        
    except ImportError:
        print("❌ Error: Módulo download_video no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        return False
    
    # PASO 2: EXTRACCIÓN DE AUDIO
    print(f"\n🔄 Paso 2/7: Extrayendo audio...")
    
    try:
        import extract_audio
        
        # Buscar video descargado
        carpeta_original = os.path.join(ruta_proyecto, "1_original")
        archivos_video = [f for f in os.listdir(carpeta_original) 
                        if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm'))]
        
        if not archivos_video:
            print("❌ No se encontró el video descargado")
            return False
            
        ruta_video = os.path.join(carpeta_original, archivos_video[0])
        
        # Preparar ruta de audio
        carpeta_audio = os.path.join(ruta_proyecto, "2_audio")
        nombre_video = os.path.splitext(archivos_video[0])[0]
        archivo_audio = os.path.join(carpeta_audio, f"{nombre_video}.wav")
        
        # Extraer audio
        exito_audio = extract_audio.extraer_audio_optimizado(ruta_video, archivo_audio)
        
        if not exito_audio:
            print("❌ Error en extracción de audio")
            return False
            
        print("✅ Audio extraído")
        
    except ImportError:
        print("❌ Error: Módulo extract_audio no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error en extracción de audio: {e}")
        return False
    
    # PASO 3: SEPARACIÓN DE AUDIO
    print(f"\n🔄 Paso 3/7: Separando música y voces...")
    
    try:
        import separate_audio
        
        # Usar la función automática del módulo
        archivos_separados = separate_audio.separar_automatico(ruta_proyecto)
        
        if archivos_separados:
            print("✅ Separación completada")
            print("   🎤 vocals.wav - Solo voces")
            print("   🎵 accompaniment.wav - Solo música")
        else:
            print("⚠️  Separación falló, continuando sin separar")
            
    except ImportError:
        print("⚠️  Módulo separate_audio no disponible")
        print("💡 Para separación instala: pip install librosa soundfile scipy")
    except Exception as e:
        print(f"⚠️  Error en separación: {e}")
    
    # PASO 4: TRANSCRIPCIÓN DE AUDIO
    print(f"\n🔄 Paso 4/7: Transcribiendo audio...")
    
    try:
        import transcribe_audio
        
        resultado_transcripcion = transcribe_audio.transcribir_automatico(ruta_proyecto)
        
        if resultado_transcripcion:
            print("✅ Transcripción completada")
            if 'idioma' in resultado_transcripcion:
                print(f"   🌐 Idioma detectado: {resultado_transcripcion['idioma']}")
            if 'texto_completo' in resultado_transcripcion:
                caracteres = len(resultado_transcripcion['texto_completo'])
                print(f"   📝 Caracteres transcritos: {caracteres}")
        else:
            print("⚠️  Transcripción falló, continuando...")
            
    except ImportError:
        print("⚠️  Módulo transcribe_audio no disponible")
        print("💡 Para transcripción instala: pip install openai-whisper")
    except Exception as e:
        print(f"⚠️  Error en transcripción: {e}")
    
    # PASO 5: TRADUCCIÓN AL ESPAÑOL
    print(f"\n🔄 Paso 5/7: Traduciendo al español...")
    
    try:
        import translate_text
        
        resultado_traduccion = translate_text.traducir_automatico(ruta_proyecto)
        
        if resultado_traduccion:
            print("✅ Traducción completada")
            if 'costo' in resultado_traduccion and resultado_traduccion['costo'] > 0:
                print(f"   💰 Costo: ${resultado_traduccion['costo']:.4f}")
            else:
                print("   💰 Costo: Gratis (Google Translate)")
            
            if 'texto_traducido' in resultado_traduccion:
                caracteres_es = len(resultado_traduccion['texto_traducido'])
                print(f"   📝 Caracteres en español: {caracteres_es}")
        else:
            print("⚠️  Traducción falló")
            
    except ImportError:
        print("⚠️  Módulo translate_text no disponible")
        print("💡 Para traducción instala: pip install openai python-dotenv googletrans==4.0.0-rc1")
    except Exception as e:
        print(f"⚠️  Error en traducción: {e}")
    
    # PASO 6: GENERACIÓN DE AUDIO EN ESPAÑOL (TTS)
    print(f"\n🔄 Paso 6/7: Generando audio en español...")
    
    try:
        import generate_spanish_audio
        
        # PASO 6: En main.py esto ya funciona correctamente
        print("\n🎭 ¿Qué voz prefieres?")
        print("1. 👩 Mujer (recomendado)")  
        print("2. 👨 Hombre")
        genero = input("Elige (1/2): ").strip()
        genero_elegido = 'Male' if genero == '2' else 'Female'
        
        resultado_tts = await generate_spanish_audio.generar_automatico(ruta_proyecto, genero_elegido)
    
        
        if resultado_tts:
            print("✅ Audio en español generado")
            if 'voz_usada' in resultado_tts:
                voz = resultado_tts['voz_usada']
                print(f"   🎙️ Voz: {voz['nombre']} ({voz['locale']})")
            
            if 'archivo_audio' in resultado_tts:
                try:
                    tamaño = os.path.getsize(resultado_tts['archivo_audio']) / 1024 / 1024
                    print(f"   📊 Tamaño: {tamaño:.1f} MB")
                except:
                    pass
        else:
            print("⚠️  Generación de audio falló")
            
    except ImportError:
        print("⚠️  Módulo generate_spanish_audio no disponible")
        print("💡 Para TTS instala: pip install edge-tts")
    except Exception as e:
        print(f"⚠️  Error en generación de audio: {e}")
    
    # PASO 7: GENERACIÓN DE VIDEO FINAL
    print(f"\n🔄 Paso 7/7: Generando video final...")
    
    try:
        import combine_audio
        
        resultado_video = combine_audio.procesar_proyecto_completo(ruta_proyecto)
        
        if resultado_video:
            print("✅ Video final generado")
            
            # Buscar archivo de video final
            carpeta_final = os.path.join(ruta_proyecto, "6_final")
            if os.path.exists(carpeta_final):
                videos_finales = [f for f in os.listdir(carpeta_final) 
                                if f.lower().endswith(('.mp4', '.avi', '.mkv'))]
                if videos_finales:
                    video_final = os.path.join(carpeta_final, videos_finales[0])
                    try:
                        tamaño = os.path.getsize(video_final) / 1024 / 1024
                        print(f"   📊 Tamaño: {tamaño:.1f} MB")
                        print(f"   📁 Archivo: {videos_finales[0]}")
                    except:
                        pass
        else:
            print("⚠️  Generación de video final falló")
            
    except ImportError:
        print("⚠️  Módulo combine_audio no disponible")
        print("💡 Verifica que FFmpeg esté instalado")
    except Exception as e:
        print(f"⚠️  Error en generación de video: {e}")
    
    # RESUMEN FINAL
    print("\n🎉 PROCESAMIENTO COMPLETADO")
    print("=" * 40)
    print(f"📁 Proyecto: {nombre_proyecto}")
    print(f"📹 Video descargado: ✅")
    print(f"🎵 Audio extraído: ✅")
    
    # Verificar separación
    carpeta_separado = os.path.join(ruta_proyecto, "audio_separado")
    if os.path.exists(carpeta_separado):
        archivos_sep = [f for f in os.listdir(carpeta_separado) if f.endswith('.wav')]
        if len(archivos_sep) >= 2:
            print(f"🎼 Audio separado: ✅")
        else:
            print(f"🎼 Audio separado: ❌")
    else:
        print(f"🎼 Audio separado: ❌")
    
    # Verificar transcripción
    carpeta_transcripcion = os.path.join(ruta_proyecto, "3_transcripcion")
    if os.path.exists(carpeta_transcripcion):
        archivos_trans = [f for f in os.listdir(carpeta_transcripcion) if f.endswith('.txt')]
        if archivos_trans:
            print(f"🎤 Transcripción: ✅")
        else:
            print(f"🎤 Transcripción: ❌")
    else:
        print(f"🎤 Transcripción: ❌")
    
    # Verificar traducción
    carpeta_traduccion = os.path.join(ruta_proyecto, "4_traduccion")
    if os.path.exists(carpeta_traduccion):
        archivos_trad = [f for f in os.listdir(carpeta_traduccion) if f.endswith('_es.txt')]
        if archivos_trad:
            print(f"🌐 Traducción: ✅")
        else:
            print(f"🌐 Traducción: ❌")
    else:
        print(f"🌐 Traducción: ❌")
    
    # Verificar audio en español
    carpeta_audio_es = os.path.join(ruta_proyecto, "5_audio_es")
    if os.path.exists(carpeta_audio_es):
        archivos_audio_es = [f for f in os.listdir(carpeta_audio_es) if f.endswith('.wav')]
        if archivos_audio_es:
            print(f"🎙️ Audio en español: ✅")
        else:
            print(f"🎙️ Audio en español: ❌")
    else:
        print(f"🎙️ Audio en español: ❌")
    
    # Verificar video final
    carpeta_final = os.path.join(ruta_proyecto, "6_final")
    if os.path.exists(carpeta_final):
        archivos_finales = [f for f in os.listdir(carpeta_final) 
                          if f.lower().endswith(('.mp4', '.avi', '.mkv'))]
        if archivos_finales:
            print(f"🎬 Video final: ✅")
        else:
            print(f"🎬 Video final: ❌")
    else:
        print(f"🎬 Video final: ❌")
    
    print(f"📂 Ubicación: downloads/{nombre_proyecto}/")
    print()
    
    # Verificar si todo salió bien
    if (os.path.exists(carpeta_separado) and 
        os.path.exists(carpeta_transcripcion) and 
        os.path.exists(carpeta_traduccion) and 
        os.path.exists(carpeta_audio_es) and 
        os.path.exists(carpeta_final)):
        
        videos_finales = [f for f in os.listdir(carpeta_final) 
                         if f.lower().endswith(('.mp4', '.avi', '.mkv'))]
        if videos_finales:
            print("🎊 ¡TRADUCCIÓN COMPLETA!")
            print("🎬 Tu video está 100% traducido al español")
            print(f"📁 Video final: {videos_finales[0]}")
        else:
            print("🔄 Proceso casi completo - falta video final")
    else:
        print("🔄 Algunos pasos fallaron - revisa los mensajes arriba")
    
    # LIMPIEZA AUTOMÁTICA DE ARCHIVOS TEMPORALES
    try:
        import cleanup_temp_files
        cleanup_temp_files.limpiar_proyecto(ruta_proyecto)
        print("🧹 Archivos temporales eliminados")
    except:
        pass  # Si no está el módulo, continuar sin limpiar
    
    return True

async def main_async():
    """Función principal asíncrona"""
    # Limpiar pantalla
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Mostrar banner
    mostrar_banner()
    
    # Crear estructura base
    crear_carpeta_base()
    
    print("📝 INGRESA LA URL DEL VIDEO:")
    print()
    
    # Solicitar URL
    while True:
        url = input("🔗 URL de YouTube: ").strip()
        
        if not url:
            print("❌ URL vacía. Intenta de nuevo.")
            continue
            
        if not validar_url_youtube(url):
            print("❌ URL no válida. Debe ser de YouTube.")
            print("💡 Ejemplo: https://youtube.com/watch?v=...")
            continue
            
        break
    
    print()
    
    # PROCESO AUTOMÁTICO COMPLETO
    exito = await proceso_automatico(url)
    
    if exito:
        print("\n🎊 ¡PROCESO COMPLETADO!")
        print("🔮 Tu video traducido está listo")
    else:
        print("\n❌ Error en el proceso automático")
        print("💡 Verifica la URL e intenta de nuevo")
    
    # Pausa antes de terminar
    input("\nPresiona Enter para salir...")

def main():
    """Función principal que maneja asyncio"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()