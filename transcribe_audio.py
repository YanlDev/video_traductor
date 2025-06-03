#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: TRANSCRIPCIÓN DE AUDIO
==============================
Transcribe audio a texto usando OpenAI Whisper (local)
"""

import os
import json
import time
from datetime import datetime, timedelta

def verificar_whisper():
    """Verifica que Whisper esté disponible"""
    try:
        import whisper
        print("✅ OpenAI Whisper disponible")
        return True
    except ImportError as e:
        print(f"❌ Whisper no disponible: {e}")
        print("💡 Instalar con: pip install openai-whisper")
        return False

def formatear_timestamp(segundos):
    """Convierte segundos a formato HH:MM:SS,mmm para subtítulos"""
    td = timedelta(seconds=segundos)
    horas = int(td.total_seconds() // 3600)
    minutos = int((td.total_seconds() % 3600) // 60)
    segs = td.total_seconds() % 60
    
    return f"{horas:02d}:{minutos:02d}:{segs:06.3f}".replace('.', ',')

def transcribir_con_whisper(ruta_audio, modelo='small'):
    """Transcribe audio usando Whisper"""
    try:
        import whisper
        
        print(f"🤖 Cargando modelo Whisper '{modelo}'...")
        model = whisper.load_model(modelo)
        
        print(f"🎵 Transcribiendo audio...")
        print(f"📁 Archivo: {os.path.basename(ruta_audio)}")
        
        inicio = time.time()
        resultado = model.transcribe(ruta_audio, language=None, task='transcribe', verbose=False)
        duracion = time.time() - inicio
        
        texto_completo = resultado['text'].strip()
        idioma_detectado = resultado['language']
        
        segmentos = []
        if 'segments' in resultado:
            for seg in resultado['segments']:
                segmentos.append({
                    'inicio': seg['start'],
                    'fin': seg['end'],
                    'texto': seg['text'].strip()
                })
        
        print(f"✅ Transcripción completada en {duracion:.1f} segundos")
        print(f"🌐 Idioma detectado: {idioma_detectado}")
        print(f"📝 Caracteres transcritos: {len(texto_completo)}")
        
        return {
            'texto_completo': texto_completo,
            'idioma': idioma_detectado,
            'modelo_usado': modelo,
            'duracion_proceso': duracion,
            'segmentos': segmentos,
            'archivo_audio': ruta_audio,
            'timestamp_proceso': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        return None

def generar_subtitulos_srt(segmentos, ruta_salida):
    """Genera archivo de subtítulos en formato SRT"""
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            for i, segmento in enumerate(segmentos, 1):
                inicio = formatear_timestamp(segmento['inicio'])
                fin = formatear_timestamp(segmento['fin'])
                texto = segmento['texto']
                
                f.write(f"{i}\n")
                f.write(f"{inicio} --> {fin}\n")
                f.write(f"{texto}\n\n")
        
        print(f"📄 Subtítulos SRT: {os.path.basename(ruta_salida)}")
        return True
        
    except Exception as e:
        print(f"❌ Error generando SRT: {e}")
        return False

def transcribir_automatico(ruta_proyecto):
    """Función para transcribir automáticamente desde el proceso principal"""
    try:
        if not verificar_whisper():
            return None
        
        # Buscar archivo de audio en el proyecto
        carpeta_audio = os.path.join(ruta_proyecto, "2_audio")
        
        if not os.path.exists(carpeta_audio):
            print("❌ No se encontró carpeta de audio")
            return None
        
        # Buscar archivo de audio
        archivos_audio = [f for f in os.listdir(carpeta_audio) 
                         if f.lower().endswith(('.wav', '.mp3', '.m4a'))]
        
        if not archivos_audio:
            print("❌ No se encontró archivo de audio")
            return None
        
        ruta_audio = os.path.join(carpeta_audio, archivos_audio[0])
        carpeta_transcripcion = os.path.join(ruta_proyecto, "3_transcripcion")
        
        # Verificar si ya está transcrito
        if os.path.exists(carpeta_transcripcion):
            archivos_existentes = [f for f in os.listdir(carpeta_transcripcion) 
                                if f.lower().endswith(('.txt', '.json'))]
            if len(archivos_existentes) >= 1:
                print("✅ Audio ya transcrito anteriormente")
                return {'texto_completo': 'Transcripción existente'}
        
        # Crear carpeta de transcripción
        os.makedirs(carpeta_transcripcion, exist_ok=True)
        
        # Realizar transcripción automática con modelo small
        print("🎤 Transcribiendo audio automáticamente...")
        resultado = transcribir_con_whisper(ruta_audio, modelo='small')
        
        if not resultado:
            return None
        
        # Generar nombre base para archivos
        nombre_base = os.path.splitext(archivos_audio[0])[0]
        
        # Guardar transcripción completa en JSON
        archivo_json = os.path.join(carpeta_transcripcion, f"{nombre_base}_transcripcion.json")
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        # Generar archivo de texto plano
        archivo_txt = os.path.join(carpeta_transcripcion, f"{nombre_base}_texto.txt")
        with open(archivo_txt, 'w', encoding='utf-8') as f:
            f.write(resultado['texto_completo'])
        
        # Generar subtítulos SRT si hay segmentos
        if resultado['segmentos']:
            archivo_srt = os.path.join(carpeta_transcripcion, f"{nombre_base}_subtitulos.srt")
            generar_subtitulos_srt(resultado['segmentos'], archivo_srt)
        
        print(f"💾 Archivos guardados en: 3_transcripcion/")
        print(f"   📄 {nombre_base}_texto.txt")
        print(f"   📊 {nombre_base}_transcripcion.json")
        if resultado['segmentos']:
            print(f"   🎬 {nombre_base}_subtitulos.srt")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en transcripción automática: {e}")
        return None

def main():
    """Función para ejecutar el módulo independientemente"""
    print("🎤 TRANSCRIPCIÓN DE AUDIO A TEXTO")
    print("=" * 40)
    
    if not verificar_whisper():
        return
    
    # Buscar proyectos disponibles
    if not os.path.exists("downloads"):
        print("❌ No existe carpeta downloads")
        return
    
    proyectos = []
    for item in os.listdir("downloads"):
        ruta_proyecto = os.path.join("downloads", item)
        if os.path.isdir(ruta_proyecto):
            carpeta_audio = os.path.join(ruta_proyecto, "2_audio")
            carpeta_transcripcion = os.path.join(ruta_proyecto, "3_transcripcion")
            
            if os.path.exists(carpeta_audio):
                archivos_audio = [f for f in os.listdir(carpeta_audio) 
                                if f.lower().endswith(('.wav', '.mp3', '.m4a'))]
                
                ya_transcrito = False
                if os.path.exists(carpeta_transcripcion):
                    archivos_transcripcion = [f for f in os.listdir(carpeta_transcripcion) 
                                            if f.lower().endswith(('.txt', '.json'))]
                    ya_transcrito = len(archivos_transcripcion) > 0
                
                if archivos_audio and not ya_transcrito:
                    proyectos.append({'nombre': item, 'ruta': ruta_proyecto})
    
    if not proyectos:
        print("❌ No hay proyectos con audio para transcribir")
        return
    
    print(f"📂 PROYECTOS DISPONIBLES ({len(proyectos)}):")
    for i, proyecto in enumerate(proyectos, 1):
        print(f"{i}. {proyecto['nombre']}")
    
    try:
        seleccion = int(input(f"\nSelecciona proyecto (1-{len(proyectos)}): ")) - 1
        if 0 <= seleccion < len(proyectos):
            proyecto_elegido = proyectos[seleccion]
            transcribir_automatico(proyecto_elegido['ruta'])
        else:
            print("❌ Selección inválida")
    except ValueError:
        print("❌ Número inválido")
    except KeyboardInterrupt:
        print("\n❌ Cancelado")

if __name__ == "__main__":
    main()