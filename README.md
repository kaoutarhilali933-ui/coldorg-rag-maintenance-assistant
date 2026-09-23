# COLDORG RAG Maintenance Assistant

Prototype of a Retrieval-Augmented Generation (RAG) assistant designed to help
maintenance technicians diagnose equipment issues using historical
interventions and technical documentation.

The system retrieves relevant maintenance knowledge, reranks it using business
metadata, and generates a grounded technician-oriented answer with source
citations.

## Status

Functional prototype.

## Main features

- 30 historical maintenance interventions;
- 4 technical sheets;
- 48 indexed knowledge chunks;
- multilingual semantic embeddings;
- persistent vector search with ChromaDB;
- metadata-aware retrieval reranking;
- local answer generation with Llama 3.2 through Ollama;
- source citations in generated answers;
- automatic validation of generated source IDs;
- retrieval and end-to-end evaluation scripts.

## Architecture

```text
User question
     |
     v
Query embedding
     |
     v
Semantic retrieval
Top-20 candidates
     |
     v
Metadata-aware reranking
     |
     v
Top-5 documents
     |
     v
Context filtering
     |
     v
Grounded prompt
     |
     v
Llama 3.2 via Ollama
     |
     v
Technician-oriented answer
with source citations
```

## Project structure

```text
coldorg-rag-maintenance-assistant/
├── data/
│   ├── interventions.json
│   ├── questions_test.json
│   └── docs/
├── results/
│   ├── baseline_results.md
│   ├── evaluation_plan.md
│   ├── hybrid_results.md
│   └── rag_evaluation.md
├── src/
│   ├── generator.py
│   ├── indexer.py
│   ├── ingestion.py
│   ├── rag.py
│   └── retriever.py
├── evaluate.py
├── evaluate_rag.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Chunking strategy

### Historical interventions

The project uses one historical intervention as one chunk.

Each intervention is already a compact business unit containing information
such as:

- equipment;
- brand;
- equipment type;
- error code;
- symptom;
- diagnosis;
- solution;
- replaced parts.

Keeping these fields together avoids separating a symptom from its diagnosis
or corresponding solution.

For this reason, arbitrary fixed-size splitting is not applied to historical
interventions.

### Technical sheets

Technical sheets use a different strategy.

Each sheet is split by meaningful technical section, such as an error code,
maintenance topic, or recurring equipment problem.

Examples include:

- Frisquet: E133, E125, E110, annual maintenance, wear parts;
- Daikin: U4, E7, AH, 7H, maintenance;
- Atlantic: water leak, insufficient cooling, abnormal noise, maintenance;
- Saunier Duval: F28, F20, maintenance, wear parts.

The four technical sheets produce 18 technical chunks.

Combined with the 30 historical interventions, the indexed corpus contains:

**48 records**

## Metadata strategy

Each RAG record contains structured metadata in addition to its textual
content.

Common metadata fields include:

- `source_type`;
- `source_id`;
- `marque`;
- `type_equipement`;
- `code_erreur`;
- `equipement`.

Historical interventions also contain the intervention `date`.

Metadata is kept separately from the embedded text so that it can be used for
reranking, filtering, traceability, and future retrieval improvements.

## Embedding model

The project uses:

```text
intfloat/multilingual-e5-small
```

through Sentence Transformers.

It was selected because it:

- supports French and multilingual content;
- is designed for semantic retrieval;
- remains lightweight enough for a local prototype;
- provides a good balance between retrieval quality and computational cost.

Following the E5 retrieval format:

- documents use the `passage:` prefix;
- user questions use the `query:` prefix.

Embeddings are normalized before similarity comparison.

## Vector database

The project uses ChromaDB as a persistent local vector database.

The local index is stored in:

```text
chroma_db/
```

This directory is excluded from Git because it can be rebuilt from the source
data.

To rebuild the vector index:

```bash
python src/indexer.py
```

The index contains 48 records.

## Baseline retrieval

The initial baseline uses pure semantic vector similarity with a Top-K of 5.

It was evaluated on the five provided test questions.

Baseline result:

```text
Expected sources retrieved: 12 / 13
Recall@5: 92.31%
```

The main limitation appeared on the no-error-code heat-pump question.

The relevant historical intervention `INT-021` was retrieved, but the
complementary technical chunk `daikin_entretien` was outside the Top-5.

## Retrieval improvement

The improved retriever first retrieves a wider semantic candidate pool and
then applies lightweight metadata-aware reranking.

The system retrieves the Top-20 semantic candidates and reranks them using:

```text
Exact error-code match      +0.050
Explicit absence of code    +0.030
Exact brand match           +0.003
```

The brand bonus is intentionally small.

Brand is treated as a preference rather than a strict filter because useful
historical cases may come from another manufacturer.

For example, the no-error-code Daikin question benefits from historical
intervention `INT-021`, which describes a similar symptom on another brand.

### Retrieval results

| Question | Baseline | Improved |
|---|---:|---:|
| Q1 - Frisquet E133 | 4 / 4 | 4 / 4 |
| Q2 - Atlantic water leak | 2 / 2 | 2 / 2 |
| Q3 - Daikin U4 | 2 / 2 | 2 / 2 |
| Q4 - Saunier Duval F28 recurring fault | 3 / 3 | 3 / 3 |
| Q5 - Heat pump without error code | 1 / 2 | 2 / 2 |

Improved result:

```text
Expected sources retrieved: 13 / 13
Recall@5: 100.00%
```

This result applies only to the five provided evaluation questions and should
not be interpreted as proof of perfect retrieval performance on unseen data.

The reranking weights are heuristic and were adjusted using the provided
evaluation questions. They should therefore be validated on a larger,
independent test set before production use.

## Local generation with Ollama

Answer generation runs locally using Llama 3.2 through Ollama.

This avoids requiring a paid cloud LLM API for the prototype.

The generator is instructed to:

- use only information from the retrieved context;
- avoid unsupported technical claims;
- distinguish possible causes from certainties;
- cite exact `source_id` values;
- avoid inventing source IDs;
- prioritize documents directly related to the symptom or error code;
- avoid turning preventive maintenance operations into confirmed failure
  causes.

For questions containing an explicit error code, documents carrying a
different explicit error code are removed from the generation context.

## Citation validation

Generated answers are checked automatically.

The validator extracts citations such as:

```text
[INT-001]
[frisquet_e133]
```

and checks that every cited identifier belongs to the context actually
provided to the LLM.

On the five provided test questions:

```text
Answers with valid source IDs: 5 / 5
```

This validation checks citation identifiers only.

It does not prove that every generated sentence is perfectly supported by the
cited source. A qualitative review of generated answers is still necessary.

## End-to-end evaluation

Run:

```bash
python evaluate_rag.py
```

The script executes:

```text
retrieval
→ metadata-aware reranking
→ context filtering
→ local generation
→ citation validation
```

for the five provided test questions.

The generated evaluation report is stored in:

```text
results/rag_evaluation.md
```

## Installation

### 1. Create a Python virtual environment

Python 3.11 was used during development.

```powershell
python -m venv .venv
```

On Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Ollama and Llama 3.2

Install Ollama, then download the model:

```bash
ollama run llama3.2
```

After the model has been downloaded, Ollama exposes a local API on:

```text
http://localhost:11434
```

No external LLM API key is required.

### 4. Build the vector index

```bash
python src/indexer.py
```

### 5. Evaluate retrieval

```bash
python evaluate.py
```

### 6. Evaluate the complete RAG pipeline

```bash
python evaluate_rag.py
```

A single example can also be executed with:

```bash
python src/generator.py
```

## Current limitations

The prototype intentionally remains small and simple.

Observed limitations include:

- the evaluation dataset contains only five questions;
- heuristic reranking weights were adjusted using the provided evaluation set;
- retrieval may still return technically related but secondary documents;
- a valid citation identifier does not guarantee sentence-level factual
  grounding;
- Llama 3.2 is a small local model and may occasionally overuse retrieved
  information;
- metadata values are currently loaded from Chroma at query time;
- there is no dedicated BM25 or lexical retrieval component;
- there is no production user interface.

These limitations should be addressed before deploying the system in a real
maintenance environment.

## Scaling from 30 to 10,000 interventions

The current architecture can be extended to a larger maintenance history
without fundamentally changing the RAG approach.

For approximately 10,000 interventions, I would consider:

1. **Incremental indexing**  
   Index only new or modified interventions rather than rebuilding the whole
   collection.

2. **Metadata normalization**  
   Maintain controlled values for manufacturers, equipment families, models,
   error codes, dates, and sites.

3. **Cached metadata vocabulary**  
   Avoid loading all known metadata values from the vector database for every
   query.

4. **Semantic + lexical retrieval**  
   Combine dense embeddings with BM25 or another lexical method for exact
   error codes, references, part numbers, and equipment models.

5. **Two-stage retrieval**  
   Retrieve a wider candidate pool and apply a dedicated reranker before
   sending documents to the LLM.

6. **Larger evaluation dataset**  
   Build a test set containing real technician questions, expected sources,
   difficult negative examples, and previously unseen equipment.

7. **Monitoring**  
   Track retrieval quality, unanswered questions, invalid citations, latency,
   and technician feedback.

8. **Production vector infrastructure**  
   For higher volume or concurrency, move from a purely local prototype to a
   server-based or managed vector database.

## Possible future improvements

Potential next steps include:

- BM25 + semantic hybrid search;
- learned reranking;
- structured intent detection;
- stronger sentence-level citation validation;
- automated groundedness evaluation;
- technician feedback loops;
- lightweight web interface;
- support for additional manufacturers and document formats.

## Evaluation summary

```text
Knowledge base:
30 historical interventions
18 technical chunks
48 indexed records

Baseline retrieval:
Recall@5 = 12/13 = 92.31%

Improved retrieval:
Recall@5 = 13/13 = 100.00%

End-to-end RAG:
5/5 answers used only valid retrieved source IDs
```

These results were measured on the provided evaluation set and are not intended
to claim perfect performance on unseen production data.