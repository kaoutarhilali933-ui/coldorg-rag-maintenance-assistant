# Hybrid retrieval results

The improved retrieval combines semantic similarity with lightweight
domain-aware metadata reranking.

## Strategy

The system first retrieves the Top-20 semantic candidates.

It then reranks them using:

- semantic similarity score;
- exact error-code match bonus: `+0.05`;
- exact brand match bonus: `+0.003`;
- explicit no-error-code match bonus: `+0.03`.

The brand is intentionally used as a preference signal rather than a strict
filter so that relevant cross-brand interventions can still be retrieved.

## Results

| Question | Baseline | Hybrid |
|---|---:|---:|
| Q1 - Frisquet E133 | 4 / 4 | 4 / 4 |
| Q2 - Atlantic water leak | 2 / 2 | 2 / 2 |
| Q3 - Daikin U4 | 2 / 2 | 2 / 2 |
| Q4 - Saunier Duval F28 recurring fault | 3 / 3 | 3 / 3 |
| Q5 - Daikin heating without error code | 1 / 2 | 2 / 2 |

## Overall comparison

Baseline expected-source Recall@5:

**12 / 13 = 92.31%**

Hybrid expected-source Recall@5:

**13 / 13 = 100.00%**

## Key observation

The main baseline failure was Q5.

With pure vector retrieval, `INT-021` was retrieved but
`daikin_entretien` was outside the Top-5 and appeared at rank 12
when inspecting a larger candidate pool.

The hybrid reranking moved:

- `INT-021` to rank 1;
- `daikin_entretien` to rank 2.

This improvement was achieved without degrading the results of Q1 to Q4.

These results are measured on the five provided evaluation questions and
should not be interpreted as proof of perfect retrieval performance on
unseen production data.