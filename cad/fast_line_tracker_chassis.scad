// =====================================================================
//  Fast line tracker - châssis imprimable 3D (420-314)
//  Nano ESP32 + TB6612FNG + 2 moteurs TT + 5 capteurs Keyestudio + HC-SR04
//  Unités : mm.  Avant du robot = +Y.  Dessus de la plaque = +Z.
//
//  Choisir la pièce à exporter avec la variable PART :
//    "assemblage"  aperçu de toutes les pièces en position
//    "chassis"     plaque principale (déjà retournée pour l'impression)
//    "barre"       barre des 5 capteurs de ligne
//    "entretoise"  entretoise de la barre capteurs (en imprimer 2)
//    "hcsr04"      support du capteur ultrason
// =====================================================================

PART = "assemblage";

// ---------- Paramètres à mesurer / ajuster ----------
plaque_l      = 150;   // largeur (X)
plaque_L      = 180;   // longueur (Y)
plaque_ep     = 3.5;   // épaisseur
coin_r        = 12;

roue_d        = 65;    // diamètre des roues TT
moteur_L      = 70;    // longueur moteur TT
moteur_h      = 22.5;  // hauteur moteur (verticale une fois monté)
moteur_ep     = 18.8;  // épaisseur moteur (direction de l'axe)
axe_depuis_bout = 11;  // distance axe -> bout côté réducteur (mesurer!)
axe_y         = 10;    // position Y de l'axe des roues sur la plaque

roulette_h    = 20;    // hauteur totale de la roue folle (mesurer!)
roulette_entraxe = 25; // entraxe des 2 trous de la roue folle (mesurer!)
roulette_y    = -75;

capteur_pas   = 18;    // espacement entre capteurs de ligne
capteur_hauteur = 20;  // hauteur du DESSOUS de la barre au-dessus du sol
barre_ep      = 4;

hc_entraxe    = 26;    // entraxe des 2 transducteurs du HC-SR04
hc_trou_d     = 16.8;

inter_l       = 19.2;  // découpe interrupteur (mini rocker KCD11)
inter_h       = 12.9;

m3            = 3.3;   // trou de passage M3
m3_pilote     = 2.8;   // trou pour vis M3 autotaraudeuse dans le plastique
$fn = 48;

// ---------- Valeurs dérivées ----------
H_plaque  = roue_d/2 + moteur_h/2;              // dessous de plaque -> sol
moteur_x  = plaque_l/2 - moteur_ep/2;           // centre moteur en X
moteur_y_av = axe_y + axe_depuis_bout;          // bout avant du moteur
entretoise_h = H_plaque - capteur_hauteur - barre_ep;
barre_y   = plaque_L/2 + 8;                     // centre des capteurs (devant la plaque)
barre_fix = [[-45, plaque_L/2 - 6], [45, plaque_L/2 - 6]];

echo(str("Hauteur dessous de plaque / sol = ", H_plaque, " mm"));
echo(str("Hauteur entretoise capteurs = ", entretoise_h, " mm"));
echo(str("Hauteur bloc roue folle = ", H_plaque - roulette_h, " mm"));

// ---------- Outils ----------
module plaque_arrondie(l, L, ep, r) {
    linear_extrude(ep) offset(r) square([l - 2*r, L - 2*r], center = true);
}
module oblong(l, w, h) {   // trou oblong le long de Y
    hull() for (s = [-1, 1]) translate([0, s*(l - w)/2, 0]) cylinder(d = w, h = h);
}
module oblong_x(l, w, h) { rotate([0, 0, 90]) oblong(l, w, h); }

// ---------- Plaque principale (orientation montage) ----------
module chassis() {
    difference() {
        union() {
            plaque_arrondie(plaque_l, plaque_L, plaque_ep, coin_r);
            // glissières des moteurs (sous la plaque)
            for (s = [-1, 1]) {
                // rail intérieur
                translate([s*(moteur_x - moteur_ep/2 - 0.2) - (s > 0 ? 3 : 0), moteur_y_av - moteur_L, -10])
                    cube([3, moteur_L, 10]);
                // butée avant
                translate([s > 0 ? moteur_x - moteur_ep/2 - 3.2 : -plaque_l/2, moteur_y_av, -10])
                    cube([moteur_ep + 3.2, 3, 10]);
            }
            // bloc de la roue folle
            translate([0, roulette_y, -(H_plaque - roulette_h)])
                linear_extrude(H_plaque - roulette_h) offset(4)
                    square([roulette_entraxe + 6, 12], center = true);
        }
        // fentes de serre-câbles pour les moteurs + encoches au bord
        for (s = [-1, 1]) for (y = [axe_y - 20, axe_y - 48]) {
            translate([s*(moteur_x - moteur_ep/2 - 6), y, -20]) oblong(5, 2.8, 40);
            translate([s*plaque_l/2, y, -20]) cube([3, 5, 40], center = true);
        }
        // trous pilotes de la roue folle
        for (s = [-1, 1]) translate([s*roulette_entraxe/2, roulette_y, -H_plaque])
            cylinder(d = m3_pilote, h = H_plaque - roulette_h + 1 - 3 + 12);
        // grille M3 (fixation libre : breadboard, batterie, TB6612...)
        for (x = [-40 : 10 : 40]) for (y = [-60 : 10 : 60])
            translate([x, y, -1]) cylinder(d = m3, h = plaque_ep + 2);
        // fixation de la barre capteurs
        for (p = barre_fix) translate([p[0], p[1], -1]) cylinder(d = m3, h = plaque_ep + 2);
        // fixation du support HC-SR04
        for (x = [-18, 18]) translate([x, plaque_L/2 - 12, -1]) cylinder(d = m3, h = plaque_ep + 2);
        // passages de fils
        translate([0, plaque_L/2 - 22, -1]) oblong_x(30, 8, plaque_ep + 2);   // capteurs
        for (s = [-1, 1]) translate([s*46, axe_y + 20, -1]) oblong(16, 6, plaque_ep + 2); // moteurs
        // découpe de l'interrupteur
        translate([52, -70, plaque_ep/2]) cube([inter_l, inter_h, plaque_ep + 2], center = true);
    }
}

// ---------- Barre des 5 capteurs ----------
module barre() {
    difference() {
        translate([0, (barre_fix[0][1] + barre_y)/2, 0])
            linear_extrude(barre_ep) offset(5)
                square([110 - 10, (barre_y - barre_fix[0][1]) + 14 - 10], center = true);
        for (p = barre_fix) translate([p[0], p[1], -1]) cylinder(d = m3, h = barre_ep + 2);
        for (i = [-2 : 2]) translate([i*capteur_pas, barre_y, -1]) oblong(8, m3, barre_ep + 2);
    }
}

module entretoise() {
    difference() { cylinder(d = 8, h = entretoise_h); translate([0, 0, -1]) cylinder(d = m3, h = entretoise_h + 2); }
}

// ---------- Support HC-SR04 (posé sur le dessus, à l'avant) ----------
hc_l = 50; hc_h = 26; hc_ep = 3; hc_base = 16;
module hcsr04() {
    difference() {
        union() {
            cube([hc_l, hc_ep, hc_h]);                         // face avant
            cube([hc_l, hc_base, hc_ep]);                      // semelle
            for (x = [2, hc_l - 5]) hull() {                   // goussets
                translate([x, 0, 0]) cube([3, hc_base, hc_ep]);
                translate([x, 0, 0]) cube([3, hc_ep, hc_h - 4]);
            }
        }
        for (s = [-1, 1]) translate([hc_l/2 + s*hc_entraxe/2, -1, hc_h/2 + 1])
            rotate([-90, 0, 0]) cylinder(d = hc_trou_d, h = hc_ep + 2);
        for (s = [-1, 1]) translate([hc_l/2 + s*18, hc_base/2 + 2, -1]) cylinder(d = m3, h = hc_ep + 2);
    }
}

// ---------- Aperçu des composants (non imprimés) ----------
module fantomes() {
    for (s = [-1, 1]) {
        color("gold") translate([s*moteur_x - moteur_ep/2, moteur_y_av - moteur_L, -moteur_h])
            cube([moteur_ep, moteur_L, moteur_h]);
        color("dimgray") translate([s*(plaque_l/2 + 16), axe_y, -moteur_h/2])
            rotate([0, 90, 0]) cylinder(d = roue_d, h = 26, center = true);
    }
    color("silver") translate([0, roulette_y, -H_plaque + roulette_h/2]) sphere(d = roulette_h * 0.8);
    color("white") translate([-41, 15, plaque_ep]) cube([82, 55, 9]);              // breadboard
    color("teal")  translate([-9, 22, plaque_ep + 9]) cube([18, 45, 4]);           // Nano ESP32
    color("black") translate([-21, -84, plaque_ep]) cube([42, 65, 3]);             // boîtier 2x18650
    color("seagreen") for (x = [-10, 10]) translate([x, -51.5, plaque_ep + 12]) rotate([90, 0, 0]) cylinder(d = 18, h = 65, center = true);
    color("dimgray") translate([-27, -22, plaque_ep]) cube([54, 10, 3]);              // WS2812 (repère)
    color("darkgreen") for (i = [-2 : 2])
        translate([i*capteur_pas - 5, barre_y - 18, -(H_plaque - capteur_hauteur) - 9]) cube([10, 30, 1.6]);
}

// ---------- Sélection ----------
if (PART == "chassis") {
    rotate([180, 0, 0]) translate([0, 0, -plaque_ep]) chassis();     // dessus sur le plateau
} else if (PART == "barre") {
    barre();
} else if (PART == "entretoise") {
    entretoise();
} else if (PART == "hcsr04") {
    rotate([90, 0, 0]) hcsr04();                                       // face avant sur le plateau
} else {
    color("burlywood") chassis();
    color("tan") translate([0, 0, -(H_plaque - capteur_hauteur)]) barre();
    color("tan") for (p = barre_fix) translate([p[0], p[1], -entretoise_h]) entretoise();
    color("tan") translate([hc_l/2, plaque_L/2 - 12 + hc_base/2 + 2, plaque_ep]) rotate([0, 0, 180]) hcsr04();
    %fantomes();
}
