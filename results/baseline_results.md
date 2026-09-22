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

The baseline performs well on questions that contain explicit equipment names
and error codes.

For Q1, Q3 and Q4, short technical codes such as `E133`, `U4` and `F28`
are correctly retrieved within the Top-5. In this dataset, these codes do not
appear to be the main weakness of the semantic baseline.

Q2 also works well without an error code: the semantic model correctly links
the user's description of water leaking under the air conditioner with the
technical section about an indoor-unit water leak.

The main limitation appears on Q5, which is a more functional question without
an error code. The retriever finds the relevant historical intervention
`INT-021`, but the technical maintenance chunk `daikin_entretien` does not
appear in the Top-5.

This suggests that pure vector similarity can favor historically similar
interventions while missing a complementary technical document that is useful
for diagnosis.

The next retrieval improvement should therefore be guided by this observed
failure, using structured metadata and domain-specific signals rather than
adding rules arbitrarily.