#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO: TRADUCCIÓN DE TEXTO
===========================
Traduce transcripciones del inglés al español usando OpenAI o Google Translate
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv


def verificar_openai():
    """Verifica si OpenAI está disponible y configurado"""
    try:
        import openai
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  OPENAI_API_KEY no encontrada en .env")
            return False
        
        openai.api_key = api_key
        print("✅ OpenAI configurado correctamente")
        return True
    except ImportError:
        print("⚠️  OpenAI no instalado (pip install openai)")
        return False
    except Exception as e:
        print(f"⚠️  Error configurando OpenAI: {e}")
        return False


def verificar_google_translate():
    """Verifica si Google Translate está disponible"""
    try:
        from googletrans import Translator
        print("✅ Google Translate disponible")
        return True
    except ImportError:
        print("⚠️  Google Translate no instalado (pip install googletrans==4.0.0-rc1)")
        return False
    except Exception as e:
        print(f"⚠️  Error con Google Translate: {e}")
        return False


def traducir_con_openai(texto):
    """Traduce texto usando OpenAI GPT"""
    try:
        import openai

        print("🤖 Traduciendo con OpenAI...")

        response = openai.ChatCompletion.create(
            model="gpt-4o",  # o gpt-4o-mini si quieres reducir costo
            messages=[
                {
                    "role": "system",
                    "content": """Eres un traductor profesional experto. Traduce el siguiente texto del inglés al español de manera natural y precisa.

INSTRUCCIONES:
- Mantén el tono y estilo original
- Usa terminología técnica apropiada cuando sea necesario
- Para contenido técnico: usa términos establecidos en español
- Para contenido casual: traduce de forma natural y coloquial
- Conserva nombres propios, marcas y productos en inglés
- Prioriza la naturalidad del español sobre la traducción literal
- Si hay jerga o expresiones idiomáticas, usa equivalentes en español

El resultado debe sonar como si fuera escrito originalmente en español."""
                },
                {
                    "role": "user",
                    "content": f"Traduce este texto al español:\n\n{texto}"
                }
            ],
            max_tokens=4000,
            temperature=0.3
        )

        traduccion = response.choices[0].message["content"].strip()

        # Calcular tokens (estimación)
        tokens_entrada = len(texto) // 4
        tokens_salida = len(traduccion) // 4
        costo = (tokens_entrada * 0.00015 + tokens_salida * 0.0006) / 1000

        print(f"✅ Traducido con OpenAI (costo: ~${costo:.4f})")
        return traduccion, costo

    except Exception as e:
        print(f"❌ Error en OpenAI: {e}")
        raise


def traducir_con_google(texto):
    """Traduce texto usando Google Translate"""
    try:
        from googletrans import Translator

        print("🔄 Traduciendo con Google Translate...")

        translator = Translator()
        max_chunk = 4500

        if len(texto) <= max_chunk:
            resultado = translator.translate(texto, src='en', dest='es')
            traduccion = resultado.text
        else:
            oraciones = texto.split('. ')
            chunks = []
            chunk_actual = ""

            for oracion in oraciones:
                if len(chunk_actual + oracion) <= max_chunk:
                    chunk_actual += oracion + ". "
                else:
                    if chunk_actual:
                        chunks.append(chunk_actual.strip())
                    chunk_actual = oracion + ". "

            if chunk_actual:
                chunks.append(chunk_actual.strip())

            print(f"📝 Dividiendo en {len(chunks)} fragmentos...")

            traducciones = []
            for i, chunk in enumerate(chunks, 1):
                print(f"   🔄 Fragmento {i}/{len(chunks)}")
                resultado = translator.translate(chunk, src='en', dest='es')
                traducciones.append(resultado.text)

            traduccion = " ".join(traducciones)

        print("✅ Traducido con Google Translate (gratis)")
        return traduccion, 0.0

    except Exception as e:
        print(f"❌ Error en Google Translate: {e}")
        raise


def traducir_texto(texto):
    """Función principal que intenta OpenAI primero, luego Google"""
    if not texto.strip():
        print("❌ Texto vacío")
        return None, 0.0

    print(f"📝 Texto a traducir: {len(texto)} caracteres")
    print(f"   Muestra: {texto[:100]}...")

    if verificar_openai():
        try:
            return traducir_con_openai(texto)
        except Exception as e:
            print(f"⚠️  OpenAI falló: {e}")
            print("🔄 Cambiando a Google Translate...")

    if verificar_google_translate():
        try:
            return traducir_con_google(texto)
        except Exception as e:
            print(f"❌ Google Translate también falló: {e}")
            return None, 0.0
    else:
        print("❌ Ningún servicio de traducción disponible")
        return None, 0.0


def traducir_automatico(ruta_proyecto):
    """Función automática para traducir desde el proceso principal"""
    try:
        carpeta_transcripcion = os.path.join(ruta_proyecto, "3_transcripcion")
        if not os.path.exists(carpeta_transcripcion):
            print("❌ No se encontró carpeta de transcripción")
            return None

        archivos_txt = [f for f in os.listdir(carpeta_transcripcion)
                        if f.endswith('_texto.txt')]
        if not archivos_txt:
            print("❌ No se encontró archivo de transcripción")
            return None

        archivo_transcripcion = os.path.join(carpeta_transcripcion, archivos_txt[0])
        with open(archivo_transcripcion, 'r', encoding='utf-8') as f:
            texto_original = f.read().strip()

        if not texto_original:
            print("❌ Archivo de transcripción vacío")
            return None

        carpeta_traduccion = os.path.join(ruta_proyecto, "4_traduccion")
        if os.path.exists(carpeta_traduccion):
            archivos_existentes = [f for f in os.listdir(carpeta_traduccion)
                                   if f.endswith('_es.txt')]
            if archivos_existentes:
                print("✅ Traducción ya existe")
                return {'texto_traducido': 'Traducción existente'}

        os.makedirs(carpeta_traduccion, exist_ok=True)

        print("🌐 Iniciando traducción automática...")

        texto_traducido, costo = traducir_texto(texto_original)
        if not texto_traducido:
            print("❌ Error en la traducción")
            return None

        nombre_base = os.path.splitext(archivos_txt[0])[0].replace('_texto', '')
        archivo_traduccion = os.path.join(carpeta_traduccion, f"{nombre_base}_es.txt")

        with open(archivo_traduccion, 'w', encoding='utf-8') as f:
            f.write(texto_traducido)

        metadata = {
            'archivo_original': archivo_transcripcion,
            'archivo_traduccion': archivo_traduccion,
            'caracteres_original': len(texto_original),
            'caracteres_traducido': len(texto_traducido),
            'costo_estimado': costo,
            'timestamp': datetime.now().isoformat()
        }

        archivo_metadata = os.path.join(carpeta_traduccion, f"{nombre_base}_metadata.json")
        with open(archivo_metadata, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"💾 Archivos guardados en: 4_traduccion/")
        print(f"   📄 {nombre_base}_es.txt")
        print(f"   📊 {nombre_base}_metadata.json")
        print(f"📊 Original: {len(texto_original)} chars → Traducido: {len(texto_traducido)} chars")
        if costo > 0:
            print(f"💰 Costo total: ${costo:.4f}")

        return {
            'texto_traducido': texto_traducido,
            'costo': costo,
            'archivo_salida': archivo_traduccion
        }

    except Exception as e:
        print(f"❌ Error en traducción automática: {e}")
        return None


def main():
    """Función para ejecutar el módulo independientemente"""
    print("🌐 TRADUCCIÓN DE TEXTO")
    print("=" * 30)

    openai_ok = verificar_openai()
    google_ok = verificar_google_translate()

    if not openai_ok and not google_ok:
        print("❌ No hay servicios de traducción disponibles")
        print("💡 Instala: pip install openai googletrans==4.0.0-rc1")
        print("💡 Y configura OPENAI_API_KEY en archivo .env")
        return

    if not os.path.exists("downloads"):
        print("❌ No existe carpeta downloads")
        return

    proyectos = []
    for item in os.listdir("downloads"):
        ruta_proyecto = os.path.join("downloads", item)
        if os.path.isdir(ruta_proyecto):
            carpeta_transcripcion = os.path.join(ruta_proyecto, "3_transcripcion")
            carpeta_traduccion = os.path.join(ruta_proyecto, "4_traduccion")

            if os.path.exists(carpeta_transcripcion):
                archivos_txt = [f for f in os.listdir(carpeta_transcripcion)
                                if f.endswith('_texto.txt')]

                ya_traducido = False
                if os.path.exists(carpeta_traduccion):
                    archivos_es = [f for f in os.listdir(carpeta_traduccion)
                                   if f.endswith('_es.txt')]
                    ya_traducido = len(archivos_es) > 0

                if archivos_txt and not ya_traducido:
                    proyectos.append({'nombre': item, 'ruta': ruta_proyecto})

    if not proyectos:
        print("❌ No hay proyectos con transcripción para traducir")
        return

    print(f"📂 PROYECTOS DISPONIBLES ({len(proyectos)}):")
    for i, proyecto in enumerate(proyectos, 1):
        print(f"{i}. {proyecto['nombre']}")

    try:
        seleccion = int(input(f"\nSelecciona proyecto (1-{len(proyectos)}): ")) - 1
        if 0 <= seleccion < len(proyectos):
            proyecto_elegido = proyectos[seleccion]
            resultado = traducir_automatico(proyecto_elegido['ruta'])

            if resultado:
                print("\n🎉 ¡TRADUCCIÓN COMPLETADA!")
        else:
            print("❌ Selección inválida")
    except ValueError:
        print("❌ Número inválido")
    except KeyboardInterrupt:
        print("\n❌ Cancelado")


if __name__ == "__main__":
    main()
