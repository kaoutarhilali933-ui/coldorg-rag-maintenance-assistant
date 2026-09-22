import json
from collections import Counter
from pathlib import Path

DATA_PATH = Path("data/interventions.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    interventions = json.load(f)

# Nombre total d'interventions
print(f"Nombre total d'interventions : {len(interventions)}")

# Comptage des marques
marques = Counter(item["marque"] for item in interventions)

# Comptage des types d'équipements
types = Counter(item["type_equipement"] for item in interventions)

# Récupération des codes erreur non nuls
codes = [
    item["code_erreur"]
    for item in interventions
    if item["code_erreur"] is not None
]

codes_counter = Counter(codes)

# Nombre d'interventions sans code erreur
sans_code = sum(
    1
    for item in interventions
    if item["code_erreur"] is None
)

# Affichage des marques
print("\nMarques :")
for marque, count in marques.items():
    print(f"- {marque}: {count}")

# Affichage des types d'équipements
print("\nTypes d'équipements :")
for type_eq, count in types.items():
    print(f"- {type_eq}: {count}")

# Affichage du nombre d'interventions sans code erreur
print(f"\nInterventions sans code erreur : {sans_code}")

# Affichage des codes erreur récurrents
print("\nCodes erreur récurrents :")
for code, count in codes_counter.items():
    if count > 1:
        print(f"- {code}: {count}")

# Détail des codes erreur récurrents
print("\nDétail des codes erreur récurrents :")

for code, count in codes_counter.items():
    if count > 1:
        print(f"\nCode {code} ({count} interventions)")

        for item in interventions:
            if item["code_erreur"] == code:
                print(
                    f"- {item['id']} | "
                    f"{item['marque']} | "
                    f"{item['symptome']} | "
                    f"Diagnostic: {item['diagnostic']}"
                )

# Détail des interventions sans code erreur
print("\nInterventions sans code erreur :")

for item in interventions:
    if item["code_erreur"] is None:
        print(
            f"- {item['id']} | "
            f"{item['marque']} | "
            f"{item['type_equipement']} | "
            f"{item['symptome']}"
        )