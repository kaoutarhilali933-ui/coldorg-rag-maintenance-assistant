import chromadb
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "coldorg_maintenance"


def load_embedding_model():
    """Charge le modèle d'embeddings utilisé par le RAG."""

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return model


def embed_document(model, text):
    """Transforme un document en vecteur numérique."""

    text_with_prefix = f"passage: {text}"

    embedding = model.encode(
        text_with_prefix,
        normalize_embeddings=True,
    )

    return embedding


def embed_query(model, query):
    """Transforme une question utilisateur en vecteur numérique."""

    query_with_prefix = f"query: {query}"

    embedding = model.encode(
        query_with_prefix,
        normalize_embeddings=True,
    )

    return embedding


def get_vector_collection():
    """Charge la collection Chroma déjà construite."""

    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
    )

    collection = client.get_collection(
        name=COLLECTION_NAME,
    )

    return collection


def search_similar(model, query, top_k=5):
    """Recherche les chunks les plus proches d'une question."""

    collection = get_vector_collection()

    query_embedding = embed_query(
        model,
        query,
    )

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "embeddings",
        ],
    )

    retrieved_results = []

    for index in range(len(results["ids"][0])):
        document_embedding = results["embeddings"][0][index]

        similarity_score = sum(
            float(query_value) * float(document_value)
            for query_value, document_value in zip(
                query_embedding,
                document_embedding,
            )
        )

        retrieved_results.append(
            {
                "source_id": results["ids"][0][index],
                "source_type": results["metadatas"][0][index][
                    "source_type"
                ],
                "score": similarity_score,
                "text": results["documents"][0][index],
                "metadata": results["metadatas"][0][index],
            }
        )

    return retrieved_results


if __name__ == "__main__":
    model = load_embedding_model()

    print("Modèle d'embeddings chargé avec succès.")
    print(f"Modèle : {EMBEDDING_MODEL_NAME}")

    test_query = (
        "Code erreur E133 sur une chaudière Frisquet Prestige "
        "Condensation 25kW. La chaudière ne redémarre pas depuis "
        "ce matin. Quelles sont les causes possibles et comment "
        "diagnostiquer ?"
    )

    print("\nQuestion :")
    print(test_query)

    results = search_similar(
        model,
        test_query,
        top_k=5,
    )

    print("\n--- TOP 5 RÉSULTATS ---")

    for rank, result in enumerate(results, start=1):
        print(f"\nRésultat {rank}")
        print(f"Source ID : {result['source_id']}")
        print(f"Source type : {result['source_type']}")
        print(f"Score : {result['score']:.4f}")
        print("Texte :")
        print(result["text"])