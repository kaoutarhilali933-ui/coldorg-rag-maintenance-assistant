# COLDORG RAG Maintenance Assistant

Prototype d'assistant IA basé sur une architecture RAG pour aider les techniciens de maintenance à exploiter les interventions historiques et les fiches techniques COLDORG.

## Status

Work in progress.

## Chunking strategy

For historical maintenance interventions, the project uses one intervention as one chunk.

Each intervention is short and already represents a complete business unit containing the equipment, brand, error code, symptom, diagnosis, solution, and replaced parts.

Keeping these fields together avoids separating a symptom from its diagnosis or the corresponding solution.

For this reason, no arbitrary fixed-size splitting, for example every 500 characters, is applied to the intervention dataset.