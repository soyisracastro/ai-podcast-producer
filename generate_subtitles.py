# Script: generate_subtitles.py
# Requisitos: pip install openai-whisper
# Descripción: Genera subtítulos (.srt) desde el audio original usando Whisper AI

import os
import warnings
import whisper
from datetime import timedelta

# Ignorar warnings innecesarios
warnings.filterwarnings("ignore")

# --- CONFIGURACIÓN ---
INPUT_DIR = "./input"
OUTPUT_DIR = "./output"

def format_timestamp(seconds):
    """
    Convierte segundos flotantes a formato SRT: HH:MM:SS,mmm
    Ejemplo: 65.123 -> 00:01:05,123
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(segments, output_path):
    """
    Genera archivo .srt desde los segmentos de Whisper
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            # Número de subtítulo
            f.write(f"{i}\n")
            # Timestamp (inicio --> fin)
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            f.write(f"{start} --> {end}\n")
            # Texto del subtítulo
            f.write(f"{segment['text'].strip()}\n")
            # Línea vacía separadora
            f.write("\n")

def main():
    print("=" * 60)
    print("  GENERADOR DE SUBTÍTULOS - AI PODCAST PRODUCER")
    print("=" * 60)

    # 1. Buscar archivo .m4a en /input
    print("\n--> Paso 1/4: Buscando archivo de audio...")
    m4a_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.m4a') and os.path.isfile(os.path.join(INPUT_DIR, f))]

    if len(m4a_files) == 0:
        print("❌ ERROR: No se encontró ningún archivo .m4a en el directorio /input")
        print("Por favor, coloca tu audio de NotebookLM en la carpeta /input")
        return
    elif len(m4a_files) > 1:
        print("⚠️  ADVERTENCIA: Se encontraron múltiples archivos .m4a:")
        for idx, file in enumerate(m4a_files, 1):
            print(f"   {idx}. {file}")
        print(f"\nUsando el primer archivo: {m4a_files[0]}")

    input_file = os.path.join(INPUT_DIR, m4a_files[0])
    filename = os.path.splitext(m4a_files[0])[0]
    output_srt = os.path.join(OUTPUT_DIR, f"{filename}.srt")

    print(f"✓ Archivo encontrado: {m4a_files[0]}")

    # 2. Cargar modelo de Whisper
    print("\n--> Paso 2/4: Cargando modelo de IA Whisper...")
    print("    Modelos disponibles: tiny, base, small, medium, large")
    print("    Usando: 'base' (mejor balance velocidad/precisión)")
    print("    💡 Tip: Para español de alta calidad usa 'medium' o 'large'")

    try:
        # Opciones de modelo:
        # - tiny: Muy rápido, menos preciso (~1GB RAM)
        # - base: Rápido, buena precisión (~1GB RAM) ← RECOMENDADO
        # - small: Más lento, mejor precisión (~2GB RAM)
        # - medium: Lento, excelente precisión (~5GB RAM)
        # - large: Muy lento, máxima precisión (~10GB RAM)
        model = whisper.load_model("base")
    except Exception as e:
        print(f"❌ ERROR al cargar el modelo: {e}")
        return

    # 3. Transcribir audio
    print("\n--> Paso 3/4: Transcribiendo audio (esto puede tardar varios minutos)...")
    print("    Procesando con timestamps precisos para subtítulos...")

    try:
        # Transcribir con opciones optimizadas para subtítulos
        result = model.transcribe(
            input_file,
            language="es",           # Forzar español para mejor precisión
            task="transcribe",       # 'transcribe' mantiene idioma original
            verbose=False,           # No mostrar progreso detallado
            word_timestamps=False    # Timestamps por frase (mejor para SRT)
        )

        segments = result['segments']
        total_segments = len(segments)

        print(f"✓ Transcripción completada: {total_segments} segmentos detectados")

        # Mostrar preview de los primeros 3 segmentos
        print("\n📝 Preview de transcripción:")
        for i, seg in enumerate(segments[:3], 1):
            start = format_timestamp(seg['start'])
            text_preview = seg['text'].strip()[:60]
            print(f"   {i}. [{start}] {text_preview}...")

        if total_segments > 3:
            print(f"   ... y {total_segments - 3} segmentos más")

    except Exception as e:
        print(f"❌ ERROR durante la transcripción: {e}")
        return

    # 4. Generar archivo .srt
    print(f"\n--> Paso 4/4: Generando archivo de subtítulos...")

    try:
        # Crear directorio /output si no existe
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        generate_srt(segments, output_srt)

        print(f"✓ Archivo generado exitosamente")

    except Exception as e:
        print(f"❌ ERROR al guardar el archivo: {e}")
        return

    # 5. Resumen final
    print("\n" + "=" * 60)
    print("✅ ¡PROCESO COMPLETADO!")
    print("=" * 60)
    print(f"📂 Archivo generado:")
    print(f"   {output_srt}")
    print(f"\n📊 Estadísticas:")
    print(f"   • Total de subtítulos: {total_segments}")
    print(f"   • Duración total: {format_timestamp(segments[-1]['end'])}")
    print(f"   • Idioma detectado: {result.get('language', 'N/A')}")
    print("\n💡 Siguiente paso:")
    print("   Importa el archivo .srt en tu editor de video o YouTube")
    print("=" * 60)

if __name__ == "__main__":
    main()
