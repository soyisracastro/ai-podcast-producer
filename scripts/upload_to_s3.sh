#!/bin/bash

# ==================================================================================
# Script: upload_to_s3.sh
# Propósito: Subir archivo .zip del directorio /archives a AWS S3
# Prerequisito: AWS CLI configurado (aws configure)
# Uso: ./upload_to_s3.sh <archivo.zip> <nombre_bucket>
# ==================================================================================

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que se pasaron los argumentos necesarios
if [ $# -lt 2 ]; then
    echo "Uso: $0 <archivo.zip> <nombre_bucket> [carpeta_s3]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 podcast_episode_20231127.zip my-podcast-bucket"
    echo "  $0 podcast_episode_20231127.zip my-podcast-bucket episodes/2023"
    exit 1
fi

ARCHIVE_FILE="$1"
S3_BUCKET="$2"
S3_FOLDER="${3:-}"  # Opcional

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVES_DIR="$PROJECT_DIR/archives"

# Si no se especifica ruta completa, buscar en /archives
if [ ! -f "$ARCHIVE_FILE" ]; then
    ARCHIVE_FILE="$ARCHIVES_DIR/$ARCHIVE_FILE"
fi

# Verificar que el archivo existe
if [ ! -f "$ARCHIVE_FILE" ]; then
    print_error "Archivo no encontrado: $ARCHIVE_FILE"
    exit 1
fi

# Verificar que AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI no está instalado"
    echo "Instala con: brew install awscli"
    echo "Luego configura con: aws configure"
    exit 1
fi

# Construir ruta S3
FILENAME=$(basename "$ARCHIVE_FILE")
if [ -n "$S3_FOLDER" ]; then
    S3_PATH="s3://$S3_BUCKET/$S3_FOLDER/$FILENAME"
else
    S3_PATH="s3://$S3_BUCKET/$FILENAME"
fi

echo ""
print_info "=== UPLOAD TO S3 ==="
print_info "Archivo local: $ARCHIVE_FILE"
print_info "Destino S3: $S3_PATH"
echo ""

# Subir archivo a S3
print_info "Subiendo archivo..."
aws s3 cp "$ARCHIVE_FILE" "$S3_PATH"

if [ $? -eq 0 ]; then
    print_info "✓ Archivo subido exitosamente"

    # Generar URL presignada (válida por 7 días)
    print_info "Generando URL de descarga temporal..."
    PRESIGNED_URL=$(aws s3 presign "$S3_PATH" --expires-in 604800)

    echo ""
    print_info "URL de descarga (válida por 7 días):"
    echo "$PRESIGNED_URL"
    echo ""
else
    print_error "Error al subir archivo a S3"
    exit 1
fi
