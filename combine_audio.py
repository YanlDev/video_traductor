#!/usr/bin/env python3
import os
import subprocess

def combinar_audios_ffmpeg(audio_voces_es, audio_musica, archivo_salida, volumen_voces=1.0, volumen_musica=0.3):
    """Combina voces en español con música usando FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_voces_es,
            '-i', audio_musica,
            '-filter_complex', 
            f'[0:a]volume={volumen_voces}[voice];[1:a]volume={volumen_musica}[music];[voice][music]amix=inputs=2:duration=first[out]',
            '-map', '[out]',
            '-c:a', 'pcm_s16le',
            '-loglevel', 'error',
            archivo_salida
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Audios combinados: {os.path.basename(archivo_salida)}")
        return True
        
    except Exception as e:
        print(f"❌ Error combinando audios: {e}")
        return False

def verificar_video_tiene_audio(archivo_video):
    """Verifica que el video tenga audio integrado"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'a:0', 
            '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', 
            archivo_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Si hay output, significa que tiene audio
        tiene_audio = len(result.stdout.strip()) > 0
        
        if tiene_audio:
            print(f"✅ Video con audio integrado verificado")
            return True
        else:
            print(f"❌ Video NO tiene audio integrado")
            return False
            
    except Exception as e:
        print(f"⚠️  No se pudo verificar audio: {e}")
        return False

def combinar_video_audio_ffmpeg_mejorado(video_original, audio_combinado, video_final):
    """Combina video con audio y VERIFICA que funcione"""
    try:
        # Comando FFmpeg más explícito
        cmd = [
            'ffmpeg', '-y',
            '-i', video_original,
            '-i', audio_combinado,
            '-c:v', 'copy',              # Copiar video
            '-c:a', 'aac', '-b:a', '128k',  # Audio AAC 128k
            '-map', '0:v:0',             # Video del primer archivo
            '-map', '1:a:0',             # Audio del segundo archivo
            '-shortest',                 # Duración del más corto
            '-avoid_negative_ts', 'make_zero',
            '-loglevel', 'error',
            video_final
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # VERIFICAR que el video tenga audio
        if verificar_video_tiene_audio(video_final):
            print(f"✅ Video final con audio: {os.path.basename(video_final)}")
            return True
        else:
            print(f"❌ FALLO: Video sin audio integrado")
            return False
        
    except Exception as e:
        print(f"❌ Error generando video con audio: {e}")
        return False

def verificar_ffmpeg():
    """Verifica que FFmpeg esté disponible"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        print("❌ FFmpeg no encontrado. Instálalo desde: https://ffmpeg.org/")
        return False

def procesar_proyecto_completo(ruta_proyecto):
    """
    Proceso completo:
    1. Combina voces ES + música original
    2. Combina este audio con el video original
    """
    
    if not verificar_ffmpeg():
        return False
    
    print(f"🎬 Procesando proyecto: {os.path.basename(ruta_proyecto)}")
    
    # Definir rutas
    carpeta_original = os.path.join(ruta_proyecto, "1_original")
    carpeta_separado = os.path.join(ruta_proyecto, "audio_separado")
    carpeta_audio_es = os.path.join(ruta_proyecto, "5_audio_es")
    carpeta_final = os.path.join(ruta_proyecto, "6_final")
    
    # Buscar video original
    videos = [f for f in os.listdir(carpeta_original) 
              if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm'))]
    if not videos:
        print("❌ No se encontró video original")
        return False
    video_original = os.path.join(carpeta_original, videos[0])
    
    # Buscar música separada
    musica_files = [f for f in os.listdir(carpeta_separado) 
                   if 'accompaniment' in f.lower() and f.endswith('.wav')]
    if not musica_files:
        print("❌ No se encontró música separada")
        return False
    audio_musica = os.path.join(carpeta_separado, musica_files[0])
    
    # Buscar voces en español
    voces_es_files = [f for f in os.listdir(carpeta_audio_es) 
                    if f.endswith('.wav')]
    if not voces_es_files:
        print("❌ No se encontró audio en español")
        return False
    audio_voces_es = os.path.join(carpeta_audio_es, voces_es_files[0])
    
    # Crear carpeta final
    os.makedirs(carpeta_final, exist_ok=True)
    
    # Generar nombres de archivos
    nombre_base = os.path.splitext(videos[0])[0]
    audio_combinado = os.path.join(carpeta_final, f"{nombre_base}_audio_final.wav")
    video_final = os.path.join(carpeta_final, f"{nombre_base}_ESPAÑOL.mp4")
    
    # PASO 1: Combinar voces españolas + música original
    print("\n🎵 Paso 1: Combinando voces en español + música original...")
    if not combinar_audios_ffmpeg(audio_voces_es, audio_musica, audio_combinado):
        return False
    
    # PASO 2: Combinar audio final con video original
    print("\n🎬 Paso 2: Generando video final...")
    if not combinar_video_audio_ffmpeg_mejorado(video_original, audio_combinado, video_final):
        return False
    
    # Mostrar información del resultado
    try:
        tamaño = os.path.getsize(video_final) / 1024 / 1024
        print(f"\n🎉 ¡COMPLETADO!")
        print(f"📁 Video final: {video_final}")
        print(f"📊 Tamaño: {tamaño:.1f} MB")
    except:
        pass
    
    return True

def main():
    """Función principal - busca y procesa proyectos"""
    
    if not os.path.exists("downloads"):
        print("❌ No existe carpeta downloads")
        return
    
    # Buscar proyectos listos para procesar
    proyectos_listos = []
    
    for item in os.listdir("downloads"):
        ruta_proyecto = os.path.join("downloads", item)
        
        if not os.path.isdir(ruta_proyecto):
            continue
        
        # Verificar que tenga todos los archivos necesarios
        tiene_video = os.path.exists(os.path.join(ruta_proyecto, "1_original"))
        tiene_separado = os.path.exists(os.path.join(ruta_proyecto, "audio_separado"))
        tiene_audio_es = os.path.exists(os.path.join(ruta_proyecto, "5_audio_es"))
        
        if tiene_video and tiene_separado and tiene_audio_es:
            # Verificar que no tenga ya video final
            carpeta_final = os.path.join(ruta_proyecto, "6_final")
            ya_procesado = False
            
            if os.path.exists(carpeta_final):
                videos_finales = [f for f in os.listdir(carpeta_final) 
                                if f.lower().endswith(('.mp4', '.avi', '.mkv'))]
                ya_procesado = len(videos_finales) > 0
            
            if not ya_procesado:
                proyectos_listos.append((item, ruta_proyecto))
    
    if not proyectos_listos:
        print("❌ No hay proyectos listos para procesar")
        print("💡 Necesitas: video original + audio separado + audio en español")
        return
    
    # Mostrar proyectos disponibles
    print("📂 PROYECTOS LISTOS PARA VIDEO FINAL:")
    print("=" * 40)
    
    for i, (nombre, _) in enumerate(proyectos_listos, 1):
        print(f"{i}. {nombre}")
    
    # Seleccionar proyecto
    try:
        seleccion = int(input(f"\nSelecciona proyecto (1-{len(proyectos_listos)}): ")) - 1
        
        if 0 <= seleccion < len(proyectos_listos):
            nombre, ruta = proyectos_listos[seleccion]
            
            print(f"\n✅ Procesando: {nombre}")
            
            # Confirmar
            continuar = input("¿Continuar? (s/n): ").lower().strip()
            if continuar in ['s', 'si', 'sí', 'y', 'yes']:
                procesar_proyecto_completo(ruta)
            else:
                print("❌ Cancelado")
        else:
            print("❌ Selección inválida")
            
    except ValueError:
        print("❌ Número inválido")
    except KeyboardInterrupt:
        print("\n❌ Cancelado por usuario")

if __name__ == "__main__":
    main()