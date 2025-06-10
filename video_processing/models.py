"""Modelos de datos para el sistema de descarga"""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path

#MODELOS PARA DESCARGA DE VIDEOS
@dataclass
class VideoInfo:
    """Información del video"""
    titulo: str
    duracion: int
    canal: str
    id: str
    url: str
    
    def get_duration_formatted(self) -> str:
        """Formatea la duración de manera legible"""
        if not self.duracion:
            return "Desconocida"
        
        horas = self.duracion // 3600
        minutos = (self.duracion % 3600) // 60
        segs = self.duracion % 60
        
        if horas > 0:
            return f"{int(horas):02d}:{int(minutos):02d}:{int(segs):02d}"
        else:
            return f"{int(minutos):02d}:{int(segs):02d}"

@dataclass
class DownloadProgress:
    """Progreso de descarga"""
    percentage: float
    downloaded_bytes: int
    total_bytes: Optional[int]
    status: str
    message: str = "Descargando"

@dataclass
class DownloadResult:
    """Resultado de descarga"""
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    video_info: Optional[VideoInfo] = None
    
    
#MODELO PARA EXTRACCION Y SEPARACION DE AUDIO
@dataclass
class AudioExtractionResult:
    """Resultado de extracción de audio"""
    success: bool
    audio_file_path: Optional[str] = None
    original_video_path: Optional[str] = None
    audio_format: str = "wav"
    sample_rate: int = 16000
    duration_seconds: float = 0.0
    file_size_mb: float = 0.0
    error_message: Optional[str] = None

@dataclass
class AudioSeparationResult:
    """Resultado de separación de audio"""
    success: bool
    vocals_path: Optional[str] = None
    accompaniment_path: Optional[str] = None
    original_audio_path: Optional[str] = None
    separation_method: str = ""
    processing_time_seconds: float = 0.0
    quality_score: float = 0.0  # 0-1, estimación de calidad
    error_message: Optional[str] = None

@dataclass
class AudioProcessingProgress:
    """Progreso de procesamiento de audio"""
    stage: str  # "extracting", "separating", "analyzing"
    percentage: float
    current_step: str
    estimated_time_remaining: float = 0.0