import os
import time
import subprocess
import gc
from pathlib import Path
from typing import Optional, Callable

from moviepy.video.io.VideoFileClip import VideoFileClip

from .interfaces import IAudioExtractor, IAudioSeparator, IAudioQualityAnalyzer
from .models import AudioExtractionResult, AudioSeparationResult, AudioProcessingProgress

class MoviePyAudioExtractor(IAudioExtractor):
    """Extractor de audio usando MoviePy + FFmpeg optimizado"""
    
    def extract_audio(self, video_path: str, output_path: str, format: str = "wav", sample_rate: int = 16000, progress_callback: Optional[Callable[[AudioProcessingProgress], None]] = None) -> AudioExtractionResult:
        """Extrae audio optimizado para Spleeter"""
        
        start_time = time.time()
        
        try:
            # Callback de progreso
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="extracting",
                    percentage=10,
                    current_step="Cargando video..."
                ))
            
            print("🎵 Cargando video...")
            video = VideoFileClip(video_path)
            
            if video.audio is None:
                video.close()
                return AudioExtractionResult(
                    success=False,
                    error_message="El video no contiene audio"
                )
            
            # Progreso
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="extracting",
                    percentage=30,
                    current_step="Extrayendo audio temporal..."
                ))
            
            # Crear archivo temporal
            temp_path = output_path.replace(f".{format}", f"_temp.{format}")
            
            print("🔧 Extrayendo audio temporal...")
            video.audio.write_audiofile(temp_path, logger=None, verbose=False)
            
            duration = video.duration
            video.close()
            
            # Progreso
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="extracting",
                    percentage=60,
                    current_step="Optimizando para Spleeter..."
                ))
            
            print("🚀 Optimizando audio para Spleeter...")
            
            # Optimizar con FFmpeg para Spleeter
            comando = [
                "ffmpeg", "-y", "-i", temp_path,
                "-ac", "1",  # Mono (Spleeter funciona mejor)
                "-ar", str(sample_rate),  # Sample rate optimizado
                "-acodec", "pcm_s16le",  # WAV PCM 16-bit
                "-af", "volume=1.2",  # Ligero boost de volumen
                "-loglevel", "error",
                "-hide_banner",
                output_path
            ]
            
            subprocess.run(comando, check=True, capture_output=True)
            
            # Limpiar temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Progreso final
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="extracting",
                    percentage=100,
                    current_step="Audio extraído correctamente"
                ))
            
            # Calcular estadísticas
            file_size_mb = os.path.getsize(output_path) / 1024 / 1024
            processing_time = time.time() - start_time
            
            print(f"✅ Audio extraído: {file_size_mb:.1f}MB en {processing_time:.1f}s")
            
            return AudioExtractionResult(
                success=True,
                audio_file_path=output_path,
                original_video_path=video_path,
                audio_format=format,
                sample_rate=sample_rate,
                duration_seconds=duration,
                file_size_mb=file_size_mb
            )
            
        except Exception as e:
            return AudioExtractionResult(
                success=False,
                error_message=f"Error extrayendo audio: {str(e)}"
            )


    """Separador de audio usando Spleeter (Spotify)"""
    
    def __init__(self, model_name: str = "spleeter:2stems-16kHz"):
        """
        Inicializar con modelo específico
        Opciones: 2stems-16kHz, 4stems-16kHz, 5stems-16kHz
        """
        self.model_name = model_name
        self._separator = None
        self._initialize_separator()
    
    def _initialize_separator(self):
        """Inicializa Spleeter de forma lazy"""
        try:
            from spleeter.separator import Separator
            
            print(f"🤖 Inicializando Spleeter modelo '{self.model_name}'...")
            self._separator = Separator(self.model_name)
            print("✅ Spleeter listo para usar")
            
        except ImportError:
            raise ImportError(
                "Spleeter no está instalado. Instalar con: pip install spleeter"
            )
        except Exception as e:
            raise RuntimeError(f"Error inicializando Spleeter: {str(e)}")
    
    def separate_audio(self, audio_path: str, output_directory: str,
                      progress_callback: Optional[Callable[[AudioProcessingProgress], None]] = None) -> AudioSeparationResult:
        """Separa audio usando Spleeter"""
        
        start_time = time.time()
        
        try:
            # Verificar que el archivo existe
            if not os.path.exists(audio_path):
                return AudioSeparationResult(
                    success=False,
                    error_message=f"Archivo de audio no encontrado: {audio_path}"
                )
            
            # Crear directorio de salida
            os.makedirs(output_directory, exist_ok=True)
            
            # Progreso inicial
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=10,
                    current_step="Preparando separación..."
                ))
            
            print("🎵 Iniciando separación con Spleeter...")
            print(f"📁 Audio: {os.path.basename(audio_path)}")
            print(f"🤖 Modelo: {self.model_name}")
            
            # Cargar audio
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=20,
                    current_step="Cargando audio..."
                ))
            
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Cargar audio para Spleeter
            waveform, sample_rate = librosa.load(audio_path, sr=None, mono=False)
            
            # Asegurar formato estéreo para Spleeter
            if len(waveform.shape) == 1:
                waveform = np.stack([waveform, waveform])
            
            # Progreso
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=40,
                    current_step="Ejecutando separación IA..."
                ))
            
            # Ejecutar separación
            print("🧠 Ejecutando separación con IA...")
            prediction = self._separator.separate(waveform)
            
            # Progreso
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=80,
                    current_step="Guardando archivos separados..."
                ))
            
            # Guardar resultados
            base_name = Path(audio_path).stem
            vocals_path = os.path.join(output_directory, f"{base_name}_vocals.wav")
            accompaniment_path = os.path.join(output_directory, f"{base_name}_accompaniment.wav")
            
            # Guardar vocals
            vocals = prediction['vocals']
            sf.write(vocals_path, vocals.T, sample_rate)
            
            # Guardar accompaniment
            accompaniment = prediction['accompaniment']
            sf.write(accompaniment_path, accompaniment.T, sample_rate)
            
            # Progreso final
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=100,
                    current_step="Separación completada"
                ))
            
            processing_time = time.time() - start_time
            
            print(f"✅ Separación completada en {processing_time:.1f}s")
            print(f"   🎤 Vocals: {os.path.basename(vocals_path)}")
            print(f"   🎵 Música: {os.path.basename(accompaniment_path)}")
            
            # Analizar calidad
            quality_analyzer = BasicAudioQualityAnalyzer()
            quality_score = quality_analyzer.analyze_separation_quality(vocals_path, accompaniment_path)
            
            # Limpiar memoria
            del prediction, waveform
            gc.collect()
            
            return AudioSeparationResult(
                success=True,
                vocals_path=vocals_path,
                accompaniment_path=accompaniment_path,
                original_audio_path=audio_path,
                separation_method=f"Spleeter-{self.model_name}",
                processing_time_seconds=processing_time,
                quality_score=quality_score
            )
            
        except Exception as e:
            return AudioSeparationResult(
                success=False,
                error_message=f"Error en separación Spleeter: {str(e)}"
            )

class LibrosaFallbackSeparator(IAudioSeparator):
    """Separador de fallback usando Librosa (tu código actual)"""
    
    def separate_audio(self, audio_path: str, output_directory: str,
                      progress_callback: Optional[Callable[[AudioProcessingProgress], None]] = None) -> AudioSeparationResult:
        """Separación básica con Librosa como fallback"""
        
        start_time = time.time()
        
        try:
            print("📊 Usando separación Librosa (fallback)...")
            
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=20,
                    current_step="Cargando con Librosa..."
                ))
            
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Cargar audio
            y, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=50,
                    current_step="Aplicando HPSS..."
                ))
            
            # Tu algoritmo actual de separación
            y_harmonic, y_percussive = librosa.effects.hpss(y, margin=3.0)
            
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=80,
                    current_step="Guardando resultados..."
                ))
            
            # Guardar archivos
            os.makedirs(output_directory, exist_ok=True)
            base_name = Path(audio_path).stem
            
            vocals_path = os.path.join(output_directory, f"{base_name}_vocals.wav")
            accompaniment_path = os.path.join(output_directory, f"{base_name}_accompaniment.wav")
            
            # Usar percussive como "vocals" y harmonic como "accompaniment"
            sf.write(vocals_path, y_percussive, sr)
            sf.write(accompaniment_path, y_harmonic, sr)
            
            processing_time = time.time() - start_time
            
            if progress_callback:
                progress_callback(AudioProcessingProgress(
                    stage="separating",
                    percentage=100,
                    current_step="Separación básica completada"
                ))
            
            print(f"✅ Separación Librosa completada en {processing_time:.1f}s")
            
            return AudioSeparationResult(
                success=True,
                vocals_path=vocals_path,
                accompaniment_path=accompaniment_path,
                original_audio_path=audio_path,
                separation_method="Librosa-HPSS",
                processing_time_seconds=processing_time,
                quality_score=0.6  # Score fijo para Librosa
            )
            
        except Exception as e:
            return AudioSeparationResult(
                success=False,
                error_message=f"Error en separación Librosa: {str(e)}"
            )

class BasicAudioQualityAnalyzer(IAudioQualityAnalyzer):
    """Analizador básico de calidad de separación"""
    
    def analyze_separation_quality(self, vocals_path: str, accompaniment_path: str) -> float:
        """Analiza calidad básica basada en energía y separación"""
        
        try:
            import librosa
            import numpy as np
            
            # Cargar archivos
            vocals, sr = librosa.load(vocals_path, sr=22050)
            accompaniment, sr = librosa.load(accompaniment_path, sr=22050)
            
            # Calcular energías
            vocals_energy = np.mean(vocals ** 2)
            accompaniment_energy = np.mean(accompaniment ** 2)
            
            # Verificar que ambos tienen contenido
            if vocals_energy < 0.001 or accompaniment_energy < 0.001:
                return 0.3  # Separación pobre
            
            # Calcular ratio de separación
            total_energy = vocals_energy + accompaniment_energy
            energy_balance = min(vocals_energy, accompaniment_energy) / max(vocals_energy, accompaniment_energy)
            
            # Score basado en balance (0.5 = perfecto balance)
            balance_score = 1.0 - abs(0.5 - energy_balance) * 2
            
            # Score final (entre 0.4 y 0.95)
            quality_score = 0.4 + (balance_score * 0.55)
            
            return min(quality_score, 0.95)
            
        except Exception:
            return 0.5  # Score neutral si no se puede analizar