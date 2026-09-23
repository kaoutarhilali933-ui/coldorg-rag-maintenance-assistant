import json
from pathlib import Path

from src.generator import answer_question
from src.retriever import load_embedding_model


QUESTIONS_PATH = Path("data/questions_test.json")
RESULTS_PATH = Path("results/rag_evaluation.md")


def load_test_questions():
    """Charge les questions d'évaluation."""

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    return questions


def get_question_text(question):
    """Récupère le texte d'une question."""

    if isinstance(question, dict):
        return question["question"]

    return question


if __name__ == "__main__":
    questions = load_test_questions()

    print(
        f"Nombre de questions à tester : "
        f"{len(questions)}"
    )

    print("\nChargement du modèle d'embeddings...")

    model = load_embedding_model()

    print("Modèle chargé.")

    valid_answers = 0

    report_lines = [
        "# End-to-end RAG evaluation",
        "",
        "This evaluation runs the complete RAG pipeline:",
        "",
        "1. hybrid retrieval;",
        "2. context filtering;",
        "3. local generation with Llama 3.2 through Ollama;",
        "4. citation validation.",
        "",
    ]

    for index, question in enumerate(
        questions,
        start=1,
    ):
        question_text = get_question_text(question)

        print("\n" + "=" * 70)
        print(f"QUESTION {index}")
        print("=" * 70)

        print(question_text)

        print("\nGénération en cours...")

        try:
            answer, validation = answer_question(
                model,
                question_text,
            )

            if validation["is_valid"]:
                valid_answers += 1

            print("\n--- RÉPONSE ---\n")
            print(answer)

            print("\n--- VALIDATION ---")

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

            report_lines.extend(
                [
                    f"## Question {index}",
                    "",
                    f"**Question:** {question_text}",
                    "",
                    "### Generated answer",
                    "",
                    answer,
                    "",
                    "### Citation validation",
                    "",
                    (
                        "**Cited sources:** "
                        + ", ".join(
                            sorted(
                                validation[
                                    "cited_source_ids"
                                ]
                            )
                        )
                    ),
                    "",
                    (
                        "**Invalid sources:** "
                        + (
                            ", ".join(
                                sorted(
                                    validation[
                                        "invalid_source_ids"
                                    ]
                                )
                            )
                            or "None"
                        )
                    ),
                    "",
                    (
                        "**Citation validation:** "
                        + (
                            "PASS"
                            if validation["is_valid"]
                            else "FAIL"
                        )
                    ),
                    "",
                ]
            )

        except Exception as exc:
            print(
                f"\nErreur sur la question "
                f"{index}: {exc}"
            )

            report_lines.extend(
                [
                    f"## Question {index}",
                    "",
                    f"**Question:** {question_text}",
                    "",
                    f"**Execution error:** {exc}",
                    "",
                ]
            )

    print("\n" + "=" * 70)
    print("RÉSULTAT GLOBAL")
    print("=" * 70)

    print(
        f"Réponses avec citations valides : "
        f"{valid_answers}/{len(questions)}"
    )

    report_lines.extend(
        [
            "## Global citation result",
            "",
            (
                f"Answers with valid source IDs: "
                f"**{valid_answers}/{len(questions)}**"
            ),
            "",
            (
                "Citation validation only checks that cited source IDs "
                "exist in the retrieved context. It does not by itself "
                "prove that every generated statement is fully supported "
                "by the cited source."
            ),
            "",
        ]
    )

    RESULTS_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print(
        f"\nRapport enregistré dans : "
        f"{RESULTS_PATH}"
    )