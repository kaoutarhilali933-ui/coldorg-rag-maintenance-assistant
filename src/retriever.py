from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"


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


if __name__ == "__main__":
    model = load_embedding_model()

    print("Modèle d'embeddings chargé avec succès.")
    print(f"Modèle : {EMBEDDING_MODEL_NAME}")

    # Test d'un document

    test_document = (
        "Code erreur E133 sur une chaudière Frisquet. "
        "Défaut d'allumage."
    )

    document_embedding = embed_document(
        model,
        test_document,
    )

    print("\nEmbedding du document créé avec succès.")
    print(f"Dimension du vecteur : {len(document_embedding)}")
    print(f"Premières valeurs : {document_embedding[:5]}")

    # Test d'une question utilisateur

    test_query = (
        "Code E133 sur une chaudière Frisquet, "
        "quelles sont les causes possibles ?"
    )

    query_embedding = embed_query(
        model,
        test_query,
    )

    print("\nEmbedding de la question créé avec succès.")
    print(f"Dimension du vecteur : {len(query_embedding)}")
    print(f"Premières valeurs : {query_embedding[:5]}")