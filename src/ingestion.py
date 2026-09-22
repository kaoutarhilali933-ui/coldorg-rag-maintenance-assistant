import json
from pathlib import Path


DATA_PATH = Path("data/interventions.json")


def load_interventions():
    """Charge les interventions depuis le fichier JSON."""
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        interventions = json.load(file)

    return interventions


def intervention_to_document(intervention):
    """Transforme une intervention en document texte pour le RAG."""

    # Gestion du code erreur absent
    code_erreur = intervention["code_erreur"] or "Aucun code erreur"

    # Gestion d'une liste de pièces vide
    if intervention["pieces_remplacees"]:
        pieces = ", ".join(intervention["pieces_remplacees"])
    else:
        pieces = "Aucune pièce remplacée"

    document = (
        f"Intervention : {intervention['id']}\n"
        f"Équipement : {intervention['equipement']}\n"
        f"Marque : {intervention['marque']}\n"
        f"Type d'équipement : {intervention['type_equipement']}\n"
        f"Code erreur : {code_erreur}\n"
        f"Symptôme : {intervention['symptome']}\n"
        f"Diagnostic : {intervention['diagnostic']}\n"
        f"Solution : {intervention['solution']}\n"
        f"Pièces remplacées : {pieces}"
    )

    return document


def build_intervention_documents(interventions):
    """Transforme toutes les interventions en documents RAG."""

    documents = []

    for intervention in interventions:
        document = intervention_to_document(intervention)
        documents.append(document)

    return documents


def validate_documents(documents):
    """Vérifie que les documents RAG sont correctement construits."""

    assert len(documents) == 30, "Le nombre de documents devrait être 30."

    for document in documents:
        assert "None" not in document, "Un document contient encore la valeur None."
        assert "Symptôme :" in document, "Un document ne contient pas de symptôme."
        assert "Diagnostic :" in document, "Un document ne contient pas de diagnostic."
        assert "Solution :" in document, "Un document ne contient pas de solution."

    print("Validation réussie : tous les documents RAG sont corrects.")


if __name__ == "__main__":
    interventions = load_interventions()

    documents = build_intervention_documents(interventions)

    validate_documents(documents)

    print(f"Nombre d'interventions chargées : {len(interventions)}")
    print(f"Nombre de documents RAG créés : {len(documents)}")

    print("\n--- Premier document RAG ---")
    print(documents[0])