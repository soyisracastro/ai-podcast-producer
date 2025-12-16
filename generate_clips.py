# Script: generate_clips.py
# Requisitos: pip install moviepy
# Descripción: Genera clips de video automáticamente desde el metadata.json

import os
import json
import re
import unicodedata
from moviepy.editor import VideoFileClip
from pathlib import Path

# --- CONFIGURACIÓN ---
INPUT_DIR = "./input"
OUTPUT_DIR = "./output"
VIDEO_DIR = "./output"  # El video final está en /output después de assemble_video.py
METADATA_DIR = "./output/metadata"
CLIPS_DIR = "./output/clips"
VIRAL_CLIPS_DIR = "./output/viral_clips"

def sanitize_filename(filename):
    """
    Sanitiza el nombre del archivo removiendo caracteres inválidos

    - Remueve acentos de vocales (á → a, é → e, etc.)
    - Elimina signos de interrogación (¿?)
    - Elimina signos de admiración (¡!)
    - Remueve otros caracteres especiales
    - Convierte espacios múltiples en uno solo

    Args:
        filename: Nombre original del archivo

    Returns:
        str: Nombre sanitizado sin acentos ni caracteres especiales
    """
    # 1. Remover acentos y diacríticos (á → a, é → e, ñ → n, etc.)
    # Normalizar a NFD (descomponer caracteres acentuados)
    filename = unicodedata.normalize('NFD', filename)
    # Remover marcas de acento (categoría 'Mn' = Nonspacing Mark)
    filename = ''.join(char for char in filename if unicodedata.category(char) != 'Mn')

    # 2. Remover signos de interrogación y admiración (¿? ¡!)
    filename = filename.replace('¿', '').replace('?', '')
    filename = filename.replace('¡', '').replace('!', '')

    # 3. Remover otros caracteres no permitidos en nombres de archivo
    # Windows: < > : " / \ | ? *
    # Además: comas, puntos (excepto el de extensión), paréntesis, corchetes
    filename = re.sub(r'[<>:"/\\|*,;()\[\]{}]', '', filename)

    # 4. Remover espacios múltiples y reemplazar con uno solo
    filename = re.sub(r'\s+', ' ', filename)

    # 5. Limitar longitud para evitar errores del sistema de archivos
    filename = filename[:150]

    # 6. Remover espacios al inicio y final
    return filename.strip()

def timestamp_to_seconds(timestamp_str):
    """
    Convierte timestamp (HH:MM:SS o MM:SS) a segundos totales

    Args:
        timestamp_str: "01:23:45" o "23:45"

    Returns:
        float: Total de segundos
    """
    parts = timestamp_str.split(':')

    if len(parts) == 3:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
    elif len(parts) == 2:
        hours, minutes, seconds = 0, int(parts[0]), int(parts[1])
    else:
        return 0

    return hours * 3600 + minutes * 60 + seconds

def find_video_file(base_filename):
    """
    Busca el archivo de video correspondiente en /output (generado por assemble_video.py)

    Args:
        base_filename: Nombre base del archivo (sin extensión)

    Returns:
        str: Ruta completa del archivo de video, o None si no se encuentra
    """
    # Buscar en /output con extensiones comunes de video
    extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v']

    # Primero intentar con el nombre exacto
    for ext in extensions:
        video_path = os.path.join(VIDEO_DIR, f"{base_filename}{ext}")
        if os.path.exists(video_path):
            return video_path

    # Buscar cualquier archivo de video en /output que coincida parcialmente
    if os.path.exists(VIDEO_DIR):
        for file in os.listdir(VIDEO_DIR):
            if file.lower().endswith(tuple(extensions)):
                # Verificar si el nombre base coincide (sin considerar extensión)
                file_base = os.path.splitext(file)[0]
                if base_filename.lower() in file_base.lower() or file_base.lower() in base_filename.lower():
                    return os.path.join(VIDEO_DIR, file)

    return None

def generate_clip(video_clip, clip_info, output_path, clip_type="clip"):
    """
    Genera un clip individual de video

    Args:
        video_clip: Objeto VideoFileClip de moviepy
        clip_info: Diccionario con información del clip (start, end, title, etc.)
        output_path: Ruta donde guardar el clip
        clip_type: Tipo de clip ("clip" o "viral_clip")
    """
    try:
        # Convertir timestamps a segundos
        start_time = timestamp_to_seconds(clip_info['start'])
        end_time = timestamp_to_seconds(clip_info['end'])

        # Validar timestamps
        if start_time >= end_time:
            print(f"⚠️  Timestamps inválidos para '{clip_info.get('title', 'Sin título')}': {clip_info['start']} - {clip_info['end']}")
            return False

        if end_time > video_clip.duration:
            print(f"⚠️  End time ({clip_info['end']}) excede la duración del video para '{clip_info.get('title', 'Sin título')}'")
            end_time = video_clip.duration

        # Extraer subclip
        print(f"   Extrayendo: {clip_info['start']} - {clip_info['end']} ({end_time - start_time:.1f}s)")
        subclip = video_clip.subclip(start_time, end_time)

        # Generar nombre de archivo
        title = clip_info.get('seo_title', clip_info.get('title', 'Sin título'))
        sanitized_title = sanitize_filename(title)
        filename = f"{clip_type}_{sanitized_title}.mp4"
        full_path = os.path.join(output_path, filename)

        # Exportar clip
        print(f"   Guardando: {filename}")
        subclip.write_videofile(
            full_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,
            preset="medium",
            threads=4,
            logger=None  # Suprimir logs verbosos de moviepy
        )

        print(f"   ✓ Generado: {filename}")
        return True

    except Exception as e:
        print(f"   ❌ Error generando clip '{clip_info.get('title', 'Sin título')}': {e}")
        return False

def main():
    print("=" * 80)
    print("  GENERADOR DE CLIPS - AI PODCAST PRODUCER")
    print("=" * 80)

    # 1. Buscar archivo metadata.json más reciente
    print("\n--> Paso 1/5: Buscando archivo de metadata...")

    if not os.path.exists(METADATA_DIR):
        print(f"❌ ERROR: Directorio {METADATA_DIR} no existe")
        print("Por favor, ejecuta primero: python analyze_chapters.py")
        return

    metadata_files = [f for f in os.listdir(METADATA_DIR) if f.endswith('_metadata.json')]

    if len(metadata_files) == 0:
        print(f"❌ ERROR: No se encontró ningún archivo *_metadata.json en {METADATA_DIR}")
        print("Por favor, ejecuta primero: python analyze_chapters.py")
        return
    elif len(metadata_files) > 1:
        print("⚠️  Se encontraron múltiples archivos de metadata:")
        for idx, file in enumerate(metadata_files, 1):
            print(f"   {idx}. {file}")
        print(f"\nUsando el más reciente: {metadata_files[0]}")

    metadata_path = os.path.join(METADATA_DIR, metadata_files[0])
    print(f"✓ Metadata encontrado: {metadata_files[0]}")

    # 2. Cargar metadata
    print("\n--> Paso 2/5: Cargando metadata...")
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        viral_clips = metadata.get('viral_clips', [])
        chapter_clips = metadata.get('chapter_clips', [])

        print(f"✓ Metadata cargado")
        print(f"   • Clips virales: {len(viral_clips)}")
        print(f"   • Clips de capítulo: {len(chapter_clips)}")

        if len(viral_clips) == 0 and len(chapter_clips) == 0:
            print("❌ No hay clips para generar en el metadata")
            return

    except Exception as e:
        print(f"❌ ERROR al cargar metadata: {e}")
        return

    # 3. Buscar archivo de video
    print("\n--> Paso 3/5: Buscando archivo de video...")

    # Extraer nombre base del archivo metadata
    base_filename = os.path.splitext(metadata_files[0])[0].replace('_metadata', '')
    print(f"   Buscando video para: {base_filename}")

    video_path = find_video_file(base_filename)

    if not video_path:
        print(f"❌ ERROR: No se encontró archivo de video en {VIDEO_DIR}")
        print(f"   Buscado: {base_filename}.mp4 (o .mov, .avi, .mkv)")
        print("\nAsegúrate de que el video final esté en /output")
        print("Ejecuta primero: python assemble_video.py")
        return

    print(f"✓ Video encontrado: {os.path.basename(video_path)}")

    # 4. Cargar video
    print("\n--> Paso 4/5: Cargando video...")
    try:
        video = VideoFileClip(video_path)
        print(f"✓ Video cargado")
        print(f"   • Duración: {video.duration:.1f}s ({video.duration // 60:.0f}:{video.duration % 60:02.0f})")
        print(f"   • Resolución: {video.w}x{video.h}")
        print(f"   • FPS: {video.fps}")
    except Exception as e:
        print(f"❌ ERROR al cargar video: {e}")
        return

    # 5. Crear directorios de salida
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(VIRAL_CLIPS_DIR, exist_ok=True)

    # 6. Generar clips virales
    print("\n--> Paso 5/5: Generando clips...")

    success_count = 0
    fail_count = 0

    if len(viral_clips) > 0:
        print(f"\n📱 Generando {len(viral_clips)} clips virales (short)...")
        for idx, clip in enumerate(viral_clips, 1):
            print(f"\n[{idx}/{len(viral_clips)}] {clip.get('title', 'Sin título')}")
            if generate_clip(video, clip, VIRAL_CLIPS_DIR, clip_type="viral_clip"):
                success_count += 1
            else:
                fail_count += 1

    # 7. Generar clips de capítulo
    if len(chapter_clips) > 0:
        print(f"\n📺 Generando {len(chapter_clips)} clips de capítulo (long)...")
        for idx, clip in enumerate(chapter_clips, 1):
            print(f"\n[{idx}/{len(chapter_clips)}] {clip.get('title', 'Sin título')}")
            if generate_clip(video, clip, CLIPS_DIR, clip_type="clip"):
                success_count += 1
            else:
                fail_count += 1

    # 8. Cerrar video
    video.close()

    # 9. Resumen final
    print("\n" + "=" * 80)
    print("✅ ¡GENERACIÓN DE CLIPS COMPLETADA!")
    print("=" * 80)
    print(f"\n📊 RESUMEN:")
    print(f"   • Clips generados exitosamente: {success_count}")
    print(f"   • Clips con errores: {fail_count}")
    print(f"\n📂 ARCHIVOS GENERADOS:")
    print(f"   • Clips virales: {VIRAL_CLIPS_DIR}/")
    print(f"   • Clips de capítulo: {CLIPS_DIR}/")
    print(f"\n💡 SIGUIENTE PASO:")
    print(f"   1. Revisa los clips generados en las carpetas de salida")
    print(f"   2. Usa los clips para publicar en redes sociales según el calendario")
    print(f"   3. Consulta '{base_filename}_calendar.csv' para el plan de publicación")
    print("=" * 80)

if __name__ == "__main__":
    main()
