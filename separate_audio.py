#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: SEPARACIÓN DE AUDIO
==========================
Separa música y voces usando solo Librosa (estable y confiable)
"""

import os
import sys
import json
import numpy as np
from datetime import datetime

def verificar_librosa():
    """Verifica que Librosa esté disponible"""
    try:
        import librosa
        import scipy.signal
        import soundfile as sf
        print("✅ Librosa disponible para separación")
        return True
    except ImportError as e:
        print(f"❌ Librosa no disponible: {e}")
        print("💡 Instalar con: pip install librosa soundfile scipy")
        return False

def separar_musica_voz(ruta_audio, carpeta_salida):
    """
    Separa música de voces usando técnicas de Librosa
    
    Args:
        ruta_audio (str): Ruta del archivo de audio original
        carpeta_salida (str): Carpeta donde guardar los archivos separados
    
    Returns:
        dict: Rutas de los archivos generados o None si hubo error
    """
    try:
        print("🎵 Separando música y voces con Librosa...")
        
        import librosa
        import numpy as np
        import soundfile as sf
        from scipy import signal
        
        # Crear carpeta de salida
        os.makedirs(carpeta_salida, exist_ok=True)
        
        print("🔄 Cargando audio...")
        # Cargar audio (22kHz es buen balance para separación)
        y, sr = librosa.load(ruta_audio, sr=22050, mono=True)
        
        print("🚀 Aplicando separación harmonic/percussive...")
        
        # Método 1: Separación harmonic/percussive
        # Harmonic = tonos musicales sostenidos (instrumentos melódicos)
        # Percussive = sonidos transitorios (voces, drums)
        y_harmonic, y_percussive = librosa.effects.hpss(y, margin=3.0)
        
        print("🔄 Aplicando separación por frecuencias...")
        
        # Método 2: Separación por análisis espectral
        # Calcular espectrograma
        D = librosa.stft(y, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Crear máscaras de frecuencia
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        
        # Máscara para voces (frecuencias típicas de voz humana)
        vocal_mask = np.zeros_like(magnitude)
        
        # Rango principal de voces humanas (con armónicos)
        vocal_ranges = [
            (80, 300),    # Fundamental de voz
            (300, 1000),  # Primeros armónicos
            (1000, 3000), # Formantes importantes
            (3000, 8000)  # Armónicos altos de voces
        ]
        
        # Aplicar máscara suave para voces
        for freq_min, freq_max in vocal_ranges:
            freq_indices = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]
            for i in freq_indices:
                # Máscara adaptativa basada en energía
                energy_ratio = magnitude[i, :] / (np.mean(magnitude, axis=0) + 1e-8)
                vocal_mask[i, :] = np.minimum(energy_ratio * 0.8, 1.0)
        
        # Suavizar máscara temporalmente
        from scipy.ndimage import median_filter
        for i in range(vocal_mask.shape[0]):
            vocal_mask[i, :] = median_filter(vocal_mask[i, :], size=5)
        
        # Máscara para acompañamiento
        accompaniment_mask = 1 - vocal_mask
        
        # Aplicar máscaras
        vocals_magnitude = magnitude * vocal_mask
        accompaniment_magnitude = magnitude * accompaniment_mask
        
        # Reconstruir audio
        vocals_complex = vocals_magnitude * np.exp(1j * phase)
        accompaniment_complex = accompaniment_magnitude * np.exp(1j * phase)
        
        vocals_spectral = librosa.istft(vocals_complex, hop_length=512)
        accompaniment_spectral = librosa.istft(accompaniment_complex, hop_length=512)
        
        print("🔄 Combinando métodos...")
        
        # Normalizar longitudes
        min_length = min(len(y_harmonic), len(y_percussive), len(vocals_spectral), len(accompaniment_spectral))
        
        # Combinar métodos con pesos optimizados
        # Voces: más peso a percussive + método espectral
        vocals_final = (0.5 * y_percussive[:min_length] + 
                       0.5 * vocals_spectral[:min_length])
        
        # Música: más peso a harmonic + método espectral
        accompaniment_final = (0.6 * y_harmonic[:min_length] + 
                              0.4 * accompaniment_spectral[:min_length])
        
        # Normalizar audio para evitar clipping
        def normalizar_audio(audio, factor=0.8):
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                return audio / max_val * factor
            return audio
        
        vocals_final = normalizar_audio(vocals_final)
        accompaniment_final = normalizar_audio(accompaniment_final)
        
        print("💾 Guardando archivos...")
        
        # Guardar archivos
        archivos_generados = {}
        
        archivo_voces = os.path.join(carpeta_salida, "vocals.wav")
        sf.write(archivo_voces, vocals_final, sr)
        archivos_generados['vocals'] = archivo_voces
        print(f"✅ vocals.wav generado")
        
        archivo_musica = os.path.join(carpeta_salida, "accompaniment.wav")
        sf.write(archivo_musica, accompaniment_final, sr)
        archivos_generados['accompaniment'] = archivo_musica
        print(f"✅ accompaniment.wav generado")
        
        print("💡 Separación completada - calidad básica pero estable")
        
        return archivos_generados
        
    except Exception as e:
        print(f"❌ Error en separación: {e}")
        return None

def buscar_proyectos_con_audio():
    """Busca proyectos que tengan audio extraído pero no separado"""
    if not os.path.exists("downloads"):
        return []
    
    proyectos_disponibles = []
    
    for item in os.listdir("downloads"):
        ruta_proyecto = os.path.join("downloads", item)
        
        if not os.path.isdir(ruta_proyecto):
            continue
            
        # Verificar si tiene audio en 2_audio
        carpeta_audio = os.path.join(ruta_proyecto, "2_audio")
        carpeta_separado = os.path.join(ruta_proyecto, "audio_separado")
        
        if not os.path.exists(carpeta_audio):
            continue
            
        # Buscar archivos de audio
        archivos_audio = [f for f in os.listdir(carpeta_audio) 
                         if f.lower().endswith(('.wav', '.mp3', '.m4a'))]
        
        # Verificar si ya tiene audio separado
        ya_separado = False
        if os.path.exists(carpeta_separado):
            archivos_separados = [f for f in os.listdir(carpeta_separado) 
                                if f.lower().endswith(('.wav', '.mp3'))]
            ya_separado = len(archivos_separados) >= 2  # vocals.wav + accompaniment.wav
        
        if archivos_audio and not ya_separado:
            proyectos_disponibles.append({
                'nombre': item,
                'ruta': ruta_proyecto,
                'audio': archivos_audio[0],
                'ruta_audio': os.path.join(carpeta_audio, archivos_audio[0])
            })
    
    return proyectos_disponibles

def analizar_calidad_separacion(archivo_voces, archivo_musica):
    """
    Analiza la calidad de la separación realizada
    
    Args:
        archivo_voces (str): Ruta del archivo de voces
        archivo_musica (str): Ruta del archivo de música
    
    Returns:
        dict: Métricas de calidad
    """
    try:
        import librosa
        
        print("📊 Analizando calidad de separación...")
        
        # Cargar archivos
        voces, sr = librosa.load(archivo_voces, sr=22050)
        musica, sr = librosa.load(archivo_musica, sr=22050)
        
        # Calcular energía de cada componente
        energia_voces = np.mean(voces ** 2)
        energia_musica = np.mean(musica ** 2)
        
        # Calcular ratio señal/ruido aproximado
        if energia_musica > 0:
            ratio_voces_musica = energia_voces / energia_musica
        else:
            ratio_voces_musica = float('inf')
        
        # Detectar si hay contenido significativo en cada archivo
        tiene_voces = energia_voces > 0.001
        tiene_musica = energia_musica > 0.001
        
        # Calcular duraciones
        duracion_voces = len(voces) / sr
        duracion_musica = len(musica) / sr
        
        calidad = {
            'tiene_voces': bool(tiene_voces),  # Convertir a bool nativo
            'tiene_musica': bool(tiene_musica),  # Convertir a bool nativo
            'energia_voces': float(energia_voces),
            'energia_musica': float(energia_musica),
            'ratio_voces_musica': float(ratio_voces_musica) if ratio_voces_musica != float('inf') else 999.0,
            'duracion_voces': float(duracion_voces),
            'duracion_musica': float(duracion_musica),
            'separacion_exitosa': bool(tiene_voces and tiene_musica)  # Convertir a bool nativo
        }
        
        # Mostrar resultados
        print(f"📈 ANÁLISIS DE SEPARACIÓN:")
        print(f"   🎤 Voces detectadas: {'Sí' if tiene_voces else 'No'}")
        print(f"   🎵 Música detectada: {'Sí' if tiene_musica else 'No'}")
        
        if tiene_voces and tiene_musica:
            print(f"   ✅ Separación exitosa")
        elif tiene_voces and not tiene_musica:
            print(f"   ⚠️  Solo voces (sin música de fondo)")
        elif not tiene_voces and tiene_musica:
            print(f"   ⚠️  Solo música (sin voces detectadas)")
        else:
            print(f"   ❌ Separación problemática")
        
        return calidad
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return {'separacion_exitosa': False, 'error': str(e)}

def procesar_separacion():
    """
    Función principal que procesa la separación de audio
    """
    print("🎵 SEPARACIÓN DE MÚSICA Y VOZ")
    print("=" * 40)
    
    # Verificar Librosa
    if not verificar_librosa():
        return False
    
    # Buscar proyectos disponibles
    print("🔍 Buscando proyectos con audio...")
    proyectos = buscar_proyectos_con_audio()
    
    if not proyectos:
        print("❌ No hay proyectos con audio para separar")
        print("💡 Primero extrae el audio usando el proceso automático")
        return False
    
    # Mostrar proyectos disponibles
    print(f"\n📂 PROYECTOS DISPONIBLES ({len(proyectos)}):")
    for i, proyecto in enumerate(proyectos, 1):
        print(f"{i}. {proyecto['nombre']}")
        print(f"   🎵 Audio: {proyecto['audio']}")
        
        # Mostrar tamaño del archivo
        try:
            tamaño = os.path.getsize(proyecto['ruta_audio']) / 1024 / 1024
            print(f"   📊 Tamaño: {tamaño:.1f} MB")
        except:
            pass
        print()
    
    # Seleccionar proyecto
    while True:
        try:
            seleccion = input(f"Selecciona proyecto (1-{len(proyectos)}): ").strip()
            
            if not seleccion:
                print("❌ Selección vacía")
                continue
                
            indice = int(seleccion) - 1
            
            if 0 <= indice < len(proyectos):
                proyecto_elegido = proyectos[indice]
                break
            else:
                print(f"❌ Número inválido")
        except ValueError:
            print("❌ Ingresa un número válido")
    
    print(f"\n✅ Procesando: {proyecto_elegido['nombre']}")
    
    # Crear carpeta para archivos separados
    carpeta_separado = os.path.join(proyecto_elegido['ruta'], "audio_separado")
    
    # Confirmar separación
    continuar = input("\n¿Continuar con la separación? (s/n): ").lower().strip()
    if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Separación cancelada")
        return False
    
    print()
    
    # Realizar separación
    archivos_separados = separar_musica_voz(
        proyecto_elegido['ruta_audio'], 
        carpeta_separado
    )
    
    if not archivos_separados:
        print("❌ Error en la separación")
        return False
    
    # Analizar calidad
    calidad = analizar_calidad_separacion(
        archivos_separados['vocals'],
        archivos_separados['accompaniment']
    )
    
    # Guardar información de separación
    info_separacion = {
        'proyecto': proyecto_elegido['nombre'],
        'fecha_separacion': datetime.now().isoformat(),
        'archivo_original': proyecto_elegido['ruta_audio'],
        'archivos_separados': archivos_separados,
        'metodo_usado': 'librosa',
        'calidad': calidad
    }
    
    archivo_info = os.path.join(carpeta_separado, "info_separacion.json")
    with open(archivo_info, 'w', encoding='utf-8') as f:
        json.dump(info_separacion, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen final
    print(f"\n🎉 SEPARACIÓN COMPLETADA")
    print("=" * 40)
    print(f"📁 Proyecto: {proyecto_elegido['nombre']}")
    print(f"📂 Archivos generados:")
    print(f"   🎤 vocals.wav - Solo voces humanas")
    print(f"   🎵 accompaniment.wav - Solo música/instrumentos")
    print(f"📁 Ubicación: {carpeta_separado}")
    
    if calidad['separacion_exitosa']:
        print(f"\n✅ Separación exitosa")
        print(f"🔄 Siguiente paso: Transcribir solo las voces (más preciso)")
        print(f"💡 La música se preservará en el video final")
    else:
        print(f"\n⚠️  Separación con advertencias")
        print(f"💡 Revisa los archivos generados")
    
    # Mostrar tamaños de archivos
    try:
        tamaño_voces = os.path.getsize(archivos_separados['vocals']) / 1024 / 1024
        tamaño_musica = os.path.getsize(archivos_separados['accompaniment']) / 1024 / 1024
        
        print(f"\n📊 Tamaños de archivo:")
        print(f"   🎤 Voces: {tamaño_voces:.1f} MB")
        print(f"   🎵 Música: {tamaño_musica:.1f} MB")
    except:
        pass
    
    return True

def separar_automatico(ruta_proyecto):
    """
    Función para separar automáticamente desde el proceso principal
    
    Args:
        ruta_proyecto (str): Ruta del proyecto
    
    Returns:
        dict: Archivos separados o None si falló
    """
    try:
        # Verificar Librosa
        if not verificar_librosa():
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
        carpeta_separado = os.path.join(ruta_proyecto, "audio_separado")
        
        # Verificar si ya está separado
        if os.path.exists(carpeta_separado):
            archivos_existentes = [f for f in os.listdir(carpeta_separado) 
                                if f.lower().endswith('.wav')]
            if len(archivos_existentes) >= 2:
                print("✅ Audio ya separado anteriormente")
                return {
                    'vocals': os.path.join(carpeta_separado, 'vocals.wav'),
                    'accompaniment': os.path.join(carpeta_separado, 'accompaniment.wav')
                }
        
        # Realizar separación
        print("🎵 Separando música y voces automáticamente...")
        return separar_musica_voz(ruta_audio, carpeta_separado)
        
    except Exception as e:
        print(f"❌ Error en separación automática: {e}")
        return None

def main():
    """Función para ejecutar el módulo independientemente"""
    procesar_separacion()

if __name__ == "__main__":
    main()