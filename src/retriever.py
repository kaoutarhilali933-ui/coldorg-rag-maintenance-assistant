import re

import chromadb
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "coldorg_maintenance"

BRAND_BONUS = 0.003
ERROR_CODE_BONUS = 0.05
NO_ERROR_CODE_BONUS = 0.03


EQUIPMENT_TYPE_ALIASES = {
    "pac_air_eau": [
        "pompe à chaleur air/eau",
        "pompe a chaleur air/eau",
        "pompe à chaleur",
        "pompe a chaleur",
        "pac",
    ],
    "climatisation": [
        "climatiseur",
        "climatisation",
    ],
    "chaudiere_gaz": [
        "chaudière",
        "chaudiere",
    ],
    "chauffe_eau_thermo": [
        "chauffe-eau thermodynamique",
        "chauffe eau thermodynamique",
        "ballon thermodynamique",
    ],
    "vmc": [
        "vmc",
    ],
}


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


def search_candidates(model, query, candidate_k=20):
    """Récupère un ensemble plus large de candidats avant reranking."""

    candidates = search_similar(
        model,
        query,
        top_k=candidate_k,
    )

    return candidates


_METADATA_CACHE = None


def reset_metadata_cache():
    """Vide le cache des marques et codes erreur connus."""

    global _METADATA_CACHE
    _METADATA_CACHE = None


def get_known_metadata_values():
    """Récupère les marques et codes erreur connus dans Chroma."""

    global _METADATA_CACHE

    if _METADATA_CACHE is not None:
        return _METADATA_CACHE

    collection = get_vector_collection()

    data = collection.get(
        include=["metadatas"],
    )

    brands = set()
    error_codes = set()

    for metadata in data["metadatas"]:
        marque = metadata.get("marque", "")
        code_erreur = metadata.get("code_erreur", "")

        if marque:
            brands.add(marque)

        if code_erreur:
            error_codes.add(code_erreur)

    _METADATA_CACHE = (brands, error_codes)

    return _METADATA_CACHE


def find_brand(query, brands):
    """Détecte la marque mentionnée dans la question."""

    query_lower = query.lower()

    for brand in sorted(brands, key=len, reverse=True):
        if brand.lower() in query_lower:
            return brand

    return None


def find_error_code(query, error_codes):
    """Détecte un code erreur explicite dans la question."""

    for error_code in sorted(error_codes, key=len, reverse=True):
        has_digit = any(
            character.isdigit()
            for character in error_code
        )

        if has_digit:
            searched_text = query.upper()
            searched_code = error_code.upper()
        else:
            searched_text = query
            searched_code = error_code

        pattern = (
            rf"(?<!\w)"
            rf"{re.escape(searched_code)}"
            rf"(?!\w)"
        )

        if re.search(pattern, searched_text):
            return error_code

    return None


def find_equipment_type(query):
    """Détecte le type d'équipement explicitement mentionné."""

    query_lower = query.lower()

    for equipment_type, aliases in EQUIPMENT_TYPE_ALIASES.items():
        for alias in aliases:
            pattern = (
                rf"(?<!\w)"
                rf"{re.escape(alias.lower())}"
                rf"(?!\w)"
            )

            if re.search(pattern, query_lower):
                return equipment_type

    return None


def detect_query_signals(query):
    """Détecte les signaux métier présents dans une question."""

    brands, error_codes = get_known_metadata_values()

    query_lower = query.lower()

    no_error_code = any(
        expression in query_lower
        for expression in [
            "aucun code erreur",
            "pas de code erreur",
            "sans code erreur",
            "aucun code d'erreur",
            "pas de code d'erreur",
            "sans code d'erreur",
        ]
    )

    detected_brand = find_brand(
        query,
        brands,
    )

    detected_equipment_type = find_equipment_type(
        query,
    )

    if no_error_code:
        detected_error_code = None
    else:
        detected_error_code = find_error_code(
            query,
            error_codes,
        )

    return {
        "marque": detected_brand,
        "code_erreur": detected_error_code,
        "aucun_code_erreur": no_error_code,
        "type_equipement": detected_equipment_type,
    }


def calculate_metadata_bonus(metadata, query_signals):
    """Calcule les bonus métier à partir des métadonnées."""

    brand_bonus = 0.0
    error_code_bonus = 0.0
    no_error_code_bonus = 0.0

    detected_brand = query_signals["marque"]
    detected_error_code = query_signals["code_erreur"]
    no_error_code = query_signals["aucun_code_erreur"]

    document_brand = metadata.get("marque", "")
    document_error_code = metadata.get("code_erreur", "")

    if (
        detected_brand
        and document_brand.lower() == detected_brand.lower()
    ):
        brand_bonus = BRAND_BONUS

    if (
        detected_error_code
        and document_error_code.upper() == detected_error_code.upper()
    ):
        error_code_bonus = ERROR_CODE_BONUS

    if (
        no_error_code
        and document_error_code == ""
    ):
        no_error_code_bonus = NO_ERROR_CODE_BONUS

    total_bonus = (
        brand_bonus
        + error_code_bonus
        + no_error_code_bonus
    )

    return {
        "brand_bonus": brand_bonus,
        "error_code_bonus": error_code_bonus,
        "no_error_code_bonus": no_error_code_bonus,
        "total_bonus": total_bonus,
    }


def rerank_candidates(candidates, query_signals, top_k=5):
    """Rerank les candidats avec le score sémantique et les métadonnées."""

    reranked_results = []

    no_error_code = query_signals["aucun_code_erreur"]
    detected_error_code = query_signals["code_erreur"]
    detected_equipment_type = query_signals["type_equipement"]

    for candidate in candidates:
        document_error_code = candidate["metadata"].get(
            "code_erreur",
            "",
        )

        document_equipment_type = candidate["metadata"].get(
            "type_equipement",
            "",
        )

        # Si le technicien précise explicitement qu'aucun code erreur
        # n'est affiché, les documents associés à un code erreur précis
        # décrivent une situation différente et sont écartés.
        if no_error_code and document_error_code:
            continue

        # Si le technicien mentionne un code erreur précis,
        # les documents associés à un AUTRE code erreur sont écartés.
        # Les documents sans code restent autorisés car ils peuvent
        # contenir une procédure générale ou un symptôme pertinent.
        if (
            detected_error_code
            and document_error_code
            and document_error_code.upper()
            != detected_error_code.upper()
        ):
            continue

        # Si le type d'équipement est explicitement identifiable dans
        # la question, on écarte les documents d'un autre type.
        # La marque n'est volontairement pas utilisée comme filtre :
        # un cas similaire d'une autre marque peut rester pertinent.
        if (
            detected_equipment_type
            and document_equipment_type
            and document_equipment_type != detected_equipment_type
        ):
            continue

        bonuses = calculate_metadata_bonus(
            candidate["metadata"],
            query_signals,
        )

        hybrid_score = (
            candidate["score"]
            + bonuses["total_bonus"]
        )

        reranked_candidate = candidate.copy()

        reranked_candidate["semantic_score"] = candidate["score"]
        reranked_candidate["brand_bonus"] = bonuses["brand_bonus"]
        reranked_candidate["error_code_bonus"] = bonuses[
            "error_code_bonus"
        ]
        reranked_candidate["no_error_code_bonus"] = bonuses[
            "no_error_code_bonus"
        ]
        reranked_candidate["metadata_bonus"] = bonuses["total_bonus"]
        reranked_candidate["hybrid_score"] = hybrid_score

        reranked_results.append(reranked_candidate)

    reranked_results.sort(
        key=lambda result: result["hybrid_score"],
        reverse=True,
    )

    return reranked_results[:top_k]


def search_hybrid(model, query, candidate_k=20, top_k=5):
    """Effectue une recherche vectorielle suivie d'un reranking métier."""

    candidates = search_candidates(
        model,
        query,
        candidate_k=candidate_k,
    )

    query_signals = detect_query_signals(query)

    results = rerank_candidates(
        candidates,
        query_signals,
        top_k=top_k,
    )

    return results


if __name__ == "__main__":
    model = load_embedding_model()

    test_query = (
        "Le client dit que sa PAC Daikin chauffe mais que la maison "
        "reste froide. La PAC ne montre aucun code erreur. Que vérifier ?"
    )

    signals = detect_query_signals(test_query)

    print("--- SIGNAUX DÉTECTÉS ---")
    print(f"Marque : {signals['marque']}")
    print(f"Code erreur : {signals['code_erreur']}")
    print(
        f"Aucun code erreur indiqué : "
        f"{signals['aucun_code_erreur']}"
    )
    print(
        f"Type d'équipement : "
        f"{signals['type_equipement']}"
    )

    results = search_hybrid(
        model,
        test_query,
        candidate_k=20,
        top_k=5,
    )

    print("\n--- TOP 5 APRÈS RERANKING ---")

    for rank, result in enumerate(results, start=1):
        print(
            f"\n{rank}. {result['source_id']} "
            f"| {result['source_type']}"
        )
        print(
            f"Type équipement : "
            f"{result['metadata'].get('type_equipement', '')}"
        )
        print(
            f"Score sémantique : "
            f"{result['semantic_score']:.4f}"
        )
        print(
            f"Bonus marque : "
            f"{result['brand_bonus']:.4f}"
        )
        print(
            f"Bonus code exact : "
            f"{result['error_code_bonus']:.4f}"
        )
        print(
            f"Bonus absence de code : "
            f"{result['no_error_code_bonus']:.4f}"
        )
        print(
            f"Score hybride : "
            f"{result['hybrid_score']:.4f}"
        )