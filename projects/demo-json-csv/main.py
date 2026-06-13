import csv
import json
import os
import sys
from typing import List, Dict

def convert_json_to_csv(json_file: str, csv_file: str) -> bool:
    """Convierte un archivo JSON a CSV."""
    if not os.path.exists(json_file):
        print(f"Error: {json_file} no encontrado.")
        return False

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("Error: El JSON debe ser una lista de objetos.")
            return False

        if not data:
            print("Warning: JSON vacío.")
            return True

        keys = data[0].keys()
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        
        print(f"Éxito: {csv_file} generado.")
        return True
    except Exception as e:
        print(f"Error crítico: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python main.py input.json output.csv")
    else:
        convert_json_to_csv(sys.argv[1], sys.argv[2])
