import chromadb

from ingestion import (
    build_all_records,
    load_interventions,
    load_technical_sheets,
)
from retriever import (
    EMBEDDING_MODEL_NAME,
    load_embedding_model,
)


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "coldorg_maintenance"


def get_chroma_collection():
    """Crée ou récupère la collection Chroma persistante."""

    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
    )

    return collection


def index_records(collection, records, model):
    """Calcule les embeddings et ajoute ou met à jour les records dans Chroma."""

    ids = []
    documents = []
    metadatas = []

    for record in records:
        ids.append(record["metadata"]["source_id"])
        documents.append(record["text"])
        metadatas.append(record["metadata"])

    passages = [
        f"passage: {document}"
        for document in documents
    ]

    print("Calcul des embeddings...")

    embeddings = model.encode(
        passages,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print("Indexation terminée.")


if __name__ == "__main__":

    # Chargement des données originales

    interventions = load_interventions()
    technical_sheets = load_technical_sheets()

    records = build_all_records(
        interventions,
        technical_sheets,
    )

    print(f"Nombre de records à indexer : {len(records)}")

    # Chargement du modèle d'embeddings

    print("\nChargement du modèle d'embeddings...")

    model = load_embedding_model()

    print(f"Modèle chargé : {EMBEDDING_MODEL_NAME}")

    # Initialisation de ChromaDB

    print("\nInitialisation de ChromaDB...")

    collection = get_chroma_collection()

    print(
        f"Éléments présents avant indexation : "
        f"{collection.count()}"
    )

    # Indexation

    index_records(
        collection,
        records,
        model,
    )

    print(
        f"\nNombre d'éléments après indexation : "
        f"{collection.count()}"
    )