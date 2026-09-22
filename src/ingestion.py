import json
from pathlib import Path


DATA_PATH = Path("data/interventions.json")
DOCS_PATH = Path("data/docs")


TECHNICAL_CONFIGURATIONS = [
    {
        "filename": "fiche_frisquet_prestige.txt",
        "marque": "Frisquet",
        "equipement": "Prestige Condensation",
        "type_equipement": "chaudiere_gaz",
        "context": (
            "Fabricant : Frisquet\n"
            "Équipement : Prestige Condensation\n"
            "Type : Chaudière gaz à condensation murale"
        ),
        "sections": [
            {
                "title": "E133 — Défaut d'allumage",
                "source_id": "frisquet_e133",
                "code_erreur": "E133",
            },
            {
                "title": "E125 — Défaut de circulation / surchauffe primaire",
                "source_id": "frisquet_e125",
                "code_erreur": "E125",
            },
            {
                "title": "E110 — Surchauffe échangeur",
                "source_id": "frisquet_e110",
                "code_erreur": "E110",
            },
            {
                "title": "--- ENTRETIEN ANNUEL ---",
                "source_id": "frisquet_entretien",
                "code_erreur": "",
            },
            {
                "title": "--- PIÈCES D'USURE COURANTES ---",
                "source_id": "frisquet_pieces_usure",
                "code_erreur": "",
            },
        ],
    },
    {
        "filename": "fiche_daikin_altherma.txt",
        "marque": "Daikin",
        "equipement": "Altherma 3",
        "type_equipement": "pac_air_eau",
        "context": (
            "Fabricant : Daikin\n"
            "Équipement : Altherma 3\n"
            "Type : Pompe à chaleur air/eau"
        ),
        "sections": [
            {
                "title": "U4 — Défaut de communication unité intérieure/extérieure",
                "source_id": "daikin_u4",
                "code_erreur": "U4",
            },
            {
                "title": "E7 — Défaut moteur ventilateur (unité extérieure)",
                "source_id": "daikin_e7",
                "code_erreur": "E7",
            },
            {
                "title": "AH — Défaut pompe à eau",
                "source_id": "daikin_ah",
                "code_erreur": "AH",
            },
            {
                "title": "7H — Basse pression réfrigérant",
                "source_id": "daikin_7h",
                "code_erreur": "7H",
            },
            {
                "title": "--- ENTRETIEN RECOMMANDÉ ---",
                "source_id": "daikin_entretien",
                "code_erreur": "",
            },
        ],
    },
    {
        "filename": "fiche_atlantic_climatisation.txt",
        "marque": "Atlantic",
        "equipement": "Idéa",
        "type_equipement": "climatisation",
        "context": (
            "Fabricant : Atlantic\n"
            "Équipement : Idéa\n"
            "Type : Climatiseur mural réversible"
        ),
        "sections": [
            {
                "title": "Fuite d'eau unité intérieure",
                "source_id": "atlantic_fuite_eau",
                "code_erreur": "",
            },
            {
                "title": "Ne refroidit plus / souffle tiède",
                "source_id": "atlantic_ne_refroidit_plus",
                "code_erreur": "",
            },
            {
                "title": "Bruit anormal",
                "source_id": "atlantic_bruit_anormal",
                "code_erreur": "",
            },
            {
                "title": "--- ENTRETIEN ---",
                "source_id": "atlantic_entretien",
                "code_erreur": "",
            },
        ],
    },
    {
        "filename": "fiche_saunier_duval_themaplus.txt",
        "marque": "Saunier Duval",
        "equipement": "ThemaPlus Condens",
        "type_equipement": "chaudiere_gaz",
        "context": (
            "Fabricant : Saunier Duval\n"
            "Équipement : ThemaPlus Condens\n"
            "Type : Chaudière gaz à condensation murale mixte"
        ),
        "sections": [
            {
                "title": "F28 — Défaut d'allumage (échec après plusieurs tentatives)",
                "source_id": "saunier_f28",
                "code_erreur": "F28",
            },
            {
                "title": "F20 — Surchauffe / sécurité température",
                "source_id": "saunier_f20",
                "code_erreur": "F20",
            },
            {
                "title": "--- ENTRETIEN ANNUEL ---",
                "source_id": "saunier_entretien",
                "code_erreur": "",
            },
            {
                "title": "--- PIÈCES D'USURE ---",
                "source_id": "saunier_pieces_usure",
                "code_erreur": "",
            },
        ],
    },
]


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


def build_technical_records(technical_sheets):
    """Construit les chunks techniques avec leurs métadonnées."""

    records = []

    for configuration in TECHNICAL_CONFIGURATIONS:
        filename = configuration["filename"]

        section_titles = [
            section["title"]
            for section in configuration["sections"]
        ]

        chunks = split_sheet_by_sections(
            technical_sheets[filename],
            section_titles,
        )

        chunks = add_context_to_chunks(
            chunks,
            configuration["context"],
        )

        for chunk, section in zip(chunks, configuration["sections"]):
            record = {
                "text": chunk,
                "metadata": {
                    "source_type": "technical_sheet",
                    "source_id": section["source_id"],
                    "marque": configuration["marque"],
                    "type_equipement": configuration["type_equipement"],
                    "code_erreur": section["code_erreur"],
                    "equipement": configuration["equipement"],
                },
            }

            records.append(record)

    return records


def build_technical_chunks(technical_sheets):
    """Retourne uniquement le texte des chunks techniques."""

    records = build_technical_records(technical_sheets)

    return [record["text"] for record in records]


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


def intervention_to_record(intervention):
    """Crée un chunk d'intervention avec son texte et ses métadonnées."""

    record = {
        "text": intervention_to_document(intervention),
        "metadata": {
            "source_type": "intervention",
            "source_id": intervention["id"],
            "marque": intervention["marque"],
            "type_equipement": intervention["type_equipement"],
            "code_erreur": intervention["code_erreur"] or "",
            "equipement": intervention["equipement"],
            "date": intervention["date"],
        },
    }

    return record


def build_intervention_records(interventions):
    """Construit les chunks d'intervention avec leurs métadonnées."""

    records = []

    for intervention in interventions:
        record = intervention_to_record(intervention)
        records.append(record)

    return records


def build_intervention_documents(interventions):
    """Transforme toutes les interventions en documents RAG."""

    documents = []

    for intervention in interventions:
        document = intervention_to_document(intervention)
        documents.append(document)

    return documents


def build_all_records(interventions, technical_sheets):
    """Regroupe tous les records RAG du projet."""

    intervention_records = build_intervention_records(interventions)
    technical_records = build_technical_records(technical_sheets)

    all_records = intervention_records + technical_records

    return all_records


def validate_documents(documents):
    """Vérifie que les documents RAG sont correctement construits."""

    assert len(documents) == 30, "Le nombre de documents devrait être 30."

    for document in documents:
        assert "None" not in document
        assert "Symptôme :" in document
        assert "Diagnostic :" in document
        assert "Solution :" in document

    print("Validation réussie : tous les documents RAG sont corrects.")


def validate_all_records(records):
    """Vérifie la cohérence de l'ensemble du corpus RAG."""

    assert len(records) == 48, (
        "Le corpus RAG devrait contenir 48 records."
    )

    required_metadata = {
        "source_type",
        "source_id",
        "marque",
        "type_equipement",
        "code_erreur",
        "equipement",
    }

    source_ids = []

    for record in records:
        assert "text" in record, "Un record ne contient pas de texte."
        assert "metadata" in record, "Un record ne contient pas de métadonnées."

        assert isinstance(record["text"], str), (
            "Le texte d'un record doit être une chaîne."
        )

        assert record["text"].strip(), (
            "Un record contient un texte vide."
        )

        metadata = record["metadata"]

        missing_metadata = required_metadata - set(metadata.keys())

        assert not missing_metadata, (
            f"Métadonnées manquantes : {missing_metadata}"
        )

        for key, value in metadata.items():
            assert value is not None, (
                f"La métadonnée '{key}' contient None."
            )

        assert metadata["source_type"] in {
            "intervention",
            "technical_sheet",
        }, "source_type invalide."

        assert metadata["source_id"], (
            "Un record possède un source_id vide."
        )

        source_ids.append(metadata["source_id"])

    assert len(source_ids) == len(set(source_ids)), (
        "Les source_id doivent être uniques."
    )

    print("Validation réussie : les 48 records RAG sont cohérents.")


if __name__ == "__main__":

    # CHARGEMENT DES DONNÉES

    interventions = load_interventions()
    technical_sheets = load_technical_sheets()

    # INTERVENTIONS

    documents = build_intervention_documents(interventions)
    intervention_records = build_intervention_records(interventions)

    validate_documents(documents)

    print(f"Nombre d'interventions chargées : {len(interventions)}")
    print(f"Nombre de documents RAG créés : {len(documents)}")
    print(
        f"Nombre de chunks intervention avec métadonnées : "
        f"{len(intervention_records)}"
    )

    print("\n--- Métadonnées INT-001 ---")
    print(intervention_records[0]["metadata"])

    int_003_record = next(
        record
        for record in intervention_records
        if record["metadata"]["source_id"] == "INT-003"
    )

    print("\n--- Métadonnées INT-003 ---")
    print(int_003_record["metadata"])

    # FICHES TECHNIQUES

    print(f"\nNombre de fiches techniques chargées : {len(technical_sheets)}")

    technical_records = build_technical_records(technical_sheets)

    print(
        f"Nombre de chunks techniques avec métadonnées : "
        f"{len(technical_records)}"
    )

    assert len(technical_records) == 18, (
        "Le nombre total de chunks techniques devrait être 18."
    )

    print("Validation réussie : 18 chunks techniques ont été créés.")

    daikin_u4_record = next(
        record
        for record in technical_records
        if record["metadata"]["source_id"] == "daikin_u4"
    )

    print("\n--- Métadonnées Daikin U4 ---")
    print(daikin_u4_record["metadata"])

    atlantic_fuite_record = next(
        record
        for record in technical_records
        if record["metadata"]["source_id"] == "atlantic_fuite_eau"
    )

    print("\n--- Métadonnées Atlantic fuite d'eau ---")
    print(atlantic_fuite_record["metadata"])

    # CORPUS RAG COMPLET

    all_records = build_all_records(
        interventions,
        technical_sheets,
    )

    validate_all_records(all_records)

    print(f"\nNombre total de records RAG : {len(all_records)}")