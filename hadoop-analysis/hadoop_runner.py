#!/usr/bin/env python3
# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
"""Ejecuta el analisis Hadoop usando Hadoop Streaming.
Alternativa nativa de Python al script bash para Windows."""

import subprocess
import sys
import os

ANALYSES = {
    "1": ("avg_price_by_brand", "Average price by brand"),
    "2": ("avg_price_by_fuel", "Average price by fuel type"),
    "3": ("mileage_by_brand", "Average mileage by brand"),
    "4": ("doors_by_brand", "Number of doors by brand"),
    "5": ("owners_vs_price", "Previous owners vs price"),
    "6": ("electric_vs_gas_by_year", "Electric vs Gasoline comparison"),
}


def run_hadoop_streaming(analysis_key):
    if analysis_key not in ANALYSES:
        print("Invalid analysis")
        return

    analysis_name, description = ANALYSES[analysis_key]
    print(f"\n=== Running: {description} ===")

    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car_sales.csv")
    mapper_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapper.py")
    reducer_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reducer.py")

    hadoop_cmd = [
        "mapred", "streaming",
        "-input", f"car_sales.csv",
        "-output", f"output_{analysis_name}",
        "-mapper", f"python3 mapper.py {analysis_name}",
        "-reducer", "python3 reducer.py",
        "-file", mapper_py,
        "-file", reducer_py,
        "-file", data_file,
    ]
    print("Command:", " ".join(hadoop_cmd))
    try:
        subprocess.run(hadoop_cmd, check=True)
        print("Analysis completed. Results in output_{analysis_name}/")
    except FileNotFoundError:
        print("Hadoop is not installed. Use 'python3 analysis.py --interactive'")
    except subprocess.CalledProcessError as e:
        print(f"Error running Hadoop: {e}")


if __name__ == "__main__":
    print("===== HADOOP CAR ANALYSIS =====")
    print("Note: Requires Hadoop installed and configured.")
    print("If you don't have Hadoop, use: python3 analysis.py --interactive")
    print()
    for k, v in ANALYSES.items():
        print(f"  {k}. {v[1]}")
    choice = input("Select an analysis: ").strip()
    if choice in ANALYSES:
        run_hadoop_streaming(choice)
