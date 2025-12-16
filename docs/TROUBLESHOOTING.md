# Guía de Resolución de Problemas - AI Podcast Producer

## Problema: Asignación Incorrecta de Speakers

### Síntomas
- El mismo avatar tiene voces de hombre y mujer en el video final
- En `editing_guide.json` hay secuencias largas (>15 segmentos) del mismo HOST
- Los hosts están mal asignados en ciertos rangos de tiempo

### Causa
El modelo de diarización (pyannote) a veces confunde a los speakers, especialmente:
- Cuando hay cambios de tono o volumen en las voces
- En segmentos muy cortos
- Cuando hay solapamiento de voces
- Con audios de baja calidad

---

## Soluciones Implementadas

### 1. Mejoras en `split_audios.py`

**Cambios realizados:**

#### A) Configuración optimizada del pipeline
```python
pipeline_params = {
    "min_speakers": 2,
    "max_speakers": 2
}
diarization = pipeline(TEMP_WAV, **pipeline_params)
```

**Beneficios:**
- Fuerza al modelo a detectar exactamente 2 speakers
- Evita que detecte speakers fantasma
- Mejora la consistencia en la asignación

#### B) Validación automática post-procesamiento
El script ahora detecta automáticamente secuencias sospechosas (>15 segmentos consecutivos del mismo host) y te alerta:

```
⚠️  ADVERTENCIA: Se detectaron 1 secuencias sospechosas:
   HOST_B: 19 segmentos consecutivos (160.3s - 248.0s, duración: 87.7s)
```

---

### 2. Herramientas de Debugging

#### `debug_diarization.py` - Análisis Detallado

**Uso:**
```bash
python3 debug_diarization.py
```

**Qué hace:**
- Analiza el archivo `editing_guide.json`
- Detecta secuencias sospechosas
- Muestra distribución temporal por minuto
- Identifica segmentos muy cortos (<0.5s)
- Calcula estadísticas de duración por host

**Ejemplo de salida:**
```
⚠️  HOST_B: 19 segmentos consecutivos
   Tiempo: 160.31s - 248.01s (87.69s de duración)
   Índices: 29 - 47

Minuto 3 (180s-240s): A=0, B=13 ⚠️  SOSPECHOSO
```

---

#### `fix_speaker_assignment.py` - Corrección Manual

**Uso:**
```bash
# Intercambiar hosts en un rango específico (en segundos)
python3 fix_speaker_assignment.py --swap-range 160 248

# Especificar archivos de entrada/salida
python3 fix_speaker_assignment.py --swap-range 160 248 \
    --input ./output/editing_guide.json \
    --output ./output/editing_guide_fixed.json
```

**Qué hace:**
- Intercambia HOST_A ↔ HOST_B en el rango de tiempo especificado
- Crea un backup automático del archivo original
- Ejecuta análisis de validación automáticamente
- Muestra estadísticas antes y después

**Ejemplo:**
```bash
$ python3 fix_speaker_assignment.py --swap-range 160 248

📂 Archivo cargado: ./output/editing_guide.json

Estadísticas:
  Total segmentos: 168
  HOST_A: 73 segmentos
  HOST_B: 95 segmentos

💾 Backup creado: ./output/editing_guide.json.backup_20251215_143022

🔄 Intercambiando hosts en rango 160.0s - 248.0s...
   ✓ 19 segmentos intercambiados

💾 Archivo guardado: ./output/editing_guide.json

Estadísticas:
  Total segmentos: 168
  HOST_A: 92 segmentos
  HOST_B: 76 segmentos
```

---

## Flujo de Trabajo Recomendado

### Opción 1: Re-ejecutar con configuración mejorada (RECOMENDADO)

```bash
# 1. Ejecutar split_audios.py con las mejoras
python3 split_audios.py

# 2. El script te alertará si detecta problemas
# 3. Si hay problemas, intenta ejecutar de nuevo (a veces mejora)
```

**Ventajas:**
- Más preciso desde el inicio
- No requiere corrección manual
- Aprovecha la configuración optimizada del modelo

---

### Opción 2: Corregir archivo existente

Si ya tienes un `editing_guide.json` con problemas:

```bash
# 1. Analizar el problema
python3 debug_diarization.py

# 2. Identificar el rango problemático (ejemplo: 160s - 248s)

# 3. Corregir intercambiando hosts en ese rango
python3 fix_speaker_assignment.py --swap-range 160 248

# 4. Re-ejecutar split_audios.py si necesitas regenerar los audios
```

---

## Consejos para Mejorar la Precisión

### 1. Calidad del Audio Original
- Usa audios de alta calidad (mínimo 128 kbps)
- Evita audios con mucho ruido de fondo
- Asegúrate de que las voces estén balanceadas en volumen

### 2. Características del Podcast
El modelo funciona mejor cuando:
- Las voces son claramente distinguibles (hombre/mujer ideal)
- Hay pausas claras entre turnos de habla
- No hay solapamiento excesivo de voces

### 3. Re-procesamiento
- Si el resultado no es bueno, intenta ejecutar `split_audios.py` de nuevo
- El modelo tiene cierta variabilidad, a veces da mejores resultados en el segundo intento

---

## Ejemplo Completo: Corregir el Problema Detectado

Basado en el análisis que muestra 19 segmentos consecutivos de HOST_B entre 160-248s:

```bash
# 1. Analizar el problema
python3 debug_diarization.py
# Salida: ⚠️  HOST_B: 19 segmentos consecutivos (160.3s - 248.0s)

# 2. Escuchar el audio original en ese rango para confirmar
# - Abre el audio en input/
# - Navega al minuto 2:40 (160s) hasta 4:08 (248s)
# - Confirma que realmente son dos voces alternándose

# 3. Corregir intercambiando
python3 fix_speaker_assignment.py --swap-range 160 248

# 4. Validar la corrección
python3 debug_diarization.py
# Ahora debería mostrar: ✓ No se detectaron secuencias sospechosas

# 5. Si modificaste editing_guide.json, necesitas regenerar los audios
# IMPORTANTE: Respalda los archivos existentes primero
mv output/track_host_A.mp3 output/track_host_A.mp3.backup
mv output/track_host_B.mp3 output/track_host_B.mp3.backup

# Re-ejecuta split_audios.py (usará el editing_guide.json corregido)
# NO - mejor re-ejecutar todo desde cero para asegurar consistencia
```

---

## Notas Importantes

### ⚠️ Limitaciones del Modelo
- Pyannote es el mejor modelo de código abierto para diarización, pero no es perfecto
- La precisión típica es ~85-95% dependiendo de la calidad del audio
- Puede confundir speakers en segmentos muy cortos o con solapamiento

### 🔄 Consistencia
- Si modificas `editing_guide.json` manualmente, los archivos de audio (`track_host_A.mp3`, `track_host_B.mp3`) pueden no coincidir
- En ese caso, es mejor re-ejecutar `split_audios.py` desde cero con el audio original

### 💾 Backups
- Siempre se crean backups automáticos antes de modificar archivos
- Los backups tienen el formato: `archivo.json.backup_YYYYMMDD_HHMMSS`

---

## Preguntas Frecuentes

**P: ¿Por qué no se puede hacer 100% automático?**
R: La diarización de speakers es un problema complejo de IA. El modelo hace su mejor esfuerzo, pero la variabilidad en voces humanas hace imposible garantizar 100% de precisión.

**P: ¿Debo siempre usar min_speakers y max_speakers=2?**
R: Sí, si sabes que tu podcast tiene exactamente 2 personas. Esto mejora significativamente la precisión.

**P: ¿Qué pasa si tengo 3+ speakers?**
R: Necesitarías modificar `pipeline_params` en `split_audios.py` para ajustar `max_speakers`. Sin embargo, el resto del código está diseñado para 2 hosts (HOST_A y HOST_B), por lo que requerirías cambios adicionales.

**P: ¿Puedo editar manualmente editing_guide.json?**
R: Sí, es un archivo JSON estándar. Simplemente cambia `"host": "HOST_A"` por `"host": "HOST_B"` donde sea necesario. Usa `debug_diarization.py` para validar tus cambios.

---

## Soporte

Si encuentras problemas adicionales:
1. Ejecuta `debug_diarization.py` y guarda la salida
2. Revisa esta guía para soluciones conocidas
3. Considera compartir el rango problemático del audio para análisis
