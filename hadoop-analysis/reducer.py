#!/usr/bin/env python3
# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
"""Reducer para Hadoop Streaming.
Recibe pares (clave, valor, count) y calcula promedios."""

import sys

current_key = None
total = 0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) < 3:
        continue
    key = parts[0]
    value = float(parts[1])
    c = int(parts[2])

    if key != current_key:
        if current_key is not None and count > 0:
            avg = total / count
            print(f"{current_key}\t{avg:.2f}")
        current_key = key
        total = 0
        count = 0

    total += value
    count += c

if current_key is not None and count > 0:
    avg = total / count
    print(f"{current_key}\t{avg:.2f}")
