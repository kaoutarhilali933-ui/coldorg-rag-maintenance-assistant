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

- Défaut d'allumage due à une pression gaz en entrée insuffisante (15 mbar au lieu de 20 mbar) [INT-011]
- Électrode d'allumage encrassée ou mal positionnée [frisquet_e133]
- Fil de masse desserré sur le boîtier de contrôle [INT-001]
- Problème d'ionisation (courant < 1 microA) [frisquet_e133]
- Carte électronique défaillante (rare) [frisquet_e133]

## Vérifications recommandées

- Vérifier que le robinet gaz est ouvert [frisquet_e133]
- Vérifier la pression gaz en entrée (20 mbar pour G20) [INT-011]
- Inspecter et nettoyer l'électrode d'allumage [frisquet_e133]
- Vérifier l'écart électrode (3mm) [frisquet_e133]
- Contrôler le fil de masse et les connexions [INT-001]
- Mesurer le courant d'ionisation (doit être > 1 microA) [frisquet_e133]

## Actions ou solutions possibles

- Réglage temporaire du débit gaz [INT-011]
- Nettoyage électrode d'allumage [INT-001]
- Resserrage du fil de masse [INT-001]
- Reset du boîtier [INT-001]
- Ouverture du robinet gaz [INT-029]
- Purge de la ligne gaz [INT-029]
- Contact GRDF pour signalement basse pression réseau [INT-011]
- Test allumage OK après stabilisation pression [INT-011]

## Sources utilisées
- [INT-001]
- [INT-029]
- [INT-011]
- [frisquet_e133]

### Citation validation

**Cited sources:** INT-001, INT-011, INT-029, frisquet_e133

**Invalid sources:** None

**Citation validation:** PASS

## Question 2

**Question:** J'ai une fuite d'eau qui coule le long du mur sous mon climatiseur Atlantic Idéa. Qu'est-ce que ça peut être ?

### Generated answer

## Causes possibles

- Bac de condensat obstrué (algues, poussière) [atlantic_fuite_eau]
- Tuyau d'évacuation bouché ou mal penté [atlantic_fuite_eau]
- Pompe de relevage en panne (si installée) [atlantic_fuite_eau]
- Unité intérieure pas de niveau [atlantic_fuite_eau]

## Vérifications recommandées

- Vérifier la pression de réfrigérant [atlantic_ne_refroidit_plus]
- Vérifier les filtres intérieurs [atlantic_ne_refroidit_plus]
- Vérifier la pente du tuyau d'évacuation [atlantic_fuite_eau]
- Vérifier les supports anti-vibrations des liaisons [atlantic_bruit_anormal]

## Actions ou solutions possibles

- Nettoyer le bac de condensat [atlantic_fuite_eau]
- Déboucher le tuyau d'évacuation [atlantic_fuite_eau]
- Vérifier et corriger la pente [atlantic_fuite_eau]
- Installer une pastille anti-algues [atlantic_fuite_eau]
- Resserrer la fixation murale [atlantic_bruit_anormal]
- Ajouter des cales en mousse [atlantic_bruit_anormal]
- Nettoyer le ventilateur tangentiel [atlantic_bruit_anormal]
- Vérifier les supports anti-vibrations des liaisons [atlantic_bruit_anormal]

## Sources utilisées
- [atlantic_fuite_eau]
- [atlantic_ne_refroidit_plus]
- [atlantic_bruit_anormal]

### Citation validation

**Cited sources:** atlantic_bruit_anormal, atlantic_fuite_eau, atlantic_ne_refroidit_plus

**Invalid sources:** None

**Citation validation:** PASS

## Question 3

**Question:** Ma pompe à chaleur Daikin Altherma affiche le code U4, plus de chauffage ni d'eau chaude. Quelles pièces dois-je prévoir ?

### Generated answer

## Causes possibles
- Câble de communication coupé, endommagé ou mal branché [INT-002]
- Bornier de connexion oxydé [INT-002]
- Carte électronique (intérieure ou extérieure) défaillante [INT-002]

## Vérifications recommandées
- Vérifier le câble de communication (4 fils, continuité) [INT-002]
- Inspecter les borniers des deux unités [INT-002]
- Tester la tension de communication (env. 30V DC entre les bornes) [INT-002]
- Vérifier la continuité du câble de communication dans la gaine anti-rongeurs [daikin_u4]

## Actions ou solutions possibles
- Remplacement du câble de communication 4 fils [INT-002]
- Passage dans une gaine de protection anti-rongeurs [INT-002]
- Remise en service et test communication OK [INT-002]

## Sources utilisées
- [INT-002]
- [daikin_u4]

### Citation validation

**Cited sources:** INT-002, daikin_u4

**Invalid sources:** None

**Citation validation:** PASS

## Question 4

**Question:** Un client a une chaudière Saunier Duval ThemaPlus Condens en panne avec le code F28 pour la troisième fois ce mois. Qu'est-ce qui peut expliquer un défaut récurrent ?

### Generated answer

## Causes possibles
- Défaut d'allumage récurrent, cartes électroniques défaillantes ou traces d'oxydation sur les connecteurs [INT-023]
- Électrovanne gaz fatiguée ou défectueuse, courant de commande faible et ionisation instable [INT-004]
- Pas de gaz (robinet fermé, pression insuffisante) ou câblage de l'électrode défectueux [saunier_f28]

## Vérifications recommandées
- Vérifier l'arrivée de gaz et la pression (20 mbar) [saunier_f28]
- Inspecter l'électrode (état, position, câblage) [saunier_f28]
- Mesurer le courant d'ionisation (> 1 microA requis) [saunier_f28]
- Tester l'électrovanne gaz (tension de commande, courant) [INT-004]
- Contrôler la combustion après remplacement de l'électrovanne gaz combinée : CO = 28ppm, tirage OK [INT-004]

## Actions ou solutions possibles
- Remplacement de la carte électronique principale [INT-023]
- Remplacement de l'électrovanne gaz combinée [INT-004]
- Nettoyage de tous les connecteurs [INT-023]
- Nettoyage de l'électrode d'ionisation [INT-004]

## Sources utilisées
- [INT-023]
- [saunier_f28]
- [INT-004]

### Citation validation

**Cited sources:** INT-004, INT-023, saunier_f28

**Invalid sources:** None

**Citation validation:** PASS

## Question 5

**Question:** Le client dit que sa PAC Daikin chauffe mais que la maison reste froide. La PAC ne montre aucun code erreur. Que vérifier ?

### Generated answer

## Causes possibles

- Courbe de chauffe mal réglée (pente trop faible) [INT-021]
- Appoint électrique non activé [INT-021]
- Défaut moteur ventilateur unité extérieure [INT-005]
- Roulement du ventilateur grippé, hélice bloquée [INT-005]
- Défaut communication entre unité intérieure et extérieure [INT-002]
- Câble de communication endommagé par des rongeurs dans la gaine technique [INT-002]
- Résistance d'appoint jamais activée [INT-009]
- Mode éco activé (chauffe uniquement en heures creuses mais contrat HC/HP non souscrit) [INT-009]

## Vérifications recommandées

- Vérification des pressions de fonctionnement [daikin_entretien]
- Contrôle du niveau de réfrigérant (sous-refroidissement, surchauffe) [daikin_entretien]
- Vérification de l'anode du ballon ECS (si ballon intégré) [daikin_entretien]
- Contrôle des raccords frigorifiques (étanchéité) [daikin_entretien]
- Test des sécurités (haute pression, basse pression, antigel) [daikin_entretien]
- Vérification de la courbe de chauffe [daikin_entretien]
- Vérification de la charge de réfrigérant [daikin_entretien]
- Vérification de l'état du compresseur (intensité, vibrations) [daikin_entretien]

## Actions ou solutions possibles

- Réglage de la courbe de chauffe : pente 1.2, décalage +2 [INT-021]
- Activation de l'appoint électrique en dessous de -3°C [INT-021]
- Remplacement du câble de communication 4 fils [INT-002]
- Passage dans une gaine de protection anti-rongeurs [INT-002]
- Remplacement du moteur ventilateur complet et du condensateur de démarrage [INT-005]
- Nettoyage de la batterie extérieure (encrassée) [INT-005]
- Désactivation du mode éco (pas de contrat HC) [INT-009]
- Activation de la résistance d'appoint en mode boost temporaire [INT-009]

## Sources utilisées
- [INT-021]
- [daikin_entretien]
- [INT-002]
- [INT-005]
- [INT-009]

### Citation validation

**Cited sources:** INT-002, INT-005, INT-009, INT-021, daikin_entretien

**Invalid sources:** None

**Citation validation:** PASS

## Global citation result

Answers with valid source IDs: **5/5**

Citation validation only checks that cited source IDs exist in the retrieved context. It does not by itself prove that every generated statement is fully supported by the cited source.
