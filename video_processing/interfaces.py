"""Interfaces/contratos del sistema"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from .models import VideoInfo, DownloadProgress, DownloadResult, AudioExtractionResult, AudioSeparationResult, AudioProcessingProgress

# INTERFACES PARA DESCARGA DE VIDEOS
class IVideoInfoExtractor(ABC):
    """Interface para extraer información de videos"""
    
    @abstractmethod
    def extract_info(self, url: str) -> Optional[VideoInfo]:
        """Extrae información básica del video"""
        pass

class IVideoDownloader(ABC):
    """Interface para descargar videos"""
    
    @abstractmethod
    def download(self, url: str, output_path: str, 
                progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> DownloadResult:
        """Descarga un video"""
        pass

class IFileNameSanitizer(ABC):
    """Interface para limpiar nombres de archivos"""
    
    @abstractmethod
    def sanitize(self, filename: str, max_length: int = 30) -> str:
        """Limpia y valida nombres de archivos"""
        pass

class IProgressDisplay(ABC):
    """Interface para mostrar progreso"""
    
    @abstractmethod
    def show_progress(self, progress: DownloadProgress) -> None:
        """Muestra el progreso de descarga"""
        pass

# INTERFACES PARA EXTRACCION Y SEPARACION DE AUDIO
class IAudioExtractor(ABC):
    """Interface para extraer audio de videos"""
    
    @abstractmethod
    def extract_audio(self, video_path: str, output_path: str, format: str = "wav", sample_rate: int = 16000, progress_callback: Optional[Callable[[AudioProcessingProgress], None]] = None) -> AudioExtractionResult:
        """Extrae audio del video en el formato especificado"""
        pass

class IAudioSeparator(ABC):
    """Interface para separar audio en componentes"""
    
    @abstractmethod
    def separate_audio(self, audio_path: str, output_directory: str,
                      progress_callback: Optional[Callable[[AudioProcessingProgress], None]] = None) -> AudioSeparationResult:
        """Separa audio en voces y acompañamiento"""
        pass

class IAudioQualityAnalyzer(ABC):
    """Interface para analizar calidad de separación"""
    
    @abstractmethod
    def analyze_separation_quality(self, vocals_path: str, accompaniment_path: str) -> float:
        """Analiza y retorna score de calidad (0-1)"""
        pass