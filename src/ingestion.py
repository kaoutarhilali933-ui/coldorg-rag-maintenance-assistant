import json
from pathlib import Path


DATA_PATH = Path("data/interventions.json")
DOCS_PATH = Path("data/docs")


def load_interventions():
    """Charge les interventions depuis le fichier JSON."""
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        interventions = json.load(file)

    return interventions


def load_technical_sheets():
    """Charge toutes les fiches techniques du dossier data/docs."""

    sheets = {}

    for file_path in sorted(DOCS_PATH.glob("*.txt")):
        with open(file_path, "r", encoding="utf-8") as file:
            sheets[file_path.name] = file.read()

    return sheets


def split_sheet_by_sections(text, section_titles):
    """Découpe une fiche technique selon des titres de sections métier."""

    chunks = []

    for index, title in enumerate(section_titles):
        start = text.find(title)

        if start == -1:
            raise ValueError(f"Section introuvable : {title}")

        if index + 1 < len(section_titles):
            next_title = section_titles[index + 1]
            end = text.find(next_title, start)
        else:
            end = len(text)

        chunk = text[start:end].strip()
        chunks.append(chunk)

    return chunks


def add_context_to_chunks(chunks, context):
    """Ajoute le contexte de la fiche technique à chaque chunk."""

    enriched_chunks = []

    for chunk in chunks:
        enriched_chunk = f"{context.strip()}\n\n{chunk}"
        enriched_chunks.append(enriched_chunk)

    return enriched_chunks


def build_technical_chunks(technical_sheets):
    """Construit les chunks métier de toutes les fiches techniques."""

    configurations = [
        {
            "filename": "fiche_frisquet_prestige.txt",
            "context": (
                "Fabricant : Frisquet\n"
                "Équipement : Prestige Condensation\n"
                "Type : Chaudière gaz à condensation murale"
            ),
            "sections": [
                "E133 — Défaut d'allumage",
                "E125 — Défaut de circulation / surchauffe primaire",
                "E110 — Surchauffe échangeur",
                "--- ENTRETIEN ANNUEL ---",
                "--- PIÈCES D'USURE COURANTES ---",
            ],
        },
        {
            "filename": "fiche_daikin_altherma.txt",
            "context": (
                "Fabricant : Daikin\n"
                "Équipement : Altherma 3\n"
                "Type : Pompe à chaleur air/eau"
            ),
            "sections": [
                "U4 — Défaut de communication unité intérieure/extérieure",
                "E7 — Défaut moteur ventilateur (unité extérieure)",
                "AH — Défaut pompe à eau",
                "7H — Basse pression réfrigérant",
                "--- ENTRETIEN RECOMMANDÉ ---",
            ],
        },
        {
            "filename": "fiche_atlantic_climatisation.txt",
            "context": (
                "Fabricant : Atlantic\n"
                "Équipement : Idéa\n"
                "Type : Climatiseur mural réversible"
            ),
            "sections": [
                "Fuite d'eau unité intérieure",
                "Ne refroidit plus / souffle tiède",
                "Bruit anormal",
                "--- ENTRETIEN ---",
            ],
        },
        {
            "filename": "fiche_saunier_duval_themaplus.txt",
            "context": (
                "Fabricant : Saunier Duval\n"
                "Équipement : ThemaPlus Condens\n"
                "Type : Chaudière gaz à condensation murale mixte"
            ),
            "sections": [
                "F28 — Défaut d'allumage (échec après plusieurs tentatives)",
                "F20 — Surchauffe / sécurité température",
                "--- ENTRETIEN ANNUEL ---",
                "--- PIÈCES D'USURE ---",
            ],
        },
    ]

    technical_chunks = []

    for configuration in configurations:
        filename = configuration["filename"]
        context = configuration["context"]
        sections = configuration["sections"]

        chunks = split_sheet_by_sections(
            technical_sheets[filename],
            sections,
        )

        chunks = add_context_to_chunks(
            chunks,
            context,
        )

        technical_chunks.extend(chunks)

    return technical_chunks


def intervention_to_document(intervention):
    """Transforme une intervention en document texte pour le RAG."""

    code_erreur = intervention["code_erreur"] or "Aucun code erreur"

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
        assert "None" not in document
        assert "Symptôme :" in document
        assert "Diagnostic :" in document
        assert "Solution :" in document

    print("Validation réussie : tous les documents RAG sont corrects.")


if __name__ == "__main__":

    # INTERVENTIONS

    interventions = load_interventions()
    documents = build_intervention_documents(interventions)

    validate_documents(documents)

    print(f"Nombre d'interventions chargées : {len(interventions)}")
    print(f"Nombre de documents RAG créés : {len(documents)}")

    # FICHES TECHNIQUES

    technical_sheets = load_technical_sheets()

    print(f"\nNombre de fiches techniques chargées : {len(technical_sheets)}")

    technical_chunks = build_technical_chunks(technical_sheets)

    print(f"Nombre total de chunks techniques : {len(technical_chunks)}")

    assert len(technical_chunks) == 18, (
        "Le nombre total de chunks techniques devrait être 18."
    )

    print("Validation réussie : 18 chunks techniques ont été créés.")

    # Vérification d'un chunk important pour les questions de test

    daikin_u4_chunk = next(
        chunk
        for chunk in technical_chunks
        if "U4 — Défaut de communication" in chunk
    )

    print("\n--- Vérification du chunk Daikin U4 ---")
    print(daikin_u4_chunk)