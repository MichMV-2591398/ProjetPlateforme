# Fast Line Tracker — Robot suiveur de ligne rapide

**Cours :** 420-314 — Épreuve finale (Automne 2026)  
**Plateforme :** Arduino Nano ESP32 (ABX00083), programmé en MicroPython   

## Membres de l'équipe
- David
- Michael

---

## Livrable 1 — Choix de projet et plan de projet

| Élément demandé | Où le trouver |
| :--- | :--- |
| **Description du problème choisi et de la fonction du prototype** | [Section 1](#1-problème-choisi-et-fonction-du-prototype) |
| **Diagramme :** [`docs/diagramme_fonctionnel.png`](docs/diagramme_fonctionnel.png) |
| **Liste préliminaire des composants** | [Section 4](#4-liste-préliminaire-du-matériel) |
| **Attribution préliminaire des broches** | [Section 6](#6-branchements-et-numéros-de-broches-attribution-préliminaire) |
| **Répartition initiale du travail** | [Section 7](#7-répartition-initiale-du-travail) |
| **Lien du dépôt GitHub** | En-tête ci-dessus |

---

## 1. Problème choisi et fonction du prototype

### Problème
Dans les entrepôts et les usines, des robots mobiles suivent des lignes tracées au sol pour transporter du matériel. Ces robots doivent :
- aller le plus vite possible sans quitter leur trajet ;
- s'arrêter d'eux-mêmes si quelque chose bloque le passage ;
- signaler clairement leur état aux personnes autour, par exemple quand la batterie est faible ou quand ils ont perdu leur trajet.

### Fonction du prototype
Le prototype est un robot suiveur de ligne rapide, à l'échelle réduite. Il :
- lit en continu 5 capteurs infrarouges pour savoir où se trouve la ligne ;
- corrige la vitesse de ses deux roues pour rester centré sur la ligne ;
- s'arrête devant un obstacle détecté par un capteur ultrason, puis repart quand la voie est libre ;
- surveille la charge de sa batterie et s'arrête de façon sécuritaire avant qu'elle ne soit trop faible ;
- signale s'il a perdu la ligne, au lieu de continuer au hasard.

Une personne peut démarrer et arrêter le robot avec un bouton et régler sa vitesse avec un potentiomètre, sans modifier le code. L'état du robot est affiché par une LED RVB et une barre de 8 DEL WS2812B.

---

## 2. Diagramme fonctionnel

> **Fonctionnement :**
> - Les entrées (à gauche) sont lues et filtrées par le Nano ESP32.
> - La position de la ligne sert à calculer l'écart de vitesse entre la roue gauche et la roue droite.
> - La machine à états décide du mode selon la distance de l'obstacle, la charge de la batterie, la présence de la ligne et les appuis sur le bouton.
> - Les sorties (à droite) dépendent du mode et des mesures : les moteurs bougent, la LED RVB indique l'état et la barre WS2812B affiche la vitesse et le mode.

---

## 3. Correspondance avec le cahier des charges

| Exigence de l'énoncé | Réalisation |
| :--- | :--- |
| **Capteur à sortie analogique** | Diviseur de tension sur la batterie (mesure de la charge), lu par l'ADC |
| **Capteur à sortie numérique** | 5 capteurs de ligne Keyestudio + capteur ultrason HC-SR04 |
| **Sortie analogique / PWM** | 2 moteurs TT commandés en PWM par le TB6612FNG |
| **Sortie numérique (marche/arrêt)** | LED RVB d'état (chaque couleur allumée ou éteinte) |
| **Composant nouveau** | Barre de 8 DEL adressables WS2812B (protocole NeoPixel, 1 fil) |
| **Au moins 2 modes** | ATTENTE, SUIVI, OBSTACLE, LIGNE PERDUE, BATTERIE FAIBLE |
| **Interaction locale** | Bouton (changer de mode) + potentiomètre (vitesse de base) |
| **Rétroaction perceptible** | Mouvement + lumière (LED RVB et barre WS2812B) |
| **Fonctionnement autonome** | Démarre seul à la mise sous tension (`main.py`) |

---

## 4. Liste préliminaire du matériel

| Qté | Composant | Rôle |
| :-: | :--- | :--- |
| 1 | Arduino Nano ESP32 (ABX00083) | Microcontrôleur |
| 1 | Pilote moteurs TB6612FNG | Commande des 2 moteurs |
| 2 | Moteurs TT jaunes + roues 65 mm | Propulsion |
| 1 | Roue folle à bille | Appui arrière |
| 5 | Capteurs de suivi de ligne Keyestudio | Détection de la ligne |
| 1 | Capteur ultrason HC-SR04 (alimenté en 3,3 V) | Détection d'obstacle |
| 1 | Barre WS2812B 8 DEL + résistance 330 Ω | Affichage de la vitesse et du mode |
| 1 | LED RGB | État du robot |
| 1 | Bouton poussoir | Changement de mode |
| 1 | Potentiomètre 10 kΩ | Réglage de la vitesse |
| 2 | Résistances 20 kΩ et 10 kΩ | Diviseur de mesure de la batterie |
| 1 | Batterie 2S 7,4 V (2× 18650) + boîtier + chargeur | Alimentation |
| 1 | Interrupteur ON/OFF | Coupure générale |
| 1 | Châssis imprimé en 3D (voir `cad/`) | Structure |
| 1 | Mini breadboard + fils Dupont | Raccordement |
---

## 5. Schéma de câblage

* Version vectorielle : `docs/schema_cablage.svg`
* Le plan électrique détaillé (calculs, justification des raccordements, sécurité) se trouve dans [`docs/PLAN_ELECTRIQUE.md`](docs/PLAN_ELECTRIQUE.md).

### Alimentation
- Batterie 2S (7,4 V), puis interrupteur, puis bus +7,4 V. Ce bus alimente :
  - `VIN` du Nano ESP32 ;
  - `VM` du TB6612FNG (moteurs) ;
  - le diviseur de mesure de la batterie.
- `3V3` du Nano, puis rail 3V3 : capteurs de ligne, HC-SR04, barre WS2812B, `VCC` et `STBY` du TB6612, potentiomètre.
- Toutes les masses sont communes.

---

## 6. Branchements et numéros de broches (attribution préliminaire)

> ℹ️ *En MicroPython, on utilise le numéro GPIO (colonne GPIO), pas le nom de la broche Arduino.*

| Broche Nano | GPIO | Raccordée à | Type |
| :--- | :-: | :--- | :--- |
| **A0** | 1 | Capteur de ligne S1 (extrême gauche) | Entrée numérique |
| **A1** | 2 | Capteur de ligne S2 | Entrée numérique |
| **A2** | 3 | Capteur de ligne S3 (centre) | Entrée numérique |
| **A3** | 4 | Capteur de ligne S4 | Entrée numérique |
| **A4** | 11 | Capteur de ligne S5 (extrême droite) | Entrée numérique |
| **A5** | 12 | Diviseur batterie 20 kΩ / 10 kΩ | Entrée analogique (ADC) |
| **A6** | 13 | Potentiomètre 10 kΩ (curseur) | Entrée analogique (ADC) |
| **A7** | 14 | LED RVB — vert (via 100 Ω) | Sortie numérique |
| **D2** | 5 | Bouton de mode (autre patte → GND) | Entrée numérique, pull-up interne |
| **D3** | 6 | TB6612 PWMA (vitesse moteur gauche) | Sortie PWM |
| **D4** | 7 | TB6612 AIN1 | Sortie numérique |
| **D5** | 8 | TB6612 AIN2 | Sortie numérique |
| **D6** | 9 | LED RVB — bleu (via 100 Ω) | Sortie numérique |
| **D7** | 10 | TB6612 BIN1 | Sortie numérique |
| **D8** | 17 | TB6612 BIN2 | Sortie numérique |
| **D9** | 18 | TB6612 PWMB (vitesse moteur droit) | Sortie PWM |
| **D10** | 21 | HC-SR04 TRIG | Sortie numérique |
| **D11** | 38 | HC-SR04 ECHO | Entrée numérique |
| **D12** | 47 | Barre WS2812B DIN (via 330 Ω) | Sortie numérique série |
| **D13** | 48 | LED RVB — rouge (via 220 Ω) | Sortie numérique |
| **VIN** | — | Bus +7,4 V | Alimentation |
| **3V3** | — | Rail 3V3 | Alimentation |
| **GND** | — | Rail GND commun | Masse |

La broche `STBY` du TB6612 est reliée en permanence au rail 3V3, ce qui laisse le pilote toujours actif.

---

## 7. Répartition initiale du travail

Le travail est partagé en deux volets. Chaque membre fait ses propres commits pour la partie dont il est responsable, et les deux membres doivent comprendre l'ensemble du projet.

| Volet | Responsable | Tâches |
| :--- | :--- | :--- |
| **Matériel et mouvement** | David | Câblage et alimentation (batterie, interrupteur, rail 3V3), châssis imprimé en 3D, classe Moteurs (TB6612FNG, PWM), lecture et calibration des 5 capteurs de ligne, algorithme de suivi (position pondérée et correction proportionnelle). |
| **Interaction, sécurité et rétroaction** | Michael | HC-SR04 (distance, obstacle), mesure de la batterie (diviseur, filtrage, seuil), potentiomètre et bouton (anti-rebond, appui court ou long), LED RVB et barre WS2812B (`affichage.py`), machine à états et gestion des erreurs. |
| **Commun** | Les deux | Programmes de test dans `test/`, intégration dans `main.py`, `README`, vidéo de secours, journal de contribution. |


---

## 8. Installation et exécution

### Prérequis
- Firmware MicroPython pour Arduino Nano ESP32 installé sur la carte (disponible via *Arduino Lab for MicroPython* ou [micropython.org](https://micropython.org)).
- *Thonny* ou *Arduino Lab for MicroPython* pour copier les fichiers sur la carte.

### Étapes
1. Cloner le dépôt :
   ```bash
   git clone [https://github.com/MichMV-2591398/ProjetPlateforme.git](https://github.com/MichMV-2591398/ProjetPlateforme.git)
