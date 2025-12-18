#!/bin/bash

# ==================================================================================
# Script: archive_and_clean.sh
# Propósito: Archivar contenido de /input y /output en un .zip y limpiar directorios
# Uso: ./archive_and_clean.sh [nombre_episodio]
# ==================================================================================

set -e  # Detener ejecución si hay errores

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio base del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="$PROJECT_DIR/input"
OUTPUT_DIR="$PROJECT_DIR/output"
ARCHIVES_DIR="$PROJECT_DIR/archives"

# ==================================================================================
# FUNCIONES
# ==================================================================================

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_directories() {
    if [ ! -d "$INPUT_DIR" ]; then
        print_error "Directorio /input no existe"
        exit 1
    fi

    if [ ! -d "$OUTPUT_DIR" ]; then
        print_error "Directorio /output no existe"
        exit 1
    fi
}

check_content() {
    local input_files=$(find "$INPUT_DIR" -type f 2>/dev/null | wc -l)
    local output_files=$(find "$OUTPUT_DIR" -type f 2>/dev/null | wc -l)

    if [ "$input_files" -eq 0 ] && [ "$output_files" -eq 0 ]; then
        print_warning "No hay archivos en /input ni /output para archivar"
        read -p "¿Deseas continuar de todas formas? (y/n): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            print_info "Operación cancelada"
            exit 0
        fi
    fi
}

# ==================================================================================
# SCRIPT PRINCIPAL
# ==================================================================================

echo ""
print_info "=== ARCHIVE & CLEAN SCRIPT ==="
echo ""

# Verificar que existan los directorios
check_directories

# Verificar que haya contenido para archivar
check_content

# Crear directorio de archives si no existe
if [ ! -d "$ARCHIVES_DIR" ]; then
    mkdir -p "$ARCHIVES_DIR"
    print_info "Directorio /archives creado"
fi

# Determinar nombre del archivo
if [ -z "$1" ]; then
    # Si no se proporciona nombre, buscar archivo .m4a en /input
    M4A_FILE=$(find "$INPUT_DIR" -maxdepth 1 -type f -name "*.m4a" | head -n 1)

    if [ -n "$M4A_FILE" ]; then
        # Extraer nombre del archivo sin extensión
        M4A_BASENAME=$(basename "$M4A_FILE" .m4a)
        # Sanitizar nombre (reemplazar espacios y caracteres especiales)
        EPISODE_NAME=$(echo "$M4A_BASENAME" | tr ' ' '_' | tr -cd '[:alnum:]_-')
        ARCHIVE_NAME="${EPISODE_NAME}.zip"
        print_info "Nombre detectado del archivo .m4a: $M4A_BASENAME"
    else
        # Si no hay archivo .m4a, usar timestamp
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        ARCHIVE_NAME="podcast_episode_${TIMESTAMP}.zip"
        print_info "No se encontró archivo .m4a, usando timestamp"
    fi
else
    # Usar nombre proporcionado (sanitizado)
    EPISODE_NAME=$(echo "$1" | tr ' ' '_' | tr -cd '[:alnum:]_-')
    ARCHIVE_NAME="${EPISODE_NAME}.zip"
fi

ARCHIVE_PATH="$ARCHIVES_DIR/$ARCHIVE_NAME"

# Verificar si el archivo ya existe
if [ -f "$ARCHIVE_PATH" ]; then
    print_warning "El archivo $ARCHIVE_NAME ya existe"
    read -p "¿Deseas sobrescribirlo? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "Operación cancelada"
        exit 0
    fi
fi

echo ""
print_info "Archivando contenido..."
print_info "Ruta del archivo: $ARCHIVE_PATH"
echo ""

# Crear el archivo ZIP
cd "$PROJECT_DIR"
zip -r "$ARCHIVE_PATH" input output -x "*.DS_Store" "*/.*" 2>/dev/null || true

# Verificar que el ZIP se creó correctamente
if [ -f "$ARCHIVE_PATH" ]; then
    ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
    print_info "✓ Archivo creado exitosamente: $ARCHIVE_NAME ($ARCHIVE_SIZE)"

    # Mostrar contenido del ZIP
    echo ""
    print_info "Contenido del archivo:"
    unzip -l "$ARCHIVE_PATH"
    echo ""
else
    print_error "Error al crear el archivo ZIP"
    exit 1
fi

# Confirmar antes de limpiar
echo ""
print_warning "⚠️  ADVERTENCIA: Se eliminará todo el contenido de /input y /output"
read -p "¿Deseas continuar con la limpieza? (y/n): " confirm

if [ "$confirm" == "y" ] || [ "$confirm" == "Y" ]; then
    print_info "Limpiando directorios..."

    # Eliminar contenido de /input
    if [ -d "$INPUT_DIR" ]; then
        rm -rf "$INPUT_DIR"/*
        print_info "✓ Directorio /input limpiado"
    fi

    # Eliminar contenido de /output
    if [ -d "$OUTPUT_DIR" ]; then
        rm -rf "$OUTPUT_DIR"/*
        print_info "✓ Directorio /output limpiado"
    fi

    echo ""
    print_info "=== PROCESO COMPLETADO ==="
    print_info "Archivo guardado en: $ARCHIVE_PATH"
    print_info "Directorios listos para nuevo trabajo"
    echo ""
    print_info "Próximos pasos:"
    echo "  1. Subir $ARCHIVE_NAME a tu servicio de nube (OneDrive/S3)"
    echo "  2. Colocar nuevo audio en /input/podcast_notebooklm.m4a"
    echo "  3. Ejecutar: python split_audios.py"
    echo ""
else
    print_info "Limpieza cancelada. El archivo ZIP se mantiene en: $ARCHIVE_PATH"
    echo ""
fi
