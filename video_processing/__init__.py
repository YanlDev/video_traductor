"""Exports principales del paquete"""

from .services import VideoDownloadService
from .factories import VideoDownloaderFactory
from .models import VideoInfo, DownloadResult, DownloadProgress
from .interfaces import IVideoDownloader, IVideoInfoExtractor

# Lo que se puede importar directamente
__all__ = [
    'VideoDownloadService',
    'VideoDownloaderFactory', 
    'VideoInfo',
    'DownloadResult',
    'DownloadProgress',
    'IVideoDownloader',
    'IVideoInfoExtractor'
]