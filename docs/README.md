# Documentación - AI Podcast Producer

Bienvenido a la documentación completa del proyecto AI Podcast Producer.

---

## 📚 Guías Disponibles

### 🚀 Inicio Rápido
- **[../README.md](../README.md)** - Documentación principal del proyecto
  - Instalación y configuración
  - Flujo de trabajo completo
  - Estructura del proyecto

### 🔧 Debugging y Troubleshooting

#### [QUICK_START_DEBUG.md](QUICK_START_DEBUG.md) - Guía Rápida (3 pasos)
**📖 Lee esto primero si tienes problemas con speakers**
- Guía rápida de 3 pasos para detectar y corregir errores
- Ejemplos prácticos con comandos
- ~5 minutos de lectura

#### [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guía Completa
**📖 Referencia completa de resolución de problemas**
- Explicación detallada de problemas comunes
- Soluciones paso a paso
- Consejos para mejorar la precisión
- FAQs

#### [SPEAKER_DETECTION_IMPROVEMENTS.md](SPEAKER_DETECTION_IMPROVEMENTS.md) - Detalles Técnicos
**📖 Para desarrolladores y usuarios avanzados**
- Explicación técnica de las mejoras implementadas
- Comparación antes/después
- Algoritmos de detección
- Roadmap de mejoras futuras

### 📦 Archivado y Backup

#### [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md) - Guía de Archivado
**📖 Workflow de archivado y backup**
- Cómo archivar episodios completados
- Scripts de automatización
- Upload a cloud (AWS S3, OneDrive, etc.)
- Mejores prácticas

---

## 🗺️ Guía de Navegación Rápida

### ¿Qué guía necesito?

| Situación | Guía Recomendada | Tiempo |
|-----------|------------------|---------|
| 🆕 Primera vez usando el proyecto | [README.md](../README.md) | 10 min |
| ⚠️ Problema con asignación de speakers | [QUICK_START_DEBUG.md](QUICK_START_DEBUG.md) | 5 min |
| 🔍 Quiero entender el problema a fondo | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 15 min |
| 🛠️ Detalles técnicos de las mejoras | [SPEAKER_DETECTION_IMPROVEMENTS.md](SPEAKER_DETECTION_IMPROVEMENTS.md) | 20 min |
| 📦 Archivar episodio completado | [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md) | 10 min |

---

## 🔧 Herramientas de Debugging

El proyecto incluye herramientas para debugging:

### Scripts disponibles:
```bash
# Analizar calidad de asignación de speakers
python3 debug_diarization.py

# Corregir asignaciones incorrectas
python3 fix_speaker_assignment.py --swap-range [inicio] [fin]
```

**Documentación:** Ver [QUICK_START_DEBUG.md](QUICK_START_DEBUG.md) para uso detallado

---

## 🚦 Flujo de Trabajo Recomendado

### 1. Configuración Inicial
→ [README.md](../README.md) - Sección "Installation"

### 2. Primer Episodio
→ [README.md](../README.md) - Sección "Usage"

### 3. Si hay problemas con speakers
→ [QUICK_START_DEBUG.md](QUICK_START_DEBUG.md)

### 4. Archivar episodio completado
→ [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md)

---

## 📖 Resumen de Cada Documento

### [QUICK_START_DEBUG.md](QUICK_START_DEBUG.md)
**Tipo:** Guía práctica
**Audiencia:** Todos los usuarios
**Contenido:**
- 3 pasos para detectar y corregir problemas
- Ejemplos con comandos reales
- Síntomas comunes
- Solución de problemas básicos

---

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**Tipo:** Referencia completa
**Audiencia:** Usuarios con problemas recurrentes
**Contenido:**
- Explicación técnica de causas
- Todas las soluciones disponibles
- Flujo de trabajo detallado
- Casos de uso complejos
- Preguntas frecuentes

---

### [SPEAKER_DETECTION_IMPROVEMENTS.md](SPEAKER_DETECTION_IMPROVEMENTS.md)
**Tipo:** Documentación técnica
**Audiencia:** Desarrolladores y usuarios avanzados
**Contenido:**
- Detalles de implementación
- Comparación antes/después
- Algoritmos utilizados
- Mejoras de precisión
- Roadmap futuro

---

### [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md)
**Tipo:** Workflow guide
**Audiencia:** Todos los usuarios
**Contenido:**
- Scripts de archivado automático
- Upload a AWS S3
- Integración con OneDrive/Google Drive
- Mejores prácticas de backup

---

## 🔗 Enlaces Externos Útiles

### Modelos de IA
- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) - Modelo de diarización
- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) - Modelo de segmentación

### Servicios
- [HeyGen](https://www.heygen.com/) - Generación de videos con avatares
- [OpenAI Whisper](https://github.com/openai/whisper) - Transcripción de audio

---

## 💡 Contribuir a la Documentación

Si encuentras errores o quieres mejorar la documentación:

1. Los archivos están en formato Markdown
2. Mantén el estilo consistente
3. Incluye ejemplos prácticos
4. Actualiza este índice si añades nuevos documentos

---

## 📞 Soporte

Si tienes preguntas no cubiertas en la documentación:

1. Revisa las secciones relevantes arriba
2. Consulta los FAQs en [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Ejecuta las herramientas de debugging para obtener más información

---

**Última actualización:** Diciembre 2024
