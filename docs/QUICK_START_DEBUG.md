# Guía Rápida: Debugging de Asignación de Speakers

## 🎯 Objetivo
Detectar y corregir rápidamente errores en la asignación de speakers (cuando un avatar tiene dos voces diferentes).

---

## 🚀 Inicio Rápido (3 pasos)

### Paso 1: Analizar el problema
```bash
python3 debug_diarization.py
```

**¿Qué buscar?**
- Secuencias sospechosas (>15 segmentos consecutivos del mismo host)
- Minutos marcados con ⚠️ SOSPECHOSO

**Ejemplo de salida problemática:**
```
⚠️  HOST_B: 19 segmentos consecutivos
   Tiempo: 160.31s - 248.01s (87.69s de duración)

Minuto 3 (180s-240s): A=0, B=13 ⚠️  SOSPECHOSO
```

---

### Paso 2: Corregir el rango problemático
```bash
# Usar los tiempos detectados (ejemplo: 160s - 248s)
python3 fix_speaker_assignment.py --swap-range 160 248
```

**¿Qué hace?**
- Intercambia HOST_A ↔ HOST_B en ese rango
- Crea backup automático
- Muestra estadísticas antes/después

---

### Paso 3: Validar la corrección
```bash
python3 debug_diarization.py
```

**Resultado esperado:**
```
✓ No se detectaron secuencias sospechosas
```

---

## 📊 Ejemplo Real: Caso de 19 Segmentos Incorrectos

### ANTES de la corrección:
```bash
$ python3 debug_diarization.py

Total de segmentos: 168
HOST_A: 73 segmentos (344.23s totales)
HOST_B: 95 segmentos (575.96s totales)

⚠️  HOST_B: 19 segmentos consecutivos
   Tiempo: 160.31s - 248.01s (87.69s de duración)

Minuto 3 (180s-240s): A=0, B=13 ⚠️  SOSPECHOSO
                                ^^^^ Problema aquí
```

### Corrección:
```bash
$ python3 fix_speaker_assignment.py --swap-range 160 248

📂 Archivo cargado: ./output/editing_guide.json

Estadísticas:
  Total segmentos: 168
  HOST_A: 73 segmentos
  HOST_B: 95 segmentos

�� Backup creado: ./output/editing_guide.json.backup_20251215_143022

🔄 Intercambiando hosts en rango 160.0s - 248.0s...
   ✓ 19 segmentos intercambiados

💾 Archivo guardado: ./output/editing_guide.json
```

### DESPUÉS de la corrección:
```bash
$ python3 debug_diarization.py

Total de segmentos: 168
HOST_A: 92 segmentos (431.92s totales)  ← Incrementó
HOST_B: 76 segmentos (488.27s totales)  ← Decrementó

✓ No se detectaron secuencias sospechosas
```

---

## 🔍 ¿Cómo Saber si Tengo el Problema?

### Síntomas en el Video Final:
- ✗ Un avatar tiene voz de hombre Y mujer
- ✗ El mismo personaje cambia de voz en medio de la conversación
- ✗ Las voces no coinciden con los avatars seleccionados

### Síntomas en el Análisis:
```bash
python3 debug_diarization.py
```
- ✗ Secuencias de 15+ segmentos consecutivos
- ✗ Minutos marcados con ⚠️ SOSPECHOSO
- ✗ Un host con 0 segmentos en algún minuto

---

## 💡 Consejos Adicionales

### 1. Prevenir el Problema
```bash
# Ejecutar split_audios.py con las mejoras:
python3 split_audios.py

# El script ahora te alerta automáticamente:
⚠️  ADVERTENCIA: Se detectaron 1 secuencias sospechosas...
```

### 2. Re-intentar vs Corregir
**¿Cuándo re-ejecutar `split_audios.py`?**
- Cuando el problema afecta >50% del audio
- Cuando hay múltiples rangos problemáticos

**¿Cuándo usar `fix_speaker_assignment.py`?**
- Cuando el problema es localizado (1-2 rangos)
- Cuando ya generaste los videos de HeyGen
- Cuando quieres ahorrar tiempo

### 3. Verificar Antes de Continuar
```bash
# SIEMPRE valida después de corregir:
python3 debug_diarization.py

# Si todavía hay problemas, repite el proceso o re-ejecuta split_audios.py
```

---

## 📁 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `editing_guide.json` | Asignación de speakers (timestamps) |
| `editing_guide.json.backup_*` | Backup automático antes de modificar |
| `track_host_A.mp3` | Audio del HOST_A |
| `track_host_B.mp3` | Audio del HOST_B |

⚠️ **IMPORTANTE:** Si modificas `editing_guide.json`, los archivos `.mp3` pueden no coincidir. En ese caso, re-ejecuta `split_audios.py` completo.

---

## 🆘 Solución de Problemas

### Error: "No se encontró el archivo editing_guide.json"
```bash
# Asegúrate de haber ejecutado split_audios.py primero:
python3 split_audios.py
```

### Corrección no funcionó
```bash
# 1. Verificar el rango de tiempo
python3 debug_diarization.py

# 2. Intentar con un rango más amplio
python3 fix_speaker_assignment.py --swap-range 150 260

# 3. Si sigue sin funcionar, re-ejecutar desde cero
python3 split_audios.py
```

### Múltiples rangos problemáticos
```bash
# Corregir cada rango por separado:
python3 fix_speaker_assignment.py --swap-range 160 248
python3 debug_diarization.py  # Verificar

python3 fix_speaker_assignment.py --swap-range 400 500
python3 debug_diarization.py  # Verificar
```

---

## 📖 Documentación Completa

Para información más detallada:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guía completa de problemas
- [SPEAKER_DETECTION_IMPROVEMENTS.md](SPEAKER_DETECTION_IMPROVEMENTS.md) - Detalles técnicos
- [README.md](../README.md) - Documentación general

---

## ⏱️ Tiempo Estimado

| Tarea | Tiempo |
|-------|--------|
| Análisis (`debug_diarization.py`) | ~5 segundos |
| Corrección (`fix_speaker_assignment.py`) | ~2 segundos |
| Validación (`debug_diarization.py`) | ~5 segundos |
| **TOTAL** | **~15 segundos** |

Comparado con re-procesar todo:
- `split_audios.py`: ~3-5 minutos
- Regenerar videos HeyGen: ~10-15 minutos
- `assemble_video.py`: ~2-3 minutos
- **TOTAL:** ~15-23 minutos

**Ahorro de tiempo: 90-95%** ✅
