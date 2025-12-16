# Script: sync_to_notion.py
# Requisitos: pip install notion-client python-dotenv
# Descripción: Sincroniza el calendario de publicación a una base de datos de Notion
# Uso: python sync_to_notion.py [fecha_inicio]
#      donde fecha_inicio es opcional en formato DD-MM-AAAA (ej: 08-12-2024)

import os
import sys
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from notion_client import Client
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- CONFIGURACIÓN ---
METADATA_DIR = "./output/metadata"
NOTION_TOKEN = os.getenv("NOTION_TOKEN")  # Tu token de integración de Notion
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # ID de tu base de datos

# Mapeo de días de la semana
DIAS_SEMANA = {
    "Lunes": "Monday",
    "Martes": "Tuesday",
    "Miércoles": "Wednesday",
    "Jueves": "Thursday",
    "Viernes": "Friday",
    "Sábado": "Saturday",
    "Domingo": "Sunday"
}

def find_latest_calendar_csv():
    """
    Encuentra el archivo de calendario CSV más reciente en /output/metadata

    Returns:
        str: Ruta completa del archivo CSV o None si no se encuentra
    """
    if not os.path.exists(METADATA_DIR):
        return None

    calendar_files = [f for f in os.listdir(METADATA_DIR) if f.endswith('_calendar.csv')]

    if len(calendar_files) == 0:
        return None

    # Ordenar por fecha de modificación (más reciente primero)
    calendar_files.sort(key=lambda x: os.path.getmtime(os.path.join(METADATA_DIR, x)), reverse=True)

    return os.path.join(METADATA_DIR, calendar_files[0])

def parse_calendar_csv(csv_path):
    """
    Lee y parsea el archivo CSV del calendario

    Args:
        csv_path: Ruta al archivo CSV

    Returns:
        list: Lista de diccionarios con los datos del calendario
    """
    entries = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                'dia': row['Día'],
                'hora': row['Hora'],
                'tipo': row['Tipo de Contenido'],
                'titulo': row['Título'],
                'plataforma': row['Plataforma'],
                'notas': row['Notas']
            })

    return entries

def parse_start_date(date_str):
    """
    Parsea una fecha en formato DD-MM-AAAA

    Args:
        date_str: Fecha en formato DD-MM-AAAA

    Returns:
        datetime: Objeto datetime o None si el formato es inválido
    """
    try:
        fecha = datetime.strptime(date_str, "%d-%m-%Y")
        # Validar que sea un lunes
        if fecha.weekday() != 0:  # 0 = Lunes
            print(f"⚠️  ADVERTENCIA: {date_str} no es lunes ({fecha.strftime('%A')})")
            print(f"   Se usará de todas formas, pero puede causar problemas en el calendario")
        return fecha
    except ValueError:
        return None

def calculate_actual_date(dia_semana, start_date):
    """
    Calcula la fecha real basándose en el día de la semana y la fecha de inicio

    Args:
        dia_semana: Día de la semana en español (ej: "Lunes", "Martes")
        start_date: Fecha de inicio (debe ser un lunes)

    Returns:
        str: Fecha en formato ISO (AAAA-MM-DD)
    """
    # Mapeo de días a offset desde el lunes
    dias_offset = {
        "Lunes": 0,
        "Martes": 1,
        "Miércoles": 2,
        "Jueves": 3,
        "Viernes": 4,
        "Sábado": 5,
        "Domingo": 6
    }

    offset = dias_offset.get(dia_semana, 0)
    fecha_real = start_date + timedelta(days=offset)
    return fecha_real.strftime("%Y-%m-%d")

def create_notion_page(notion, database_id, entry, start_date=None):
    """
    Crea una página en la base de datos de Notion

    Args:
        notion: Cliente de Notion
        database_id: ID de la base de datos
        entry: Diccionario con los datos de la entrada
        start_date: Fecha de inicio (lunes) para calcular fechas reales

    Returns:
        dict: Respuesta de la API de Notion
    """
    properties = {
        "Día": {
            "select": {
                "name": entry['dia']
            }
        },
        "Hora": {
            "rich_text": [
                {
                    "text": {
                        "content": entry['hora']
                    }
                }
            ]
        },
        "Tipo de Contenido": {
            "select": {
                "name": entry['tipo']
            }
        },
        "Título": {
            "title": [
                {
                    "text": {
                        "content": entry['titulo']
                    }
                }
            ]
        },
        "Plataforma": {
            "multi_select": [
                {"name": platform.strip()} for platform in entry['plataforma'].split('+')
            ]
        },
        "Notas": {
            "rich_text": [
                {
                    "text": {
                        "content": entry['notas']
                    }
                }
            ]
        },
        "Publicado": {
            "checkbox": False
        }
    }

    # Agregar fecha real calculada desde el lunes de inicio
    # La fecha se calcula sumando días desde el lunes según el día de la semana
    if start_date:
        fecha_real = calculate_actual_date(entry['dia'], start_date)
        properties["Fecha"] = {
            "date": {
                "start": fecha_real
            }
        }

    return notion.pages.create(
        parent={"database_id": database_id},
        properties=properties
    )

def get_existing_entries(notion, database_id):
    """
    Obtiene todas las entradas existentes en la base de datos

    Args:
        notion: Cliente de Notion
        database_id: ID de la base de datos

    Returns:
        set: Conjunto de títulos existentes (para evitar duplicados)
    """
    # Corregido: usar el método correcto del SDK
    response = notion.databases.query(**{"database_id": database_id})

    existing_titles = set()
    for page in response.get('results', []):
        # Extraer el título de la página
        title_property = page.get('properties', {}).get('Título', {})
        title_list = title_property.get('title', [])
        if title_list and len(title_list) > 0:
            title = title_list[0].get('text', {}).get('content', '')
            if title:
                existing_titles.add(title)

    return existing_titles

def sync_calendar_to_notion(csv_path, start_date=None):
    """
    Sincroniza el calendario CSV a Notion (solo agrega nuevas entradas, no elimina existentes)

    Args:
        csv_path: Ruta al archivo CSV
        start_date: Fecha de inicio opcional (lunes) en formato datetime

    Returns:
        tuple: (success_count, skip_count, fail_count)
    """
    # Validar variables de entorno
    if not NOTION_TOKEN:
        print("❌ ERROR: Variable de entorno NOTION_TOKEN no configurada")
        print("\nPara configurarla:")
        print("   1. Copia .env.example a .env")
        print("   2. Edita .env y agrega tu token de Notion en NOTION_TOKEN")
        return 0, 0, 0

    if not NOTION_DATABASE_ID:
        print("❌ ERROR: Variable de entorno NOTION_DATABASE_ID no configurada")
        print("\nPara configurarla:")
        print("   1. Copia .env.example a .env")
        print("   2. Edita .env y agrega tu ID de base de datos en NOTION_DATABASE_ID")
        return 0, 0, 0

    # Inicializar cliente de Notion
    try:
        notion = Client(auth=NOTION_TOKEN)
        print(f"✓ Conectado a Notion")
    except Exception as e:
        print(f"❌ ERROR al conectar con Notion: {e}")
        return 0, 0, 0

    # Obtener entradas existentes
    try:
        print("   Verificando entradas existentes...")
        existing_titles = get_existing_entries(notion, NOTION_DATABASE_ID)
        print(f"   ✓ {len(existing_titles)} entradas ya existen en Notion")
    except Exception as e:
        print(f"⚠️  No se pudo obtener las entradas existentes: {e}")
        existing_titles = set()

    # Leer calendario CSV
    print(f"   Leyendo calendario: {os.path.basename(csv_path)}")
    entries = parse_calendar_csv(csv_path)
    print(f"   ✓ {len(entries)} entradas encontradas en CSV")

    # Sincronizar a Notion (solo nuevas)
    print("\n   Sincronizando a Notion...")
    success_count = 0
    skip_count = 0
    fail_count = 0

    for idx, entry in enumerate(entries, 1):
        # Verificar si ya existe
        if entry['titulo'] in existing_titles:
            print(f"   [{idx}/{len(entries)}] ⊘ Ya existe: {entry['titulo'][:50]}...")
            skip_count += 1
            continue

        # Crear nueva entrada
        try:
            create_notion_page(notion, NOTION_DATABASE_ID, entry, start_date)
            fecha_real = calculate_actual_date(entry['dia'], start_date)
            print(f"   [{idx}/{len(entries)}] ✓ {entry['dia']} {fecha_real}: {entry['titulo'][:45]}...")
            success_count += 1
        except Exception as e:
            error_msg = str(e)
            # Si el error es por la propiedad Fecha faltante
            if "Fecha is not a property that exists" in error_msg:
                print(f"\n❌ ERROR: Tu base de datos de Notion no tiene la propiedad 'Fecha'")
                print("   Para usar fechas automáticas, agrega una columna llamada 'Fecha' de tipo Date en Notion")
                print("   O ejecuta el script sin fecha: python sync_to_notion.py")
                return success_count, skip_count, fail_count + (len(entries) - idx + 1)
            else:
                print(f"   [{idx}/{len(entries)}] ❌ Error: {entry['titulo'][:50]}... - {e}")
                fail_count += 1

    return success_count, skip_count, fail_count

def main():
    print("=" * 80)
    print("  SINCRONIZACIÓN DE CALENDARIO A NOTION")
    print("=" * 80)

    # Parsear argumentos de línea de comandos
    if len(sys.argv) < 2:
        print("\n❌ ERROR: Debes especificar una fecha de inicio (lunes)")
        print("\nUso:")
        print("   python sync_to_notion.py DD-MM-AAAA")
        print("\nEjemplos:")
        print("   python sync_to_notion.py 16-12-2024  # Para la semana del 16 de diciembre")
        print("   python sync_to_notion.py 06-01-2025  # Para la semana del 6 de enero")
        print("\nNota: La fecha debe ser un lunes (inicio de semana)")
        return

    date_str = sys.argv[1]
    start_date = parse_start_date(date_str)
    if not start_date:
        print(f"❌ ERROR: Formato de fecha inválido: {date_str}")
        print("   Usa el formato DD-MM-AAAA (ejemplo: 16-12-2024)")
        return

    print(f"\n📅 Fecha de inicio configurada: {start_date.strftime('%d-%m-%Y (%A)')}")

    # 1. Buscar archivo de calendario
    print("\n--> Paso 1/2: Buscando archivo de calendario...")

    calendar_path = find_latest_calendar_csv()

    if not calendar_path:
        print(f"❌ ERROR: No se encontró ningún archivo *_calendar.csv en {METADATA_DIR}")
        print("Por favor, ejecuta primero: python analyze_chapters.py")
        return

    print(f"✓ Calendario encontrado: {os.path.basename(calendar_path)}")

    # 2. Sincronizar a Notion
    print("\n--> Paso 2/2: Sincronizando a Notion...")

    success_count, skip_count, fail_count = sync_calendar_to_notion(calendar_path, start_date)

    # 3. Resumen final
    print("\n" + "=" * 80)
    print("✅ ¡SINCRONIZACIÓN COMPLETADA!")
    print("=" * 80)
    print(f"\n📊 RESUMEN:")
    print(f"   • Entradas nuevas agregadas: {success_count}")
    print(f"   • Entradas ya existentes (omitidas): {skip_count}")
    print(f"   • Entradas con errores: {fail_count}")
    print(f"   • Semana de publicación: {start_date.strftime('%d-%m-%Y')} al {(start_date + timedelta(days=6)).strftime('%d-%m-%Y')}")
    print(f"\n💡 NOTAS:")
    print(f"   • Las entradas existentes en Notion NO fueron modificadas")
    print(f"   • Si marcaste algo como 'Publicado', seguirá así")
    print(f"   • Las fechas se calcularon automáticamente desde el lunes {start_date.strftime('%d-%m-%Y')}")
    print(f"\n💡 SIGUIENTE PASO:")
    print(f"   1. Abre tu base de datos de Notion")
    print(f"   2. Cambia la vista a 'Calendario' para ver las publicaciones por fecha")
    print(f"   3. Revisa las entradas de la semana del {start_date.strftime('%d al %d de %B')}")
    print(f"   4. Reorganiza manualmente si hay conflictos de fechas")
    print(f"   5. Usa el checkbox 'Publicado' para marcar contenido publicado")
    print("=" * 80)

if __name__ == "__main__":
    main()
