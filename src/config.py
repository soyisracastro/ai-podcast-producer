# src/config.py
# Configuracion centralizada para AI Podcast Producer

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


@dataclass
class Settings:
    """Configuracion centralizada del proyecto."""

    # === Directorios ===
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    input_dir: Path = field(default_factory=lambda: Path("./input"))
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    transcriptions_dir: Path = field(default_factory=lambda: Path("./output/transcriptions"))
    metadata_dir: Path = field(default_factory=lambda: Path("./output/metadata"))
    clips_dir: Path = field(default_factory=lambda: Path("./output/clips"))
    viral_clips_dir: Path = field(default_factory=lambda: Path("./output/viral_clips"))
    archives_dir: Path = field(default_factory=lambda: Path("./archives"))

    # === API Keys (desde .env) ===
    hf_token: Optional[str] = field(default_factory=lambda: os.getenv("HF_TOKEN"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    notion_token: Optional[str] = field(default_factory=lambda: os.getenv("NOTION_TOKEN"))
    notion_database_id: Optional[str] = field(default_factory=lambda: os.getenv("NOTION_DATABASE_ID"))

    # === Configuracion de Modelos ===
    whisper_model: str = "base"  # tiny, base, small, medium, large
    whisper_language: str = "es"
    openai_model: str = "gpt-4o-mini"
    diarization_model: str = "pyannote/speaker-diarization-3.1"

    # === Configuracion de Video ===
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    video_fps: int = 24
    video_preset: str = "medium"  # ultrafast, fast, medium, slow
    video_threads: int = 4

    # === Configuracion de Diarizacion ===
    min_speakers: int = 2
    max_speakers: int = 2
    suspicious_sequence_threshold: int = 15

    # === Extensiones de Archivo ===
    audio_extensions: tuple = ('.m4a', '.mp3', '.wav', '.ogg', '.flac')
    video_extensions: tuple = ('.mp4', '.mov', '.avi', '.mkv', '.m4v')

    def __post_init__(self):
        """Crear directorios si no existen."""
        for dir_attr in ['input_dir', 'output_dir', 'transcriptions_dir',
                         'metadata_dir', 'clips_dir', 'viral_clips_dir', 'archives_dir']:
            dir_path = getattr(self, dir_attr)
            if isinstance(dir_path, Path):
                dir_path.mkdir(parents=True, exist_ok=True)

    def validate_hf_token(self) -> bool:
        """Valida que el token de Hugging Face este configurado."""
        if not self.hf_token:
            print("❌ ERROR: No se encontro la variable HF_TOKEN.")
            print("Asegurate de tener un archivo '.env' con la linea: HF_TOKEN=hf_tu_token_aqui")
            return False
        return True

    def validate_openai_key(self) -> bool:
        """Valida que la API key de OpenAI este configurada."""
        if not self.openai_api_key:
            print("❌ ERROR: No se encontro OPENAI_API_KEY en el archivo .env")
            print("Por favor, agrega la linea: OPENAI_API_KEY=sk-tu_clave_aqui")
            print("\nPuedes obtener tu API key en: https://platform.openai.com/api-keys")
            return False
        return True

    def validate_notion(self) -> bool:
        """Valida que las credenciales de Notion esten configuradas."""
        if not self.notion_token:
            print("❌ ERROR: No se encontro NOTION_TOKEN en el archivo .env")
            return False
        if not self.notion_database_id:
            print("❌ ERROR: No se encontro NOTION_DATABASE_ID en el archivo .env")
            return False
        return True


# Instancia global de configuracion
settings = Settings()


# === Constantes adicionales ===

# Template de calendario semanal para publicacion
CALENDAR_TEMPLATE = [
    {'day': 'Lunes', 'time': '21:00', 'content_type': 'Episodio Completo', 'platform': 'YouTube + Spotify', 'is_full_episode': True},
    {'day': 'Martes', 'time': '07:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'high'},
    {'day': 'Martes', 'time': '13:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'high'},
    {'day': 'Miercoles', 'time': '07:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'medium'},
    {'day': 'Miercoles', 'time': '18:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'high'},
    {'day': 'Jueves', 'time': '13:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'medium'},
    {'day': 'Jueves', 'time': '20:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'medium'},
    {'day': 'Viernes', 'time': '07:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'priority': 'low'},
    {'day': 'Viernes', 'time': '17:00', 'content_type': 'Clip Largo', 'platform': 'YouTube', 'priority': 'low'},
    {'day': 'Sabado', 'time': '10:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'mood': 'inspirational'},
    {'day': 'Domingo', 'time': '19:00', 'content_type': 'Clip Corto', 'platform': 'TikTok/Instagram', 'mood': 'teaser'},
]

# Rangos de clips virales segun duracion del episodio
VIRAL_CLIPS_RANGES = {
    (10, 15): (4, 6),   # 10-15 min: 4-6 clips
    (15, 25): (6, 8),   # 15-25 min: 6-8 clips
    (25, 40): (8, 12),  # 25-40 min: 8-12 clips
    (40, 999): (12, 15) # 40+ min: 12-15 clips
}


def get_viral_clips_range(duration_minutes: int) -> tuple:
    """
    Obtiene el rango de clips virales recomendados segun la duracion.

    Args:
        duration_minutes: Duracion del episodio en minutos

    Returns:
        tuple: (min_clips, max_clips)
    """
    for (min_dur, max_dur), clips_range in VIRAL_CLIPS_RANGES.items():
        if min_dur <= duration_minutes < max_dur:
            return clips_range
    return (4, 6)  # Default
