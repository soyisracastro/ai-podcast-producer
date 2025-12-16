#!/bin/bash

# ==================================================================================
# EJEMPLO DE WORKFLOW COMPLETO
# Este script muestra el flujo de trabajo completo para producir un episodio
# ==================================================================================

# NO EJECUTAR TODO EL SCRIPT DE UNA VEZ - Son ejemplos paso a paso
# Copia y pega cada comando individualmente

echo "========================================="
echo "  WORKFLOW COMPLETO - AI PODCAST PRODUCER"
echo "========================================="
echo ""

# --------------------------
# PASO 1: Preparar Input
# --------------------------
echo "PASO 1: Colocar audio de NotebookLM"
echo "Ubicación: input/podcast_notebooklm.m4a"
echo ""
echo "Comando:"
echo "  cp ~/Downloads/podcast_notebooklm.m4a input/"
echo ""

# --------------------------
# PASO 2: Análisis y Splitting
# --------------------------
echo "PASO 2: Ejecutar análisis de audio"
echo "Comando:"
echo "  python split_audios.py"
echo ""
echo "Output esperado:"
echo "  - output/track_host_A.mp3"
echo "  - output/track_host_B.mp3"
echo "  - output/editing_guide.json"
echo ""

# --------------------------
# PASO 3: Generar Avatares (Manual)
# --------------------------
echo "PASO 3: Generar videos en HeyGen"
echo "  1. Ir a https://heygen.com"
echo "  2. Subir output/track_host_A.mp3 → Seleccionar avatar"
echo "  3. Subir output/track_host_B.mp3 → Seleccionar avatar"
echo "  4. Descargar videos como:"
echo "     - input/video_host_A.mp4"
echo "     - input/video_host_B.mp4"
echo ""

# --------------------------
# PASO 4: Ensamblar Video
# --------------------------
echo "PASO 4: Ensamblar video final"
echo "Comando:"
echo "  python assemble_video.py"
echo ""
echo "Output esperado:"
echo "  - output/final_episode.mp4"
echo ""

# --------------------------
# PASO 5: Archivar y Limpiar
# --------------------------
echo "PASO 5: Archivar trabajo y limpiar"
echo "Comando (con nombre personalizado):"
echo "  ./archive_and_clean.sh 'episodio_01_introduccion_ia'"
echo ""
echo "Comando (con timestamp automático):"
echo "  ./archive_and_clean.sh"
echo ""
echo "Output esperado:"
echo "  - archives/episodio_01_introduccion_ia.zip"
echo "  - input/ y output/ limpios"
echo ""

# --------------------------
# PASO 6: Subir a Nube (Opcional)
# --------------------------
echo "PASO 6A: Subir a AWS S3 (Opcional)"
echo "Comando:"
echo "  ./upload_to_s3.sh episodio_01_introduccion_ia.zip my-podcast-bucket"
echo ""
echo "PASO 6B: Subir a OneDrive (Opcional)"
echo "Comando:"
echo "  cp archives/episodio_01_introduccion_ia.zip ~/OneDrive/Podcasts/"
echo ""
echo "PASO 6C: Subir a Google Drive (Opcional)"
echo "Comando:"
echo "  cp archives/episodio_01_introduccion_ia.zip ~/Google\\ Drive/Podcasts/"
echo ""

# --------------------------
# PASO 7: Limpiar Archives Locales
# --------------------------
echo "PASO 7: Limpiar archives locales (después de confirmar subida)"
echo "Comando:"
echo "  rm archives/episodio_01_introduccion_ia.zip"
echo ""

echo "========================================="
echo "  FIN DEL WORKFLOW"
echo "========================================="
echo ""
echo "Para más información:"
echo "  - README.md - Documentación principal"
echo "  - ARCHIVE_GUIDE.md - Guía de archivado"
echo "  - SETUP_MAC.md - Setup para macOS"
