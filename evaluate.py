import json
from pathlib import Path

from src.retriever import (
    load_embedding_model,
    search_hybrid,
)


QUESTIONS_PATH = Path("data/questions_test.json")

TOP_K = 5
CANDIDATE_K = 20


EXPECTED_SOURCES = {
    1: {
        "INT-001",
        "INT-011",
        "INT-029",
        "frisquet_e133",
    },
    2: {
        "INT-003",
        "atlantic_fuite_eau",
    },
    3: {
        "INT-002",
        "daikin_u4",
    },
    4: {
        "INT-004",
        "INT-023",
        "saunier_f28",
    },
    5: {
        "INT-021",
        "daikin_entretien",
    },
}


def load_test_questions():
    """Charge les questions d'évaluation depuis le fichier JSON."""

    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)

    return questions


def get_question_text(question):
    """Récupère le texte d'une question."""

    if isinstance(question, dict):
        return question["question"]

    return question


def evaluate_retrieval(results, expected_sources):
    """Compare les sources retrouvées aux sources attendues."""

    retrieved_sources = {
        result["source_id"]
        for result in results
    }

    found_sources = expected_sources.intersection(
        retrieved_sources
    )

    return found_sources


if __name__ == "__main__":
    questions = load_test_questions()

    print(f"Nombre de questions chargées : {len(questions)}")

    print("\nChargement du modèle d'embeddings...")
    model = load_embedding_model()
    print("Modèle chargé avec succès.")

    total_expected = 0
    total_found = 0

    for index, question in enumerate(questions, start=1):
        question_text = get_question_text(question)

        print("\n" + "=" * 70)
        print(f"QUESTION {index}")
        print("=" * 70)
        print(question_text)

        results = search_hybrid(
            model,
            question_text,
            candidate_k=CANDIDATE_K,
            top_k=TOP_K,
        )

        expected_sources = EXPECTED_SOURCES[index]

        found_sources = evaluate_retrieval(
            results,
            expected_sources,
        )

        total_expected += len(expected_sources)
        total_found += len(found_sources)

        print(
            f"\n--- TOP {TOP_K} RÉSULTATS HYBRIDES ---"
        )

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. "
                f"{result['source_id']} | "
                f"{result['source_type']} | "
                f"semantic={result['semantic_score']:.4f} | "
                f"bonus={result['metadata_bonus']:.4f} | "
                f"hybrid={result['hybrid_score']:.4f}"
            )

        print(
            f"\nSources attendues retrouvées : "
            f"{len(found_sources)}/{len(expected_sources)}"
        )

        print(
            f"Retrouvées : "
            f"{sorted(found_sources)}"
        )

    recall_at_k = total_found / total_expected

    print("\n" + "=" * 70)
    print("RÉSULTAT GLOBAL DU RETRIEVAL HYBRIDE")
    print("=" * 70)

    print(
        f"Sources attendues retrouvées : "
        f"{total_found}/{total_expected}"
    )

    print(
        f"Recall@{TOP_K} : "
        f"{recall_at_k:.2%}"
    )