# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
"""Generador de dataset de coches para el analisis Hadoop."""
import csv
import random
import os

BRANDS = {
    "Toyota": ["Corolla", "Camry", "RAV4", "Yaris", "Highlander"],
    "Honda": ["Civic", "Accord", "CR-V", "Fit", "Pilot"],
    "Ford": ["Focus", "Mustang", "Explorer", "Fiesta", "Escape"],
    "BMW": ["Serie 3", "Serie 5", "X3", "X5", "Serie 1"],
    "Mercedes": ["Clase C", "Clase E", "Clase A", "GLC", "GLE"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "Polo", "ID.4"],
    "Audi": ["A3", "A4", "Q5", "Q7", "e-tron"],
    "Hyundai": ["i30", "Tucson", "Kona", "Santa Fe", "IONIQ 5"],
    "Renault": ["Clio", "Megane", "Captur", "Zoe", "Kadjar"],
    "Peugeot": ["208", "308", "3008", "5008", "e-208"],
}

FUEL_TYPES = ["Gasoline", "Diesel", "Electric", "Hybrid", "Plug-in Hybrid"]
TRANSMISSIONS = ["Manual", "Automatic"]
COLORS = ["White", "Black", "Red", "Blue", "Grey", "Silver", "Green"]
# Nota: los valores de combustible estan en ingles para que el mapper funcione correctamente
YEARS = list(range(2015, 2026))


def generate_car_data(filename="car_sales.csv", num_rows=5000):
    print(f"Generating {num_rows} rows of car data in {filename}...")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "brand", "model", "year", "price", "fuel_type",
            "mileage", "doors", "previous_owners", "transmission",
            "color", "engine_size"
        ])
        for i in range(1, num_rows + 1):
            brand = random.choice(list(BRANDS.keys()))
            model = random.choice(BRANDS[brand])
            year = random.choice(YEARS)
            base_price = {
                "Toyota": 25000, "Honda": 24000, "Ford": 23000,
                "BMW": 40000, "Mercedes": 42000, "Volkswagen": 22000,
                "Audi": 38000, "Hyundai": 20000, "Renault": 18000,
                "Peugeot": 19000,
            }[brand]
            fuel = random.choice(FUEL_TYPES)
            if fuel == "Electric":
                base_price = int(base_price * 1.4)
            elif fuel == "Hybrid":
                base_price = int(base_price * 1.2)
            age_factor = 1.0 - (2026 - year) * 0.03
            mileage = random.randint(5000, 200000)
            mileage_factor = 1.0 - (mileage / 500000)
            price = int(base_price * age_factor * mileage_factor * random.uniform(0.85, 1.15))
            price = max(price, 1000)
            doors = random.choice([3, 5])
            prev_owners = random.randint(0, 4)
            transmission = random.choice(TRANSMISSIONS)
            color = random.choice(COLORS)
            engine_size = round(random.uniform(1.0, 3.5), 1)
            if fuel in ["Electric", "Plug-in Hybrid"]:
                engine_size = round(random.uniform(0.0, 0.5), 1)
            writer.writerow([
                i, brand, model, year, price, fuel,
                mileage, doors, prev_owners, transmission,
                color, engine_size
            ])
    real_path = os.path.abspath(filename)
    print(f"Dataset generated: {real_path}")
    print(f"  - {num_rows} cars")
    print(f"  - {len(BRANDS)} brands")
    print(f"  - Columns: id, brand, model, year, price, fuel_type, mileage, doors, previous_owners, transmission, color, engine_size")


if __name__ == "__main__":
    generate_car_data()
