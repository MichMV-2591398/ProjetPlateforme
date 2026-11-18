# Châssis imprimable — Fast line tracker

## Pièces à imprimer
| Fichier | Qté | Orientation | Réglages conseillés |
|---|---|---|---|
| chassis.stl | 1 | Déjà retourné (dessus de la plaque sur le plateau) | PLA ou PETG, couche 0,2 mm, 3 parois, 20 % de remplissage, aucun support |
| barre.stl | 1 | À plat | 3 parois, 30 % |
| entretoise.stl | 2 | Debout | 100 % de remplissage |
| hcsr04.stl | 1 | Face avant à plat | 3 parois, 20 % |

Taille de la plaque : 150 × 180 mm (entre sur un plateau de 220 × 220 mm).

## Quincaillerie
- Moteurs TT : 4 serre-câbles de 3,6 mm (2 par moteur), passés dans les fentes et autour du bord de la plaque.
- Barre capteurs : 2 vis M3 × 30 + écrous (plaque → entretoise → barre) ; 5 vis M3 × 8 + écrous pour les capteurs.
- Support HC-SR04 : 2 vis M3 × 8 + écrous.
- Roue folle : 2 vis M3 autotaraudeuses × 10 dans le bloc.
- Grille de trous M3 au pas de 10 mm : breadboard (adhésif), boîtier 18650, TB6612 au besoin.

## À mesurer AVANT d'imprimer (variables en haut du fichier .scad)
- `roue_d` : diamètre des roues (défaut 65 mm)
- `axe_depuis_bout` : distance entre l'axe du moteur et le bout côté réducteur (défaut 11 mm)
- `roulette_h` et `roulette_entraxe` : hauteur totale et entraxe des trous de la roue folle
- `capteur_pas` : espacement voulu entre les capteurs (défaut 18 mm)

Ouvrir le .scad dans OpenSCAD (gratuit), changer les valeurs, choisir `PART = "chassis"` (ou une autre pièce), F6, puis Fichier → Exporter en STL.
La console affiche la hauteur calculée du bloc de la roue folle et des entretoises.
