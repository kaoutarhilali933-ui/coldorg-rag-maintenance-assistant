import re
import unicodedata

import chromadb
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "coldorg_maintenance"

BRAND_BONUS = 0.003
ERROR_CODE_BONUS = 0.05
NO_ERROR_CODE_BONUS = 0.03

# Petit complément lexical au score sémantique.
# Il ne remplace jamais les embeddings.
LEXICAL_BONUS_WEIGHT = 0.02

# Le filtrage lexical n'est activé que lorsqu'un document correspond
# très fortement aux mots de la question.
MIN_LEXICAL_PRUNING_SCORE = 0.80

# Les autres documents doivent conserver au moins 60 % du niveau
# de correspondance lexicale du meilleur document pour être gardés.
LEXICAL_KEEP_RATIO = 0.60

# On conserve toujours au moins deux sources.
MIN_CONTEXT_RESULTS = 2


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


STOPWORDS_FR = {
    "a",
    "ai",
    "au",
    "aux",
    "avec",
    "ce",
    "ces",
    "cet",
    "cette",
    "dans",
    "de",
    "des",
    "du",
    "elle",
    "en",
    "est",
    "et",
    "eux",
    "il",
    "ils",
    "je",
    "la",
    "le",
    "les",
    "leur",
    "leurs",
    "lui",
    "ma",
    "mais",
    "me",
    "mes",
    "moi",
    "mon",
    "ne",
    "nos",
    "notre",
    "nous",
    "on",
    "ou",
    "par",
    "pas",
    "pour",
    "qu",
    "que",
    "qui",
    "sa",
    "se",
    "ses",
    "son",
    "sont",
    "sous",
    "sur",
    "ta",
    "te",
    "tes",
    "toi",
    "ton",
    "tu",
    "un",
    "une",
    "vos",
    "votre",
    "vous",
    "y",
    "plus",
    "depuis",
    "ca",
    "ça",
    "etre",
    "être",
    "peut",
    "quelles",
    "quelle",
    "quels",
    "quel",
    "comment",
    "quoi",
    "dit",
    "client",
    "faire",
    "dois",
    "doit",
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


def normalize_words(text):
    """Transforme un texte en ensemble de mots significatifs."""

    normalized_text = unicodedata.normalize(
        "NFKD",
        text or "",
    )

    normalized_text = normalized_text.encode(
        "ascii",
        "ignore",
    ).decode(
        "ascii",
    )

    words = re.findall(
        r"[a-zA-Z0-9]+",
        normalized_text.lower(),
    )

    meaningful_words = {
        word
        for word in words
        if len(word) >= 3
        and word not in STOPWORDS_FR
    }

    return meaningful_words


def calculate_lexical_score(query, document_text):
    """Mesure le recouvrement lexical entre question et document.

    Le score correspond à la proportion de mots significatifs de la
    question également présents dans le document.

    Ce score complète la recherche vectorielle mais ne la remplace pas.
    """

    query_words = normalize_words(query)
    document_words = normalize_words(document_text)

    if not query_words:
        return 0.0

    common_words = query_words.intersection(
        document_words,
    )

    return len(common_words) / len(query_words)


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
        and document_error_code.upper()
        == detected_error_code.upper()
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


def select_lexically_relevant_results(
    results,
    query_signals,
):
    """Réduit un contexte très bruité lorsqu'un symptôme est très explicite.

    Le filtrage lexical n'est utilisé que :
    - sans code erreur explicite ;
    - lorsqu'il reste plus de deux résultats ;
    - lorsqu'au moins un résultat présente une très forte correspondance
      lexicale avec la question.

    Deux résultats sont toujours conservés afin de ne pas rendre le
    retrieval excessivement agressif.
    """

    if len(results) <= MIN_CONTEXT_RESULTS:
        return results

    if query_signals["code_erreur"]:
        return results

    best_lexical_score = max(
        result["lexical_score"]
        for result in results
    )

    if best_lexical_score < MIN_LEXICAL_PRUNING_SCORE:
        return results

    lexical_threshold = (
        best_lexical_score
        * LEXICAL_KEEP_RATIO
    )

    selected_results = list(
        results[:MIN_CONTEXT_RESULTS]
    )

    selected_source_ids = {
        result["source_id"]
        for result in selected_results
    }

    for result in results[MIN_CONTEXT_RESULTS:]:
        if (
            result["lexical_score"] >= lexical_threshold
            and result["source_id"] not in selected_source_ids
        ):
            selected_results.append(result)
            selected_source_ids.add(
                result["source_id"]
            )

    return selected_results


def rerank_candidates(
    candidates,
    query,
    query_signals,
    top_k=5,
):
    """Rerank les candidats avec sémantique, métadonnées et lexical."""

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
        # n'est affiché, les documents associés à un code précis
        # décrivent une situation différente et sont écartés.
        if no_error_code and document_error_code:
            continue

        # Si le technicien mentionne un code erreur précis,
        # les documents associés à un autre code sont écartés.
        if (
            detected_error_code
            and document_error_code
            and document_error_code.upper()
            != detected_error_code.upper()
        ):
            continue

        # Si le type d'équipement est explicitement identifiable,
        # on écarte les documents d'un autre type.
        # La marque n'est volontairement pas un filtre strict.
        if (
            detected_equipment_type
            and document_equipment_type
            and document_equipment_type
            != detected_equipment_type
        ):
            continue

        bonuses = calculate_metadata_bonus(
            candidate["metadata"],
            query_signals,
        )

        lexical_score = calculate_lexical_score(
            query,
            candidate["text"],
        )

        lexical_bonus = (
            lexical_score
            * LEXICAL_BONUS_WEIGHT
        )

        hybrid_score = (
            candidate["score"]
            + bonuses["total_bonus"]
            + lexical_bonus
        )

        reranked_candidate = candidate.copy()

        reranked_candidate["semantic_score"] = candidate["score"]

        reranked_candidate["brand_bonus"] = bonuses[
            "brand_bonus"
        ]

        reranked_candidate["error_code_bonus"] = bonuses[
            "error_code_bonus"
        ]

        reranked_candidate["no_error_code_bonus"] = bonuses[
            "no_error_code_bonus"
        ]

        reranked_candidate["metadata_bonus"] = bonuses[
            "total_bonus"
        ]

        reranked_candidate["lexical_score"] = lexical_score
        reranked_candidate["lexical_bonus"] = lexical_bonus
        reranked_candidate["hybrid_score"] = hybrid_score

        reranked_results.append(
            reranked_candidate
        )

    reranked_results.sort(
        key=lambda result: result["hybrid_score"],
        reverse=True,
    )

    top_results = reranked_results[:top_k]

    selected_results = select_lexically_relevant_results(
        top_results,
        query_signals,
    )

    return selected_results


def search_hybrid(model, query, candidate_k=20, top_k=5):
    """Effectue une recherche vectorielle suivie d'un reranking métier."""

    candidates = search_candidates(
        model,
        query,
        candidate_k=candidate_k,
    )

    query_signals = detect_query_signals(
        query,
    )

    results = rerank_candidates(
        candidates,
        query,
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

    signals = detect_query_signals(
        test_query,
    )

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

    print("\n--- RÉSULTATS APRÈS RERANKING ---")

    for rank, result in enumerate(
        results,
        start=1,
    ):
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
            f"Score lexical : "
            f"{result['lexical_score']:.4f}"
        )

        print(
            f"Bonus lexical : "
            f"{result['lexical_bonus']:.4f}"
        )

        print(
            f"Score hybride : "
            f"{result['hybrid_score']:.4f}"
        )