#!/usr/bin/env python3
"""
Script para corregir asignaciones incorrectas de speakers en editing_guide.json

Uso:
    python3 fix_speaker_assignment.py --swap-range 160 248

Este script intercambia los hosts en un rango específico de tiempo.
"""

import json
import argparse
import shutil
from datetime import datetime

def swap_hosts_in_range(segments, start_time, end_time):
    """Intercambia HOST_A y HOST_B en un rango de tiempo específico"""
    swapped_count = 0

    for seg in segments:
        # Si el segmento está dentro o se superpone con el rango
        if seg['start'] >= start_time and seg['end'] <= end_time:
            # Intercambiar
            if seg['host'] == 'HOST_A':
                seg['host'] = 'HOST_B'
                swapped_count += 1
            elif seg['host'] == 'HOST_B':
                seg['host'] = 'HOST_A'
                swapped_count += 1

    return swapped_count

def analyze_segments(segments):
    """Muestra estadísticas de los segmentos"""
    host_a_count = sum(1 for s in segments if s['host'] == 'HOST_A')
    host_b_count = sum(1 for s in segments if s['host'] == 'HOST_B')

    print(f"\nEstadísticas:")
    print(f"  Total segmentos: {len(segments)}")
    print(f"  HOST_A: {host_a_count} segmentos")
    print(f"  HOST_B: {host_b_count} segmentos")

def main():
    parser = argparse.ArgumentParser(
        description='Corrige asignaciones incorrectas de speakers en editing_guide.json'
    )
    parser.add_argument(
        '--swap-range',
        nargs=2,
        type=float,
        metavar=('START', 'END'),
        help='Intercambiar hosts en el rango de tiempo especificado (en segundos)'
    )
    parser.add_argument(
        '--input',
        default='./output/editing_guide.json',
        help='Archivo JSON de entrada (default: ./output/editing_guide.json)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Archivo JSON de salida (default: sobrescribe el original)'
    )

    args = parser.parse_args()

    # Determinar archivo de salida
    output_file = args.output if args.output else args.input

    # Leer archivo
    try:
        with open(args.input, 'r') as f:
            segments = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {args.input}")
        return 1
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo {args.input} no es un JSON válido")
        return 1

    print(f"📂 Archivo cargado: {args.input}")
    analyze_segments(segments)

    # Hacer backup del original
    if args.input == output_file:
        backup_file = f"{args.input}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(args.input, backup_file)
        print(f"\n💾 Backup creado: {backup_file}")

    # Procesar según los argumentos
    if args.swap_range:
        start_time, end_time = args.swap_range
        print(f"\n🔄 Intercambiando hosts en rango {start_time}s - {end_time}s...")

        swapped_count = swap_hosts_in_range(segments, start_time, end_time)
        print(f"   ✓ {swapped_count} segmentos intercambiados")

        # Guardar archivo modificado
        with open(output_file, 'w') as f:
            json.dump(segments, f, indent=4)

        print(f"\n💾 Archivo guardado: {output_file}")
        analyze_segments(segments)

        # Ejecutar análisis de debug
        print("\n" + "="*80)
        print("EJECUTANDO ANÁLISIS DE VALIDACIÓN")
        print("="*80)
        import subprocess
        subprocess.run(['python3', 'debug_diarization.py'])

    else:
        print("\n⚠️  No se especificaron acciones. Usa --swap-range para intercambiar hosts.")
        print("Ejemplo: python3 fix_speaker_assignment.py --swap-range 160 248")

    return 0

if __name__ == '__main__':
    exit(main())
