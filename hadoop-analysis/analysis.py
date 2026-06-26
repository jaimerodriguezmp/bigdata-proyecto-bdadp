# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
import csv
import sys
import os
from collections import defaultdict
from statistics import mean


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car_sales.csv")


def load_data():
    rows = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["year"] = int(row["year"])
            row["price"] = int(row["price"])
            row["mileage"] = int(row["mileage"])
            row["doors"] = int(row["doors"])
            row["previous_owners"] = int(row["previous_owners"])
            row["engine_size"] = float(row["engine_size"])
            rows.append(row)
    return rows


def analysis_avg_price_by_brand(data):
    print("\n=== 1. AVERAGE PRICE BY BRAND ===")
    groups = defaultdict(list)
    for row in data:
        groups[row["brand"]].append(row["price"])
    for brand in sorted(groups.keys()):
        avg = mean(groups[brand])
        print(f"  {brand:15s}: ${avg:>8,.2f}")


def analysis_avg_price_by_fuel(data):
    print("\n=== 2. AVERAGE PRICE BY FUEL TYPE ===")
    groups = defaultdict(list)
    for row in data:
        groups[row["fuel_type"]].append(row["price"])
    for fuel in sorted(groups.keys()):
        avg = mean(groups[fuel])
        print(f"  {fuel:20s}: ${avg:>8,.2f}")


def analysis_mileage_by_brand(data):
    print("\n=== 3. AVERAGE MILEAGE BY BRAND ===")
    groups = defaultdict(list)
    for row in data:
        groups[row["brand"]].append(row["mileage"])
    for brand in sorted(groups.keys()):
        avg = mean(groups[brand])
        print(f"  {brand:15s}: {avg:>8,.0f} km")


def analysis_doors_by_brand(data):
    print("\n=== 4. NUMBER OF DOORS BY BRAND ===")
    groups = defaultdict(lambda: defaultdict(int))
    for row in data:
        groups[row["brand"]][row["doors"]] += 1
    for brand in sorted(groups.keys()):
        counts = dict(groups[brand])
        total = sum(counts.values())
        print(f"  {brand:15s}: 3 doors={counts.get(3, 0):>4} ({counts.get(3, 0)/total*100:5.1f}%) | "
              f"5 doors={counts.get(5, 0):>4} ({counts.get(5, 0)/total*100:5.1f}%)")


def analysis_owners_vs_price(data):
    print("\n=== 5. PREVIOUS OWNERS VS AVERAGE PRICE ===")
    groups = defaultdict(list)
    for row in data:
        groups[row["previous_owners"]].append(row["price"])
    for owners in sorted(groups.keys()):
        avg = mean(groups[owners])
        print(f"  {owners} previous owner(s): ${avg:>8,.2f} average")


def analysis_electric_vs_gas_by_year(data):
    print("\n=== 6. ELECTRIC VS GASOLINE COMPARISON BY YEAR ===")
    electric = defaultdict(list)
    gasoline = defaultdict(list)
    for row in data:
        if row["fuel_type"] == "Electric":
            electric[row["year"]].append(row["price"])
        elif row["fuel_type"] == "Gasoline":
            gasoline[row["year"]].append(row["price"])
    years = sorted(set(list(electric.keys()) + list(gasoline.keys())))
    print("  {:6s} | {:>12s} | {:>12s} | {:>12s}".format("Year", "Electric", "Gasoline", "Difference"))
    print("  " + "-"*6 + " | " + "-"*12 + " | " + "-"*12 + " | " + "-"*12)
    for year in years:
        e_avg = mean(electric[year]) if electric[year] else 0
        g_avg = mean(gasoline[year]) if gasoline[year] else 0
        diff = e_avg - g_avg
        print(f"  {year:6d} | ${e_avg:>8,.0f}  | ${g_avg:>8,.0f}  | ${diff:>+8,.0f}")


def run_all_analyses():
    print("Loading data...")
    data = load_data()
    print(f"Total records: {len(data)}")
    print()

    analysis_avg_price_by_brand(data)
    print()
    analysis_avg_price_by_fuel(data)
    print()
    analysis_mileage_by_brand(data)
    print()
    analysis_doors_by_brand(data)
    print()
    analysis_owners_vs_price(data)
    print()
    analysis_electric_vs_gas_by_year(data)
    print()


def interactive():
    print("===== CAR DATA ANALYSIS WITH HADOOP =====")
    print("Loading data...")
    data = load_data()
    print(f"Total records: {len(data)}")
    while True:
        print("\n--- SELECT AN ANALYSIS ---")
        print("1. Average price by brand")
        print("2. Average price by fuel type")
        print("3. Average mileage by brand")
        print("4. Number of doors by brand")
        print("5. Previous owners vs price")
        print("6. Electric vs Gasoline comparison by year")
        print("0. Exit")
        choice = input("Option: ").strip()
        if choice == "1":
            analysis_avg_price_by_brand(data)
        elif choice == "2":
            analysis_avg_price_by_fuel(data)
        elif choice == "3":
            analysis_mileage_by_brand(data)
        elif choice == "4":
            analysis_doors_by_brand(data)
        elif choice == "5":
            analysis_owners_vs_price(data)
        elif choice == "6":
            analysis_electric_vs_gas_by_year(data)
        elif choice == "0":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive()
    else:
        run_all_analyses()
