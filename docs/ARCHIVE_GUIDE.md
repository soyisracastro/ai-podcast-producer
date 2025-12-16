# Guía de Archivado y Limpieza

Esta guía documenta el uso de los scripts de archivado y limpieza del proyecto.

## 📦 Scripts Disponibles

### 1. `archive_and_clean.sh` - Archivado y Limpieza Local

**Propósito:** Crear un archivo `.zip` con el contenido de `/input` y `/output`, y limpiar ambos directorios para preparar un nuevo trabajo.

#### Uso Básico

```bash
# Con nombre de episodio personalizado
./archive_and_clean.sh "episodio_01_intro_ia"

# Sin nombre (detecta automáticamente del archivo .m4a o usa timestamp)
./archive_and_clean.sh
```

#### ¿Qué hace el script?

1. **Verificación:** Comprueba que existen los directorios `/input` y `/output`
2. **Detección de nombre:** Si no se proporciona un nombre, busca el archivo `.m4a` en `/input` y usa su nombre (sin extensión). Si no hay archivo `.m4a`, usa timestamp
3. **Archivado:** Crea un archivo `.zip` en el directorio `/archives`
4. **Confirmación:** Solicita confirmación antes de eliminar contenido
5. **Limpieza:** Elimina todo el contenido de `/input` y `/output`
6. **Resultado:** Muestra la ubicación del archivo y próximos pasos

#### Estructura del Archivo ZIP

```
podcast_episode_YYYYMMDD_HHMMSS.zip
├── input/
│   ├── podcast_notebooklm.m4a
│   ├── video_host_A.mp4
│   └── video_host_B.mp4
└── output/
    ├── track_host_A.mp3
    ├── track_host_B.mp3
    ├── editing_guide.json
    └── final_episode.mp4
```

#### Ejemplo de Salida (Con detección automática)

```
[INFO] === ARCHIVE & CLEAN SCRIPT ===

[INFO] Nombre detectado del archivo .m4a: Audio Overview - AI and Machine Learning
[INFO] Archivando contenido...
[INFO] Ruta del archivo: /archives/Audio_Overview_-_AI_and_Machine_Learning.zip

[INFO] ✓ Archivo creado exitosamente: episodio_01_intro_ia.zip (1.2G)

[INFO] Contenido del archivo:
   1047228148  input/podcast_notebooklm.m4a
   541228148  input/video_host_A.mp4
   418228148  input/video_host_B.mp4
    16228148  output/track_host_A.mp3
    16228148  output/track_host_B.mp3
       23148  output/editing_guide.json
   277228148  output/final_episode.mp4

[WARNING] ⚠️  ADVERTENCIA: Se eliminará todo el contenido de /input y /output
¿Deseas continuar con la limpieza? (y/n): y

[INFO] Limpiando directorios...
[INFO] ✓ Directorio /input limpiado
[INFO] ✓ Directorio /output limpiado

[INFO] === PROCESO COMPLETADO ===
[INFO] Archivo guardado en: /archives/episodio_01_intro_ia.zip
[INFO] Directorios listos para nuevo trabajo
```

---

### 2. `upload_to_s3.sh` - Subida a AWS S3

**Propósito:** Subir archivos `.zip` del directorio `/archives` a un bucket de AWS S3.

#### Prerequisitos

```bash
# Instalar AWS CLI
brew install awscli

# Configurar credenciales AWS
aws configure
# Se pedirá:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name (ej: us-east-1)
# - Default output format (ej: json)
```

#### Uso Básico

```bash
# Subir a raíz del bucket
./upload_to_s3.sh episodio_01_intro_ia.zip my-podcast-bucket

# Subir a carpeta específica en S3
./upload_to_s3.sh episodio_01_intro_ia.zip my-podcast-bucket episodes/2023

# Usar ruta completa del archivo
./upload_to_s3.sh /path/to/file.zip my-podcast-bucket
```

#### ¿Qué hace el script?

1. **Validación:** Verifica que el archivo existe y AWS CLI está configurado
2. **Upload:** Sube el archivo a la ruta S3 especificada
3. **URL Presignada:** Genera una URL de descarga temporal (válida 7 días)

#### Ejemplo de Salida

```
[INFO] === UPLOAD TO S3 ===
[INFO] Archivo local: /archives/episodio_01_intro_ia.zip
[INFO] Destino S3: s3://my-podcast-bucket/episodes/2023/episodio_01_intro_ia.zip

[INFO] Subiendo archivo...
upload: ./episodio_01_intro_ia.zip to s3://my-podcast-bucket/episodes/2023/episodio_01_intro_ia.zip

[INFO] ✓ Archivo subido exitosamente
[INFO] Generando URL de descarga temporal...

[INFO] URL de descarga (válida por 7 días):
https://my-podcast-bucket.s3.amazonaws.com/episodes/2023/episodio_01_intro_ia.zip?X-Amz-Algorithm=...
```

---

## 🔄 Workflow Completo

### Opción A: Workflow con AWS S3

```bash
# 1. Archivar y limpiar
./archive_and_clean.sh "episodio_01_intro_ia"

# 2. Subir a S3
./upload_to_s3.sh episodio_01_intro_ia.zip my-podcast-bucket episodes/2023

# 3. (Opcional) Eliminar archivo local después de confirmar subida
rm archives/episodio_01_intro_ia.zip
```

### Opción B: Workflow con OneDrive/Google Drive

```bash
# 1. Archivar y limpiar
./archive_and_clean.sh "episodio_01_intro_ia"

# 2. Copiar a carpeta sincronizada de OneDrive/Google Drive
cp archives/episodio_01_intro_ia.zip ~/OneDrive/Podcasts/

# 3. (Opcional) Eliminar archivo local después de verificar sincronización
rm archives/episodio_01_intro_ia.zip
```

---

## 📁 Estructura de Directorios

Después de ejecutar los scripts:

```
ai-podcast-producer/
├── archives/                    # Archivos .zip locales (git-ignored)
│   ├── episodio_01_intro_ia.zip
│   ├── episodio_02_ml_basics.zip
│   └── podcast_episode_20231127_143022.zip
├── input/                       # ✓ LIMPIO - Listo para nuevo trabajo
├── output/                      # ✓ LIMPIO - Listo para nuevo trabajo
├── archive_and_clean.sh         # Script de archivado
├── upload_to_s3.sh              # Script de subida a S3
└── ...
```

---

## ⚙️ Configuración Avanzada

### Personalizar Compresión del ZIP

Editar `archive_and_clean.sh`, línea del comando `zip`:

```bash
# Compresión máxima (más lento, menor tamaño)
zip -9 -r "$ARCHIVE_PATH" input output -x "*.DS_Store" "*/.*"

# Compresión rápida (más rápido, mayor tamaño)
zip -1 -r "$ARCHIVE_PATH" input output -x "*.DS_Store" "*/.*"

# Sin compresión (ultra rápido)
zip -0 -r "$ARCHIVE_PATH" input output -x "*.DS_Store" "*/.*"
```

### Configurar Bucket S3 con Políticas

```bash
# Crear bucket
aws s3 mb s3://my-podcast-bucket --region us-east-1

# Habilitar versionado (opcional - mantiene historial de archivos)
aws s3api put-bucket-versioning \
  --bucket my-podcast-bucket \
  --versioning-configuration Status=Enabled

# Configurar ciclo de vida (opcional - mover a Glacier después de 90 días)
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-podcast-bucket \
  --lifecycle-configuration file://lifecycle.json
```

---

## 🛡️ Seguridad y Buenas Prácticas

### Para AWS S3

1. **No usar credenciales root:** Crea un usuario IAM específico con permisos limitados
2. **Política de bucket privado:** No hacer el bucket público a menos que sea necesario
3. **Encriptación:** Habilitar encriptación del lado del servidor (SSE-S3 o SSE-KMS)
4. **Versionado:** Considerar habilitar versionado para recuperación de archivos

### Ejemplo de Política IAM (Solo Upload)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-podcast-bucket/*"
    }
  ]
}
```

---

## 🔧 Troubleshooting

### Error: "Permission denied"

```bash
chmod +x archive_and_clean.sh
chmod +x upload_to_s3.sh
```

### Error: "AWS CLI not found"

```bash
# macOS
brew install awscli

# Linux
sudo apt-get install awscli

# Verificar instalación
aws --version
```

### Error: "Unable to locate credentials"

```bash
# Configurar AWS CLI
aws configure

# Verificar configuración
aws sts get-caller-identity
```

### El archivo ZIP es muy grande

Opciones:
1. Usar compresión máxima: `zip -9`
2. Comprimir por separado input y output
3. Excluir archivos innecesarios (ej: solo guardar `final_episode.mp4`)

---

## 📊 Costos Estimados (AWS S3)

Para un episodio típico (~1.2 GB):

| Servicio | Costo Mensual | Detalles |
|----------|---------------|----------|
| **S3 Storage** | ~$0.03/GB | $0.036 por 1.2 GB |
| **S3 Upload** | Gratis | Sin costo por PUT requests |
| **S3 Download** | ~$0.09/GB | Solo si descargas desde S3 |
| **Total** | ~$0.04/mes | Por episodio almacenado |

**Alternativa económica:** Usar **S3 Glacier Deep Archive** (~$0.00099/GB/mes) para archivos que raramente necesitas acceder.

---

## 📝 Notas Adicionales

- Los archivos `.zip` NO se suben a GitHub (están en `.gitignore`)
- El directorio `/archives` sirve como respaldo local temporal
- Se recomienda mantener al menos 2 copias: local + nube
- Considera establecer una política de retención (ej: eliminar archives locales después de 30 días)
