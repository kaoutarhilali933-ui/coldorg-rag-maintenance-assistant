# COLDORG RAG Maintenance Assistant

Prototype d'assistant IA basé sur une architecture RAG pour aider les techniciens de maintenance à exploiter les interventions historiques et les fiches techniques COLDORG.

## Status

Work in progress.

## Chunking strategy

For historical maintenance interventions, the project uses one intervention as one chunk.

Each intervention is short and already represents a complete business unit containing the equipment, brand, error code, symptom, diagnosis, solution, and replaced parts.

Keeping these fields together avoids separating a symptom from its diagnosis or the corresponding solution.

For this reason, no arbitrary fixed-size splitting, for example every 500 characters, is applied to the intervention dataset.

### Technical sheets

Technical sheets use a different chunking strategy.

Instead of treating an entire technical sheet as one large chunk, each sheet is split by meaningful business section, such as an error code or a maintenance problem.

For example:

- Frisquet: E133, E125, E110, annual maintenance, common wear parts
- Daikin: U4, E7, AH, 7H, recommended maintenance
- Atlantic: water leak, insufficient cooling, abnormal noise, maintenance
- Saunier Duval: F28, F20, annual maintenance, common wear parts

This produces 18 technical chunks from the 4 technical sheets.

Each chunk also keeps contextual information such as the manufacturer, equipment model, and equipment type so that it remains understandable when retrieved independently.

This semantic, business-oriented chunking strategy is preferred over arbitrary fixed-size splitting because it keeps each diagnostic topic and its associated causes and procedures together.
## Metadata strategy

Each RAG record contains structured metadata in addition to its textual content.

The common metadata fields are:

- `source_type`: distinguishes historical interventions from technical sheets
- `source_id`: unique identifier for traceability and source citation
- `marque`: equipment manufacturer
- `type_equipement`: normalized equipment category
- `code_erreur`: error code when available, otherwise an empty string
- `equipement`: equipment or model name

Historical interventions also include the intervention `date`.

Metadata is kept separate from the embedded text so it can later be used for filtering, ranking, traceability, and retrieval improvements.

The final corpus currently contains 48 records:

- 30 historical intervention records
- 18 technical-sheet records
## Embedding model

The prototype uses `intfloat/multilingual-e5-small` through Sentence Transformers.

This model was selected because:

- it supports multilingual content, including French;
- it is designed for semantic retrieval tasks;
- its small size is appropriate for a lightweight local prototype;
- it provides a good balance between retrieval quality and computational cost.

The RAG pipeline transforms both maintenance chunks and the user's question
into numerical vectors. Similar vectors represent semantically similar content,
which allows the retriever to find the most relevant maintenance information.

Following the E5 retrieval format, documents are encoded with the `passage:`
prefix and user questions with the `query:` prefix.
## Vector index

The project uses ChromaDB as a persistent local vector database.

The index is built from the original maintenance data and technical sheets.
Each record stores:

- a unique `source_id`;
- the original chunk text;
- its embedding vector;
- the associated metadata.

The local Chroma database is stored in `chroma_db/`.
This directory is excluded from Git because the index can be rebuilt at any time.

To rebuild the vector index from scratch:

```bash
python src/indexer.py
## Retrieval improvement

The first retrieval baseline used pure semantic vector search with the
`intfloat/multilingual-e5-small` embedding model and ChromaDB.

On the five provided evaluation questions, the baseline retrieved:

**12 / 13 expected sources — Recall@5 = 92.31%**

The main weakness appeared on the question describing a heat pump that was
heating but leaving the house cold without displaying an error code.

The relevant historical intervention (`INT-021`) was retrieved, but the
complementary technical maintenance section (`daikin_entretien`) was outside
the Top-5.

To improve retrieval, a lightweight metadata-aware reranking step was added.

The system now:

1. retrieves the Top-20 candidates using semantic similarity;
2. detects useful business signals in the user query;
3. reranks the candidates using semantic similarity and metadata bonuses.

The current heuristic weights are:

- exact error-code match: `+0.05`;
- explicit absence of an error code: `+0.03`;
- exact brand match: `+0.003`.

The brand bonus is deliberately small. Brand is treated as a preference rather
than a strict filter because useful historical cases may come from another
manufacturer.

For example, on the no-error-code heat-pump question, the relevant
cross-brand intervention `INT-021` remains useful even though the question
mentions Daikin.

After reranking, the evaluation result becomes:

**13 / 13 expected sources — Recall@5 = 100.00%**

| Question | Baseline | Improved retrieval |
|---|---:|---:|
| Q1 - Frisquet E133 | 4 / 4 | 4 / 4 |
| Q2 - Atlantic water leak | 2 / 2 | 2 / 2 |
| Q3 - Daikin U4 | 2 / 2 | 2 / 2 |
| Q4 - Saunier Duval F28 recurring fault | 3 / 3 | 3 / 3 |
| Q5 - Daikin heating without error code | 1 / 2 | 2 / 2 |

The 100% Recall@5 result is measured only on the five provided test questions.
It should not be interpreted as evidence of perfect performance on unseen
production data.
The reranking weights are heuristic and were adjusted based on the provided
evaluation questions. They should therefore be validated on a larger,
independent test set before being used in production.