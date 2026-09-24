import streamlit as st

from src.generator import (
    answer_question,
    extract_cited_source_ids,
)
from src.retriever import load_embedding_model


st.set_page_config(
    page_title="COLDORG Maintenance Assistant",
    page_icon="🔧",
    layout="centered",
)


@st.cache_resource
def get_embedding_model():
    """Charge le modèle une seule fois pour la session Streamlit."""

    return load_embedding_model()


st.title("🔧 COLDORG Maintenance Assistant")

st.write(
    """
    Assistant de maintenance basé sur une architecture **RAG**.

    Décrivez le problème rencontré sur l'équipement.
    L'assistant recherche les interventions et fiches techniques
    pertinentes, puis génère une réponse à partir des sources COLDORG.
    """
)

st.info(
    "Le diagnostic proposé est basé uniquement sur les données "
    "disponibles dans la base de connaissances du prototype."
)


question = st.text_area(
    "Question du technicien",
    placeholder=(
        "Exemple : Code erreur E133 sur une chaudière Frisquet. "
        "La chaudière ne redémarre plus. Que vérifier ?"
    ),
    height=130,
)


analyze_button = st.button(
    "Analyser la panne",
    type="primary",
    use_container_width=True,
)


if analyze_button:
    if not question.strip():
        st.warning(
            "Veuillez saisir une question avant de lancer l'analyse."
        )

    else:
        try:
            with st.spinner(
                "Recherche dans les données COLDORG "
                "et génération de la réponse..."
            ):
                model = get_embedding_model()

                answer, validation = answer_question(
                    model,
                    question.strip(),
                )

            st.success(
                "Analyse terminée"
            )

            # =====================================================
            # Réponse générée
            # =====================================================

            st.subheader(
                "Réponse"
            )

            st.markdown(
                answer
            )

            # =====================================================
            # Documents utilisés comme contexte
            # =====================================================

            retrieved_results = validation.get(
                "retrieved_results",
                [],
            )

            st.subheader(
                "Documents retrouvés"
            )

            if retrieved_results:
                st.caption(
                    f"{len(retrieved_results)} document(s) "
                    "sélectionné(s) comme contexte pour la génération."
                )

                for rank, result in enumerate(
                    retrieved_results,
                    start=1,
                ):
                    source_id = result.get(
                        "source_id",
                        "",
                    )

                    source_type = result.get(
                        "source_type",
                        "",
                    )

                    metadata = result.get(
                        "metadata",
                        {},
                    )

                    hybrid_score = result.get(
                        "hybrid_score"
                    )

                    title = (
                        f"{rank}. {source_id} — {source_type}"
                    )

                    if hybrid_score is not None:
                        title += (
                            f" — score {hybrid_score:.4f}"
                        )

                    with st.expander(
                        title
                    ):
                        st.markdown(
                            f"**Source ID :** `{source_id}`"
                        )

                        st.markdown(
                            f"**Type :** `{source_type}`"
                        )

                        marque = metadata.get(
                            "marque",
                            "",
                        )

                        if marque:
                            st.markdown(
                                f"**Marque :** {marque}"
                            )

                        type_equipement = metadata.get(
                            "type_equipement",
                            "",
                        )

                        if type_equipement:
                            st.markdown(
                                f"**Type d'équipement :** "
                                f"{type_equipement}"
                            )

                        code_erreur = metadata.get(
                            "code_erreur",
                            "",
                        )

                        if code_erreur:
                            st.markdown(
                                f"**Code erreur :** "
                                f"`{code_erreur}`"
                            )

                        st.divider()

                        semantic_score = result.get(
                            "semantic_score"
                        )

                        lexical_score = result.get(
                            "lexical_score"
                        )

                        metadata_bonus = result.get(
                            "metadata_bonus"
                        )

                        if semantic_score is not None:
                            st.write(
                                "Score sémantique : "
                                f"`{semantic_score:.4f}`"
                            )

                        if lexical_score is not None:
                            st.write(
                                "Score lexical : "
                                f"`{lexical_score:.4f}`"
                            )

                        if metadata_bonus is not None:
                            st.write(
                                "Bonus métadonnées : "
                                f"`{metadata_bonus:.4f}`"
                            )

                        if hybrid_score is not None:
                            st.write(
                                "Score hybride : "
                                f"`{hybrid_score:.4f}`"
                            )

                        st.divider()

                        st.markdown(
                            "**Contenu récupéré :**"
                        )

                        st.code(
                            result.get(
                                "text",
                                "",
                            ),
                            language=None,
                        )

            else:
                st.write(
                    "Aucun document n'a été récupéré."
                )

            # =====================================================
            # Sources citées
            # =====================================================

            cited_sources = extract_cited_source_ids(
                answer
            )

            st.subheader(
                "Sources citées"
            )

            if cited_sources:
                for source_id in sorted(
                    cited_sources
                ):
                    st.code(
                        source_id,
                        language=None,
                    )

            else:
                st.write(
                    "Aucune source citée."
                )

            # =====================================================
            # Validation automatique
            # =====================================================

            st.subheader(
                "Validation"
            )

            if validation.get(
                "is_valid"
            ):
                st.success(
                    "Les citations utilisent uniquement des sources "
                    "présentes dans le contexte récupéré."
                )

            else:
                # La bonne clé renvoyée par generator.py est
                # invalid_source_ids.
                invalid_sources = validation.get(
                    "invalid_source_ids",
                    [],
                )

                if invalid_sources:
                    st.warning(
                        "Certaines citations ne correspondent pas "
                        "aux sources autorisées : "
                        + ", ".join(
                            sorted(
                                invalid_sources
                            )
                        )
                    )

                else:
                    st.warning(
                        "Aucune citation valide n'a été détectée."
                    )

            # =====================================================
            # Contrôle des preuves
            # =====================================================

            evidence_validation = validation.get(
                "evidence_validation",
                {},
            )

            if evidence_validation:
                rejected_items = evidence_validation.get(
                    "total_dropped",
                    0,
                )

                with st.expander(
                    "Détails du contrôle de traçabilité"
                ):
                    st.write(
                        "Affirmations rejetées automatiquement : "
                        f"**{rejected_items}**"
                    )

                    st.write(
                        "Source invalide : "
                        f"{evidence_validation.get('invalid_source', 0)}"
                    )

                    st.write(
                        "Preuve absente : "
                        f"{evidence_validation.get('missing_evidence', 0)}"
                    )

                    st.write(
                        "Preuve non retrouvée dans la source : "
                        f"{evidence_validation.get('unsupported_evidence', 0)}"
                    )

                    st.write(
                        "Éléments mal formés : "
                        f"{evidence_validation.get('malformed', 0)}"
                    )

        except Exception as error:
            st.error(
                "Impossible de générer la réponse."
            )

            st.write(
                "Vérifiez que l'index Chroma a été construit "
                "et qu'Ollama est lancé avec le modèle `llama3.2`."
            )

            with st.expander(
                "Détail technique"
            ):
                st.code(
                    str(error)
                )


with st.sidebar:
    st.header(
        "À propos"
    )

    st.markdown(
        """
        **Pipeline RAG**

        1. Question du technicien
        2. Embedding multilingue
        3. Recherche vectorielle
        4. Filtrage métier par métadonnées
        5. Reranking sémantique + lexical
        6. Sélection du contexte
        7. Génération structurée avec Llama 3.2
        8. Vérification des preuves dans les sources
        9. Construction contrôlée des citations
        """
    )

    st.divider()

    st.caption(
        "Prototype COLDORG — les réponses constituent "
        "une aide au diagnostic basée sur les données disponibles."
    )