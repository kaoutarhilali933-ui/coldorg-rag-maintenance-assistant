# Evaluation Plan

Les questions de `questions_test.json` sont utilisées uniquement pour évaluer le système.

Elles ne doivent jamais être ajoutées à l'index vectoriel comme sources de connaissances.

| Question | Sujet principal | Sources attendues | Point à vérifier |
|---|---|---|---|
| Q1 | Frisquet Prestige - code E133 | Fiche Frisquet E133, INT-001, INT-011, INT-029 | Le même code erreur peut avoir plusieurs causes |
| Q2 | Atlantic Idéa - fuite d'eau | Fiche Atlantic fuite d'eau, INT-003 | Le retrieval doit retrouver le symptôme même sans code erreur |
| Q3 | Daikin Altherma - code U4 | Fiche Daikin U4, INT-002 | Retrouver le diagnostic et les pièces potentiellement nécessaires |
| Q4 | Saunier Duval - F28 récurrent | Fiche Saunier Duval F28, INT-004, INT-023 | Un défaut récurrent peut avoir plusieurs causes |
| Q5 | PAC Daikin chauffe mais maison froide | Fiche Daikin courbe de chauffe, INT-021 | Vérifier qu'une intervention d'une autre marque peut être pertinente par similarité de symptôme |

## Objectif

Ce jeu d'évaluation servira à comparer les résultats attendus avec les documents réellement retrouvés par le moteur de recherche.

Exemple :

- Question : Q1
- Sources attendues : INT-001, INT-011, INT-029
- Sources retrouvées par le système : à compléter après implémentation du retrieval