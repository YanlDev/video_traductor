#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE INSTALACIÓN - TRADUCTOR DE VIDEOS
==========================================
Instala todas las dependencias necesarias y verifica la configuración
"""

import subprocess
import sys
import os

def ejecutar_comando(comando):
    """Ejecuta un comando y devuelve True si fue exitoso"""
    try:
        print(f"🔄 Ejecutando: {comando}")
        result = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"   Salida: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def verificar_python():
    """Verifica la versión de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print("✅ Versión de Python compatible")
    return True

def verificar_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg está instalado")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg no encontrado")
    print("💡 Instalar FFmpeg:")
    print("   Windows: Descargar desde https://ffmpeg.org/download.html")
    print("   macOS: brew install ffmpeg")
    print("   Ubuntu: sudo apt install ffmpeg")
    return False

def instalar_dependencias():
    """Instala todas las dependencias de Python"""
    print("\n📦 INSTALANDO DEPENDENCIAS DE PYTHON")
    print("=" * 50)
    
    # Actualizar pip primero
    if not ejecutar_comando(f"{sys.executable} -m pip install --upgrade pip"):
        print("⚠️  No se pudo actualizar pip, continuando...")
    
    # Instalar dependencias básicas primero
    dependencias_basicas = [
        "wheel",
        "setuptools",
        "certifi",
        "requests"
    ]
    
    for dep in dependencias_basicas:
        print(f"\n🔧 Instalando {dep}...")
        if not ejecutar_comando(f"{sys.executable} -m pip install {dep}"):
            print(f"⚠️  Error instalando {dep}")
    
    # Instalar dependencias científicas con versiones específicas
    dependencias_cientificas = [
        "numpy>=1.24.0,<1.26.0",  # Versión compatible con librosa
        "scipy>=1.11.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.1"
    ]
    
    print(f"\n🧬 Instalando dependencias científicas...")
    for dep in dependencias_cientificas:
        print(f"   📊 {dep}")
        if not ejecutar_comando(f"{sys.executable} -m pip install \"{dep}\""):
            print(f"⚠️  Error instalando {dep}")
    
    # Instalar dependencias principales
    dependencias_principales = [
        "yt-dlp>=2023.12.30",
        "moviepy>=1.0.3",
        "ffmpeg-python>=0.2.0",
        "openai-whisper>=20231117",
        "openai>=1.35.0",
        "edge-tts>=6.1.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.65.0"
    ]
    
    print(f"\n🎬 Instalando dependencias principales...")
    for dep in dependencias_principales:
        print(f"   🔧 {dep}")
        if not ejecutar_comando(f"{sys.executable} -m pip install \"{dep}\""):
            print(f"⚠️  Error instalando {dep}")
    
    # Google Translate (problemático, instalación especial)
    print(f"\n🌐 Instalando Google Translate...")
    # Desinstalar versión anterior si existe
    ejecutar_comando(f"{sys.executable} -m pip uninstall googletrans -y")
    # Instalar versión específica que funciona
    if not ejecutar_comando(f"{sys.executable} -m pip install googletrans==4.0.0rc1"):
        print("⚠️  Error instalando Google Translate")
        print("💡 Esto es opcional, se puede usar solo OpenAI")

def crear_archivo_env():
    """Crea archivo .env de ejemplo"""
    if not os.path.exists('.env'):
        print("\n📝 Creando archivo .env de ejemplo...")
        
        contenido_env = """# CONFIGURACIÓN DEL TRADUCTOR DE VIDEOS
# =====================================

# OpenAI API Key (opcional pero recomendado para mejor calidad)
# Obtener en: https://platform.openai.com/api-keys
OPENAI_API_KEY=tu_api_key_aqui

# Configuraciones opcionales
# WHISPER_MODEL=small  # tiny, base, small, medium, large
# TTS_VOICE=es-ES-ElviraNeural  # Voz específica para TTS
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(contenido_env)
        
        print("✅ Archivo .env creado")
        print("💡 Edita .env y agrega tu API key de OpenAI para mejor calidad")
    else:
        print("✅ Archivo .env ya existe")

def verificar_instalacion():
    """Verifica que todo esté instalado correctamente"""
    print("\n🔍 VERIFICANDO INSTALACIÓN")
    print("=" * 40)
    
    modulos = [
        ('yt_dlp', 'Descarga de videos'),
        ('moviepy', 'Procesamiento de video'),
        ('librosa', 'Separación de audio'),
        ('whisper', 'Transcripción'),
        ('openai', 'Traducción con IA'),
        ('edge_tts', 'Síntesis de voz'),
        ('googletrans', 'Google Translate (opcional)')
    ]
    
    total_ok = 0
    for modulo, descripcion in modulos:
        try:
            __import__(modulo)
            print(f"✅ {modulo} - {descripcion}")
            total_ok += 1
        except ImportError:
            print(f"❌ {modulo} - {descripcion}")
    
    print(f"\n📊 Instalación: {total_ok}/{len(modulos)} módulos disponibles")
    
    if total_ok >= len(modulos) - 1:  # Permitir que google translate falle
        print("🎉 ¡Instalación exitosa!")
        return True
    else:
        print("⚠️  Faltan dependencias importantes")
        return False

def main():
    """Función principal de instalación"""
    print("🎬 INSTALADOR - TRADUCTOR DE VIDEOS AL ESPAÑOL")
    print("=" * 60)
    print("Este script instalará todas las dependencias necesarias")
    print()
    
    # Verificar Python
    if not verificar_python():
        print("❌ Versión de Python incompatible")
        sys.exit(1)
    
    # Verificar FFmpeg
    if not verificar_ffmpeg():
        print("\n⚠️  FFmpeg es requerido para el procesamiento de video")
        respuesta = input("¿Continuar sin FFmpeg? (s/n): ").lower().strip()
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Instalación cancelada")
            sys.exit(1)
    
    # Instalar dependencias
    print("\n🚀 Iniciando instalación de dependencias...")
    instalar_dependencias()
    
    # Crear archivo .env
    crear_archivo_env()
    
    # Verificar instalación
    if verificar_instalacion():
        print("\n🎊 ¡INSTALACIÓN COMPLETADA!")
        print("=" * 40)
        print("✅ Todas las dependencias están instaladas")
        print("🚀 Puedes ejecutar: python main.py")
        print()
        print("💡 SIGUIENTE PASO:")
        print("   1. Edita el archivo .env con tu API key de OpenAI")
        print("   2. Ejecuta: python main.py")
        print("   3. Ingresa una URL de YouTube")
    else:
        print("\n❌ Instalación incompleta")
        print("💡 Revisa los errores arriba e intenta de nuevo")

if __name__ == "__main__":
    main()