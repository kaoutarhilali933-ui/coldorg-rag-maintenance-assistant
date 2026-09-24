# COLDORG RAG Maintenance Assistant

Prototype of a Retrieval-Augmented Generation (RAG) assistant designed to help
maintenance technicians diagnose equipment issues using historical maintenance
interventions and technical documentation.

The system retrieves relevant maintenance knowledge, combines semantic,
lexical, and business signals, and generates a technician-oriented answer
grounded in the selected COLDORG sources.

The prototype also validates generated source references and supporting
evidence before displaying technical claims.

---

## Status

Functional end-to-end RAG prototype.

The current version includes:

- data ingestion and domain-aware chunking;
- multilingual embeddings;
- persistent ChromaDB vector storage;
- semantic retrieval;
- metadata-aware filtering and reranking;
- lightweight lexical relevance scoring;
- local generation with Llama 3.2 through Ollama;
- structured JSON generation;
- source ID validation;
- evidence validation;
- deterministic citation rendering;
- retrieval evaluation;
- end-to-end RAG evaluation;
- Streamlit interface with retrieved-document inspection.

---

# Quick start for reviewer

This section contains the minimum steps required to run the complete prototype.

## Prerequisites

The project was developed with:

```text
Python 3.11
Ollama
Llama 3.2
```

Ollama must be installed locally before running the generation pipeline.

---

## 1. Clone the repository

```bash
git clone https://github.com/kaoutarhilali933-ui/coldorg-rag-maintenance-assistant.git
cd coldorg-rag-maintenance-assistant
```

---

## 2. Create a virtual environment

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows Git Bash

```bash
py -3.11 -m venv .venv
source .venv/Scripts/activate
```

After activation, the terminal should display:

```text
(.venv)
```

---

## 3. Install the Python dependencies

```bash
python -m pip install -r requirements.txt
```

---

## 4. Install the local LLM

Make sure Ollama is installed.

Download Llama 3.2:

```bash
ollama pull llama3.2
```

Check that the model is available:

```bash
ollama list
```

The list should contain:

```text
llama3.2
```

If Ollama is not already running, it can be started with:

```bash
ollama serve
```

Depending on the operating system, the Ollama desktop application may already
start the service automatically.

The local API is normally available at:

```text
http://localhost:11434
```

No paid cloud LLM API key is required.

---

## 5. Build the vector index

Run:

```bash
python src/indexer.py
```

The expected index size is:

```text
48 records
```

A successful execution should show approximately:

```text
Nombre de records à indexer : 48
Nombre d'éléments après indexation : 48
```

This creates the local:

```text
chroma_db/
```

directory.

The ChromaDB index is intentionally excluded from Git because it can be rebuilt
from the source data.

---

## 6. Start the Streamlit interface

Run:

```bash
streamlit run app.py
```

or:

```bash
python -m streamlit run app.py
```

Streamlit normally opens the browser automatically.

Otherwise open:

```text
http://localhost:8501
```

---

## 7. What should I type in the interface?

The main input area is called:

```text
Question du technicien
```

Enter a maintenance problem in natural language, then click:

```text
Analyser la panne
```

### Recommended first example

Copy and paste this question into the interface:

```text
J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?
```

Then click:

```text
Analyser la panne
```

The application should display:

- a generated maintenance answer;
- possible causes;
- recommended checks;
- possible actions or solutions;
- cited source identifiers;
- retrieved documents;
- semantic scores;
- lexical scores;
- metadata bonuses;
- hybrid scores;
- citation validation;
- evidence-validation information.

---

## Other questions that can be tested

### Test question 1 — Frisquet E133

```text
Code erreur E133 sur une chaudière Frisquet Prestige Condensation 25kW. La chaudière ne redémarre pas depuis ce matin. Quelles sont les causes possibles et comment diagnostiquer ?
```

### Test question 2 — Atlantic water leak

```text
J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?
```

### Test question 3 — Daikin U4

```text
Ma pompe à chaleur Daikin Altherma affiche le code U4, plus de chauffage ni d'eau chaude. Quelles pièces dois-je prévoir ?
```

### Test question 4 — Saunier Duval F28

```text
Un client a une chaudière Saunier Duval ThemaPlus Condens en panne avec le code F28 pour la troisième fois ce mois. Qu'est-ce qui peut expliquer un défaut récurrent ?
```

### Test question 5 — Daikin without error code

```text
Le client dit que sa PAC Daikin chauffe mais que la maison reste froide. La PAC ne montre aucun code erreur. Que vérifier ?
```

These are the five supplied evaluation questions used by the evaluation
scripts.

---

# Dataset

The supplied knowledge base contains:

- 30 historical maintenance interventions;
- 4 technical documentation files;
- 18 technical-document chunks;
- 48 indexed records in total;
- 5 evaluation questions.

```text
30 historical interventions
+ 18 technical chunks
= 48 indexed records
```

---

# Architecture

```text
Technician question
        |
        v
Query embedding
(multilingual-e5-small)
        |
        v
Semantic retrieval
Top-20 candidates
        |
        v
Query signal detection
- manufacturer
- error code
- explicit absence of error code
- equipment type
        |
        v
Business filtering
- incompatible error codes
- incompatible equipment types
        |
        v
Hybrid reranking
- semantic similarity
- metadata bonuses
- lexical relevance
        |
        v
Relevant context selection
        |
        v
Generation context filtering
        |
        v
Llama 3.2 via Ollama
Structured JSON generation
        |
        v
Source ID validation
        |
        v
Evidence validation
against selected source text
        |
        v
Deterministic Markdown rendering
with controlled citations
        |
        v
Technician-oriented answer
```

---

# Simplified project structure

```text
coldorg-rag-maintenance-assistant/
├── app.py
├── data/
│   ├── interventions.json
│   ├── questions_test.json
│   └── docs/
│       ├── fiche_atlantic_climatisation.txt
│       ├── fiche_daikin_altherma.txt
│       ├── fiche_frisquet_prestige.txt
│       └── fiche_saunier_duval_themaplus.txt
├── results/
│   ├── baseline_results.md
│   ├── evaluation_plan.md
│   ├── hybrid_results.md
│   └── rag_evaluation.md
├── src/
│   ├── generator.py
│   ├── indexer.py
│   ├── ingestion.py
│   └── retriever.py
├── evaluate.py
├── evaluate_rag.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Data preparation

## Chunking strategy

Two different chunking strategies are used because historical interventions
and technical sheets have different structures.

---

## Historical interventions

Each historical intervention is kept as one chunk.

An intervention already represents a coherent maintenance event containing
information such as:

- equipment;
- manufacturer;
- equipment type;
- error code;
- symptom;
- diagnosis;
- solution;
- replaced parts.

Keeping the complete intervention together preserves the relationship between
the symptom, diagnosis, and corrective action.

For this reason, arbitrary fixed-size splitting is not applied to historical
intervention records.

---

## Technical sheets

Technical documentation is split by meaningful technical section rather than
by fixed character or token counts.

Examples include:

- Frisquet: E133, E125, E110, maintenance, wear parts;
- Daikin: U4, E7, AH, 7H, maintenance;
- Atlantic: water leak, insufficient cooling, abnormal noise, maintenance;
- Saunier Duval: F28, F20, maintenance, wear parts.

The four technical sheets produce:

```text
18 technical chunks
```

Together with the 30 historical interventions:

```text
48 indexed records
```

---

# Metadata strategy

Each record contains structured metadata in addition to its textual content.

Main metadata fields include:

```text
source_type
source_id
marque
type_equipement
code_erreur
equipement
```

Historical interventions also contain their date.

Metadata is used for:

- traceability;
- manufacturer detection;
- error-code filtering;
- equipment-type filtering;
- reranking;
- generation context selection.

The known manufacturer and error-code vocabulary is cached after its first
load so that the application does not repeatedly retrieve the same metadata
from ChromaDB during each query.

---

# Embedding model

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

Following the E5 retrieval convention:

```text
Documents: passage: ...
Queries:   query: ...
```

Embeddings are normalized before similarity comparison.

---

# Vector database

The project uses ChromaDB as a persistent local vector database.

The index is stored locally in:

```text
chroma_db/
```

This directory is excluded from Git because it can be reconstructed from the
source files.

To rebuild the vector database:

```bash
python src/indexer.py
```

Expected number of indexed records:

```text
48
```

---

# Retrieval strategy

## Baseline retrieval

The initial baseline used pure semantic vector similarity with a Top-K of 5.

The baseline was evaluated on the five supplied questions.

Result:

```text
Expected sources retrieved: 12 / 13
Recall@5: 92.31%
```

The main limitation appeared on the heat-pump question without an explicit
error code.

---

# Improved retrieval

The final retriever first retrieves a wider semantic candidate pool:

```text
Top-20 semantic candidates
```

Then it applies several domain-aware improvements before returning the final
context.

---

## Query signal detection

The system detects useful information directly from the technician question.

Signals include:

- manufacturer;
- explicit error code;
- explicit absence of error code;
- equipment type.

Examples:

```text
Frisquet
Daikin
Atlantic
Saunier Duval

E133
U4
F28

aucun code erreur

pompe à chaleur
climatiseur
chaudière
```

These signals complement semantic similarity.

---

# Business filtering

The retrieval pipeline removes clearly incompatible documents.

### Explicit absence of error code

If the technician explicitly says that no error code is displayed, documents
associated with a precise error code are removed.

For example:

```text
La PAC ne montre aucun code erreur.
```

This prevents coded-fault documentation from polluting a symptom-only context.

### Explicit error code

If the technician mentions a precise code, documents associated with another
explicit error code are excluded.

A document without an error code can still remain if it contains useful general
information.

### Equipment type

If the equipment category is explicitly identifiable, incompatible equipment
types are excluded.

For example, a climatiseur question should not retrieve a boiler document.

### Manufacturer

Manufacturer is deliberately not used as a strict filter.

A historical intervention from another manufacturer may still describe a
technically similar symptom and remain useful.

---

# Metadata bonuses

The reranker applies small business-aware bonuses.

```text
Exact error-code match       +0.050
Explicit absence of code     +0.030
Exact brand match            +0.003
```

The manufacturer bonus is intentionally much smaller than the error-code
bonus.

Semantic relevance therefore remains dominant.

These weights are heuristic and were developed using the supplied evaluation
questions.

They should be validated on a larger independent dataset before production
deployment.

---

# Lexical relevance

A lightweight lexical score complements dense semantic retrieval.

The retriever compares meaningful terms in the technician question with the
candidate document.

The final score combines:

```text
semantic similarity
+ metadata bonus
+ lexical bonus
```

This improves precision on symptom-oriented questions where exact vocabulary
is particularly informative.

For example:

```text
fuite
eau
mur
condensat
```

is particularly helpful for the Atlantic water-leak question.

For strongly explicit symptom questions, the system can also remove clearly
secondary results from the final context.

A minimum number of results is preserved so that context filtering does not
become overly aggressive.

This lexical component is intentionally lightweight.

It is not a complete BM25 implementation.

---

# Retrieval evaluation

Run:

```bash
python evaluate.py
```

Current result on the supplied evaluation set:

```text
Sources attendues retrouvées : 13/13
Documents retournés au total : 18
Recall@5 : 100.00%
Précision du contexte retourné : 72.22%
F1 retrieval : 83.87%
```

Per-question results:

| Question | Expected sources retrieved | Context precision |
|---|---:|---:|
| Q1 - Frisquet E133 | 4 / 4 | 80% |
| Q2 - Atlantic water leak | 2 / 2 | 100% |
| Q3 - Daikin U4 | 2 / 2 | 50% |
| Q4 - Saunier Duval F28 recurring fault | 3 / 3 | 60% |
| Q5 - Heat pump without error code | 2 / 2 | 100% |

The expected-source list is manually annotated and should not be considered
exhaustive ground truth.

For that reason, context precision is primarily used to compare different
retrieval versions.

A document counted as an additional result can still contain technically useful
information even when it is not part of the manually annotated expected set.

The evaluation contains only five questions.

Therefore:

```text
Recall@5 = 100%
```

does not mean that the retriever is expected to achieve perfect performance on
unseen production data.

---

# Local generation with Ollama

Answer generation runs locally using:

```text
Llama 3.2
```

through Ollama.

This avoids requiring a paid cloud LLM API.

The generator receives only the context selected by the retrieval pipeline.

For questions containing an explicit error code, the generation context can be
further restricted toward documents directly associated with that error code
when enough exact-code documents are available.

---

# Why structured generation?

An early version of the prototype asked the LLM to directly generate the final
Markdown answer and citations.

This created two possible problems:

- a valid source identifier could be associated with the wrong technical
  statement;
- citation formatting depended entirely on the LLM following the prompt.

The final architecture separates content generation from citation rendering.

Llama 3.2 is asked to generate structured JSON.

Each technical statement contains:

```json
{
  "text": "technical statement",
  "source_id": "source identifier",
  "evidence": "supporting excerpt from the source"
}
```

The three output categories are:

```text
causes
verifications
actions
```

Python validates this structure before creating the final answer.

---

# Grounding and citation validation

The final generation pipeline applies multiple validation steps.

---

## 1. Source ID validation

Every generated:

```text
source_id
```

must belong to the documents actually provided to the LLM.

If the LLM proposes a source identifier that is not part of the allowed
generation context, the corresponding statement is rejected.

This prevents an invented identifier from reaching the final answer.

---

## 2. Evidence validation

Each generated statement must also include:

```text
evidence
```

The evidence must be supported by the source referenced by `source_id`.

The validator normalizes:

- capitalization;
- accents;
- whitespace;
- punctuation.

It then accepts either:

- a normalized direct match;
- or a strong lexical overlap with shared consecutive terms.

This allows small reformulations while still checking that the claimed
supporting information is present in the selected document.

A generated statement can be rejected for:

```text
invalid source
missing evidence
unsupported evidence
malformed structure
```

The objective is to favor groundedness and traceability over maximum answer
length.

---

## 3. Deterministic citation rendering

The LLM does not create the final Markdown citations.

After validation, Python constructs them.

Example:

```text
- Bac de condensat obstrué. [INT-003]
```

Python also automatically builds:

```text
## Sources utilisées
```

from the validated source identifiers.

This means that the final citation syntax is controlled by application code
instead of depending on free-form LLM output.

---

# End-to-end RAG evaluation

Run:

```bash
python evaluate_rag.py
```

This executes:

```text
retrieval
→ business filtering
→ hybrid reranking
→ context selection
→ structured generation
→ source validation
→ evidence validation
→ deterministic citation rendering
```

for the five supplied test questions.

Current result:

```text
Réponses avec citations valides : 5/5
```

Final invalid source identifiers:

```text
0
```

The complete generated report is stored in:

```text
results/rag_evaluation.md
```

This result means that the final displayed source identifiers belong to the
authorized generation context.

Evidence validation additionally reduces incorrect source attribution.

However, this lightweight validation is not a formal natural-language
entailment proof.

---

# Running a single RAG example

Instead of evaluating all five questions, a single built-in example can be run
with:

```bash
python src/generator.py
```

This displays:

- the generated answer;
- cited source identifiers;
- citation validation;
- evidence-validation statistics;
- documents used as generation context.

---

# Streamlit interface

Start the application with:

```bash
streamlit run app.py
```

or:

```bash
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## How to use the interface

### Step 1

Locate:

```text
Question du technicien
```

### Step 2

Type or paste a maintenance question.

For example:

```text
J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?
```

### Step 3

Click:

```text
Analyser la panne
```

### Step 4

Wait for the pipeline to complete.

The first request can take longer because:

- the embedding model must be loaded into memory;
- the local Llama model may need to be loaded by Ollama.

Later requests are generally faster.

---

## Information displayed by Streamlit

The interface displays:

### Generated answer

```text
Causes possibles
Vérifications recommandées
Actions ou solutions possibles
Sources utilisées
```

### Retrieved documents

For each selected document, the interface can display:

```text
source_id
source type
manufacturer
equipment type
error code
semantic score
lexical score
metadata bonus
hybrid score
original retrieved content
```

### Cited sources

The source IDs included in the final answer are displayed separately.

### Citation validation

The application indicates whether all final citations belong to the retrieved
generation context.

### Evidence-validation details

The interface can also display how many generated statements were rejected
because of:

```text
invalid source
missing evidence
unsupported evidence
malformed output
```

---

# Example Streamlit workflow

Input:

```text
J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?
```

Relevant retrieved documents include:

```text
INT-003
atlantic_fuite_eau
```

Example final output:

```text
## Causes possibles

- Bac de condensat obstrué. [INT-003]
- Tuyau d'évacuation bouché ou mal penté. [INT-003]

## Sources utilisées

- [INT-003]
```

The user can then expand the retrieved-document sections to inspect the
original COLDORG information behind the response.

---

# Optional code sanity check

Before launching the application, Python syntax can be checked with:

```bash
python -m py_compile src/retriever.py
python -m py_compile src/generator.py
python -m py_compile evaluate.py
python -m py_compile evaluate_rag.py
python -m py_compile app.py
```

If the commands return without an error message, the Python files passed the
syntax check.

---

# Complete validation workflow

For a complete local validation:

```bash
python src/indexer.py
python evaluate.py
python evaluate_rag.py
streamlit run app.py
```

Expected retrieval result:

```text
Sources attendues retrouvées : 13/13
Recall@5 : 100.00%
Précision du contexte retourné : 72.22%
F1 retrieval : 83.87%
```

Expected end-to-end citation result:

```text
Réponses avec citations valides : 5/5
```

---

# Why RAG instead of fine-tuning?

Fine-tuning was considered as a possible extension but was not necessary for
the main objective of this prototype.

The principal requirement is access to precise, traceable maintenance
information that can evolve over time.

RAG is more appropriate for this use case because:

- technical knowledge remains stored in explicit documents;
- retrieved sources can be shown to the technician;
- new maintenance interventions can be added without retraining the LLM;
- technical documentation can be updated independently from the model;
- the available dataset is small for reliable fine-tuning;
- traceability is more important here than changing the internal knowledge of
  the language model.

Fine-tuning could become useful later for:

- response style;
- output consistency;
- domain-specific instruction following;
- specialized technician vocabulary;
- task-specific behavior.

It would be more justified with a larger collection of validated
question/answer examples.

---

# Current limitations

This project intentionally remains a small technical prototype.

Main limitations include:

- only five evaluation questions are available;
- expected retrieval sources were manually annotated;
- the expected-source set is not necessarily exhaustive;
- metadata and lexical reranking weights are heuristic;
- some retrieval rules were developed using the supplied evaluation questions;
- retrieval therefore needs validation on an independent dataset;
- lexical relevance is lightweight and is not a complete BM25 implementation;
- evidence validation uses lexical matching rather than a dedicated
  natural-language-inference model;
- conservative evidence validation can reject a useful statement when the LLM
  reformulates its evidence too strongly;
- Llama 3.2 is a relatively small local language model;
- generated content may vary slightly between executions;
- the first local generation can have noticeable latency;
- the Streamlit application is a prototype and is not intended as a production
  application.

The current design intentionally prioritizes:

```text
groundedness
traceability
source control
```

over maximum answer completeness.

---

# Scaling from 30 to 10,000 interventions

The current architecture can be extended to a larger maintenance history
without fundamentally changing the RAG approach.

For approximately 10,000 interventions, the following improvements would be
considered.

---

## 1. Incremental indexing

Index only new or modified maintenance interventions instead of rebuilding the
whole collection.

---

## 2. Metadata normalization

Maintain controlled values for:

- manufacturers;
- equipment families;
- equipment models;
- error codes;
- sites;
- dates.

This would make filtering and analytics more reliable.

---

## 3. Cached metadata vocabulary

Keep manufacturer, equipment, and error-code vocabularies in memory or in a
dedicated metadata service.

---

## 4. Dense + BM25 hybrid retrieval

Combine semantic embeddings with a real lexical search engine such as BM25.

BM25 would be particularly useful for:

- exact error codes;
- spare-part references;
- equipment models;
- serial references;
- highly specific technical vocabulary.

---

## 5. Dedicated reranking model

Retrieve a wider candidate pool and apply a dedicated cross-encoder or learned
reranker before generation.

This would provide a stronger second-stage relevance model than heuristic
bonuses alone.

---

## 6. Larger independent evaluation dataset

Build a dedicated test set containing:

- real technician questions;
- expected relevant sources;
- difficult negative examples;
- unseen equipment;
- incomplete questions;
- no-error-code cases;
- misleading metadata cases.

---

## 7. Stronger groundedness validation

Add a dedicated entailment model or another semantic verification mechanism to
check whether every final statement is supported by its cited source.

---

## 8. Monitoring

Track:

- retrieval recall;
- context precision;
- answer latency;
- unanswered questions;
- rejected generated statements;
- invalid citations;
- technician feedback.

---

## 9. Production vector infrastructure

For higher volume or concurrency, move from the purely local ChromaDB
prototype to a server-based or managed vector infrastructure.

---

# Possible future improvements

Potential next steps include:

- BM25 + dense hybrid retrieval;
- learned reranking;
- larger independent evaluation datasets;
- stronger sentence-level entailment validation;
- automated groundedness evaluation;
- technician feedback loops;
- latency monitoring;
- support for additional equipment manufacturers;
- support for more technical-document formats;
- multi-turn technician conversations;
- optional fine-tuning when enough labelled examples become available;
- authentication and user management;
- production deployment and monitoring.

---

# Evaluation summary

```text
Knowledge base
--------------
Historical interventions: 30
Technical sheets: 4
Technical chunks: 18
Indexed records: 48


Baseline retrieval
------------------
Expected sources retrieved: 12 / 13
Recall@5: 92.31%


Final retrieval
---------------
Expected sources retrieved: 13 / 13
Recall@5: 100.00%
Context precision: 72.22%
Retrieval F1: 83.87%


End-to-end RAG
--------------
Evaluation questions: 5
Answers with valid citations: 5 / 5
Invalid final source IDs: 0


Interface
---------
Streamlit prototype tested successfully
Retrieved documents can be inspected
Semantic and lexical scores can be inspected
Metadata and hybrid scores can be inspected
Citation validation is displayed
Evidence-validation statistics are displayed
```

These results were measured on the supplied evaluation set only.

They should not be interpreted as evidence of perfect performance on unseen
production data.

---

# Design choices summary

The main design decisions of this prototype are:

1. preserve complete historical interventions as coherent chunks;
2. split technical documentation by meaningful technical section;
3. use multilingual E5 embeddings for French technician questions;
4. use ChromaDB for lightweight persistent local vector retrieval;
5. retrieve a larger candidate pool before reranking;
6. combine semantic, metadata, and lexical signals;
7. keep manufacturer matching as a preference instead of a strict filter;
8. reject incompatible explicit error codes;
9. reject incompatible equipment categories;
10. handle explicit absence of an error code;
11. reduce noisy context for strongly explicit symptom queries;
12. use structured LLM generation instead of free-form source citations;
13. validate generated source identifiers;
14. validate supporting evidence against the claimed source;
15. construct final citations deterministically in Python;
16. expose retrieved documents and scores in Streamlit;
17. evaluate retrieval separately from answer generation.

The objective is not to build the most complex RAG architecture possible.

The objective is to build a small, understandable, reproducible, measurable,
and traceable maintenance assistant whose design choices can be explained,
tested, and improved.