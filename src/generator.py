import json
import re
import socket
import time
import unicodedata

from urllib import error, request

try:
    from src.retriever import (
        detect_query_signals,
        load_embedding_model,
        search_hybrid,
    )
except ModuleNotFoundError:
    from retriever import (
        detect_query_signals,
        load_embedding_model,
        search_hybrid,
    )


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# Le premier appel peut être plus long lorsque le modèle Ollama
# doit être chargé en mémoire.
OLLAMA_TIMEOUT = 600
OLLAMA_MAX_ATTEMPTS = 2
OLLAMA_RETRY_DELAY = 2


def filter_generation_context(question, results):
    """
    Sélectionne les sources les plus cohérentes avant génération.

    - Sans code erreur explicite : conserve le contexte du retriever.
    - Avec un code précis : retire les documents portant un autre code.
    - Si au moins deux documents portent exactement le code demandé,
      utilise uniquement ces documents directement liés au code.
    """

    signals = detect_query_signals(question)

    query_error_code = signals["code_erreur"]

    if not query_error_code:
        return results

    compatible_results = []
    exact_code_results = []

    for result in results:
        document_error_code = result["metadata"].get(
            "code_erreur",
            "",
        )

        if not document_error_code:
            compatible_results.append(result)
            continue

        if (
            document_error_code.upper()
            == query_error_code.upper()
        ):
            compatible_results.append(result)
            exact_code_results.append(result)

    if len(exact_code_results) >= 2:
        return exact_code_results

    return compatible_results


def format_retrieved_context(results):
    """
    Transforme les documents récupérés en blocs clairement séparés.
    """

    context_blocks = []

    for result in results:
        source_id = result["source_id"]
        source_type = result["source_type"]
        metadata = result["metadata"]
        text = result["text"]

        block = (
            f"========== SOURCE {source_id} ==========\n"
            f"source_id: {source_id}\n"
            f"source_type: {source_type}\n"
            f"marque: {metadata.get('marque', '')}\n"
            f"type_equipement: "
            f"{metadata.get('type_equipement', '')}\n"
            f"code_erreur: "
            f"{metadata.get('code_erreur', '')}\n\n"
            f"CONTENU:\n"
            f"{text}\n"
            f"========== FIN SOURCE {source_id} =========="
        )

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def build_structured_prompt(question, results):
    """
    Construit le prompt demandant une réponse JSON structurée.

    Pour chaque affirmation, le modèle doit fournir :
    - le texte de l'affirmation ;
    - un source_id ;
    - une courte preuve copiée exactement depuis cette source.
    """

    context = format_retrieved_context(results)

    allowed_source_ids = [
        result["source_id"]
        for result in results
    ]

    allowed_sources_text = ", ".join(
        allowed_source_ids
    )

    prompt = f"""
Tu es un assistant de maintenance technique COLDORG.

Tu aides un technicien en utilisant EXCLUSIVEMENT les informations
présentes dans le CONTEXTE AUTORISÉ.

Retourne UNIQUEMENT un objet JSON valide.

RÈGLES FONDAMENTALES
--------------------

- Utilise exclusivement les informations présentes dans les documents.
- N'utilise aucune connaissance extérieure.
- N'invente aucune cause, pièce, valeur, mesure, procédure ou solution.
- Une cause possible ne doit jamais être présentée comme une certitude.
- Tu n'es pas obligé d'utiliser toutes les sources.
- Ignore une source si elle n'apporte rien directement à la question.
- Ne transforme pas une opération de maintenance générale en cause de panne
  si le document ne fait pas explicitement ce lien.
- Si une information n'est pas supportée par une source, ne l'ajoute pas.
- Chaque élément doit être court, précis et utile au technicien.

TRAÇABILITÉ OBLIGATOIRE
-----------------------

Pour chaque élément généré, tu dois fournir :

1. "text"
   L'information destinée au technicien.

2. "source_id"
   L'identifiant EXACT du document qui soutient cette information.

3. "evidence"
   Un COURT EXTRAIT COPIÉ EXACTEMENT depuis le CONTENU de cette source.

La preuve "evidence" :

- doit provenir du même document que "source_id" ;
- doit être copiée depuis le document, sans reformulation ;
- doit idéalement contenir entre 4 et 20 mots ;
- doit montrer clairement pourquoi l'affirmation est supportée.

Si tu ne peux pas trouver de preuve exacte dans une source,
N'AJOUTE PAS l'affirmation.

Ne mets jamais de citation dans le champ "text".

Les SEULS source_id autorisés sont :

{allowed_sources_text}

FORMAT JSON OBLIGATOIRE
-----------------------

Retourne exactement un objet avec les clés :

"causes"
"verifications"
"actions"

Chaque clé contient une liste d'objets.

Chaque objet contient exactement :

"text"
"source_id"
"evidence"

Structure :

{{
  "causes": [
    {{
      "text": "cause possible",
      "source_id": "identifiant autorisé",
      "evidence": "extrait exact copié depuis cette source"
    }}
  ],
  "verifications": [
    {{
      "text": "vérification à effectuer",
      "source_id": "identifiant autorisé",
      "evidence": "extrait exact copié depuis cette source"
    }}
  ],
  "actions": [
    {{
      "text": "action ou solution possible",
      "source_id": "identifiant autorisé",
      "evidence": "extrait exact copié depuis cette source"
    }}
  ]
}}

IMPORTANT
---------

- Retourne uniquement le JSON.
- Aucun Markdown.
- Aucun texte avant ou après le JSON.
- Aucun commentaire.
- N'écris pas de section "Sources utilisées".
- Ne mets pas de crochets autour du source_id.
- Une catégorie peut être vide.
- Ne crée jamais une information uniquement pour remplir une catégorie.
- Une affirmation sans preuve exacte doit être omise.

QUESTION DU TECHNICIEN
----------------------

{question}

CONTEXTE AUTORISÉ
-----------------

{context}
""".strip()

    return prompt


def send_ollama_request(payload):
    """Envoie une requête HTTP à Ollama."""

    encoded_payload = json.dumps(
        payload
    ).encode("utf-8")

    http_request = request.Request(
        OLLAMA_URL,
        data=encoded_payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(
        http_request,
        timeout=OLLAMA_TIMEOUT,
    ) as response:
        raw_response = response.read().decode(
            "utf-8"
        )

    try:
        return json.loads(
            raw_response
        )

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Ollama a retourné une réponse HTTP non exploitable."
        ) from exc


def send_ollama_request_with_compatibility(payload):
    """
    Envoie la requête à Ollama.

    Si une ancienne version d'Ollama refuse `format: json`,
    une nouvelle requête est effectuée sans cette option.
    """

    try:
        return send_ollama_request(
            payload
        )

    except error.HTTPError as exc:
        if (
            exc.code == 400
            and "format" in payload
        ):
            fallback_payload = payload.copy()

            fallback_payload.pop(
                "format",
                None,
            )

            return send_ollama_request(
                fallback_payload
            )

        raise


def parse_json_response(raw_text):
    """
    Transforme la sortie du modèle en objet Python.

    Le nettoyage permet également de gérer un éventuel bloc
    ```json ... ``` ajouté malgré les instructions.
    """

    cleaned_text = raw_text.strip()

    cleaned_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    cleaned_text = re.sub(
        r"\s*```$",
        "",
        cleaned_text,
    )

    try:
        parsed = json.loads(
            cleaned_text
        )

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        cleaned_text,
        flags=re.DOTALL,
    )

    if match:
        try:
            parsed = json.loads(
                match.group(0)
            )

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        "Ollama n'a pas retourné un JSON exploitable."
    )


def generate_structured_with_ollama(prompt):
    """
    Génère une réponse JSON structurée.

    Un deuxième essai est effectué en cas de timeout,
    problème réseau ou JSON non exploitable.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": "10m",
        "options": {
            "temperature": 0.0,
            "num_predict": 1200,
        },
    }

    last_exception = None

    for attempt in range(
        1,
        OLLAMA_MAX_ATTEMPTS + 1,
    ):
        try:
            response_data = (
                send_ollama_request_with_compatibility(
                    payload
                )
            )

            raw_response = response_data.get(
                "response",
                "",
            )

            if not raw_response.strip():
                raise RuntimeError(
                    "Ollama a retourné une réponse vide."
                )

            return parse_json_response(
                raw_response
            )

        except (
            error.URLError,
            TimeoutError,
            socket.timeout,
            RuntimeError,
        ) as exc:
            last_exception = exc

            if attempt < OLLAMA_MAX_ATTEMPTS:
                time.sleep(
                    OLLAMA_RETRY_DELAY
                )

    raise RuntimeError(
        "Impossible d'obtenir une réponse JSON exploitable "
        "après plusieurs tentatives avec Ollama."
    ) from last_exception


def normalize_source_id(value):
    """Nettoie un source_id renvoyé par le modèle."""

    if value is None:
        return ""

    source_id = str(
        value
    ).strip()

    source_id = source_id.strip(
        "`"
    )

    if (
        source_id.startswith("[")
        and source_id.endswith("]")
    ):
        source_id = source_id[
            1:-1
        ].strip()

    return source_id


def normalize_for_match(text):
    """
    Normalise un texte afin de comparer une preuve au document.

    Les accents, la casse et les différences d'espaces ou de
    ponctuation ne bloquent pas la comparaison.
    """

    normalized_text = unicodedata.normalize(
        "NFKD",
        str(text or ""),
    )

    normalized_text = "".join(
        character
        for character in normalized_text
        if not unicodedata.combining(
            character
        )
    )

    normalized_text = normalized_text.lower()

    normalized_text = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized_text,
    )

    normalized_text = re.sub(
        r"\s+",
        " ",
        normalized_text,
    )

    return normalized_text.strip()


def evidence_is_supported(
    evidence,
    source_text,
):
    """
    Vérifie qu'une preuve existe réellement dans le document annoncé.

    Le modèle doit avoir copié un court extrait du document.
    """

    if not isinstance(
        evidence,
        str,
    ):
        return False

    normalized_evidence = normalize_for_match(
        evidence
    )

    normalized_source = normalize_for_match(
        source_text
    )

    if not normalized_evidence:
        return False

    evidence_words = normalized_evidence.split()

    # Une preuve trop courte comme "gaz" ou "test"
    # n'est pas assez discriminante.
    if len(evidence_words) < 3:
        return False

    return (
        normalized_evidence
        in normalized_source
    )


def remove_embedded_citations(text):
    """
    Retire une éventuelle citation ajoutée directement dans le texte.
    Python reconstruira lui-même les citations finales.
    """

    cleaned_text = re.sub(
        r"\s*\[[A-Za-z0-9_-]+\]",
        "",
        text,
    )

    return cleaned_text.strip()


def extract_source_candidates(item):
    """
    Récupère le ou les identifiants proposés par le modèle.

    Le format normal utilise `source_id`, mais une petite tolérance
    est conservée pour les réponses imparfaites du modèle.
    """

    source_value = item.get(
        "source_id"
    )

    if source_value is None:
        source_value = item.get(
            "source_ids"
        )

    if source_value is None:
        source_value = item.get(
            "sources"
        )

    if isinstance(
        source_value,
        list,
    ):
        return [
            normalize_source_id(
                value
            )
            for value in source_value
        ]

    return [
        normalize_source_id(
            source_value
        )
    ]


def sanitize_items(
    raw_items,
    allowed_source_ids,
    source_text_by_id,
):
    """
    Vérifie chaque affirmation générée.

    Une affirmation n'est conservée que si :
    - son texte est valide ;
    - son source_id est autorisé ;
    - elle possède une preuve ;
    - cette preuve existe réellement dans le document indiqué.
    """

    stats = {
        "malformed": 0,
        "invalid_source": 0,
        "missing_evidence": 0,
        "unsupported_evidence": 0,
    }

    if not isinstance(
        raw_items,
        list,
    ):
        stats["malformed"] += 1

        return [], stats

    allowed_source_ids = set(
        allowed_source_ids
    )

    clean_items = []

    for item in raw_items:
        if not isinstance(
            item,
            dict,
        ):
            stats["malformed"] += 1
            continue

        text = item.get(
            "text",
            "",
        )

        evidence = item.get(
            "evidence",
            "",
        )

        if (
            not isinstance(text, str)
            or not text.strip()
        ):
            stats["malformed"] += 1
            continue

        text = remove_embedded_citations(
            text.strip()
        )

        if (
            not isinstance(evidence, str)
            or not evidence.strip()
        ):
            stats["missing_evidence"] += 1
            continue

        source_candidates = extract_source_candidates(
            item
        )

        authorized_candidates = [
            source_id
            for source_id in source_candidates
            if source_id
            and source_id in allowed_source_ids
        ]

        if not authorized_candidates:
            stats["invalid_source"] += 1
            continue

        selected_source_id = None

        for source_id in authorized_candidates:
            source_text = source_text_by_id.get(
                source_id,
                "",
            )

            if evidence_is_supported(
                evidence,
                source_text,
            ):
                selected_source_id = source_id
                break

        if selected_source_id is None:
            stats["unsupported_evidence"] += 1
            continue

        clean_items.append(
            {
                "text": text,
                "source_id": selected_source_id,
                "evidence": evidence.strip(),
            }
        )

    return clean_items, stats


def merge_stats(*stats_objects):
    """Additionne les statistiques de rejet."""

    merged_stats = {
        "malformed": 0,
        "invalid_source": 0,
        "missing_evidence": 0,
        "unsupported_evidence": 0,
    }

    for stats in stats_objects:
        for key in merged_stats:
            merged_stats[key] += stats.get(
                key,
                0,
            )

    merged_stats["total_dropped"] = sum(
        merged_stats.values()
    )

    return merged_stats


def sanitize_structured_response(
    structured_response,
    allowed_source_ids,
    generation_results,
):
    """
    Nettoie et vérifie les trois catégories générées.
    """

    source_text_by_id = {
        result["source_id"]: result["text"]
        for result in generation_results
    }

    causes, causes_stats = sanitize_items(
        structured_response.get(
            "causes",
            [],
        ),
        allowed_source_ids,
        source_text_by_id,
    )

    verifications, verifications_stats = sanitize_items(
        structured_response.get(
            "verifications",
            [],
        ),
        allowed_source_ids,
        source_text_by_id,
    )

    actions, actions_stats = sanitize_items(
        structured_response.get(
            "actions",
            [],
        ),
        allowed_source_ids,
        source_text_by_id,
    )

    clean_response = {
        "causes": causes,
        "verifications": verifications,
        "actions": actions,
    }

    validation_stats = merge_stats(
        causes_stats,
        verifications_stats,
        actions_stats,
    )

    return (
        clean_response,
        validation_stats,
    )


def render_section(title, items):
    """
    Transforme une catégorie structurée en Markdown.

    Les citations sont ajoutées uniquement par Python.
    """

    lines = [
        f"## {title}",
        "",
    ]

    if not items:
        lines.append(
            "Information non disponible dans les sources fournies."
        )

        return "\n".join(
            lines
        )

    for item in items:
        text = item["text"].strip()

        if (
            text
            and text[-1] not in ".!?"
        ):
            text += "."

        source_id = item[
            "source_id"
        ]

        lines.append(
            f"- {text} [{source_id}]"
        )

    return "\n".join(
        lines
    )


def build_markdown_answer(clean_response):
    """
    Construit entièrement la réponse finale en Python.
    """

    sections = [
        render_section(
            "Causes possibles",
            clean_response["causes"],
        ),
        render_section(
            "Vérifications recommandées",
            clean_response["verifications"],
        ),
        render_section(
            "Actions ou solutions possibles",
            clean_response["actions"],
        ),
    ]

    cited_source_ids = set()

    for category in (
        "causes",
        "verifications",
        "actions",
    ):
        for item in clean_response[
            category
        ]:
            cited_source_ids.add(
                item["source_id"]
            )

    source_lines = [
        "## Sources utilisées",
        "",
    ]

    if cited_source_ids:
        for source_id in sorted(
            cited_source_ids
        ):
            source_lines.append(
                f"- [{source_id}]"
            )

    else:
        source_lines.append(
            "- Aucune source citée."
        )

    sections.append(
        "\n".join(
            source_lines
        )
    )

    return "\n\n".join(
        sections
    )


def extract_cited_source_ids(answer):
    """Extrait les identifiants cités entre crochets."""

    citations = re.findall(
        r"\[([A-Za-z0-9_-]+)\]",
        answer,
    )

    return set(
        citations
    )


def validate_answer_citations(
    answer,
    allowed_source_ids,
):
    """
    Vérifie que toutes les citations finales correspondent
    à des documents réellement présents dans le contexte.
    """

    cited_source_ids = extract_cited_source_ids(
        answer
    )

    allowed_source_ids = set(
        allowed_source_ids
    )

    invalid_source_ids = (
        cited_source_ids
        - allowed_source_ids
    )

    return {
        "cited_source_ids": cited_source_ids,
        "invalid_source_ids": invalid_source_ids,
        "has_citations": bool(
            cited_source_ids
        ),
        "is_valid": (
            bool(cited_source_ids)
            and not invalid_source_ids
        ),
    }


def answer_question(model, question):
    """
    Exécute le pipeline RAG complet.

    Pipeline :
    1. Retrieval hybride
    2. Sélection du contexte
    3. Génération JSON
    4. Vérification du source_id
    5. Vérification de la preuve dans le document
    6. Construction déterministe des citations
    """

    retrieved_results = search_hybrid(
        model,
        question,
        candidate_k=20,
        top_k=5,
    )

    generation_results = filter_generation_context(
        question,
        retrieved_results,
    )

    if not generation_results:
        raise RuntimeError(
            "Aucun document pertinent n'a été trouvé "
            "pour construire la réponse."
        )

    allowed_source_ids = [
        result["source_id"]
        for result in generation_results
    ]

    prompt = build_structured_prompt(
        question,
        generation_results,
    )

    structured_response = (
        generate_structured_with_ollama(
            prompt
        )
    )

    (
        clean_response,
        evidence_validation,
    ) = sanitize_structured_response(
        structured_response,
        allowed_source_ids,
        generation_results,
    )

    answer = build_markdown_answer(
        clean_response
    )

    validation = validate_answer_citations(
        answer,
        allowed_source_ids,
    )

    # Documents réellement transmis au LLM.
    validation[
        "retrieved_results"
    ] = generation_results

    # Informations de debug sur les affirmations rejetées.
    validation[
        "evidence_validation"
    ] = evidence_validation

    return answer, validation


if __name__ == "__main__":
    print(
        "Chargement du modèle d'embeddings..."
    )

    model = load_embedding_model()

    test_question = (
        "Code erreur E133 sur une chaudière Frisquet Prestige "
        "Condensation 25kW. La chaudière ne redémarre pas depuis "
        "ce matin. Quelles sont les causes possibles et comment "
        "diagnostiquer ?"
    )

    print("\nQuestion :")
    print(test_question)

    print(
        "\nGénération de la réponse RAG structurée avec Ollama..."
    )

    answer, validation = answer_question(
        model,
        test_question,
    )

    print(
        "\n--- RÉPONSE DU RAG ---\n"
    )

    print(
        answer
    )

    print(
        "\n--- VALIDATION DES CITATIONS ---"
    )

    print(
        "Sources citées :",
        sorted(
            validation[
                "cited_source_ids"
            ]
        ),
    )

    print(
        "Sources invalides :",
        sorted(
            validation[
                "invalid_source_ids"
            ]
        ),
    )

    print(
        "Citations valides :",
        validation["is_valid"],
    )

    print(
        "Validation des preuves :",
        validation[
            "evidence_validation"
        ],
    )

    print(
        "\n--- DOCUMENTS UTILISÉS COMME CONTEXTE ---"
    )

    for result in validation[
        "retrieved_results"
    ]:
        print(
            f"- {result['source_id']} "
            f"({result['source_type']})"
        )