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
INPUT_FILE = "./input/podcast_notebooklm.m4a"   # Tu archivo de entrada
TEMP_WAV = "./input/temp_audio.wav"             # Archivo temporal

# Validación de seguridad
if not HF_TOKEN:
    print("❌ ERROR: No se encontró la variable HF_TOKEN.")
    print("Asegúrate de tener un archivo '.env' con la línea: HF_TOKEN=hf_tu_token_aqui")
    exit()

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

print(f"   Se encontraron {total_segments} segmentos de voz.")

for i, (turn, _, speaker) in enumerate(tracks_list):
    # Convertir segundos a milisegundos para Pydub
    start_ms = int(turn.start * 1000)
    end_ms = int(turn.end * 1000)
    
    # A. Lógica de Audio
    voice_segment = original_audio[start_ms:end_ms]
    
    host_name = "UNKNOWN"
    
    if speaker == "SPEAKER_00":
        # Pegar voz sobre el silencio
        track_host_a = track_host_a.overlay(voice_segment, position=start_ms)
        host_name = "HOST_A"
    elif speaker == "SPEAKER_01":
        track_host_b = track_host_b.overlay(voice_segment, position=start_ms)
        host_name = "HOST_B"
    
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
with open('editing_guide.json', 'w') as f:
    json.dump(guia_video, f, indent=4)

# Limpiar archivo temporal
if os.path.exists(TEMP_WAV):
    os.remove(TEMP_WAV)

print("\n✅ ¡PROCESO FINALIZADO CON ÉXITO!")
print("📂 Archivos generados:")
print("   1. track_host_A.mp3  (Subir a HeyGen -> Generar video_host_A.mp4)")
print("   2. track_host_B.mp3  (Subir a HeyGen -> Generar video_host_B.mp4)")
print("   3. editing_guide.json (Usar con script 'montar_video.py')")