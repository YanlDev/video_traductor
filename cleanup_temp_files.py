#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: LIMPIEZA DE ARCHIVOS TEMPORALES
=======================================
Elimina todo excepto el video final
"""

import os
import shutil

def limpiar_proyecto(ruta_proyecto):
    """Elimina todos los archivos temporales, deja solo el video final"""
    if not os.path.exists(ruta_proyecto):
        return False
    
    # Carpetas a eliminar
    carpetas_temporales = [
        "1_original",
        "2_audio", 
        "audio_separado",
        "3_transcripcion",
        "4_traduccion", 
        "5_audio_es"
    ]
    
    try:
        # Eliminar carpetas temporales
        for carpeta in carpetas_temporales:
            ruta_carpeta = os.path.join(ruta_proyecto, carpeta)
            if os.path.exists(ruta_carpeta):
                shutil.rmtree(ruta_carpeta)
        
        # Eliminar archivos sueltos (mantener solo 6_final/)
        for item in os.listdir(ruta_proyecto):
            ruta_item = os.path.join(ruta_proyecto, item)
            if os.path.isfile(ruta_item):
                os.remove(ruta_item)
        
        return True
        
    except Exception:
        return False