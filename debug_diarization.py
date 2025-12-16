# Script de debugging para analizar el archivo editing_guide.json
# y detectar problemas en la asignación de speakers

import json
import sys

def analyze_editing_guide(json_path):
    """Analiza el archivo editing_guide.json para detectar problemas"""

    with open(json_path, 'r') as f:
        segments = json.load(f)

    print("=" * 80)
    print("ANÁLISIS DE ASIGNACIÓN DE SPEAKERS")
    print("=" * 80)
    print(f"\nTotal de segmentos: {len(segments)}\n")

    # Estadísticas generales
    host_a_count = sum(1 for s in segments if s['host'] == 'HOST_A')
    host_b_count = sum(1 for s in segments if s['host'] == 'HOST_B')
    host_a_duration = sum(s['duration'] for s in segments if s['host'] == 'HOST_A')
    host_b_duration = sum(s['duration'] for s in segments if s['host'] == 'HOST_B')

    print(f"HOST_A: {host_a_count} segmentos ({host_a_duration:.2f}s totales)")
    print(f"HOST_B: {host_b_count} segmentos ({host_b_duration:.2f}s totales)")
    print()

    # Detectar secuencias largas del mismo speaker
    print("SECUENCIAS SOSPECHOSAS (>10 segmentos consecutivos del mismo host):")
    print("-" * 80)

    current_host = None
    consecutive_count = 0
    sequence_start_idx = 0
    sequence_start_time = 0

    suspicious_sequences = []

    for i, seg in enumerate(segments):
        if seg['host'] == current_host:
            consecutive_count += 1
        else:
            # Registrar secuencia si es sospechosa
            if consecutive_count > 10:
                suspicious_sequences.append({
                    'host': current_host,
                    'count': consecutive_count,
                    'start_idx': sequence_start_idx,
                    'end_idx': i - 1,
                    'start_time': sequence_start_time,
                    'end_time': segments[i-1]['end']
                })

            # Resetear contador
            current_host = seg['host']
            consecutive_count = 1
            sequence_start_idx = i
            sequence_start_time = seg['start']

    # Verificar última secuencia
    if consecutive_count > 10:
        suspicious_sequences.append({
            'host': current_host,
            'count': consecutive_count,
            'start_idx': sequence_start_idx,
            'end_idx': len(segments) - 1,
            'start_time': sequence_start_time,
            'end_time': segments[-1]['end']
        })

    if suspicious_sequences:
        for seq in suspicious_sequences:
            print(f"\n⚠️  {seq['host']}: {seq['count']} segmentos consecutivos")
            print(f"   Tiempo: {seq['start_time']:.2f}s - {seq['end_time']:.2f}s ({seq['end_time'] - seq['start_time']:.2f}s de duración)")
            print(f"   Índices: {seq['start_idx']} - {seq['end_idx']}")

            # Mostrar algunos ejemplos
            print(f"   Primeros 3 segmentos:")
            for i in range(seq['start_idx'], min(seq['start_idx'] + 3, seq['end_idx'] + 1)):
                s = segments[i]
                print(f"      [{i}] {s['start']:.2f}s - {s['end']:.2f}s (duración: {s['duration']:.2f}s)")
    else:
        print("✓ No se detectaron secuencias sospechosas")

    print("\n" + "=" * 80)
    print("ANÁLISIS DE PATRONES")
    print("=" * 80)

    # Calcular duración promedio por host
    avg_duration_a = host_a_duration / host_a_count if host_a_count > 0 else 0
    avg_duration_b = host_b_duration / host_b_count if host_b_count > 0 else 0

    print(f"\nDuración promedio por segmento:")
    print(f"  HOST_A: {avg_duration_a:.2f}s")
    print(f"  HOST_B: {avg_duration_b:.2f}s")

    # Detectar segmentos muy cortos (posibles errores)
    very_short = [s for s in segments if s['duration'] < 0.5]
    print(f"\nSegmentos muy cortos (<0.5s): {len(very_short)}")
    if very_short and len(very_short) <= 10:
        for s in very_short:
            idx = segments.index(s)
            print(f"  [{idx}] {s['host']} - {s['start']:.2f}s - {s['end']:.2f}s (duración: {s['duration']:.2f}s)")

    # Análisis temporal (dividir en chunks de 60s)
    print("\n" + "=" * 80)
    print("DISTRIBUCIÓN TEMPORAL (por minuto)")
    print("=" * 80)

    total_duration = segments[-1]['end']
    num_minutes = int(total_duration / 60) + 1

    for minute in range(num_minutes):
        start = minute * 60
        end = (minute + 1) * 60

        minute_segments = [s for s in segments if start <= s['start'] < end]
        a_count = sum(1 for s in minute_segments if s['host'] == 'HOST_A')
        b_count = sum(1 for s in minute_segments if s['host'] == 'HOST_B')

        # Detectar minutos sospechosos (más del 90% es un solo host)
        total = a_count + b_count
        if total > 0:
            a_ratio = a_count / total
            b_ratio = b_count / total

            warning = ""
            if a_ratio > 0.9 or b_ratio > 0.9:
                warning = " ⚠️  SOSPECHOSO"

            print(f"Minuto {minute} ({start}s-{end}s): A={a_count}, B={b_count}{warning}")

if __name__ == "__main__":
    json_path = "./output/editing_guide.json"

    try:
        analyze_editing_guide(json_path)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {json_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
