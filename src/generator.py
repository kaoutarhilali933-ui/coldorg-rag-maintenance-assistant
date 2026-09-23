import json
import re
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


def filter_generation_context(question, results):
    """
    Élimine les sources clairement incompatibles avec la question.

    Si la question contient un code erreur explicite, un document portant
    un autre code erreur explicite est retiré du contexte.
    """

    signals = detect_query_signals(question)
    query_error_code = signals["code_erreur"]

    if not query_error_code:
        return results

    filtered_results = []

    for result in results:
        document_error_code = result["metadata"].get(
            "code_erreur",
            "",
        )

        if (
            not document_error_code
            or document_error_code.upper() == query_error_code.upper()
        ):
            filtered_results.append(result)

    return filtered_results


def format_retrieved_context(results):
    """Transforme les documents récupérés en contexte lisible."""

    context_blocks = []

    for result in results:
        source_id = result["source_id"]
        source_type = result["source_type"]
        metadata = result["metadata"]
        text = result["text"]

        block = (
            f"[{source_id}]\n"
            f"source_id: {source_id}\n"
            f"source_type: {source_type}\n"
            f"marque: {metadata.get('marque', '')}\n"
            f"code_erreur: {metadata.get('code_erreur', '')}\n"
            f"contenu:\n{text}"
        )

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def build_generation_prompt(question, results):
    """Construit un prompt RAG strict sur les sources et les citations."""

    context = format_retrieved_context(results)

    allowed_source_ids = [
        result["source_id"]
        for result in results
    ]

    allowed_sources_text = ", ".join(
        f"[{source_id}]"
        for source_id in allowed_source_ids
    )

    prompt = f"""
Tu es un assistant de maintenance technique COLDORG.

Tu aides un technicien à diagnostiquer une panne en utilisant
EXCLUSIVEMENT les informations présentes dans le contexte autorisé.

RÈGLES STRICTES
---------------
- Utilise uniquement les informations présentes dans le contexte autorisé.
- N'utilise aucune connaissance extérieure au contexte.
- N'invente aucune cause, mesure, pièce, valeur ou procédure.
- N'ajoute aucune recommandation générale provenant de tes connaissances.
- Si une information n'est pas disponible dans le contexte, dis clairement :
  "Information non disponible dans les sources fournies."
- Une cause possible ne doit jamais être présentée comme une certitude.
- Si la question contient un code erreur précis, reste centré sur ce code.
- Ignore toute source qui ne correspond pas au problème posé.
- Privilégie les sources directement liées au symptôme ou au code erreur
  décrit dans la question.
- Ne transforme jamais une opération de maintenance préventive ou une
  vérification générale en cause de panne, sauf si une source indique
  explicitement que cette anomalie peut provoquer le symptôme décrit.
- Une checklist d'entretien doit être utilisée comme liste de contrôles
  possibles, pas comme liste automatique de causes de panne.
- Si plusieurs sources sont disponibles, privilégie d'abord les interventions
  ou sections techniques qui décrivent directement le même symptôme,
  le même code erreur ou le même type de panne.

RÈGLES DE CITATION
------------------
- Chaque cause technique doit se terminer par au moins une citation.
- Chaque vérification doit se terminer par au moins une citation.
- Chaque action ou solution doit se terminer par au moins une citation.
- Utilise uniquement les source_id exacts autorisés ci-dessous.
- N'utilise jamais "Source 1", "Source 2", etc.
- N'invente jamais un source_id.
- Si une information vient de plusieurs sources, cite toutes les sources utiles.
- La section "Sources utilisées" doit contenir uniquement les source_id
  réellement cités dans la réponse.

Sources autorisées :
{allowed_sources_text}

Exemple de format attendu :
- Une cause possible décrite dans le contexte. [source_id_autorisé]
- Une vérification décrite dans le contexte. [source_id_autorisé]

IMPORTANT :
Les exemples ci-dessus illustrent uniquement le format.
N'utilise jamais le texte "source_id_autorisé" dans la réponse.
Utilise uniquement les identifiants présents dans la liste
"Sources autorisées".

QUESTION DU TECHNICIEN
-----------------------
{question}

CONTEXTE AUTORISÉ
-----------------
{context}

FORMAT DE RÉPONSE
-----------------
## Causes possibles
- Cause possible + citation(s)

## Vérifications recommandées
- Vérification + citation(s)

## Actions ou solutions possibles
- Action possible + citation(s)

## Sources utilisées
- [source_id]
""".strip()

    return prompt


def generate_with_ollama(prompt):
    """Envoie le prompt au modèle local Ollama."""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

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

    try:
        with request.urlopen(
            http_request,
            timeout=300,
        ) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

    except error.URLError as exc:
        raise RuntimeError(
            "Impossible de contacter Ollama. "
            "Vérifie que l'application Ollama est lancée."
        ) from exc

    return response_data["response"].strip()


def extract_cited_source_ids(answer):
    """Extrait les identifiants cités entre crochets."""

    citations = re.findall(
        r"\[([A-Za-z0-9_-]+)\]",
        answer,
    )

    return set(citations)


def validate_answer_citations(
    answer,
    allowed_source_ids,
):
    """
    Vérifie que les citations générées correspondent à des sources
    réellement présentes dans le contexte.
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
        "has_citations": bool(cited_source_ids),
        "is_valid": (
            bool(cited_source_ids)
            and not invalid_source_ids
        ),
    }


def answer_question(model, question):
    """Exécute le pipeline RAG complet."""

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

    prompt = build_generation_prompt(
        question,
        generation_results,
    )

    answer = generate_with_ollama(
        prompt
    )

    allowed_source_ids = [
        result["source_id"]
        for result in generation_results
    ]

    validation = validate_answer_citations(
        answer,
        allowed_source_ids,
    )

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
        "\nGénération de la réponse RAG avec Ollama..."
    )

    answer, validation = answer_question(
        model,
        test_question,
    )

    print("\n--- RÉPONSE DU RAG ---\n")
    print(answer)

    print(
        "\n--- VALIDATION DES CITATIONS ---"
    )

    print(
        "Sources citées :",
        sorted(
            validation["cited_source_ids"]
        ),
    )

    print(
        "Sources invalides :",
        sorted(
            validation["invalid_source_ids"]
        ),
    )

    print(
        "Citations valides :",
        validation["is_valid"],
    )