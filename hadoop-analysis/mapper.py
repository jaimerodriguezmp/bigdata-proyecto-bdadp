#!/usr/bin/env python3
# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
"""Mapper para Hadoop Streaming - Analisis de datos de coches.
Recibe lineas CSV por STDIN, emite pares clave-valor segun el analisis."""

import sys

ANALYSIS = sys.argv[1] if len(sys.argv) > 1 else "avg_price_by_brand"

header = sys.stdin.readline().strip().split(",")

brand_idx = header.index("brand")
year_idx = header.index("year")
price_idx = header.index("price")
fuel_idx = header.index("fuel_type")
mileage_idx = header.index("mileage")
doors_idx = header.index("doors")
owners_idx = header.index("previous_owners")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    cols = line.split(",")
    if len(cols) < len(header):
        continue

    brand = cols[brand_idx]
    year = cols[year_idx]
    price = int(cols[price_idx])
    fuel = cols[fuel_idx]
    mileage = int(cols[mileage_idx])
    doors = cols[doors_idx]
    owners = cols[owners_idx]

    if ANALYSIS == "avg_price_by_brand":
        print(f"{brand}\t{price}\t1")
    elif ANALYSIS == "avg_price_by_fuel":
        print(f"{fuel}\t{price}\t1")
    elif ANALYSIS == "mileage_by_brand":
        print(f"{brand}\t{mileage}\t1")
    elif ANALYSIS == "doors_by_brand":
        print(f"{brand}\t{doors}\t1")
    elif ANALYSIS == "owners_vs_price":
        print(f"{owners}\t{price}\t1")
    elif ANALYSIS == "electric_vs_gas_by_year":
        if fuel in ("Electric", "Gasoline"):
            print(f"{fuel}|{year}\t{price}\t1")
