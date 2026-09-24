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

Information non disponible dans les sources fournies.

## Vérifications recommandées

Information non disponible dans les sources fournies.

## Actions ou solutions possibles

- Réglage temporaire du débit gaz. [INT-011]
- Reset du boîtier. [INT-001]
- Test de fonctionnement. [INT-001]

## Sources utilisées

- [INT-001]
- [INT-011]

### Citation validation

**Cited sources:** INT-001, INT-011

**Invalid sources:** None

**Citation validation:** PASS

## Question 2

**Question:** J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?

### Generated answer

## Causes possibles

- Bac de condensat obstrué (algues, poussière). [INT-003]
- Tuyau d'évacuation bouché ou mal penté. [INT-003]
- Fuite d'eau unité intérieure pas de niveau. [atlantic_fuite_eau]

## Vérifications recommandées

- Nettoyer le bac de condensat. [INT-003]
- Déboucher le tuyau d'évacuation. [INT-003]
- Installer une pastille anti-algues. [atlantic_fuite_eau]

## Actions ou solutions possibles

- Nettoyer le bac de condensat. [INT-003]
- Déboucher le tuyau d'évacuation. [INT-003]
- Installer une pastille anti-algues. [atlantic_fuite_eau]

## Sources utilisées

- [INT-003]
- [atlantic_fuite_eau]

### Citation validation

**Cited sources:** INT-003, atlantic_fuite_eau

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

- Remplacement du câble de communication 4 fils. [INT-002]

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
- Inspecter l'électrode (état, position, câblage). [saunier_f28]
- Mesurer le courant d'ionisation (> 1 microA requis). [saunier_f28]
- Tester l'électrovanne gaz (tension de commande, courant). [saunier_f28]

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
- Activation de l'appoint électrique. [INT-021]

## Sources utilisées

- [INT-021]

### Citation validation

**Cited sources:** INT-021

**Invalid sources:** None

**Citation validation:** PASS

## Global citation result

Answers with valid source IDs: **5/5**

Citation validation only checks that cited source IDs exist in the retrieved context. It does not by itself prove that every generated statement is fully supported by the cited source.
