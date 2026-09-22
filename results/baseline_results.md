# Baseline retrieval results

The baseline uses pure vector similarity retrieval with:

- embedding model: `intfloat/multilingual-e5-small`
- vector database: ChromaDB
- retrieval strategy: semantic vector search only
- Top-K: 5
- evaluation set: 5 test questions

## Results

| Question | Expected sources found | Result |
|---|---:|---|
| Q1 - Frisquet E133 | 4 / 4 | Complete |
| Q2 - Atlantic water leak | 2 / 2 | Complete |
| Q3 - Daikin U4 | 2 / 2 | Complete |
| Q4 - Saunier Duval F28 recurring fault | 3 / 3 | Complete |
| Q5 - Daikin heating without error code | 1 / 2 | Partial |

Overall expected-source Recall@5:

**12 / 13 = 92.31%**

## Observations

The pure vector baseline performs well on questions containing explicit
equipment names and error codes.

For Q1 to Q4, all expected sources are retrieved within the Top-5.

Q5 exposes a limitation of pure semantic vector retrieval. The historical
intervention `INT-021` is retrieved, but the technical maintenance chunk
`daikin_entretien` is missing from the Top-5.

This suggests that metadata and domain-specific signals such as brand,
equipment type, error code and maintenance intent could improve retrieval.

The baseline is intentionally kept simple so that later retrieval
improvements can be compared against a measurable reference.