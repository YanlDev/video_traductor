#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: GENERACIÓN DE AUDIO EN ESPAÑOL
======================================
Genera audio en español usando voces de Microsoft Edge (edge-tts)
"""

import os
import json
import asyncio
from datetime import datetime

def verificar_edge_tts():
    """Verifica que edge-tts esté disponible"""
    try:
        import edge_tts
        print("✅ Edge-TTS disponible")
        return True
    except ImportError as e:
        print(f"❌ Edge-TTS no disponible: {e}")
        print("💡 Instalar con: pip install edge-tts")
        return False

async def obtener_voces_disponibles():
    """Obtiene lista de voces en español disponibles"""
    try:
        import edge_tts
        
        voces = await edge_tts.list_voices()
        voces_espanol = []
        
        for voz in voces:
            if voz['Locale'].startswith('es-'):
                voces_espanol.append({
                    'nombre': voz['ShortName'],
                    'genero': voz['Gender'],
                    'locale': voz['Locale'],
                    'nombre_completo': voz['FriendlyName']
                })
        
        return voces_espanol
        
    except Exception as e:
        print(f"❌ Error obteniendo voces: {e}")
        return []

def mostrar_voces_disponibles(voces):
    """Muestra las voces disponibles de forma organizada"""
    print("🎤 VOCES EN ESPAÑOL DISPONIBLES:")
    print("=" * 50)
    
    # Agrupar por región
    regiones = {}
    for voz in voces:
        region = voz['locale']
        if region not in regiones:
            regiones[region] = {'masculinas': [], 'femeninas': []}
        
        if voz['genero'] == 'Male':
            regiones[region]['masculinas'].append(voz)
        else:
            regiones[region]['femeninas'].append(voz)
    
    # Mostrar voces organizadas
    contador = 1
    voces_numeradas = []
    
    for region, generos in regiones.items():
        region_nombre = {
            'es-ES': '🇪🇸 España',
            'es-MX': '🇲🇽 México', 
            'es-AR': '🇦🇷 Argentina',
            'es-CO': '🇨🇴 Colombia',
            'es-CL': '🇨🇱 Chile',
            'es-PE': '🇵🇪 Perú',
            'es-VE': '🇻🇪 Venezuela',
            'es-CR': '🇨🇷 Costa Rica',
            'es-UY': '🇺🇾 Uruguay'
        }.get(region, region)
        
        print(f"\n{region_nombre}:")
        
        # Voces femeninas primero
        for voz in generos['femeninas']:
            print(f"  {contador}. 👩 {voz['nombre']} - {voz['nombre_completo']}")
            voces_numeradas.append(voz)
            contador += 1
            
        # Luego voces masculinas
        for voz in generos['masculinas']:
            print(f"  {contador}. 👨 {voz['nombre']} - {voz['nombre_completo']}")
            voces_numeradas.append(voz)
            contador += 1
    
    return voces_numeradas

async def generar_audio_edge(texto, voz_seleccionada, archivo_salida, callback_progreso=None):
    """Genera audio usando Edge TTS"""
    try:
        import edge_tts
        
        print(f"🎤 Generando audio con voz: {voz_seleccionada['nombre']}")
        print(f"📝 Texto: {len(texto)} caracteres")
        
        # Dividir texto en chunks si es muy largo
        max_chunk = 3000  # Edge TTS funciona mejor con chunks más pequeños
        
        if len(texto) <= max_chunk:
            chunks = [texto]
        else:
            # Dividir por oraciones para mantener naturalidad
            oraciones = texto.replace('!', '.').replace('?', '.').split('.')
            chunks = []
            chunk_actual = ""
            
            for oracion in oraciones:
                oracion = oracion.strip()
                if not oracion:
                    continue
                    
                if len(chunk_actual + oracion) <= max_chunk:
                    chunk_actual += oracion + ". "
                else:
                    if chunk_actual:
                        chunks.append(chunk_actual.strip())
                    chunk_actual = oracion + ". "
            
            if chunk_actual:
                chunks.append(chunk_actual.strip())
        
        print(f"🔄 Procesando {len(chunks)} fragmento(s)...")
        
        # Generar audio por chunks
        archivos_temporales = []
        
        for i, chunk in enumerate(chunks):
            if callback_progreso:
                callback_progreso(i + 1, len(chunks), f"Generando fragmento {i+1}")
            
            print(f"   🎵 Fragmento {i+1}/{len(chunks)}")
            
            archivo_temp = archivo_salida.replace('.wav', f'_temp_{i}.wav')
            
            # Crear comunicador Edge TTS
            communicate = edge_tts.Communicate(chunk, voz_seleccionada['nombre'])
            
            # Generar y guardar audio
            await communicate.save(archivo_temp)
            archivos_temporales.append(archivo_temp)
        
        # Si hay múltiples chunks, combinarlos
        if len(archivos_temporales) > 1:
            print("🔄 Combinando fragmentos de audio...")
            await combinar_archivos_audio(archivos_temporales, archivo_salida)
            
            # Limpiar archivos temporales
            for archivo_temp in archivos_temporales:
                try:
                    os.remove(archivo_temp)
                except:
                    pass
        else:
            # Solo un archivo, renombrarlo
            os.rename(archivos_temporales[0], archivo_salida)
        
        print(f"✅ Audio generado: {os.path.basename(archivo_salida)}")
        return True
        
    except Exception as e:
        print(f"❌ Error generando audio: {e}")
        return False

async def combinar_archivos_audio(archivos, archivo_salida):
    """Combina múltiples archivos de audio en uno solo"""
    try:
        # Usar ffmpeg para combinar archivos
        import subprocess
        
        # Crear archivo de lista para ffmpeg
        lista_archivos = archivo_salida.replace('.wav', '_lista.txt')
        
        with open(lista_archivos, 'w', encoding='utf-8') as f:
            for archivo in archivos:
                f.write(f"file '{os.path.abspath(archivo)}'\n")
        
        # Comando ffmpeg para concatenar
        comando = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', lista_archivos,
            '-c', 'copy',
            '-loglevel', 'error',
            archivo_salida
        ]
        
        subprocess.run(comando, check=True, capture_output=True)
        
        # Limpiar archivo de lista
        os.remove(lista_archivos)
        
        return True
        
    except Exception as e:
        print(f"❌ Error combinando audio: {e}")
        return False

def seleccionar_voz_automatica(voces):
    """Selecciona automáticamente una buena voz para el proyecto"""
    # Prioridades: España > México > Argentina (por claridad y neutralidad)
    prioridades = ['es-ES', 'es-MX', 'es-AR', 'es-CO']
    
    for locale in prioridades:
        voces_region = [v for v in voces if v['locale'] == locale]
        
        if voces_region:
            # Preferir voces femeninas (suelen ser más claras)
            voces_femeninas = [v for v in voces_region if v['genero'] == 'Female']
            
            if voces_femeninas:
                return voces_femeninas[0]
            else:
                return voces_region[0]
    
    # Si no encuentra ninguna de las preferidas, usar la primera disponible
    return voces[0] if voces else None

async def generar_automatico(ruta_proyecto):
    """Función automática para generar audio desde el proceso principal"""
    try:
        if not verificar_edge_tts():
            return None
        
        # Buscar traducción en el proyecto
        carpeta_traduccion = os.path.join(ruta_proyecto, "4_traduccion")
        
        if not os.path.exists(carpeta_traduccion):
            print("❌ No se encontró carpeta de traducción")
            return None
        
        # Buscar archivo de traducción
        archivos_es = [f for f in os.listdir(carpeta_traduccion) 
                      if f.endswith('_es.txt')]
        
        if not archivos_es:
            print("❌ No se encontró archivo de traducción")
            return None
        
        # Leer texto traducido
        archivo_traduccion = os.path.join(carpeta_traduccion, archivos_es[0])
        
        with open(archivo_traduccion, 'r', encoding='utf-8') as f:
            texto_espanol = f.read().strip()
        
        if not texto_espanol:
            print("❌ Archivo de traducción vacío")
            return None
        
        # Verificar si ya existe audio en español
        carpeta_audio_es = os.path.join(ruta_proyecto, "5_audio_es")
        if os.path.exists(carpeta_audio_es):
            archivos_existentes = [f for f in os.listdir(carpeta_audio_es) 
                                 if f.endswith('.wav')]
            if archivos_existentes:
                print("✅ Audio en español ya existe")
                return {'archivo_audio': os.path.join(carpeta_audio_es, archivos_existentes[0])}
        
        # Crear carpeta de audio en español
        os.makedirs(carpeta_audio_es, exist_ok=True)
        
        print("🎤 Iniciando generación de audio en español...")
        
        # Obtener voces disponibles
        voces = await obtener_voces_disponibles()
        
        if not voces:
            print("❌ No se encontraron voces en español")
            return None
        
        # Seleccionar voz automáticamente
        voz_seleccionada = seleccionar_voz_automatica(voces)
        
        if not voz_seleccionada:
            print("❌ No se pudo seleccionar una voz")
            return None
        
        print(f"🎙️ Voz seleccionada: {voz_seleccionada['nombre']} ({voz_seleccionada['locale']})")
        
        # Generar nombre del archivo de audio
        nombre_base = os.path.splitext(archivos_es[0])[0].replace('_es', '')
        archivo_audio = os.path.join(carpeta_audio_es, f"{nombre_base}_audio_es.wav")
        
        # Generar audio
        exito = await generar_audio_edge(texto_espanol, voz_seleccionada, archivo_audio)
        
        if not exito:
            print("❌ Error generando audio")
            return None
        
        # Guardar metadata
        metadata = {
            'archivo_traduccion': archivo_traduccion,
            'archivo_audio': archivo_audio,
            'voz_usada': voz_seleccionada,
            'caracteres_procesados': len(texto_espanol),
            'timestamp': datetime.now().isoformat()
        }
        
        archivo_metadata = os.path.join(carpeta_audio_es, f"{nombre_base}_audio_metadata.json")
        with open(archivo_metadata, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Archivos guardados en: 5_audio_es/")
        print(f"   🎵 {nombre_base}_audio_es.wav")
        print(f"   📊 {nombre_base}_audio_metadata.json")
        print(f"🎙️ Voz: {voz_seleccionada['nombre_completo']}")
        
        # Mostrar información del archivo
        try:
            tamaño = os.path.getsize(archivo_audio) / 1024 / 1024
            print(f"📊 Tamaño del audio: {tamaño:.1f} MB")
        except:
            pass
        
        return {
            'archivo_audio': archivo_audio,
            'voz_usada': voz_seleccionada,
            'metadata': metadata
        }
        
    except Exception as e:
        print(f"❌ Error en generación automática: {e}")
        return None

async def procesar_tts():
    """Función principal que procesa la generación de audio TTS"""
    print("🎤 GENERACIÓN DE AUDIO EN ESPAÑOL")
    print("=" * 40)
    
    if not verificar_edge_tts():
        return False
    
    # Buscar proyectos con traducción
    if not os.path.exists("downloads"):
        print("❌ No existe carpeta downloads")
        return False
    
    proyectos = []
    for item in os.listdir("downloads"):
        ruta_proyecto = os.path.join("downloads", item)
        if os.path.isdir(ruta_proyecto):
            carpeta_traduccion = os.path.join(ruta_proyecto, "4_traduccion")
            carpeta_audio_es = os.path.join(ruta_proyecto, "5_audio_es")
            
            if os.path.exists(carpeta_traduccion):
                archivos_es = [f for f in os.listdir(carpeta_traduccion) 
                             if f.endswith('_es.txt')]
                
                ya_tiene_audio = False
                if os.path.exists(carpeta_audio_es):
                    archivos_audio = [f for f in os.listdir(carpeta_audio_es) 
                                    if f.endswith('.wav')]
                    ya_tiene_audio = len(archivos_audio) > 0
                
                if archivos_es and not ya_tiene_audio:
                    proyectos.append({'nombre': item, 'ruta': ruta_proyecto})
    
    if not proyectos:
        print("❌ No hay proyectos con traducción para generar audio")
        return False
    
    print(f"📂 PROYECTOS DISPONIBLES ({len(proyectos)}):")
    for i, proyecto in enumerate(proyectos, 1):
        print(f"{i}. {proyecto['nombre']}")
    
    # Seleccionar proyecto
    try:
        seleccion = int(input(f"\nSelecciona proyecto (1-{len(proyectos)}): ")) - 1
        if not (0 <= seleccion < len(proyectos)):
            print("❌ Selección inválida")
            return False
        
        proyecto_elegido = proyectos[seleccion]
        
    except ValueError:
        print("❌ Número inválido")
        return False
    except KeyboardInterrupt:
        print("\n❌ Cancelado")
        return False
    
    print(f"\n✅ Procesando: {proyecto_elegido['nombre']}")
    
    # Obtener y mostrar voces disponibles
    print("\n🔄 Obteniendo voces disponibles...")
    voces = await obtener_voces_disponibles()
    
    if not voces:
        print("❌ No se encontraron voces en español")
        return False
    
    voces_numeradas = mostrar_voces_disponibles(voces)
    
    # Seleccionar voz
    print(f"\n💡 Recomendación: Voces de España son más neutras")
    print(f"💡 Para contenido técnico: Voces femeninas suelen ser más claras")
    
    try:
        print(f"\nOpciones:")
        print(f"0. Selección automática (recomendado)")
        seleccion_voz = input(f"Selecciona voz (0-{len(voces_numeradas)}): ").strip()
        
        if seleccion_voz == '0' or not seleccion_voz:
            voz_seleccionada = seleccionar_voz_automatica(voces)
            print(f"🤖 Voz automática: {voz_seleccionada['nombre']} ({voz_seleccionada['locale']})")
        else:
            indice_voz = int(seleccion_voz) - 1
            if 0 <= indice_voz < len(voces_numeradas):
                voz_seleccionada = voces_numeradas[indice_voz]
            else:
                print("❌ Selección inválida, usando automática")
                voz_seleccionada = seleccionar_voz_automatica(voces)
                
    except ValueError:
        print("❌ Número inválido, usando selección automática")
        voz_seleccionada = seleccionar_voz_automatica(voces)
    
    # Confirmar procesamiento
    continuar = input(f"\n¿Generar audio con {voz_seleccionada['nombre']}? (s/n): ").lower().strip()
    if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Generación cancelada")
        return False
    
    print()
    
    # Generar audio automáticamente
    resultado = await generar_automatico(proyecto_elegido['ruta'])
    
    if resultado:
        print("\n🎉 ¡AUDIO EN ESPAÑOL GENERADO!")
        print("=" * 40)
        print(f"📁 Proyecto: {proyecto_elegido['nombre']}")
        print(f"🎵 Audio generado: ✅")
        print(f"🎙️ Voz: {resultado['voz_usada']['nombre_completo']}")
        print(f"🔄 Siguiente paso: Combinar con video original")
        return True
    else:
        print("\n❌ Error generando audio")
        return False

def main():
    """Función para ejecutar el módulo independientemente"""
    try:
        asyncio.run(procesar_tts())
    except KeyboardInterrupt:
        print("\n❌ Cancelado por usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()