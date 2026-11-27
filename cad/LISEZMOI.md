# Châssis imprimable — Fast line tracker (version 2)

Cotes mesurées le 27 novembre 2026 (moteurs, roues, capteurs, HC-SR04, matrice 8x8).
Plateau de l'imprimante : 256 x 256 mm. La plaque fait 150 x 180 mm.

## Pièces à imprimer
| Fichier | Qté | Orientation | Réglages conseillés |
|---|---|---|---|
| chassis.stl | 1 | Déjà retourné (dessus de la plaque sur le plateau) | PLA ou PETG, couche 0,2 mm, 3 parois, 20 %, sans support |
| barre.stl | 1 | À plat | 3 parois, 30 % |
| entretoise.stl | 2 | Debout | 100 % |
| hcsr04.stl | 1 | Face avant à plat | 3 parois, 20 % |
| support_matrice.stl | 1 | Semelle à plat (face inclinée à 60°, sans support) | 3 parois, 20 % |
| cale_roulette.stl | 1 | Debout | 100 % — **à imprimer seulement quand la roue folle sera mesurée** |

## Valeurs calculées
- Dessous de la plaque au sol : 43,96 mm (roues de 65,57 mm)
- Entretoises de la barre capteurs : 24,76 mm → bout des capteurs IR à environ 8 mm du sol
- Capteurs IR à 90 mm devant l'axe des roues

## Quincaillerie
- Moteurs : 2 vis M2 x 25 + écrous par moteur (trous du moteur ~2,3 mm), + 1 ou 2 serre-câbles en renfort
- Barre capteurs : 2 vis M3 x 35 + écrous (plaque → entretoise → barre)
- Capteurs de ligne : 2 vis M3 x 8 + écrous par capteur (circuit sous la barre, composants vers le sol, broches vers l'arrière)
- Support HC-SR04 : 2 vis M3 x 8 + écrous ; capteur tenu par 4 vis M2 ou 2 serre-câbles
- Support matrice : 2 vis M3 x 8 + écrous dans la grille ; matrice vissée en M3 (2 paires de trous prévues)
- Cale de roue folle : 2 vis M3 autotaraudeuses par le dessus de la plaque, 2 pour la roue folle par le dessous
- Grille de trous M3 au pas de 10 mm : breadboard (adhésif), batterie externe (velcro + serre-câble), fils

## Roue folle (à faire quand elle arrivera)
Mesurer sa hauteur totale et l'entraxe de ses trous, puis changer `roulette_h` et `roulette_entraxe`
dans le fichier .scad et exporter seulement `PART = "cale_roulette"`.

## Modifier une cote
Ouvrir `fast_line_tracker_chassis.scad` dans OpenSCAD, changer la valeur en haut du fichier,
choisir la pièce avec `PART`, F6, puis Fichier → Exporter en STL.
