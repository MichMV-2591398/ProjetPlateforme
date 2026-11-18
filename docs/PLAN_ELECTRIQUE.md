# Plan électrique — Fast line tracker (420-314, épreuve finale)

Plateforme : **Arduino Nano ESP32 (ABX00083)**, programmé en MicroPython.
En MicroPython, on utilise toujours le **numéro GPIO** (ex. `Pin(6)` pour D3).

## 1. Correspondance avec les exigences de l'énoncé

| Exigence | Composant retenu | Type |
|---|---|---|
| Capteur analogique | Diviseur de tension sur la batterie (mesure de la charge) | Analogique (ADC) |
| Capteur numérique | 5 capteurs de ligne Keyestudio + HC-SR04 | Numérique |
| Sortie analogique / PWM | 2 moteurs TT via TB6612FNG (PWMA, PWMB) | PWM |
| Sortie numérique | LED RVB d'état, chaque couleur commandée en marche/arrêt | Numérique |
| Composant nouveau | Barre de 8 DEL adressables WS2812B (protocole NeoPixel) *(à faire valider par l'enseignant)* | Numérique série (1 fil) |
| Interaction locale | Bouton (changer de mode) + potentiomètre (vitesse de base) | Numérique + analogique |
| Rétroaction perceptible | Mouvement, lumière (LED RVB : vert = marche, orange = problème, rouge = arrêt; barre WS2812 : % de vitesse en bargraphe) | — |
| Au moins 2 modes | ATTENTE → SUIVI → OBSTACLE / BATTERIE FAIBLE / LIGNE PERDUE | — |

## 2. Liste des composants

| Qté | Composant | Statut |
|---|---|---|
| 1 | Arduino Nano ESP32 (ABX00083) | Possédé |
| 1 | Pilote moteurs TB6612FNG | Possédé |
| 2 | Moteurs TT + roues | Possédé |
| 5 | Capteurs de suivi de ligne Keyestudio (S, V, G) | Possédé |
| 1 | Capteur ultrason HC-SR04 | Possédé |
| 1 | Roue folle (ball caster) | À acheter |
| 1 | Batterie 2S 7,4 V (2× 18650 + boîtier) + chargeur | À acheter |
| 1 | Interrupteur ON/OFF | À acheter |
| 1 | Barre WS2812B 8 DEL | À acheter |
| 1 | Résistance 330 Ω (ligne DIN de la barre) | À acheter |
| 1 | Bouton poussoir | À acheter |
| 1 | Potentiomètre 10 kΩ | À acheter |
| 1 | LED RVB 5 mm à cathode commune + résistances 220 Ω (R), 100 Ω (G) et 100 Ω (B) | À acheter |
| 2 | Résistances 20 kΩ et 10 kΩ (diviseur batterie) | À acheter |
| 1 | Condensateur 470 µF (≥ 16 V) pour le TB6612 — recommandé | À acheter |
| 2 | Condensateurs céramiques 0,1 µF (moteurs) | À acheter |
| 1 | Mini breadboard (rails 3V3 / GND) + fils Dupont | À acheter |
| 1 | Châssis + vis / entretoises | À acheter |

## 3. Attribution des broches

| Broche Nano | GPIO | Raccordée à | Direction | Configuration MicroPython |
|---|---|---|---|---|
| A0 | 1 | Capteur ligne S1 (gauche) | Entrée num. | `Pin(1, Pin.IN)` |
| A1 | 2 | Capteur ligne S2 | Entrée num. | `Pin(2, Pin.IN)` |
| A2 | 3 | Capteur ligne S3 (centre) | Entrée num. | `Pin(3, Pin.IN)` |
| A3 | 4 | Capteur ligne S4 | Entrée num. | `Pin(4, Pin.IN)` |
| A4 | 11 | Capteur ligne S5 (droite) | Entrée num. | `Pin(11, Pin.IN)` |
| A5 | 12 | Diviseur batterie (20 k / 10 k) | Entrée analog. | `ADC(Pin(12), atten=ADC.ATTN_11DB)` |
| A6 | 13 | Curseur du potentiomètre 10 kΩ | Entrée analog. | `ADC(Pin(13), atten=ADC.ATTN_11DB)` |
| D12 | 47 | Barre WS2812B DIN (via 330 Ω) | Sortie num. (série) | `NeoPixel(Pin(47), 8)` |
| D3 | 6 | TB6612 PWMA | Sortie PWM | `PWM(Pin(6), freq=1000)` |
| D4 | 7 | TB6612 AIN1 | Sortie num. | `Pin(7, Pin.OUT)` |
| D5 | 8 | TB6612 AIN2 | Sortie num. | `Pin(8, Pin.OUT)` |
| D6 | 9 | LED RVB — bleu (via 100 Ω) | Sortie num. | `Pin(9, Pin.OUT)` |
| D7 | 10 | TB6612 BIN1 | Sortie num. | `Pin(10, Pin.OUT)` |
| D8 | 17 | TB6612 BIN2 | Sortie num. | `Pin(17, Pin.OUT)` |
| D9 | 18 | TB6612 PWMB | Sortie PWM | `PWM(Pin(18), freq=1000)` |
| D10 | 21 | HC-SR04 TRIG | Sortie num. | `Pin(21, Pin.OUT)` |
| D11 | 38 | HC-SR04 ECHO (direct, capteur alimenté en 3,3 V) | Entrée num. | `Pin(38, Pin.IN)` |
| D2 | 5 | Bouton de mode (autre patte → GND) | Entrée num. | `Pin(5, Pin.IN, Pin.PULL_UP)` |
| D13 | 48 | LED RVB — rouge (via 220 Ω) | Sortie num. | `Pin(48, Pin.OUT)` |
| A7 | 14 | LED RVB — vert (via 100 Ω) | Sortie num. | `Pin(14, Pin.OUT)` |
| — | — | TB6612 STBY relié en permanence au rail 3V3 | — | (pilote toujours actif) |
| VIN | — | Bus +7,4 V (après interrupteur) | Alim. | — |
| 3V3 | — | Rail 3V3 : capteurs ligne (V), HC-SR04 VCC, barre WS2812B, TB6612 VCC/STBY, potentiomètre | Alim. | — |
| GND | — | Rail GND commun | Masse | — |

Broches libres : D0/D1 (UART, à éviter), B0/B1.

## 4. Alimentation

- **Batterie 2S (7,4 V nominal, 8,4 V pleine charge)**, puis interrupteur, puis bus +7,4 V.
- Le bus +7,4 V alimente :
  - **VIN du Nano ESP32** (accepte de 6 à 21 V) ;
  - **VM du TB6612FNG** (moteurs) ;
  - le haut du **diviseur de mesure de la batterie**.
- **3V3 du Nano**, puis le rail 3V3 : capteurs de ligne, HC-SR04, barre WS2812B, VCC et STBY du TB6612, potentiomètre.
- Aucun convertisseur 5 V : tout ce qui n'est pas moteur fonctionne en 3,3 V.
- **Toutes les masses sont communes.**

## 5. Calculs et justification des raccordements

**Diviseur de mesure de la batterie (A5)**
V_A5 = V_bat × 10 k / (20 k + 10 k). À 8,4 V, on obtient 2,8 V, ce qui reste sous la limite de l'ADC (environ 3,1 V avec une atténuation de 11 dB).
Dans le code : `V_bat = V_mesurée × 3`. On déclenche l'alerte « batterie faible » sous environ 6,6 V (3,3 V par cellule).

**HC-SR04 en 3,3 V (D10 / D11)**
Le HC-SR04 utilisé fonctionne en 3,3 V (vérifié sur le montage). Il est alimenté par le rail 3V3 : ECHO sort donc du 3,3 V et se branche directement sur D11, sans diviseur. Aucun convertisseur 5 V n'est nécessaire dans le robot.
À valider pendant les tests : la distance mesurée reste stable et juste (vérifier à 10, 30 et 100 cm). Si les lectures deviennent erratiques, utiliser un HC-SR04P (3 à 5,5 V).

**LED RVB à cathode commune (D13 = R, A7 = G, D6 = B)**
- La patte la plus longue (cathode commune) va au GND. Chaque couleur passe par sa propre résistance.
- Rouge : (3,3 V − 2,0 V) / 220 Ω ≈ 6 mA.
- Vert et bleu : leur tension de seuil est d'environ 2,8 à 3,1 V, il reste donc peu de marge à 3,3 V. Une résistance de 100 Ω donne quelques mA, ce qui suffit pour une DEL témoin. Si le vert ou le bleu est trop faible, descendre à 68 Ω.
- Toutes les valeurs restent bien sous la limite de 40 mA par broche.
- Couleurs : vert = G seul (marche), orange/jaune = R + G (problème), rouge = R seul (arrêt), bleu = B seul (attente). En commande marche/arrêt, R + G donne plutôt un jaune ; pour un vrai orange, on peut atténuer le vert en PWM.
- *Note : la DEL intégrée au Nano (D13) s'allume aussi quand le rouge est allumé, ce qui est normal.*

**STBY du TB6612 relié au 3V3**
Pour libérer une broche pour la LED RVB, STBY est branché directement sur le rail 3V3 : le pilote est toujours actif. Pour arrêter les moteurs, le code met PWMA et PWMB à 0 (ou AIN1 = AIN2 = 0 et BIN1 = BIN2 = 0).

**Découplage des moteurs**
- 470 µF entre VM et GND, le plus près possible du TB6612.
- 0,1 µF aux bornes de chaque moteur.

Ces condensateurs évitent que le bruit des moteurs ne fasse redémarrer l'ESP32.

**Remarques sur les broches**
- A5 et A6 sont sur l'ADC2 de l'ESP32-S3. Ce n'est pas un problème tant que le Wi-Fi n'est pas activé.
- La barre WS2812B peut utiliser n'importe quelle broche GPIO, car le module `neopixel` de MicroPython génère le signal avec le périphérique RMT de l'ESP32.

**Barre WS2812B (D12)**
- Une résistance de 330 Ω en série sur DIN protège contre les surtensions sur la ligne de données.
- Consommation : environ 60 mA par DEL en blanc à pleine intensité, soit environ 480 mA pour 8 DEL. Dans le code, on limite la luminosité à environ 20 % (≈ 100 mA max), ce qui ménage la batterie et le régulateur 3,3 V du Nano.
- Alimentation : la barre est branchée sur le rail 3V3. C'est un peu sous la tension nominale des WS2812B, mais avec 8 DEL à faible luminosité ça fonctionne généralement, et le signal 3,3 V de l'ESP32 est alors parfaitement compatible. Les couleurs (surtout le bleu) sont un peu moins vives. Si la barre scintille ou affiche de mauvaises couleurs, il faudra l'alimenter en 5 V avec un convertisseur abaisseur.
- Affichage prévu : nombre de DEL allumées = % de vitesse du potentiomètre (1 DEL ≈ 12,5 %). Couleur selon le mode : vert = suivi, bleu = attente, orange = obstacle, rouge clignotant = erreur (batterie faible, ligne perdue).

## 6. Précautions de sécurité électrique

- Mettre l'interrupteur sur **OFF** pendant le téléversement par USB.
- Ne jamais brancher un 5 V sur une broche GPIO (l'ESP32 fonctionne en 3,3 V).
- Vérifier la polarité de la batterie avant de la brancher, et ne jamais court-circuiter une cellule 18650.
- Tester d'abord chaque sous-système séparément : capteurs, moteurs sans roues au sol, barre WS2812B, HC-SR04.
