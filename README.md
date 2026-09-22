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