# Script: analyze_chapters.py
# Requisitos: pip install openai
# Descripción: Analiza la transcripción del podcast para generar capítulos, descripción y thumbnail prompt

import os
import json
import csv
import warnings
from datetime import timedelta
from dotenv import load_dotenv
from openai import OpenAI

# Ignorar warnings innecesarios
warnings.filterwarnings("ignore")

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
OUTPUT_DIR = "./output"
TRANSCRIPTIONS_DIR = "./output/transcriptions"
METADATA_DIR = "./output/metadata"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def parse_srt(srt_path):
    """
    Lee un archivo .srt y extrae la transcripción completa con timestamps
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parsear bloques de subtítulos
    blocks = content.strip().split('\n\n')
    transcription = []

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # Línea 1: número (ignorar)
            # Línea 2: timestamp
            timestamp = lines[1].split(' --> ')[0]
            # Línea 3+: texto
            text = ' '.join(lines[2:])
            transcription.append({
                'timestamp': timestamp,
                'text': text
            })

    return transcription

def format_transcription_for_ai(transcription):
    """
    Formatea la transcripción para enviarla a la IA
    """
    formatted = []
    for entry in transcription:
        formatted.append(f"[{entry['timestamp']}] {entry['text']}")
    return '\n'.join(formatted)

def timestamp_to_youtube_format(timestamp_str):
    """
    Convierte timestamp SRT (HH:MM:SS,mmm) a formato YouTube (HH:MM:SS o MM:SS)
    """
    # Remover milisegundos
    time_part = timestamp_str.split(',')[0]
    parts = time_part.split(':')
    hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])

    # Si no hay horas, usar formato MM:SS
    if hours == 0:
        return f"{minutes}:{seconds:02d}"
    return f"{hours}:{minutes:02d}:{seconds:02d}"

def timestamp_to_seconds(timestamp_str):
    """
    Convierte timestamp (HH:MM:SS o MM:SS) a segundos totales

    Args:
        timestamp_str: "01:23:45" o "23:45" o "00:23:45,000"

    Returns:
        int: Total de segundos
    """
    # Remover milisegundos si existen
    time_part = timestamp_str.split(',')[0]
    parts = time_part.split(':')

    if len(parts) == 3:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
    elif len(parts) == 2:
        hours, minutes, seconds = 0, int(parts[0]), int(parts[1])
    else:
        return 0

    return hours * 3600 + minutes * 60 + seconds

def seconds_to_timestamp(total_seconds, include_hours=None):
    """
    Convierte segundos a formato timestamp (MM:SS o HH:MM:SS)

    Args:
        total_seconds: Segundos totales
        include_hours: True/False/None (None = auto-detectar)

    Returns:
        str: Timestamp formateado
    """
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Auto-detectar si necesitamos horas
    if include_hours is None:
        include_hours = hours > 0

    if include_hours or hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def calculate_duration(start_timestamp, end_timestamp):
    """
    Calcula duración entre dos timestamps y retorna formato legible

    Args:
        start_timestamp: "00:00" o "00:00:00"
        end_timestamp: "05:30" o "00:05:30"

    Returns:
        str: Duración en formato "5:30" o "1:05:30"
    """
    start_seconds = timestamp_to_seconds(start_timestamp)
    end_seconds = timestamp_to_seconds(end_timestamp)
    duration_seconds = end_seconds - start_seconds

    if duration_seconds < 0:
        return "00:00"

    return seconds_to_timestamp(duration_seconds)

def get_episode_duration(transcription):
    """
    Obtiene duración total del episodio desde la transcripción

    Args:
        transcription: Lista de entries con timestamps

    Returns:
        str: Duración total en formato legible
    """
    if not transcription or len(transcription) == 0:
        return "00:00"

    last_timestamp = transcription[-1]['timestamp']
    return timestamp_to_youtube_format(last_timestamp)

def calculate_content_density(duration_seconds, num_viral_clips):
    """
    Calcula densidad de contenido para metadata

    Args:
        duration_seconds: Duración total en segundos
        num_viral_clips: Número de clips virales generados

    Returns:
        str: 'low', 'medium', 'high'
    """
    if duration_seconds == 0:
        return 'low'

    clips_per_minute = num_viral_clips / (duration_seconds / 60)

    if clips_per_minute >= 0.5:
        return 'high'
    elif clips_per_minute >= 0.3:
        return 'medium'
    else:
        return 'low'

def validate_chapter_coverage(chapter_clips, total_episode_seconds):
    """
    Valida que los chapter_clips cubran todo el episodio sin gaps

    Args:
        chapter_clips: Lista de clips de capítulo
        total_episode_seconds: Duración total del episodio en segundos

    Returns:
        list: Lista de gaps encontrados [{'start': 'MM:SS', 'end': 'MM:SS'}]
    """
    if not chapter_clips:
        return []

    # Ordenar por start
    sorted_clips = sorted(chapter_clips, key=lambda x: timestamp_to_seconds(x['start']))

    gaps = []

    # Verificar que empiece en 00:00
    first_start = timestamp_to_seconds(sorted_clips[0]['start'])
    if first_start > 0:
        gaps.append({
            'start': '00:00',
            'end': seconds_to_timestamp(first_start)
        })

    # Verificar gaps entre clips
    for i in range(len(sorted_clips) - 1):
        current_end = timestamp_to_seconds(sorted_clips[i]['end'])
        next_start = timestamp_to_seconds(sorted_clips[i + 1]['start'])

        if next_start > current_end:
            gaps.append({
                'start': seconds_to_timestamp(current_end),
                'end': seconds_to_timestamp(next_start)
            })

    # Verificar que termine al final del episodio
    last_end = timestamp_to_seconds(sorted_clips[-1]['end'])
    if last_end < total_episode_seconds - 5:  # Tolerancia de 5 segundos
        gaps.append({
            'start': seconds_to_timestamp(last_end),
            'end': seconds_to_timestamp(total_episode_seconds)
        })

    return gaps

def enhance_analysis_with_metadata(analysis, transcription):
    """
    Enriquece el análisis con metadata calculada
    - Agrega end_timestamp a chapters
    - Agrega duration_seconds a todos los clips
    - Valida que no haya gaps en chapter_clips
    - Calcula episode_metadata

    Args:
        analysis: Diccionario con el análisis de la IA
        transcription: Lista de entries de transcripción

    Returns:
        dict: Análisis enriquecido con metadata
    """

    # 1. Calcular episode duration
    episode_duration = get_episode_duration(transcription)
    total_seconds = timestamp_to_seconds(episode_duration)

    # 2. Enriquecer chapters con end_timestamp
    chapters = analysis.get('chapters', [])
    for i, chapter in enumerate(chapters):
        if i < len(chapters) - 1:
            chapter['end_timestamp'] = chapters[i + 1]['timestamp']
        else:
            # Último capítulo termina al final del episodio
            chapter['end_timestamp'] = episode_duration

    # 3. Enriquecer viral_clips con duration_seconds y type
    viral_clips = analysis.get('viral_clips', [])
    for clip in viral_clips:
        start_sec = timestamp_to_seconds(clip['start'])
        end_sec = timestamp_to_seconds(clip['end'])
        clip['duration_seconds'] = end_sec - start_sec
        if 'type' not in clip:
            clip['type'] = 'short'

    # 4. Enriquecer chapter_clips
    chapter_clips = analysis.get('chapter_clips', [])
    for i, clip in enumerate(chapter_clips):
        start_sec = timestamp_to_seconds(clip['start'])
        end_sec = timestamp_to_seconds(clip['end'])
        clip['duration_seconds'] = end_sec - start_sec
        if 'type' not in clip:
            clip['type'] = 'long'
        if 'chapter_index' not in clip:
            clip['chapter_index'] = i

    # 5. Validar cobertura completa (chapter_clips sin gaps)
    if chapter_clips:
        gaps = validate_chapter_coverage(chapter_clips, total_seconds)
        if gaps:
            print(f"⚠️  ADVERTENCIA: Se encontraron {len(gaps)} gaps en los chapter_clips")
            for gap in gaps:
                print(f"   Gap detectado: {gap['start']} - {gap['end']}")

    # 6. Agregar episode_metadata
    analysis['episode_metadata'] = {
        'total_duration': episode_duration,
        'total_duration_seconds': total_seconds,
        'total_viral_clips': len(viral_clips),
        'total_chapter_clips': len(chapter_clips),
        'total_chapters': len(chapters),
        'content_density': calculate_content_density(total_seconds, len(viral_clips))
    }

    return analysis

def analyze_with_ai(transcription_text, episode_duration):
    """
    Envía la transcripción a OpenAI GPT-4o-mini para análisis

    Args:
        transcription_text: Transcripción formateada con timestamps
        episode_duration: Duración total del episodio (ej: "16:45")
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""Eres un experto en análisis de contenido para podcasts, YouTube, y estrategia de redes sociales.

A continuación te proporcionaré la transcripción completa de un episodio de podcast con timestamps.

DURACIÓN TOTAL DEL EPISODIO: {episode_duration}

Tu tarea es:
1. Identificar los temas principales y generar capítulos temáticos QUE CUBRAN TODO EL EPISODIO SIN GAPS
2. Crear un título clickbait (atractivo pero honesto) para YouTube
3. Escribir una descripción profesional del episodio
4. Generar un prompt detallado para crear la imagen/thumbnail 16:9 del episodio completo
5. **NUEVO**: Identificar clips virales (15-60 segundos) optimizados para redes sociales
6. **NUEVO**: Generar clips de cada capítulo completo para contenido largo

TRANSCRIPCIÓN:
{transcription_text}

---

INSTRUCCIONES DETALLADAS:

**CAPÍTULOS (chapters)**:
- IMPORTANTE: Los capítulos deben cubrir TODO el episodio sin espacios vacíos
- El primer capítulo DEBE empezar en "00:00"
- Cada capítulo debe conectar con el siguiente sin gaps
- Identifica entre 5-8 capítulos según la duración y densidad del contenido
- Cada capítulo debe tener un tema coherente y completo

**CLIPS VIRALES (viral_clips)**:
- Duración: 15-60 segundos cada uno
- Cantidad: Decide dinámicamente según la duración del episodio:
  * Episodios 10-15 min: 4-6 clips
  * Episodios 15-25 min: 6-8 clips
  * Episodios 25-40 min: 8-12 clips
  * Episodios 40+ min: 12-15 clips
- Criterios para selección:
  * Momentos impactantes, sorprendentes o emotivos
  * Frases memorables o citas destacadas
  * Datos/estadísticas impresionantes
  * Historias breves y completas
  * Humor o anécdotas
  * Consejos accionables y concretos
- Cada clip DEBE ser autosuficiente (con contexto completo)
- Prioriza variedad: diferentes temas y tonos
- Asigna un virality_score (1-10) basado en potencial de engagement

**CLIPS DE CAPÍTULO (chapter_clips)**:
- Uno por cada capítulo identificado
- Duración: Variable (del inicio al fin del capítulo)
- Deben coincidir EXACTAMENTE con los timestamps de los capítulos
- Son para personas que quieren ver el episodio por partes
- No deben tener gaps ni overlaps entre ellos

**METADATA SEO** (para cada clip):
- seo_title: Título optimizado para búsqueda (50-60 caracteres)
  * Incluye palabras clave relevantes
  * Formato: "Cómo/Qué/Por qué + [tema] | [beneficio/año]"
  * Ejemplo: "Cómo Calcular tu Aguinaldo Correctamente | Guía 2025"
- seo_description: Descripción corta (1-2 oraciones, máx 150 caracteres)
  * Resume el valor del contenido
  * Incluye call-to-action implícito
  * Ejemplo: "Aprende el método exacto para calcular tu aguinaldo. Paso a paso con ejemplos."
- thumbnail_prompt: Prompt visual específico para ESTE clip
  * Debe ser diferente del thumbnail del episodio completo
  * Describe la escena, colores, texto, elementos visuales
  * Formato 16:9, atractivo para mobile
  * Ejemplo: "Close-up de manos con calculadora y billetes de pesos, texto overlay 'CÁLCULO AGUINALDO', fondo limpio azul corporativo, estilo moderno minimalista"

**TIPO DE CONTENIDO**:
- "short" para clips virales (15-60 seg)
- "long" para clips de capítulo (duración variable, generalmente >60 seg)

Por favor, responde ÚNICAMENTE con un JSON válido en este formato exacto:

{{
  "title": "Título clickbait del episodio (máximo 100 caracteres)",
  "chapters": [
    {{
      "timestamp": "00:00",
      "title": "Introducción al tema",
      "description": "Breve descripción de qué se habla"
    }},
    {{
      "timestamp": "05:30",
      "title": "Segundo tema",
      "description": "Descripción del segundo bloque"
    }}
  ],
  "description": "Descripción completa del episodio para YouTube (3-5 párrafos)",
  "thumbnail_prompt": "Prompt detallado para DALL-E 3 o Midjourney para el thumbnail principal del episodio",
  "clips": [
    {{
      "start": "02:15",
      "end": "03:45",
      "title": "Momento destacado",
      "reason": "Por qué es bueno para viral"
    }}
  ],
  "viral_clips": [
    {{
      "start": "02:15",
      "end": "03:45",
      "title": "Momento destacado 1",
      "seo_title": "Título SEO optimizado | 2025",
      "seo_description": "Descripción breve 1-2 oraciones.",
      "thumbnail_prompt": "Prompt visual específico para este clip",
      "reason": "Por qué este fragmento es viral",
      "virality_score": 8.5,
      "type": "short"
    }}
  ],
  "chapter_clips": [
    {{
      "start": "00:00",
      "end": "05:30",
      "title": "Introducción al tema",
      "seo_title": "Introducción al Tema | Guía Completa",
      "seo_description": "Todo sobre el tema en México.",
      "thumbnail_prompt": "Prompt visual para thumbnail de capítulo",
      "chapter_index": 0,
      "type": "long"
    }}
  ]
}}

IMPORTANTE:
- Los timestamps deben estar en formato MM:SS o HH:MM:SS
- NO dejes espacios vacíos entre capítulos
- Asegúrate de que los chapter_clips cubran TODO el episodio
- Varía el tipo de contenido en viral_clips (educativo, entretenido, inspiracional)
- Los SEO titles deben ser únicos y específicos
- Los thumbnail prompts deben ser visuales y específicos"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de contenido para podcasts. Siempre respondes con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"❌ ERROR en la llamada a OpenAI: {e}")
        return None

def generate_content_table_csv(analysis, filename_base, episode_duration):
    """
    Genera tabla de contenido CSV con todos los clips

    Args:
        analysis: Diccionario con el análisis completo
        filename_base: Nombre base del archivo (sin extensión)
        episode_duration: Duración total del episodio

    Returns:
        tuple: (csv_path, all_clips)
    """
    all_clips = []

    # Recolectar viral clips
    for clip in analysis.get('viral_clips', []):
        try:
            all_clips.append({
                'seo_title': clip.get('seo_title', clip.get('title', 'Sin título')),
                'start': clip['start'],
                'duration': calculate_duration(clip['start'], clip['end']),
                'seo_description': clip.get('seo_description', ''),
                'thumbnail_prompt': clip.get('thumbnail_prompt', ''),
                'type': 'short',
                'start_seconds': timestamp_to_seconds(clip['start']),
                'virality_score': clip.get('virality_score', 5)
            })
        except Exception as e:
            print(f"⚠️  Clip viral inválido ignorado: {e}")
            continue

    # Recolectar chapter clips
    for clip in analysis.get('chapter_clips', []):
        try:
            all_clips.append({
                'seo_title': clip.get('seo_title', clip.get('title', 'Sin título')),
                'start': clip['start'],
                'duration': calculate_duration(clip['start'], clip['end']),
                'seo_description': clip.get('seo_description', ''),
                'thumbnail_prompt': clip.get('thumbnail_prompt', ''),
                'type': 'long',
                'start_seconds': timestamp_to_seconds(clip['start']),
                'virality_score': 0  # Not applicable for long clips
            })
        except Exception as e:
            print(f"⚠️  Clip de capítulo inválido ignorado: {e}")
            continue

    # Ordenar cronológicamente
    all_clips.sort(key=lambda x: x['start_seconds'])

    # Preparar filas para CSV
    csv_rows = []
    for idx, clip in enumerate(all_clips, 1):
        csv_rows.append({
            '#': idx,
            'Título SEO (YouTube)': clip['seo_title'],
            'Tiempo': clip['start'],
            'Duración': clip['duration'],
            'Descripción SEO (corta)': clip['seo_description'],
            'Prompt para Miniatura': clip['thumbnail_prompt'],
            'Tipo de Contenido': clip['type']
        })

    # Escribir CSV
    csv_path = os.path.join(METADATA_DIR, f"{filename_base}_content_table.csv")

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['#', 'Título SEO (YouTube)', 'Tiempo', 'Duración',
                      'Descripción SEO (corta)', 'Prompt para Miniatura', 'Tipo de Contenido']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    return csv_path, all_clips

def generate_publication_calendar_csv(all_clips, filename_base, episode_title):
    """
    Genera calendario de publicación con auto-asignación inteligente

    Args:
        all_clips: Lista de todos los clips (con virality_score y type)
        filename_base: Nombre base del archivo
        episode_title: Título del episodio completo

    Returns:
        str: Ruta del archivo CSV generado
    """

    # Plantilla semanal de calendario
    CALENDAR_TEMPLATE = [
        {'day': 'Lunes', 'time': '21:00', 'content_type': 'Episodio Completo', 'platform': 'YouTube + Spotify', 'is_full_episode': True},
        {'day': 'Martes', 'time': '07:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'high'},
        {'day': 'Martes', 'time': '13:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'high'},
        {'day': 'Miércoles', 'time': '07:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'medium'},
        {'day': 'Miércoles', 'time': '18:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'high'},
        {'day': 'Jueves', 'time': '13:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'medium'},
        {'day': 'Jueves', 'time': '20:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'medium'},
        {'day': 'Viernes', 'time': '07:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'low'},
        {'day': 'Viernes', 'time': '17:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'low'},
        {'day': 'Sábado', 'time': '10:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'mood': 'inspirational'},
        {'day': 'Domingo', 'time': '19:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'mood': 'teaser'},
    ]

    # Separar clips por tipo
    short_clips = [c for c in all_clips if c['type'] == 'short']
    long_clips = [c for c in all_clips if c['type'] == 'long']

    # Ordenar por calidad/relevancia
    # Para shorts: ordenar por virality_score (mayor primero)
    short_clips.sort(key=lambda x: x.get('virality_score', 5), reverse=True)
    # Para longs: mantener orden cronológico (ya ordenados por start_seconds)

    # Inicializar calendario
    calendar = []
    short_index = 0
    long_index = 0

    for slot in CALENDAR_TEMPLATE:
        row = {
            'day': slot['day'],
            'time': slot['time'],
            'content_type': slot['content_type'],
            'title': '',
            'platform': slot.get('platform', ''),
            'notes': ''
        }

        # Episodio completo (lunes)
        if slot.get('is_full_episode'):
            row['title'] = episode_title
            row['notes'] = 'Episodio completo'

        # Asignar clips cortos
        elif 'Corto' in slot['content_type']:
            if short_index < len(short_clips):
                clip = short_clips[short_index]
                row['title'] = clip['seo_title']
                row['notes'] = f"Duración: {clip['duration']} | Inicio: {clip['start']}"

                # Mood especial para sábado/domingo
                if slot.get('mood') == 'inspirational':
                    row['notes'] += ' | Contenido inspiracional'
                elif slot.get('mood') == 'teaser':
                    row['notes'] += ' | Teaser para próximo episodio'

                short_index += 1
            else:
                row['title'] = '[Reutilizar contenido previo]'
                row['notes'] = 'No hay suficientes clips cortos'

        # Asignar clips largos
        elif 'Largo' in slot['content_type']:
            if long_index < len(long_clips):
                clip = long_clips[long_index]
                row['title'] = clip['seo_title']
                row['notes'] = f"Duración: {clip['duration']} | Inicio: {clip['start']}"
                long_index += 1
            else:
                row['title'] = '[Reutilizar contenido previo]'
                row['notes'] = 'No hay suficientes clips largos'

        calendar.append(row)

    # Escribir CSV
    csv_path = os.path.join(METADATA_DIR, f"{filename_base}_calendar.csv")

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Día', 'Hora', 'Tipo de Contenido', 'Título', 'Plataforma', 'Notas'
        ])
        writer.writeheader()

        for row in calendar:
            writer.writerow({
                'Día': row['day'],
                'Hora': row['time'],
                'Tipo de Contenido': row['content_type'],
                'Título': row['title'],
                'Plataforma': row['platform'],
                'Notas': row['notes']
            })

    return csv_path

def generate_youtube_description(analysis):
    """
    Genera el archivo de descripción formateado para YouTube
    """
    lines = []

    # Título
    lines.append("=" * 80)
    lines.append("TÍTULO DEL VIDEO")
    lines.append("=" * 80)
    lines.append(analysis['title'])
    lines.append("")

    # Descripción
    lines.append("=" * 80)
    lines.append("DESCRIPCIÓN")
    lines.append("=" * 80)
    lines.append(analysis['description'])
    lines.append("")

    # Capítulos
    lines.append("=" * 80)
    lines.append("CAPÍTULOS (YouTube Timestamps)")
    lines.append("=" * 80)
    for chapter in analysis['chapters']:
        lines.append(f"{chapter['timestamp']} - {chapter['title']}")
    lines.append("")

    # Thumbnail prompt
    lines.append("=" * 80)
    lines.append("PROMPT PARA THUMBNAIL/PORTADA (16:9)")
    lines.append("=" * 80)
    lines.append(analysis['thumbnail_prompt'])
    lines.append("")
    lines.append("💡 Usa este prompt en DALL-E 3, Midjourney, o cualquier generador de imágenes IA")
    lines.append("=" * 80)

    return '\n'.join(lines)

def main():
    print("=" * 80)
    print("  ANALIZADOR DE CAPÍTULOS Y METADATA - AI PODCAST PRODUCER")
    print("=" * 80)

    # 1. Validar API Key
    if not OPENAI_API_KEY:
        print("\n❌ ERROR: No se encontró OPENAI_API_KEY en el archivo .env")
        print("Por favor, agrega la línea: OPENAI_API_KEY=sk-tu_clave_aqui")
        print("\nPuedes obtener tu API key en: https://platform.openai.com/api-keys")
        return

    # 2. Buscar archivo .srt en /output/transcriptions
    print("\n--> Paso 1/5: Buscando archivo de subtítulos...")
    srt_files = [f for f in os.listdir(TRANSCRIPTIONS_DIR) if f.endswith('.srt') and os.path.isfile(os.path.join(TRANSCRIPTIONS_DIR, f))]

    if len(srt_files) == 0:
        print("❌ ERROR: No se encontró ningún archivo .srt en /output/transcriptions")
        print("Por favor, ejecuta primero: python generate_subtitles.py")
        return
    elif len(srt_files) > 1:
        print("⚠️  Se encontraron múltiples archivos .srt:")
        for idx, file in enumerate(srt_files, 1):
            print(f"   {idx}. {file}")
        print(f"\nUsando el más reciente: {srt_files[0]}")

    srt_path = os.path.join(TRANSCRIPTIONS_DIR, srt_files[0])
    filename_base = os.path.splitext(srt_files[0])[0]

    print(f"✓ Archivo encontrado: {srt_files[0]}")

    # 3. Parsear transcripción
    print("\n--> Paso 2/5: Leyendo transcripción...")
    try:
        transcription = parse_srt(srt_path)
        total_entries = len(transcription)
        print(f"✓ Se cargaron {total_entries} segmentos de transcripción")

        # Calcular duración total del episodio
        if transcription:
            episode_duration = get_episode_duration(transcription)
            episode_seconds = timestamp_to_seconds(episode_duration)
            print(f"✓ Duración total: {episode_duration} ({episode_seconds} segundos)")
        else:
            episode_duration = "00:00"
            episode_seconds = 0
    except Exception as e:
        print(f"❌ ERROR al leer el archivo .srt: {e}")
        return

    # 4. Formatear para IA
    print("\n--> Paso 3/5: Preparando análisis con IA...")
    transcription_text = format_transcription_for_ai(transcription)

    # Calcular tokens aproximados (4 caracteres ≈ 1 token)
    estimated_tokens = len(transcription_text) // 4
    estimated_cost = (estimated_tokens / 1_000_000) * 0.15  # $0.15 por millón de tokens de entrada

    print(f"   Caracteres de transcripción: {len(transcription_text):,}")
    print(f"   Tokens estimados: ~{estimated_tokens:,}")
    print(f"   Costo estimado: ~${estimated_cost:.4f} USD")

    # 5. Analizar con IA
    print("\n--> Paso 4/5: Analizando contenido con GPT-4o-mini...")
    print("   (Esto puede tardar 10-30 segundos dependiendo de la longitud)")

    analysis = analyze_with_ai(transcription_text, episode_duration)

    if not analysis:
        print("❌ ERROR: No se pudo completar el análisis")
        return

    print(f"✓ Análisis completado exitosamente")
    print(f"   • Título generado: {analysis['title'][:60]}...")
    print(f"   • Capítulos detectados: {len(analysis['chapters'])}")
    print(f"   • Clips sugeridos: {len(analysis.get('clips', []))}")

    # 6. Enriquecer análisis con metadata
    print("\n--> Enriqueciendo análisis con metadata...")
    analysis = enhance_analysis_with_metadata(analysis, transcription)
    print(f"✓ Metadata agregada")
    print(f"   • Clips virales: {analysis['episode_metadata']['total_viral_clips']}")
    print(f"   • Clips de capítulo: {analysis['episode_metadata']['total_chapter_clips']}")

    # 6. Generar archivos de salida
    print("\n--> Paso 5/5: Generando archivos de salida...")

    # Crear directorio metadata si no existe
    os.makedirs(METADATA_DIR, exist_ok=True)

    try:
        # A. chapters.json (Capítulos estructurados)
        chapters_path = os.path.join(METADATA_DIR, f"{filename_base}_chapters.json")
        with open(chapters_path, 'w', encoding='utf-8') as f:
            json.dump(analysis['chapters'], f, indent=2, ensure_ascii=False)
        print(f"✓ {chapters_path}")

        # B. clips_guide.json (Guía de clips para redes sociales)
        if 'clips' in analysis and analysis['clips']:
            clips_path = os.path.join(METADATA_DIR, f"{filename_base}_clips.json")
            with open(clips_path, 'w', encoding='utf-8') as f:
                json.dump(analysis['clips'], f, indent=2, ensure_ascii=False)
            print(f"✓ {clips_path}")

        # C. youtube_description.txt (Descripción completa lista para copiar)
        description_path = os.path.join(METADATA_DIR, f"{filename_base}_youtube.txt")
        description_text = generate_youtube_description(analysis)
        with open(description_path, 'w', encoding='utf-8') as f:
            f.write(description_text)
        print(f"✓ {description_path}")

        # D. metadata.json (Todo junto para referencia)
        metadata_path = os.path.join(METADATA_DIR, f"{filename_base}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✓ {metadata_path}")

        # E. content_table.csv (Tabla de contenido para producción)
        content_csv, all_clips = generate_content_table_csv(analysis, filename_base, episode_duration)
        print(f"✓ {content_csv}")

        # F. calendar.csv (Calendario de publicación semanal)
        calendar_csv = generate_publication_calendar_csv(all_clips, filename_base, analysis['title'])
        print(f"✓ {calendar_csv}")

    except Exception as e:
        print(f"❌ ERROR al guardar archivos: {e}")
        return

    # 7. Resumen final
    print("\n" + "=" * 80)
    print("✅ ¡ANÁLISIS COMPLETADO!")
    print("=" * 80)
    print(f"\n📺 TÍTULO SUGERIDO:")
    print(f"   {analysis['title']}")
    print(f"\n📂 ARCHIVOS GENERADOS:")
    print(f"   1. {filename_base}_youtube.txt          → YouTube description")
    print(f"   2. {filename_base}_chapters.json        → Chapters structured")
    print(f"   3. {filename_base}_clips.json           → Legacy clips")
    print(f"   4. {filename_base}_metadata.json        → Complete metadata")
    print(f"   5. {filename_base}_content_table.csv    → Content table with SEO")
    print(f"   6. {filename_base}_calendar.csv         → Publication calendar")
    print(f"\n💡 SIGUIENTE PASO:")
    print(f"   1. Abre '{filename_base}_youtube.txt' para ver toda la info")
    print(f"   2. Revisa '{filename_base}_content_table.csv' para planificar clips")
    print(f"   3. Usa '{filename_base}_calendar.csv' para programar publicaciones")
    print(f"   4. Usa el prompt del thumbnail para generar la portada")
    print("=" * 80)

if __name__ == "__main__":
    main()
