# Script: analyze_chapters.py
# Requisitos: pip install openai
# Descripción: Analiza la transcripción del podcast para generar capítulos, descripción y thumbnail prompt

import os
import json
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

def analyze_with_ai(transcription_text):
    """
    Envía la transcripción a OpenAI GPT-4o-mini para análisis
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""Eres un experto en análisis de contenido para podcasts y YouTube.

A continuación te proporcionaré la transcripción completa de un episodio de podcast con timestamps.

Tu tarea es:
1. Identificar los temas principales y generar capítulos temáticos
2. Crear un título clickbait (atractivo pero honesto) para YouTube
3. Escribir una descripción profesional del episodio
4. Generar un prompt detallado para crear la imagen/thumbnail 16:9

TRANSCRIPCIÓN:
{transcription_text}

---

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
  "description": "Descripción completa del episodio para YouTube (3-5 párrafos, incluye los temas principales)",
  "thumbnail_prompt": "Prompt detallado para DALL-E 3 o Midjourney describiendo la imagen ideal para el thumbnail en formato 16:9. Debe ser visual, específico y atractivo.",
  "clips": [
    {{
      "start": "02:15",
      "end": "03:45",
      "title": "Momento destacado 1",
      "reason": "Por qué este fragmento es bueno para un clip corto"
    }},
    {{
      "start": "08:20",
      "end": "10:00",
      "title": "Momento destacado 2",
      "reason": "Por qué este fragmento funciona como clip"
    }}
  ]
}}

IMPORTANTE:
- Los timestamps deben estar en formato MM:SS o HH:MM:SS
- Identifica entre 3-7 capítulos según la duración
- Sugiere 2-5 clips potenciales (máximo 2 minutos cada uno)
- El título debe ser atractivo pero no sensacionalista
- La descripción debe ser informativa y profesional
- El prompt del thumbnail debe ser muy visual y descriptivo"""

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

    # 2. Buscar archivo .srt en /output
    print("\n--> Paso 1/5: Buscando archivo de subtítulos...")
    srt_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.srt') and os.path.isfile(os.path.join(OUTPUT_DIR, f))]

    if len(srt_files) == 0:
        print("❌ ERROR: No se encontró ningún archivo .srt en /output")
        print("Por favor, ejecuta primero: python generate_subtitles.py")
        return
    elif len(srt_files) > 1:
        print("⚠️  Se encontraron múltiples archivos .srt:")
        for idx, file in enumerate(srt_files, 1):
            print(f"   {idx}. {file}")
        print(f"\nUsando el más reciente: {srt_files[0]}")

    srt_path = os.path.join(OUTPUT_DIR, srt_files[0])
    filename_base = os.path.splitext(srt_files[0])[0]

    print(f"✓ Archivo encontrado: {srt_files[0]}")

    # 3. Parsear transcripción
    print("\n--> Paso 2/5: Leyendo transcripción...")
    try:
        transcription = parse_srt(srt_path)
        total_entries = len(transcription)
        print(f"✓ Se cargaron {total_entries} segmentos de transcripción")

        # Calcular duración aproximada
        if transcription:
            last_timestamp = transcription[-1]['timestamp']
            print(f"✓ Duración aproximada: {last_timestamp}")
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

    analysis = analyze_with_ai(transcription_text)

    if not analysis:
        print("❌ ERROR: No se pudo completar el análisis")
        return

    print(f"✓ Análisis completado exitosamente")
    print(f"   • Título generado: {analysis['title'][:60]}...")
    print(f"   • Capítulos detectados: {len(analysis['chapters'])}")
    print(f"   • Clips sugeridos: {len(analysis.get('clips', []))}")

    # 6. Generar archivos de salida
    print("\n--> Paso 5/5: Generando archivos de salida...")

    try:
        # A. chapters.json (Capítulos estructurados)
        chapters_path = os.path.join(OUTPUT_DIR, f"{filename_base}_chapters.json")
        with open(chapters_path, 'w', encoding='utf-8') as f:
            json.dump(analysis['chapters'], f, indent=2, ensure_ascii=False)
        print(f"✓ {chapters_path}")

        # B. clips_guide.json (Guía de clips para redes sociales)
        if 'clips' in analysis and analysis['clips']:
            clips_path = os.path.join(OUTPUT_DIR, f"{filename_base}_clips.json")
            with open(clips_path, 'w', encoding='utf-8') as f:
                json.dump(analysis['clips'], f, indent=2, ensure_ascii=False)
            print(f"✓ {clips_path}")

        # C. youtube_description.txt (Descripción completa lista para copiar)
        description_path = os.path.join(OUTPUT_DIR, f"{filename_base}_youtube.txt")
        description_text = generate_youtube_description(analysis)
        with open(description_path, 'w', encoding='utf-8') as f:
            f.write(description_text)
        print(f"✓ {description_path}")

        # D. metadata.json (Todo junto para referencia)
        metadata_path = os.path.join(OUTPUT_DIR, f"{filename_base}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✓ {metadata_path}")

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
    print(f"   1. {filename_base}_youtube.txt     → Copiar/pegar en YouTube")
    print(f"   2. {filename_base}_chapters.json   → Capítulos estructurados")
    print(f"   3. {filename_base}_clips.json      → Clips para redes sociales")
    print(f"   4. {filename_base}_metadata.json   → Metadata completa")
    print(f"\n💡 SIGUIENTE PASO:")
    print(f"   1. Abre '{filename_base}_youtube.txt' para ver toda la info")
    print(f"   2. Usa el prompt del thumbnail para generar la portada")
    print(f"   3. Copia los capítulos y descripción a YouTube")
    print("=" * 80)

if __name__ == "__main__":
    main()
