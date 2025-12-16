# Script: montar_video.py
# Requisitos: pip install moviepy

import json
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- CONFIGURACIÓN ---
INPUT_DIR = "./input"
OUTPUT_DIR = "./output"
# Archivos de entrada (Debes traerlos de HeyGen)
FILE_VIDEO_A = "./input/video_host_A.mp4"
FILE_VIDEO_B = "./input/video_host_B.mp4"
# Archivo generado por el script anterior
JSON_GUIA = "./output/editing_guide.json"

def montar_video():
    print("--> Paso 1/4: Buscando archivo de audio original...")

    # Buscar archivo .m4a en /input para determinar el nombre de salida
    m4a_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.m4a') and os.path.isfile(os.path.join(INPUT_DIR, f))]

    if len(m4a_files) == 0:
        print("❌ ERROR: No se encontró ningún archivo .m4a en /input")
        return

    # Usar el nombre del archivo original para el output
    filename_base = os.path.splitext(m4a_files[0])[0]
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"{filename_base}.mp4")

    print(f"✓ Archivo original encontrado: {m4a_files[0]}")
    print(f"✓ El video final se guardará como: {filename_base}.mp4")

    print("\n--> Paso 2/4: Verificando archivos...")

    # Validaciones
    files_needed = [FILE_VIDEO_A, FILE_VIDEO_B, JSON_GUIA]
    missing = [f for f in files_needed if not os.path.exists(f)]

    if missing:
        print(f"❌ ERROR: Faltan archivos necesarios: {missing}")
        print("   Asegúrate de haber corrido 'split_audios.py' y de haber descargado los videos de HeyGen.")
        return

    print("\n--> Paso 3/4: Cargando videos y procesando cortes de cámara...")
    
    # Cargar videos en memoria
    # Nota: audio=True es importante para mantener el audio que generó HeyGen
    clip_a = VideoFileClip(FILE_VIDEO_A)
    clip_b = VideoFileClip(FILE_VIDEO_B)
    
    with open(JSON_GUIA, 'r') as f:
        guia = json.load(f)
    
    clips_finales = []
    tiempo_actual = 0.0
    
    # Variable para saber quién fue el último en hablar (para planos de reacción)
    ultimo_host_activo = "HOST_A" 

    total_cortes = len(guia)

    for i, bloque in enumerate(guia):
        inicio = bloque['start']
        fin = bloque['end']
        host_actual = bloque['host']

        # --- LÓGICA DE "REACCIÓN" (Rellenar silencios) ---
        # Si hay un espacio vacío entre el corte anterior y este...
        if inicio > tiempo_actual:
            duracion_gap = inicio - tiempo_actual
            if duracion_gap > 0.1: # Ignoramos micro-gaps menores a 100ms
                # Rellenamos con el video del ÚLTIMO que habló (se queda escuchando)
                if ultimo_host_activo == "HOST_A":
                    gap = clip_a.subclip(tiempo_actual, inicio)
                else:
                    gap = clip_b.subclip(tiempo_actual, inicio)
                clips_finales.append(gap)

        # --- LÓGICA DE "ACCIÓN" (El que habla) ---
        if host_actual == "HOST_A":
            segmento = clip_a.subclip(inicio, fin)
            ultimo_host_activo = "HOST_A"
        else:
            segmento = clip_b.subclip(inicio, fin)
            ultimo_host_activo = "HOST_B"
        
        clips_finales.append(segmento)
        
        # Avanzamos el cursor
        tiempo_actual = fin
        
        # Feedback visual
        if i % 5 == 0:
            print(f"   Montando corte {i}/{total_cortes}...", end="\r")

    print(f"   Montando corte {total_cortes}/{total_cortes} - Listo.")

    print("\n--> Paso 4/4: Renderizando video final (Ve por un café ☕)...")
    
    # Unir todo
    video_final = concatenate_videoclips(clips_finales, method="compose")
    
    # Exportar
    # preset="medium" es buen balance. Usa "ultrafast" si solo estás probando.
    video_final.write_videofile(
        OUTPUT_FILE, 
        codec="libx264", 
        audio_codec="aac", 
        fps=24,
        preset="medium",
        threads=4
    )

    print(f"\n✅ ¡PRODUCCIÓN TERMINADA! Video guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    montar_video()