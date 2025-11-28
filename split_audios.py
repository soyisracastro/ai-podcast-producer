# Script definitivo: split_audios.py
# Requisitos: pip install pyannote.audio pydub torch python-dotenv

import os
import json
import warnings
from dotenv import load_dotenv

# Ignorar warnings innecesarios
warnings.filterwarnings("ignore")


from pyannote.audio import Pipeline
from pydub import AudioSegment
from huggingface_hub import login

# 1. Cargar variables de entorno (.env)
# Esto busca el archivo .env en la misma carpeta y carga HF_TOKEN
load_dotenv()

# --- CONFIGURACIÓN ---
HF_TOKEN = os.getenv("HF_TOKEN")
INPUT_DIR = "./input"
TEMP_WAV = "./input/temp_audio.wav"             # Archivo temporal

# Validación de seguridad
if not HF_TOKEN:
    print("❌ ERROR: No se encontró la variable HF_TOKEN.")
    print("Asegúrate de tener un archivo '.env' con la línea: HF_TOKEN=hf_tu_token_aqui")
    exit()

# Buscar archivo .m4a en el directorio /input
print("--> Buscando archivo .m4a en /input...")
m4a_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.m4a') and os.path.isfile(os.path.join(INPUT_DIR, f))]

if len(m4a_files) == 0:
    print("❌ ERROR: No se encontró ningún archivo .m4a en el directorio /input")
    print("Por favor, coloca tu audio de NotebookLM en la carpeta /input")
    exit()
elif len(m4a_files) > 1:
    print("⚠️  ADVERTENCIA: Se encontraron múltiples archivos .m4a:")
    for idx, file in enumerate(m4a_files, 1):
        print(f"   {idx}. {file}")
    print(f"\nUsando el primer archivo: {m4a_files[0]}")
    INPUT_FILE = os.path.join(INPUT_DIR, m4a_files[0])
else:
    INPUT_FILE = os.path.join(INPUT_DIR, m4a_files[0])
    print(f"✓ Archivo encontrado: {m4a_files[0]}")

# 2. Preprocesamiento (M4A -> WAV)
print(f"--> Paso 1/5: Convirtiendo audio a WAV para la IA...")
try:
    # Usamos pydub para leer el m4a y guardarlo como wav
    original_audio = AudioSegment.from_file(INPUT_FILE, format="m4a")
    original_audio.export(TEMP_WAV, format="wav")
except Exception as e:
    print(f"❌ Error al leer el audio. Verifica que tengas FFmpeg instalado.")
    print(f"Detalle del error: {e}")
    exit()

# 3. Cargar el modelo de IA
print("--> Paso 2/5: Cargando modelo de Diarización (esto puede tardar)...")
try:
    login(token=HF_TOKEN)

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1"
    )
except Exception as e:
    print(f"❌ ERROR TÉCNICO AL CARGAR EL MODELO:")
    print(f"------------------------------------------------")
    print(f"{e}")  # <--- ESTO ES LO QUE NECESITAMOS VER
    print(f"------------------------------------------------")
    print(f"Si el error menciona 'libsndfile' o 'torchaudio', es un problema de instalación, no de token.")
    exit()

# 4. Analizar quién habla
print(f"--> Paso 3/5: Analizando conversación e identificando voces...")
diarization = pipeline(TEMP_WAV)

# 5. Procesamiento de Pistas y JSON
print("--> Paso 4/5: Generando pistas sincronizadas y guía de video...")

# Crear pistas mudas base (misma duración que el original)
track_host_a = AudioSegment.silent(duration=len(original_audio), frame_rate=original_audio.frame_rate)
track_host_b = AudioSegment.silent(duration=len(original_audio), frame_rate=original_audio.frame_rate)

guia_video = []

# Convertimos a lista para poder contar el total y usar una barra de progreso real
tracks_list = list(diarization.itertracks(yield_label=True))
total_segments = len(tracks_list)

# Identificar todos los speakers únicos detectados
unique_speakers = set()
for turn, _, speaker in tracks_list:
    unique_speakers.add(speaker)

print(f"   Se encontraron {total_segments} segmentos de voz.")
print(f"   Speakers detectados: {sorted(unique_speakers)}")

# Mapeo dinámico de speakers basado en ORDEN DE APARICIÓN (quién habla primero)
speaker_mapping = {}
speakers_in_order = []

# Obtener speakers en orden de aparición
for turn, _, speaker in tracks_list:
    if speaker not in speakers_in_order:
        speakers_in_order.append(speaker)

# Asignar HOST_A al que habla primero, HOST_B al segundo
for idx, speaker in enumerate(speakers_in_order):
    if idx == 0:
        speaker_mapping[speaker] = "HOST_A"
        print(f"   HOST_A asignado a '{speaker}' (habla primero en {tracks_list[0][0].start:.2f}s)")
    elif idx == 1:
        speaker_mapping[speaker] = "HOST_B"
        # Encontrar cuándo habla por primera vez HOST_B
        first_b_time = next((turn.start for turn, _, spk in tracks_list if spk == speaker), 0)
        print(f"   HOST_B asignado a '{speaker}' (habla primero en {first_b_time:.2f}s)")
    else:
        # Si hay más de 2 speakers, asignar a HOST_B por defecto
        speaker_mapping[speaker] = "HOST_B"
        print(f"   ⚠️  ADVERTENCIA: Se detectó un tercer speaker '{speaker}', será asignado a HOST_B")

print(f"   Mapeo final: {speaker_mapping}")
print()

for i, (turn, _, speaker) in enumerate(tracks_list):
    # Convertir segundos a milisegundos para Pydub
    start_ms = int(turn.start * 1000)
    end_ms = int(turn.end * 1000)
    
    # A. Lógica de Audio usando mapeo dinámico
    voice_segment = original_audio[start_ms:end_ms]

    # Obtener el nombre del host del mapeo
    host_name = speaker_mapping.get(speaker, "UNKNOWN")

    # Pegar voz sobre el silencio del track correspondiente
    if host_name == "HOST_A":
        track_host_a = track_host_a.overlay(voice_segment, position=start_ms)
    elif host_name == "HOST_B":
        track_host_b = track_host_b.overlay(voice_segment, position=start_ms)
    
    # B. Lógica de Video (JSON)
    guia_video.append({
        "host": host_name,
        "start": turn.start,
        "end": turn.end,
        "duration": turn.end - turn.start
    })
    
    # Feedback visual simple
    if i % 10 == 0: # Imprimir cada 10 segmentos para no saturar la consola
        print(f"   Procesando... {i}/{total_segments}", end="\r")

print(f"   Procesando... {total_segments}/{total_segments} - ¡Listo!")

# 6. Guardar Archivos
print("--> Paso 5/5: Guardando archivos finales...")

# Audios para HeyGen
track_host_a.export("./output/track_host_A.mp3", format="mp3")
track_host_b.export("./output/track_host_B.mp3", format="mp3")

# JSON para el script de video
with open('./output/editing_guide.json', 'w') as f:
    json.dump(guia_video, f, indent=4)

# Limpiar archivo temporal
if os.path.exists(TEMP_WAV):
    os.remove(TEMP_WAV)

print("\n✅ ¡PROCESO FINALIZADO CON ÉXITO!")
print("📂 Archivos generados:")
print("   1. track_host_A.mp3  (Subir a HeyGen -> Generar video_host_A.mp4)")
print("   2. track_host_B.mp3  (Subir a HeyGen -> Generar video_host_B.mp4)")
print("   3. editing_guide.json (Usar con script 'montar_video.py')")