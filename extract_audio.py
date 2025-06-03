from moviepy.video.io.VideoFileClip import VideoFileClip
import subprocess
import os

def extraer_audio_optimizado(ruta_video, ruta_audio_salida, mostrar_progreso_callback=None):
    """
    Extrae audio del video, luego lo convierte a formato WAV 16kHz mono usando ffmpeg.
    """
    try:
        print("🎵 Cargando video...")
        video = VideoFileClip(ruta_video)
        
        if video.audio is None:
            print("❌ El video no contiene audio")
            video.close()
            return False
        
        print("🔧 Extrayendo audio temporal...")
        ruta_audio_temporal = ruta_audio_salida.replace(".wav", "_temp.wav")
        video.audio.write_audiofile(ruta_audio_temporal, logger=None)
        video.close()
        
        print("🚀 Convirtiendo audio a formato optimizado...")
        
        # ffmpeg conversion (silencioso)
        comando = [
            "ffmpeg", "-y", "-i", ruta_audio_temporal,
            "-ac", "1",           # Mono
            "-ar", "16000",       # 16kHz
            "-acodec", "pcm_s16le",  # WAV PCM 16-bit
            "-af", "volume=1.5",  # Aumentar volumen
            "-loglevel", "error", # Solo errores
            "-hide_banner",       # Sin banner
            ruta_audio_salida
        ]
        subprocess.run(comando, check=True, capture_output=True)
        
        os.remove(ruta_audio_temporal)
        
        print("✅ Audio optimizado generado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False