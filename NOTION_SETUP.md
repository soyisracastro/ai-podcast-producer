# Guía de Configuración: Integración con Notion

Esta guía te ayudará a configurar la sincronización automática del calendario de publicación a una base de datos de Notion.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Crear una Integración en Notion](#paso-1-crear-una-integración-en-notion)
3. [Paso 2: Crear la Base de Datos en Notion](#paso-2-crear-la-base-de-datos-en-notion)
4. [Paso 3: Conectar la Integración a tu Base de Datos](#paso-3-conectar-la-integración-a-tu-base-de-datos)
5. [Paso 4: Configurar Variables de Entorno](#paso-4-configurar-variables-de-entorno)
6. [Paso 5: Instalar Dependencias](#paso-5-instalar-dependencias)
7. [Paso 6: Ejecutar la Sincronización](#paso-6-ejecutar-la-sincronización)
8. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

- Cuenta de Notion (gratuita o de pago)
- Python 3.8 o superior instalado
- Haber ejecutado `python analyze_chapters.py` previamente (para generar el calendario CSV)

---

## Paso 1: Crear una Integración en Notion

1. Ve a [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Haz clic en **"+ New integration"**
3. Configura tu integración:
   - **Name**: "AI Podcast Producer" (o el nombre que prefieras)
   - **Logo**: Opcional
   - **Associated workspace**: Selecciona tu workspace
   - **Type**: Internal integration
   - **Capabilities**:
     - ✅ Read content
     - ✅ Update content
     - ✅ Insert content
4. Haz clic en **"Submit"**
5. **IMPORTANTE**: Copia el **"Internal Integration Token"** (comienza con `secret_...`)
   - Este es tu `NOTION_TOKEN`
   - Guárdalo en un lugar seguro, lo necesitarás más adelante

---

## Paso 2: Crear la Base de Datos en Notion

### Opción A: Crear Base de Datos desde Cero

1. Abre Notion y crea una nueva página
2. Escribe `/database` y selecciona **"Table - Inline"**
3. Nombra tu base de datos: **"Calendario de Publicación"**
4. Crea las siguientes propiedades (columnas):

| Nombre de Propiedad | Tipo de Propiedad | Opciones |
|---------------------|-------------------|----------|
| **Título** | Title | - |
| **Día** | Select | Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo |
| **Fecha** | Date | - |
| **Hora** | Text | - |
| **Tipo de Contenido** | Select | Episodio Completo, Clip Largo, Clip Corto |
| **Plataforma** | Multi-select | YouTube, Spotify, TikTok, Instagram, TikTok/Instagram |
| **Notas** | Text | - |
| **Publicado** | Checkbox | - |

### Opción B: Duplicar Plantilla (Recomendado)

Si prefieres, puedes duplicar esta plantilla pre-configurada:

```
[Enlace a plantilla de Notion - a crear]
```

---

## Paso 3: Conectar la Integración a tu Base de Datos

1. Abre tu base de datos en Notion
2. Haz clic en los **3 puntos** (⋯) en la esquina superior derecha
3. Selecciona **"Add connections"**
4. Busca tu integración **"AI Podcast Producer"** y selecciónala
5. Haz clic en **"Confirm"**

---

## Paso 4: Obtener el Database ID

1. Abre tu base de datos en Notion en tu navegador
2. Copia la URL de la página. Se verá algo así:
   ```
   https://www.notion.so/1234567890abcdef1234567890abcdef?v=...
   ```
3. El **Database ID** es la parte entre `/` y `?`:
   ```
   1234567890abcdef1234567890abcdef
   ```
4. Copia este ID, lo necesitarás en el siguiente paso

---

## Paso 5: Configurar Variables de Entorno

### En macOS/Linux:

Abre tu terminal y ejecuta:

```bash
# Configurar el token de Notion
export NOTION_TOKEN="secret_TuTokenAqui..."

# Configurar el ID de la base de datos
export NOTION_DATABASE_ID="1234567890abcdef1234567890abcdef"
```

**Para hacer esto permanente**, añade estas líneas a tu archivo `~/.zshrc` o `~/.bashrc`:

```bash
echo 'export NOTION_TOKEN="secret_TuTokenAqui..."' >> ~/.zshrc
echo 'export NOTION_DATABASE_ID="1234567890abcdef1234567890abcdef"' >> ~/.zshrc
source ~/.zshrc
```

### En Windows (PowerShell):

```powershell
$env:NOTION_TOKEN="secret_TuTokenAqui..."
$env:NOTION_DATABASE_ID="1234567890abcdef1234567890abcdef"
```

### Usando archivo .env (Alternativa):

Crea un archivo `.env` en la raíz del proyecto:

```bash
NOTION_TOKEN=secret_TuTokenAqui...
NOTION_DATABASE_ID=1234567890abcdef1234567890abcdef
```

Y modifica el script para usar `python-dotenv`.

---

## Paso 6: Instalar Dependencias

Ejecuta en tu terminal:

```bash
pip install notion-client
```

O instala todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

---

## Paso 7: Ejecutar la Sincronización

Una vez configurado todo, ejecuta el script especificando la fecha de inicio (lunes):

```bash
python sync_to_notion.py DD-MM-AAAA
```

**Ejemplos:**

```bash
# Para publicar en la semana del 16 de diciembre de 2024
python sync_to_notion.py 16-12-2024

# Para publicar en la semana del 6 de enero de 2025
python sync_to_notion.py 06-01-2025

# Para publicar en la semana del 9 de diciembre de 2024
python sync_to_notion.py 09-12-2024
```

**Nota importante**: La fecha debe ser un **lunes** (inicio de semana). El script calculará automáticamente las fechas para martes, miércoles, etc.

El script:
1. Buscará el calendario CSV más reciente en `/output/metadata`
2. Calculará las fechas reales basándose en el lunes que especificaste
3. Verificará qué entradas ya existen (para evitar duplicados)
4. Sincronizará solo las entradas nuevas a tu base de datos
5. Mostrará un resumen de éxito/errores

### Salida Esperada:

```
================================================================================
  SINCRONIZACIÓN DE CALENDARIO A NOTION
================================================================================

📅 Fecha de inicio configurada: 16-12-2024 (Monday)

--> Paso 1/2: Buscando archivo de calendario...
✓ Calendario encontrado: Aguinaldo_Cálculo_Obligaciones_y_Exención_de_ISR_calendar.csv

--> Paso 2/2: Sincronizando a Notion...
✓ Conectado a Notion
   Verificando entradas existentes...
   ✓ 0 entradas ya existen en Notion
   Leyendo calendario: Aguinaldo_Cálculo_Obligaciones_y_Exención_de_ISR_calendar.csv
   ✓ 11 entradas encontradas en CSV

   Sincronizando a Notion...
   [1/11] ✓ Lunes 2024-12-16: ¡Descubre el Secreto del Aguinaldo!...
   [2/11] ✓ Lunes 2024-12-16: Introducción al Aguinaldo...
   [3/11] ✓ Martes 2024-12-17: ¿Por qué el Aguinaldo es un Derecho?...
   ...

================================================================================
✅ ¡SINCRONIZACIÓN COMPLETADA!
================================================================================

📊 RESUMEN:
   • Entradas nuevas agregadas: 11
   • Entradas ya existentes (omitidas): 0
   • Entradas con errores: 0
   • Semana de publicación: 16-12-2024 al 22-12-2024

💡 NOTAS:
   • Las entradas existentes en Notion NO fueron modificadas
   • Si marcaste algo como 'Publicado', seguirá así
   • Las fechas se calcularon automáticamente desde el lunes 16-12-2024

💡 SIGUIENTE PASO:
   1. Abre tu base de datos de Notion
   2. Cambia la vista a 'Calendario' para ver las publicaciones por fecha
   3. Revisa las entradas de la semana del 16 al 22 de December
   4. Reorganiza manualmente si hay conflictos de fechas
   5. Usa el checkbox 'Publicado' para marcar contenido publicado
================================================================================
```

---

## Gestión de Publicaciones en Notion

Una vez sincronizado el calendario:

1. **Vista de Calendario**:
   - En Notion, crea una vista de tipo "Calendario"
   - Configúrala para usar la propiedad "Fecha"
   - Verás visualmente qué contenido publicar cada día

2. **Planificar**:
   - Revisa el calendario semanal en la vista de calendario
   - Arrastra y suelta contenido si necesitas cambiar fechas

3. **Publicar**:
   - Cuando publiques un clip/episodio, marca el checkbox "Publicado"
   - El contenido publicado se puede ocultar con filtros

4. **Filtrar**: Usa vistas de Notion para:
   - Ver solo contenido pendiente de publicación (Publicado = false)
   - Agrupar por día de la semana
   - Filtrar por plataforma (YouTube, TikTok, Instagram, etc.)
   - Ver solo un tipo de contenido (Episodio Completo, Clip Largo, Clip Corto)
   - Ver contenido de una semana específica

5. **Re-sincronizar**:
   - Si generas un nuevo episodio, ejecuta el script con una nueva fecha de inicio
   - Ejemplo: `python sync_to_notion.py 23-12-2024` para la siguiente semana
   - El script no duplicará contenido que ya existe

---

## Solución de Problemas

### Error: "NOTION_TOKEN no configurada"

**Causa**: La variable de entorno no está configurada.

**Solución**: Asegúrate de ejecutar:
```bash
export NOTION_TOKEN="secret_TuTokenAqui..."
```

O verifica que esté en tu archivo `.zshrc`/`.bashrc`.

---

### Error: "NOTION_DATABASE_ID no configurada"

**Causa**: La variable de entorno no está configurada.

**Solución**: Copia el Database ID desde la URL de tu base de datos y ejecuta:
```bash
export NOTION_DATABASE_ID="1234567890abcdef1234567890abcdef"
```

---

### Error: "Could not find database with ID"

**Causa**: La integración no tiene acceso a la base de datos.

**Solución**:
1. Abre tu base de datos en Notion
2. Haz clic en **⋯ → Add connections**
3. Selecciona tu integración "AI Podcast Producer"
4. Intenta sincronizar de nuevo

---

### Error: "Object `select` does not match schema"

**Causa**: Las opciones de "Select" en Notion no coinciden con los valores del CSV.

**Solución**:
1. Abre tu base de datos en Notion
2. Edita la propiedad **"Día"** y añade las opciones:
   - Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo
3. Edita la propiedad **"Tipo de Contenido"** y añade:
   - Episodio Completo, Clip Largo, Clip Corto
4. Edita la propiedad **"Plataforma"** (Multi-select) y añade:
   - YouTube, Spotify, TikTok, Instagram, TikTok/Instagram

---

### Las entradas se duplican cada vez que sincronizo

**Causa**: El script está configurado para limpiar las entradas existentes antes de sincronizar.

**Comportamiento Esperado**: Esto es intencional. El script archiva las entradas antiguas y crea nuevas. Tus checkboxes "Publicado" se perderán.

**Solución Alternativa**: Si quieres preservar el estado "Publicado", modifica el script:

1. Abre [sync_to_notion.py](sync_to_notion.py)
2. En la línea donde llamas a `sync_calendar_to_notion()`:
   ```python
   # Cambiar esto:
   sync_calendar_to_notion(calendar_path, clear_existing=True)

   # Por esto:
   sync_calendar_to_notion(calendar_path, clear_existing=False)
   ```
3. Esto evitará que se archiven las entradas existentes, pero puede crear duplicados si el calendario no cambia

---

## Automatización Avanzada (Opcional)

Si quieres automatizar completamente el flujo, puedes crear un script bash que ejecute todo el pipeline:

```bash
#!/bin/bash
# workflow_completo.sh

# 1. Generar análisis y calendario
python analyze_chapters.py

# 2. Generar clips de video
python generate_clips.py

# 3. Sincronizar a Notion
python sync_to_notion.py

echo "✅ Workflow completo ejecutado!"
```

Hazlo ejecutable:
```bash
chmod +x workflow_completo.sh
./workflow_completo.sh
```

---

## Recursos Adicionales

- [Documentación oficial de Notion API](https://developers.notion.com/)
- [notion-client Python library](https://github.com/ramnes/notion-sdk-py)
- [Guía de creación de integraciones](https://developers.notion.com/docs/create-a-notion-integration)

---

## Soporte

Si encuentras problemas no cubiertos en esta guía, revisa:

1. Los logs del script para mensajes de error específicos
2. Que todas las propiedades de la base de datos coincidan exactamente con los nombres esperados
3. Que la integración tenga permisos de lectura, escritura e inserción

---

**¡Listo!** Ahora puedes gestionar todo tu calendario de publicación directamente desde Notion con sincronización automática desde tu pipeline de producción.
