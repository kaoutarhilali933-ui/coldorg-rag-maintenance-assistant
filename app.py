import streamlit as st

from src.generator import answer_question, extract_cited_source_ids
from src.retriever import load_embedding_model


st.set_page_config(
    page_title="COLDORG Maintenance Assistant",
    page_icon="🔧",
    layout="centered",
)


@st.cache_resource
def get_embedding_model():
    """Charge le modèle une seule fois pour toute la session Streamlit."""
    return load_embedding_model()


st.title("🔧 COLDORG Maintenance Assistant")

st.write(
    """
    Assistant de maintenance basé sur une architecture **RAG**.

    Décrivez le problème rencontré sur l'équipement.
    L'assistant recherche les interventions et fiches techniques pertinentes,
    puis génère une réponse à partir des sources COLDORG.
    """
)

st.info(
    "Le diagnostic proposé est basé uniquement sur les données disponibles "
    "dans la base de connaissances du prototype."
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
        st.warning("Veuillez saisir une question avant de lancer l'analyse.")

    else:
        try:
            with st.spinner(
                "Recherche dans les données COLDORG et génération de la réponse..."
            ):
                model = get_embedding_model()

                answer, validation = answer_question(
                    model,
                    question.strip(),
                )

            st.success("Analyse terminée")

            st.subheader("Réponse")
            st.markdown(answer)

            cited_sources = extract_cited_source_ids(answer)

            st.subheader("Sources citées")

            if cited_sources:
                for source_id in cited_sources:
                    st.code(source_id, language=None)
            else:
                st.write("Aucune source citée.")

            if validation.get("is_valid"):
                st.caption(
                    "✓ Les identifiants de sources cités appartiennent "
                    "au contexte récupéré par le RAG."
                )
            else:
                invalid_sources = validation.get("invalid_sources", [])

                st.warning(
                    "Certaines citations n'ont pas pu être validées : "
                    + ", ".join(invalid_sources)
                )

        except Exception as error:
            st.error("Impossible de générer la réponse.")

            st.write(
                "Vérifiez notamment que l'index Chroma a été construit "
                "et qu'Ollama est lancé avec le modèle `llama3.2`."
            )

            with st.expander("Détail technique"):
                st.code(str(error))


with st.sidebar:
    st.header("À propos")

    st.markdown(
        """
        **Pipeline**

        1. Question du technicien
        2. Embedding multilingue
        3. Recherche vectorielle
        4. Reranking par métadonnées
        5. Sélection du contexte
        6. Génération locale avec Llama 3.2
        7. Validation des citations
        """
    )

    st.divider()

    st.caption(
        "Prototype COLDORG — les réponses doivent rester "
        "interprétées comme une aide au diagnostic."
    )