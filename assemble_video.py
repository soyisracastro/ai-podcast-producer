# Script: montar_video.py
# Requisitos: pip install moviepy

import json
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- CONFIGURACIÓN ---
# Archivos de entrada (Debes traerlos de HeyGen)
FILE_VIDEO_A = "video_host_A.mp4" 
FILE_VIDEO_B = "video_host_B.mp4"
# Archivo generado por el script anterior
JSON_GUIA = "editing_guide.json"
# Salida
OUTPUT_FILE = "final_episode.mp4"

def montar_video():
    print("--> Paso 1/3: Verificando archivos...")
    
    # Validaciones
    files_needed = [FILE_VIDEO_A, FILE_VIDEO_B, JSON_GUIA]
    missing = [f for f in files_needed if not os.path.exists(f)]
    
    if missing:
        print(f"❌ ERROR: Faltan archivos necesarios: {missing}")
        print("   Asegúrate de haber corrido 'split_audios.py' y de haber descargado los videos de HeyGen.")
        return

    print("--> Paso 2/3: Cargando videos y procesando cortes de cámara...")
    
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

    print("--> Paso 3/3: Renderizando video final (Ve por un café ☕)...")
    
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