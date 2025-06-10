"""Servicios principales del sistema"""

import os
from typing import Optional, Callable
from .interfaces import IVideoDownloader, IVideoInfoExtractor  
from .models import DownloadResult, DownloadProgress

class VideoDownloadService:
    """Servicio principal para descarga de videos"""
    
    def __init__(self, downloader: IVideoDownloader, info_extractor: IVideoInfoExtractor):
        """Constructor con inyección de dependencias"""
        self.downloader = downloader
        self.info_extractor = info_extractor
    
    def download_video(self, url: str, output_directory: str, 
                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
                      ask_confirmation: bool = True) -> DownloadResult:
        """Descarga un video completo con validaciones"""
        
        # Validar URL
        if not self._is_valid_youtube_url(url):
            return DownloadResult(
                success=False,
                error_message="URL de YouTube no válida"
            )
        
        # Crear directorio
        os.makedirs(output_directory, exist_ok=True)
        
        # Extraer información
        print("🔍 Obteniendo información del video...")
        video_info = self.info_extractor.extract_info(url)
        
        if not video_info:
            return DownloadResult(
                success=False,
                error_message="No se pudo obtener información del video"
            )
        
        # Mostrar información
        self._display_video_info(video_info)
        
        # Confirmar descarga (opcional)
        if ask_confirmation and not self._confirm_download():
            return DownloadResult(
                success=False,
                error_message="Descarga cancelada por el usuario"
            )
        
        # Descargar
        print("\n🚀 Iniciando descarga...")
        return self.downloader.download(url, output_directory, progress_callback)
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """Valida si es una URL de YouTube"""
        valid_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
        return any(domain in url.lower() for domain in valid_domains)
    
    def _display_video_info(self, video_info) -> None:
        """Muestra información del video"""
        print("\n📊 INFORMACIÓN DEL VIDEO")
        print("-" * 40)
        print(f"🎬 Título: {video_info.titulo}")
        print(f"👤 Canal: {video_info.canal}")
        print(f"⏱️  Duración: {video_info.get_duration_formatted()}")
        print(f"🆔 ID: {video_info.id}")
        print()
    
    def _confirm_download(self) -> bool:
        """Confirma si el usuario quiere continuar"""
        response = input("¿Continuar con la descarga? (s/n): ").lower().strip()
        return response in ['s', 'si', 'sí', 'y', 'yes']