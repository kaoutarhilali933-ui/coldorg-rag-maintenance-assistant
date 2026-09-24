# End-to-end RAG evaluation

This evaluation runs the complete RAG pipeline:

1. hybrid retrieval;
2. context filtering;
3. local generation with Llama 3.2 through Ollama;
4. citation validation.

## Question 1

**Question:** Code erreur E133 sur une chaudière Frisquet Prestige Condensation 25kW. La chaudière ne redémarre pas depuis ce matin. Quelles sont les causes possibles et comment diagnostiquer ?

### Generated answer

## Causes possibles

- Pas d'arrivée de gaz. [INT-001]
- Électrode d'allumage encrassée ou mal positionnée. [INT-001]
- Fil de masse desserré sur le boîtier de contrôle. [INT-001]
- Problème d'ionisation. [frisquet_e133]

## Vérifications recommandées

Information non disponible dans les sources fournies.

## Actions ou solutions possibles

- Nettoyer l'électrode d'allumage. [INT-001]
- Contact GRDF pour signalement basse pression réseau. [INT-011]

## Sources utilisées

- [INT-001]
- [INT-011]
- [frisquet_e133]

### Citation validation

**Cited sources:** INT-001, INT-011, frisquet_e133

**Invalid sources:** None

**Citation validation:** PASS

## Question 2

**Question:** J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?

### Generated answer

## Causes possibles

- Bac de condensat obstrué (algues, poussière). [INT-003]

## Vérifications recommandées

- Nettoyer le bac de condensat. [INT-003]

## Actions ou solutions possibles

- Nettoyer le bac de condensat. [INT-003]

## Sources utilisées

- [INT-003]

### Citation validation

**Cited sources:** INT-003

**Invalid sources:** None

**Citation validation:** PASS

## Question 3

**Question:** Ma pompe à chaleur Daikin Altherma affiche le code U4, plus de chauffage ni d'eau chaude. Quelles pièces dois-je prévoir ?

### Generated answer

## Causes possibles

- Câble de communication coupé, endommagé ou mal branché. [INT-002]

## Vérifications recommandées

Information non disponible dans les sources fournies.

## Actions ou solutions possibles

Information non disponible dans les sources fournies.

## Sources utilisées

- [INT-002]

### Citation validation

**Cited sources:** INT-002

**Invalid sources:** None

**Citation validation:** PASS

## Question 4

**Question:** Un client a une chaudière Saunier Duval ThemaPlus Condens en panne avec le code F28 pour la troisième fois ce mois. Qu'est-ce qui peut expliquer un défaut récurrent ?

### Generated answer

## Causes possibles

- Défaut d'allumage récurrent. [INT-023]

## Vérifications recommandées

- Vérifier l'arrivée de gaz et la pression (20 mbar). [saunier_f28]

## Actions ou solutions possibles

- Remplacement de la carte électronique principale. [INT-023]
- Remplacement de l'électrovanne gaz combinée. [INT-004]

## Sources utilisées

- [INT-004]
- [INT-023]
- [saunier_f28]

### Citation validation

**Cited sources:** INT-004, INT-023, saunier_f28

**Invalid sources:** None

**Citation validation:** PASS

## Question 5

**Question:** Le client dit que sa PAC Daikin chauffe mais que la maison reste froide. La PAC ne montre aucun code erreur. Que vérifier ?

### Generated answer

## Causes possibles

- Courbe de chauffe mal réglée. [INT-021]

## Vérifications recommandées

- Vérification de la courbe de chauffe. [INT-021]

## Actions ou solutions possibles

- Réglage de la courbe de chauffe. [INT-021]

## Sources utilisées

- [INT-021]

### Citation validation

**Cited sources:** INT-021

**Invalid sources:** None

**Citation validation:** PASS

## Global citation result

Answers with valid source IDs: **5/5**

Citation validation only checks that cited source IDs exist in the retrieved context. It does not by itself prove that every generated statement is fully supported by the cited source.
