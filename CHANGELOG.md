# Changelog

## [2024-11-27] - Mejoras en Detección Automática de Archivos

### 🎯 Cambios Principales

#### 1. Detección Automática de Archivos `.m4a` en `split_audios.py`

**Antes:**
- El script esperaba un archivo con nombre fijo: `podcast_notebooklm.m4a`
- Requería renombrar manualmente el archivo descargado de NotebookLM

**Ahora:**
- El script busca automáticamente cualquier archivo `.m4a` en `/input`
- Detecta y procesa el archivo sin necesidad de renombrarlo
- Muestra advertencia si hay múltiples archivos `.m4a` y usa el primero

**Beneficios:**
- No necesitas renombrar los archivos descargados de NotebookLM
- El nombre original del archivo se preserva para identificación
- Facilita el workflow al eliminar un paso manual

#### 2. Nomenclatura Inteligente en `archive_and_clean.sh`

**Antes:**
- Sin argumento: usaba timestamp genérico `podcast_episode_YYYYMMDD_HHMMSS.zip`
- Con argumento: usaba el nombre proporcionado

**Ahora:**
- Sin argumento: detecta el nombre del archivo `.m4a` y lo usa como nombre del ZIP
- Si no hay archivo `.m4a`: usa timestamp como fallback
- Con argumento: usa el nombre proporcionado (comportamiento sin cambios)

**Ejemplo:**
```bash
# Archivo en /input: "Audio Overview - AI and Machine Learning.m4a"
./archive_and_clean.sh
# Crea: Audio_Overview_-_AI_and_Machine_Learning.zip

# O puedes sobrescribir el nombre:
./archive_and_clean.sh "episodio_01"
# Crea: episodio_01.zip
```

**Beneficios:**
- Nomenclatura consistente entre el audio original y el archivo archivado
- Fácil identificación del contenido sin necesidad de especificar nombre manualmente
- Fallback inteligente a timestamp si no hay archivo `.m4a`

---

### 📝 Cambios en Archivos

#### Modificados:
- **split_audios.py** (líneas 21-48)
  - Añadida lógica de detección automática de archivos `.m4a`
  - Mensajes informativos sobre archivo detectado
  - Manejo de múltiples archivos `.m4a` (usa el primero)

- **archive_and_clean.sh** (líneas 85-107)
  - Añadida lógica de extracción de nombre desde archivo `.m4a`
  - Sanitización de nombre (reemplazo de espacios y caracteres especiales)
  - Fallback a timestamp si no se encuentra archivo `.m4a`

#### Actualizados (Documentación):
- **README.md**
  - Actualizada sección "Step 1: Audio Analysis & Splitting"
  - Actualizada sección "Step 4: Archive & Clean"

- **ARCHIVE_GUIDE.md**
  - Añadida explicación de detección automática de nombres
  - Actualizado ejemplo de salida con detección automática

---

### 🔄 Workflow Mejorado

**Antes:**
```bash
# 1. Descargar audio de NotebookLM
# 2. Renombrar manualmente a "podcast_notebooklm.m4a"
# 3. Mover a /input
python split_audios.py

# Después de producir:
./archive_and_clean.sh "nombre_manual_del_episodio"
```

**Ahora:**
```bash
# 1. Descargar audio de NotebookLM
# 2. Mover a /input (sin renombrar)
python split_audios.py  # Detecta automáticamente

# Después de producir:
./archive_and_clean.sh  # Usa el nombre original del audio
```

---

### ✅ Testing

Probado con archivo: `Listas_negras_del_SAT_EFOS_y_EDOS.m4a`

**Resultados:**
```
✓ split_audios.py detecta correctamente el archivo
✓ archive_and_clean.sh extrae el nombre: Listas_negras_del_SAT_EFOS_y_EDOS.zip
✓ Sanitización funciona correctamente (espacios → guiones bajos)
✓ Fallback a timestamp funciona cuando no hay archivos .m4a
```

---

### 🚀 Próximas Mejoras Sugeridas

- [ ] Opción para seleccionar archivo específico si hay múltiples `.m4a`
- [ ] Validación de formato de archivo antes de procesar
- [ ] Detección de archivos duplicados antes de archivar
- [ ] Opción para preservar archives locales por X días antes de eliminar

---

## Versiones Anteriores

### [2024-11-20] - Sistema de Archivado y Limpieza
- Añadido `archive_and_clean.sh` para archivado automático
- Añadido `upload_to_s3.sh` para subida opcional a AWS S3
- Creado `ARCHIVE_GUIDE.md` con documentación completa
- Actualizado `.gitignore` para excluir `/archives`

### [2024-11-19] - Release Inicial
- Implementado `split_audios.py` con diarización de speakers
- Implementado `assemble_video.py` con lógica multi-cámara
- Documentación inicial en `README.md` y `SETUP_MAC.md`
