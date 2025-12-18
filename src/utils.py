# src/utils.py
# Funciones de utilidad compartidas entre todos los scripts

import os
import re
import unicodedata
from datetime import timedelta
from pathlib import Path
from typing import List, Optional, Union


def timestamp_to_seconds(timestamp_str: str) -> int:
    """
    Convierte timestamp (HH:MM:SS, MM:SS, o HH:MM:SS,mmm) a segundos totales.

    Args:
        timestamp_str: Timestamp en formato "01:23:45", "23:45", o "00:23:45,000"

    Returns:
        int: Total de segundos

    Examples:
        >>> timestamp_to_seconds("01:30")
        90
        >>> timestamp_to_seconds("01:00:00")
        3600
        >>> timestamp_to_seconds("00:01:30,500")
        90
    """
    # Remover milisegundos si existen (formato SRT)
    time_part = timestamp_str.split(',')[0]
    parts = time_part.split(':')

    if len(parts) == 3:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
    elif len(parts) == 2:
        hours, minutes, seconds = 0, int(parts[0]), int(parts[1])
    else:
        return 0

    return hours * 3600 + minutes * 60 + seconds


def seconds_to_timestamp(total_seconds: Union[int, float], include_hours: Optional[bool] = None) -> str:
    """
    Convierte segundos a formato timestamp (MM:SS o HH:MM:SS).

    Args:
        total_seconds: Segundos totales
        include_hours: True/False/None (None = auto-detectar basado en duracion)

    Returns:
        str: Timestamp formateado

    Examples:
        >>> seconds_to_timestamp(90)
        "1:30"
        >>> seconds_to_timestamp(3661)
        "1:01:01"
        >>> seconds_to_timestamp(90, include_hours=True)
        "0:01:30"
    """
    total_seconds = int(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Auto-detectar si necesitamos horas
    if include_hours is None:
        include_hours = hours > 0

    if include_hours or hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def format_timestamp_srt(seconds: float) -> str:
    """
    Convierte segundos flotantes a formato SRT: HH:MM:SS,mmm

    Args:
        seconds: Segundos con decimales (ej: 65.123)

    Returns:
        str: Timestamp en formato SRT (ej: "00:01:05,123")

    Examples:
        >>> format_timestamp_srt(65.123)
        "00:01:05,123"
        >>> format_timestamp_srt(3661.5)
        "01:01:01,500"
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def calculate_duration(start_timestamp: str, end_timestamp: str) -> str:
    """
    Calcula duracion entre dos timestamps y retorna formato legible.

    Args:
        start_timestamp: Timestamp inicial (ej: "00:00" o "00:00:00")
        end_timestamp: Timestamp final (ej: "05:30" o "00:05:30")

    Returns:
        str: Duracion en formato "5:30" o "1:05:30"

    Examples:
        >>> calculate_duration("00:00", "05:30")
        "5:30"
        >>> calculate_duration("01:00:00", "02:30:00")
        "1:30:00"
    """
    start_seconds = timestamp_to_seconds(start_timestamp)
    end_seconds = timestamp_to_seconds(end_timestamp)
    duration_seconds = end_seconds - start_seconds

    if duration_seconds < 0:
        return "00:00"

    return seconds_to_timestamp(duration_seconds)


def sanitize_filename(filename: str, max_length: int = 150) -> str:
    """
    Sanitiza el nombre del archivo removiendo caracteres invalidos.

    - Remueve acentos de vocales (a -> a, e -> e, etc.)
    - Elimina signos de interrogacion y admiracion
    - Remueve otros caracteres especiales
    - Convierte espacios multiples en uno solo
    - Limita longitud para evitar errores del sistema de archivos

    Args:
        filename: Nombre original del archivo
        max_length: Longitud maxima del nombre (default: 150)

    Returns:
        str: Nombre sanitizado sin acentos ni caracteres especiales

    Examples:
        >>> sanitize_filename("Como Calcular tu Aguinaldo?")
        "Como Calcular tu Aguinaldo"
        >>> sanitize_filename("Episodio #1: Introduccion!")
        "Episodio 1 Introduccion"
    """
    # 1. Remover acentos y diacriticos (a -> a, e -> e, n -> n, etc.)
    filename = unicodedata.normalize('NFD', filename)
    filename = ''.join(char for char in filename if unicodedata.category(char) != 'Mn')

    # 2. Remover signos de interrogacion y admiracion
    filename = filename.replace('¿', '').replace('?', '')
    filename = filename.replace('¡', '').replace('!', '')

    # 3. Remover otros caracteres no permitidos en nombres de archivo
    filename = re.sub(r'[<>:"/\\|*,;()\[\]{}#]', '', filename)

    # 4. Remover espacios multiples y reemplazar con uno solo
    filename = re.sub(r'\s+', ' ', filename)

    # 5. Limitar longitud
    filename = filename[:max_length]

    # 6. Remover espacios al inicio y final
    return filename.strip()


def find_input_files(
    extension: str = '.m4a',
    directory: Union[str, Path] = './input',
    return_first: bool = True
) -> Union[Optional[Path], List[Path]]:
    """
    Busca archivos con una extension especifica en un directorio.

    Args:
        extension: Extension del archivo a buscar (ej: '.m4a', '.srt')
        directory: Directorio donde buscar (default: './input')
        return_first: Si True, retorna solo el primer archivo encontrado

    Returns:
        Path o List[Path]: Ruta(s) del archivo(s) encontrado(s), o None si no hay

    Examples:
        >>> find_input_files('.m4a')
        PosixPath('./input/podcast.m4a')
        >>> find_input_files('.srt', './output/transcriptions', return_first=False)
        [PosixPath('./output/transcriptions/ep1.srt'), ...]
    """
    directory = Path(directory)

    if not directory.exists():
        return None if return_first else []

    # Asegurar que la extension empiece con punto
    if not extension.startswith('.'):
        extension = f'.{extension}'

    files = [
        directory / f
        for f in os.listdir(directory)
        if f.endswith(extension) and (directory / f).is_file()
    ]

    # Ordenar por fecha de modificacion (mas reciente primero)
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    if return_first:
        return files[0] if files else None

    return files


def find_video_file(base_filename: str, directory: Union[str, Path] = './output') -> Optional[Path]:
    """
    Busca un archivo de video correspondiente en un directorio.

    Args:
        base_filename: Nombre base del archivo (sin extension)
        directory: Directorio donde buscar (default: './output')

    Returns:
        Path: Ruta completa del archivo de video, o None si no se encuentra
    """
    directory = Path(directory)
    extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v']

    # Primero intentar con el nombre exacto
    for ext in extensions:
        video_path = directory / f"{base_filename}{ext}"
        if video_path.exists():
            return video_path

    # Buscar cualquier archivo de video que coincida parcialmente
    if directory.exists():
        for file in directory.iterdir():
            if file.suffix.lower() in extensions:
                file_base = file.stem
                if base_filename.lower() in file_base.lower() or file_base.lower() in base_filename.lower():
                    return file

    return None


def print_header(title: str, width: int = 80) -> None:
    """
    Imprime un header formateado para los scripts.

    Args:
        title: Titulo a mostrar
        width: Ancho total del header
    """
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_step(step: int, total: int, message: str) -> None:
    """
    Imprime un paso del proceso con formato consistente.

    Args:
        step: Numero del paso actual
        total: Total de pasos
        message: Mensaje a mostrar
    """
    print(f"\n--> Paso {step}/{total}: {message}")


def print_success(message: str) -> None:
    """Imprime mensaje de exito."""
    print(f"✓ {message}")


def print_error(message: str) -> None:
    """Imprime mensaje de error."""
    print(f"❌ ERROR: {message}")


def print_warning(message: str) -> None:
    """Imprime mensaje de advertencia."""
    print(f"⚠️  ADVERTENCIA: {message}")
