# 📋 Checklist de Producción de Episodio

**Episodio:** [Nombre del episodio]
**Fecha de publicación:** [Lunes de la semana target]
**Estado:** 🟡 En progreso

---

## ✅ Checklist de Pasos

### 1️⃣ Preparación Inicial
- [ ] Colocar audio `.m4a` en `/input/`
- [ ] Colocar videos de avatares en `/input/` (si aplica)
  - [ ] `video_host_A.mp4`
  - [ ] `video_host_B.mp4`
- [ ] Activar entorno virtual: `source venv/bin/activate`

---

### 2️⃣ Procesamiento de Audio
- [ ] Ejecutar división de audios: `python split_audios.py`
  - **Output esperado:**
    - `output/track_host_A.mp3`
    - `output/track_host_B.mp3`
    - `output/editing_guide.json`
- [ ] Verificar asignación de voces (si hay problema, ver docs)

---

### 3️⃣ Generación de Videos (HeyGen) - MANUAL
- [ ] Subir `track_host_A.mp3` a HeyGen
- [ ] Subir `track_host_B.mp3` a HeyGen
- [ ] Descargar videos generados
- [ ] Mover videos a `/input/` con nombres correctos

---

### 4️⃣ Transcripción y Subtítulos
- [ ] Generar subtítulos: `python generate_subtitles.py`
  - **Output esperado:**
    - `output/transcriptions/{nombre}.srt`
    - `output/transcriptions/{nombre}.txt`

---

### 5️⃣ Análisis con IA (Metadata y Calendario)
- [ ] Generar análisis de capítulos: `python analyze_chapters.py`
  - **Output esperado:**
    - `output/metadata/{nombre}_youtube.txt` - Metadata de YouTube
    - `output/metadata/{nombre}_chapters.json` - Capítulos estructurados
    - `output/metadata/{nombre}_metadata.json` - Análisis completo
    - `output/metadata/{nombre}_content_table.csv` - Tabla SEO
    - `output/metadata/{nombre}_calendar.csv` - Calendario de publicación
- [ ] Revisar y ajustar metadata si es necesario

---

### 6️⃣ Generación de Marcadores Visuales (Opcional)
- [ ] Generar guía visual: `python generate_visual_markers.py`
  - **Output esperado:**
    - `output/metadata/{nombre}_visual_guide.txt`
    - `output/metadata/{nombre}_visual_timeline.csv`
    - `output/metadata/{nombre}_visual_markers.json`

---

### 7️⃣ Ensamblaje de Video Final
- [ ] Ensamblar video: `python assemble_video.py`
  - **Output esperado:**
    - `output/{nombre}.mp4` - Video final editado

---

### 8️⃣ Generación de Clips
- [ ] Generar clips automáticos: `python generate_clips.py`
  - **Output esperado:**
    - `output/viral_clips/viral_clip_{titulo}.mp4` (4-15 clips virales)
    - `output/clips/clip_{titulo}.mp4` (clips por capítulo)
- [ ] Verificar calidad de clips generados

---

### 9️⃣ Sincronización con Notion
- [ ] Sincronizar calendario: `python sync_to_notion.py DD-MM-AAAA`
  - **Ejemplo:** `python sync_to_notion.py 16-12-2024`
- [ ] Verificar que todas las entradas estén en Notion
- [ ] Cambiar a vista "Calendario" en Notion
- [ ] Ajustar fechas manualmente si es necesario

---

### 🔟 Publicación de Contenido

#### YouTube - Episodio Completo
- [ ] Subir video completo a YouTube
- [ ] Copiar título desde `_youtube.txt`
- [ ] Copiar descripción desde `_youtube.txt`
- [ ] Agregar capítulos desde `_youtube.txt`
- [ ] Subir miniatura (usar prompt de `_youtube.txt`)
- [ ] Agregar tags y categoría
- [ ] Programar o publicar
- [ ] Marcar como "Publicado" en Notion

#### Spotify/Apple Podcasts - Audio
- [ ] Exportar audio del video final
- [ ] Subir a distribuidor de podcasts
- [ ] Marcar como "Publicado" en Notion

#### TikTok/Instagram - Clips Virales
- [ ] Publicar clips virales según calendario
- [ ] Usar títulos SEO de `_content_table.csv`
- [ ] Marcar cada uno como "Publicado" en Notion

#### YouTube Shorts/Clips
- [ ] Publicar clips de capítulos
- [ ] Usar títulos y descripciones de `_content_table.csv`
- [ ] Marcar como "Publicado" en Notion

---

### 1️⃣1️⃣ Archivo y Limpieza
- [ ] Archivar proyecto: `./archive_and_clean.sh`
  - **Output:** `archives/{nombre}.zip` (incluye input/ y output/)
- [ ] Confirmar que el ZIP se creó correctamente (verificar tamaño)
- [ ] Verificar que `/input` y `/output` estén vacíos
- [ ] (Opcional) Subir archivo a nube (OneDrive/S3/Google Drive)
- [ ] Listo para siguiente episodio ✨

---

## 📊 Métricas y Notas

**Archivos generados:**
- Videos: [ ] clips
- Metadata: [ ] archivos
- Tamaño total: [ ] GB

**Tiempo de producción:**
- Inicio: _______________
- Fin: _______________
- Total: _______________

**Notas adicionales:**
```
[Espacio para notas sobre el episodio, problemas encontrados, mejoras, etc.]
```

---

## 🔗 Referencias Rápidas

- [README.md](README.md) - Documentación principal
- [NOTION_SETUP.md](NOTION_SETUP.md) - Setup de Notion
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Solución de problemas
- [QUICK_START_DEBUG.md](docs/QUICK_START_DEBUG.md) - Debug rápido

---

**Estado Final:** 🟢 Completado | 🟡 En progreso | 🔴 Bloqueado
