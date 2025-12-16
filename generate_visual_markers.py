# Script: generate_visual_markers.py
# Requisitos: pip install openai
# Descripción: Genera prompts para imágenes e infografías con timestamps estratégicos

import os
import json
import warnings
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
    Lee un archivo .srt y extrae la transcripción con timestamps
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.strip().split('\n\n')
    transcription = []

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            timestamp = lines[1].split(' --> ')[0]
            text = ' '.join(lines[2:])
            transcription.append({
                'timestamp': timestamp,
                'text': text
            })

    return transcription

def format_transcription_with_timestamps(transcription):
    """
    Formatea la transcripción con timestamps para análisis
    """
    formatted = []
    for entry in transcription:
        formatted.append(f"[{entry['timestamp']}] {entry['text']}")
    return '\n'.join(formatted)

def analyze_visual_opportunities(transcription_text):
    """
    Analiza la transcripción y genera prompts visuales con timestamps
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""Eres un experto en producción audiovisual y diseño gráfico para YouTube.

Analiza la siguiente transcripción de podcast con timestamps y genera elementos visuales estratégicos para mantener la atención de la audiencia.

TRANSCRIPCIÓN:
{transcription_text}

---

INSTRUCCIONES:

Identifica momentos clave donde insertar elementos visuales:

1. **IMÁGENES FOTOREALISTAS** - Para conceptos, personas, lugares, ejemplos visuales
   - Timestamp exacto donde debe aparecer
   - Prompt detallado para DALL-E 3 / Midjourney (estilo fotorealista profesional)
   - Duración sugerida en pantalla (segundos)

2. **INFOGRAFÍAS** - Para datos densos, cálculos, comparaciones, procesos
   - Timestamp exacto donde debe aparecer
   - Descripción detallada del contenido de la infografía
   - Tipo: tabla, gráfico de barras, diagrama de flujo, comparación, etc.
   - Duración sugerida en pantalla (segundos)

3. **TEXTO EN PANTALLA** - Para frases clave, estadísticas impactantes, citas
   - Timestamp exacto
   - Texto exacto a mostrar
   - Estilo sugerido

CRITERIOS:
- Inserta elementos cada 20-40 segundos para mantener atención
- Prioriza infografías cuando haya números, cálculos o datos complejos
- Usa imágenes fotorealistas para contexto visual y storytelling
- Los prompts de imagen deben ser muy específicos y descriptivos
- Las infografías deben simplificar información compleja

Responde ÚNICAMENTE con JSON válido:

{{
  "visual_markers": [
    {{
      "type": "photo",
      "timestamp": "00:00:15",
      "duration_seconds": 5,
      "prompt": "Prompt detallado para generar imagen fotorealista de alta calidad, 16:9 aspect ratio, profesional, cinematográfico",
      "context": "Breve explicación de por qué esta imagen aquí"
    }},
    {{
      "type": "infographic",
      "timestamp": "00:01:30",
      "duration_seconds": 8,
      "title": "Título de la infografía",
      "content": {{
        "type": "table",
        "description": "Descripción detallada de qué mostrar en la infografía",
        "data": "Datos específicos a incluir"
      }},
      "context": "Por qué necesitamos una infografía aquí"
    }},
    {{
      "type": "text_overlay",
      "timestamp": "00:02:45",
      "duration_seconds": 3,
      "text": "Texto exacto a mostrar",
      "style": "bold/quote/statistic",
      "context": "Por qué resaltar este texto"
    }}
  ],
  "summary": {{
    "total_markers": 10,
    "photos": 4,
    "infographics": 3,
    "text_overlays": 3,
    "strategy": "Explicación de la estrategia visual general del video"
  }}
}}

IMPORTANTE:
- Genera entre 8-15 marcadores visuales dependiendo de la duración
- Los timestamps deben ser precisos y coincidir con el contenido
- Los prompts de imagen deben ser muy descriptivos (mínimo 30 palabras)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en producción audiovisual y diseño gráfico. Respondes siempre con JSON válido."},
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

def generate_visual_guide(analysis, output_path):
    """
    Genera guía visual formateada para el editor
    """
    lines = []

    lines.append("=" * 80)
    lines.append("GUÍA DE ELEMENTOS VISUALES PARA EDICIÓN")
    lines.append("=" * 80)
    lines.append("")

    summary = analysis.get('summary', {})
    lines.append(f"📊 RESUMEN:")
    lines.append(f"   Total de marcadores: {summary.get('total_markers', 0)}")
    lines.append(f"   • Imágenes fotorealistas: {summary.get('photos', 0)}")
    lines.append(f"   • Infografías: {summary.get('infographics', 0)}")
    lines.append(f"   • Textos en pantalla: {summary.get('text_overlays', 0)}")
    lines.append("")
    lines.append(f"💡 ESTRATEGIA:")
    lines.append(f"   {summary.get('strategy', 'N/A')}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    markers = analysis.get('visual_markers', [])

    # Agrupar por tipo
    photos = [m for m in markers if m['type'] == 'photo']
    infographics = [m for m in markers if m['type'] == 'infographic']
    text_overlays = [m for m in markers if m['type'] == 'text_overlay']

    # SECCIÓN: IMÁGENES FOTOREALISTAS
    if photos:
        lines.append("🖼️  IMÁGENES FOTOREALISTAS")
        lines.append("=" * 80)
        for i, marker in enumerate(photos, 1):
            lines.append(f"\n[{i}] TIMESTAMP: {marker['timestamp']} (Duración: {marker['duration_seconds']}s)")
            lines.append(f"    Contexto: {marker['context']}")
            lines.append(f"    ")
            lines.append(f"    PROMPT PARA DALL-E / MIDJOURNEY:")
            lines.append(f"    {marker['prompt']}")
            lines.append("")

    # SECCIÓN: INFOGRAFÍAS
    if infographics:
        lines.append("\n📊 INFOGRAFÍAS Y GRÁFICOS")
        lines.append("=" * 80)
        for i, marker in enumerate(infographics, 1):
            lines.append(f"\n[{i}] TIMESTAMP: {marker['timestamp']} (Duración: {marker['duration_seconds']}s)")
            lines.append(f"    Título: {marker['title']}")
            lines.append(f"    Contexto: {marker['context']}")
            lines.append(f"    ")
            lines.append(f"    CONTENIDO DE LA INFOGRAFÍA:")
            content = marker.get('content', {})
            lines.append(f"    Tipo: {content.get('type', 'N/A')}")
            lines.append(f"    Descripción: {content.get('description', 'N/A')}")
            if 'data' in content:
                lines.append(f"    Datos: {content.get('data')}")
            lines.append("")

    # SECCIÓN: TEXTOS EN PANTALLA
    if text_overlays:
        lines.append("\n💬 TEXTOS EN PANTALLA")
        lines.append("=" * 80)
        for i, marker in enumerate(text_overlays, 1):
            lines.append(f"\n[{i}] TIMESTAMP: {marker['timestamp']} (Duración: {marker['duration_seconds']}s)")
            lines.append(f"    Texto: \"{marker['text']}\"")
            lines.append(f"    Estilo: {marker.get('style', 'normal')}")
            lines.append(f"    Contexto: {marker['context']}")
            lines.append("")

    lines.append("=" * 80)
    lines.append("💡 NOTAS DE PRODUCCIÓN:")
    lines.append("   1. Genera las imágenes usando los prompts en DALL-E 3 o Midjourney")
    lines.append("   2. Crea las infografías en Canva/Figma usando las especificaciones")
    lines.append("   3. Inserta los elementos en los timestamps indicados")
    lines.append("   4. Ajusta las duraciones según el ritmo del video")
    lines.append("=" * 80)

    return '\n'.join(lines)

def generate_timeline_csv(markers, output_path):
    """
    Genera CSV con timeline para importar en editores de video
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("Timestamp,Type,Duration,Description\n")

        # Markers
        for marker in markers:
            timestamp = marker['timestamp']
            marker_type = marker['type']
            duration = marker['duration_seconds']

            # Descripción según tipo
            if marker_type == 'photo':
                desc = f"IMAGE: {marker['prompt'][:50]}..."
            elif marker_type == 'infographic':
                desc = f"INFOGRAPHIC: {marker['title']}"
            elif marker_type == 'text_overlay':
                desc = f"TEXT: {marker['text']}"
            else:
                desc = "N/A"

            # Escapar comillas en CSV
            desc = desc.replace('"', '""')

            f.write(f'{timestamp},{marker_type},{duration},"{desc}"\n')

def main():
    print("=" * 80)
    print("  GENERADOR DE MARCADORES VISUALES - AI PODCAST PRODUCER")
    print("=" * 80)

    # 1. Validar API Key
    if not OPENAI_API_KEY:
        print("\n❌ ERROR: No se encontró OPENAI_API_KEY en el archivo .env")
        print("Por favor, agrega la línea: OPENAI_API_KEY=sk-tu_clave_aqui")
        return

    # 2. Buscar archivo .srt
    print("\n--> Paso 1/4: Buscando archivo de subtítulos...")
    srt_files = [f for f in os.listdir(TRANSCRIPTIONS_DIR) if f.endswith('.srt') and os.path.isfile(os.path.join(TRANSCRIPTIONS_DIR, f))]

    if len(srt_files) == 0:
        print("❌ ERROR: No se encontró ningún archivo .srt en /output/transcriptions")
        print("Por favor, ejecuta primero: python generate_subtitles.py")
        return

    srt_path = os.path.join(TRANSCRIPTIONS_DIR, srt_files[0])
    filename_base = os.path.splitext(srt_files[0])[0]

    print(f"✓ Archivo encontrado: {srt_files[0]}")

    # 3. Parsear transcripción
    print("\n--> Paso 2/4: Analizando transcripción...")
    try:
        transcription = parse_srt(srt_path)
        total_entries = len(transcription)
        print(f"✓ Se cargaron {total_entries} segmentos")

        if transcription:
            last_timestamp = transcription[-1]['timestamp']
            print(f"✓ Duración del contenido: {last_timestamp}")
    except Exception as e:
        print(f"❌ ERROR al leer el archivo: {e}")
        return

    # 4. Analizar con IA
    print("\n--> Paso 3/4: Generando marcadores visuales con IA...")
    transcription_text = format_transcription_with_timestamps(transcription)

    # Calcular costo
    estimated_tokens = len(transcription_text) // 4
    estimated_cost = (estimated_tokens / 1_000_000) * 0.15

    print(f"   Tokens estimados: ~{estimated_tokens:,}")
    print(f"   Costo estimado: ~${estimated_cost:.4f} USD")
    print("   Analizando momentos clave para elementos visuales...")

    analysis = analyze_visual_opportunities(transcription_text)

    if not analysis:
        print("❌ ERROR: No se pudo completar el análisis")
        return

    markers = analysis.get('visual_markers', [])
    summary = analysis.get('summary', {})

    print(f"✓ Análisis completado")
    print(f"   • Total de marcadores: {summary.get('total_markers', len(markers))}")
    print(f"   • Imágenes: {summary.get('photos', 0)}")
    print(f"   • Infografías: {summary.get('infographics', 0)}")
    print(f"   • Textos: {summary.get('text_overlays', 0)}")

    # 5. Generar archivos
    print("\n--> Paso 4/4: Generando archivos de salida...")

    try:
        os.makedirs(METADATA_DIR, exist_ok=True)

        # A. Guía visual completa (TXT)
        guide_path = os.path.join(METADATA_DIR, f"{filename_base}_visual_guide.txt")
        guide_text = generate_visual_guide(analysis, guide_path)
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_text)
        print(f"✓ {guide_path}")

        # B. Timeline CSV (para importar en editores)
        csv_path = os.path.join(METADATA_DIR, f"{filename_base}_visual_timeline.csv")
        generate_timeline_csv(markers, csv_path)
        print(f"✓ {csv_path}")

        # C. JSON completo
        json_path = os.path.join(METADATA_DIR, f"{filename_base}_visual_markers.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✓ {json_path}")

    except Exception as e:
        print(f"❌ ERROR al guardar archivos: {e}")
        return

    # 6. Resumen
    print("\n" + "=" * 80)
    print("✅ ¡MARCADORES VISUALES GENERADOS!")
    print("=" * 80)
    print(f"\n📂 ARCHIVOS GENERADOS:")
    print(f"   1. {filename_base}_visual_guide.txt")
    print(f"      → Guía completa con prompts y especificaciones")
    print(f"   2. {filename_base}_visual_timeline.csv")
    print(f"      → Timeline para importar en editores (Premiere, DaVinci)")
    print(f"   3. {filename_base}_visual_markers.json")
    print(f"      → Datos estructurados (JSON)")
    print(f"\n💡 SIGUIENTE PASO:")
    print(f"   1. Revisa la guía visual")
    print(f"   2. Genera las imágenes usando los prompts en DALL-E/Midjourney")
    print(f"   3. Crea las infografías en Canva/Figma")
    print(f"   4. Importa el CSV en tu editor de video como marcadores")
    print(f"\n🎨 HERRAMIENTAS RECOMENDADAS:")
    print(f"   • Imágenes: DALL-E 3, Midjourney, Leonardo AI")
    print(f"   • Infografías: Canva, Figma, Adobe Express")
    print(f"   • Edición: DaVinci Resolve, Premiere Pro, Final Cut Pro")
    print("=" * 80)

if __name__ == "__main__":
    main()
