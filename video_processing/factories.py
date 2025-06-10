"""Factories para crear configuraciones"""

from .services import VideoDownloadService
from .downloaders import (YouTubeDownloader, YouTubeInfoExtractor, SimpleFileNameSanitizer, ConsoleProgressDisplay)
from .interfaces import IVideoDownloader, IVideoInfoExtractor

class VideoDownloaderFactory:
    """Factory para crear diferentes configuraciones de downloader"""
    
    @staticmethod
    def create_youtube_downloader() -> VideoDownloadService:
        """Crea downloader configurado para YouTube"""
        file_sanitizer = SimpleFileNameSanitizer()
        progress_display = ConsoleProgressDisplay()
        info_extractor = YouTubeInfoExtractor()
        
        downloader = YouTubeDownloader(file_sanitizer, progress_display)
        
        return VideoDownloadService(downloader, info_extractor)
    
    @staticmethod
    def create_custom_downloader(downloader: IVideoDownloader, 
                                info_extractor: IVideoInfoExtractor) -> VideoDownloadService:
        """Crea downloader con implementaciones personalizadas"""
        return VideoDownloadService(downloader, info_extractor)
