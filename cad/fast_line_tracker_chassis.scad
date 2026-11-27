// =====================================================================
//  Fast line tracker - châssis imprimable 3D (420-314) - version 2
//  Cotes mesurées par David le 27 novembre 2026.
//  Unités : mm.  Avant du robot = +Y.  Dessus de la plaque = +Z.
//
//  Choisir la pièce à exporter avec la variable PART :
//    "assemblage"      aperçu de toutes les pièces en position
//    "chassis"         plaque principale (déjà retournée pour l'impression)
//    "barre"           barre des 5 capteurs de ligne
//    "entretoise"      entretoise de la barre capteurs (en imprimer 2)
//    "hcsr04"          support du capteur ultrason
//    "support_matrice" support incliné de la matrice 8x8
//    "cale_roulette"   cale de la roue folle (à imprimer quand on l'aura)
// =====================================================================

PART = "assemblage";

// ---------- Plaque ----------
plaque_l   = 150;     // largeur (X)
plaque_L   = 180;     // longueur (Y)
plaque_ep  = 4;       // épaisseur
coin_r     = 12;

// ---------- Roues et moteurs TT (mesurés) ----------
roue_d          = 65.57;
roue_largeur    = 25.13;
moteur_L        = 61.98;   // longueur réducteur + moteur
moteur_h        = 22.35;   // hauteur (verticale une fois monté)
moteur_ep       = 19.04;   // épaisseur (dans le sens de l'axe)
axe_depuis_bout = 10.45;   // A : bout du réducteur -> centre de l'axe
trous_axe       = 17.68;   // C : centre de l'axe -> centre des trous
trous_entraxe   = 14.78;   // B : distance entre les 2 trous (verticale)
trou_moteur_d   = 2.5;     // trou mesuré ~2,26 mm -> vis M2
axe_y           = 10;      // position Y de l'axe des roues sur la plaque

// ---------- Capteurs de ligne Keyestudio (mesurés) ----------
capt_L        = 41.65;     // longueur du circuit
capt_W        = 10.45;     // largeur du circuit
capt_trou1    = 26.49;     // bout côté broches -> trou 1
capt_trou2    = 37.70;     // bout côté broches -> trou 2
capt_ir       = 8.33;      // bout côté capteur -> centre du capteur IR
capt_ir_h     = 5.6;       // face du circuit -> bout du capteur IR
pcb_ep        = 1.6;       // épaisseur du circuit
ir_sol        = 8;         // hauteur voulue du bout du capteur IR au-dessus du sol
capteur_pas   = 18;        // espacement entre les capteurs (ligne de ~19 mm)
barre_ep      = 4;

// ---------- HC-SR04 (mesuré) ----------
hc_entraxe    = 27.11;     // distance entre les centres des yeux
hc_trou_d     = 16.6;      // yeux de 15,86 mm + jeu
hc_vis_L      = 41.65;     // entraxe des vis du circuit (horizontal)
hc_vis_H      = 16.70;     // entraxe des vis du circuit (vertical)

// ---------- Matrice 8x8 (mesurée) ----------
mat_L         = 51.81;
mat_W         = 32.37;
mat_entraxe   = 21.63;     // entraxe des trous de fixation

// ---------- Roue folle (à mesurer quand elle arrivera) ----------
roulette_h       = 20;     // hauteur totale de la roue folle
roulette_entraxe = 25;     // entraxe de ses 2 trous
roulette_y       = -75;

m3        = 3.3;   // passage de vis M3
m3_pilote = 2.8;   // vis M3 autotaraudeuse dans le plastique
$fn = 48;

// ---------- Valeurs calculées ----------
H_plaque     = roue_d / 2 + moteur_h / 2;                 // dessous de plaque -> sol
barre_sol    = ir_sol + capt_ir_h + pcb_ep;               // dessous de la barre -> sol
entretoise_h = H_plaque - barre_sol - barre_ep;
moteur_x     = plaque_l / 2 - moteur_ep / 2;              // centre du moteur en X
moteur_y_av  = axe_y + axe_depuis_bout;                   // bout avant (réducteur)
trous_y      = axe_y - trous_axe;                         // Y des trous du moteur
barre_y      = plaque_L / 2 + 10;                         // ligne des capteurs IR
barre_fix    = [[-50, plaque_L / 2 - 6], [50, plaque_L / 2 - 6]];
hc_fix_y     = plaque_L / 2 - 12;
cale_h       = H_plaque - roulette_h;

echo(str("Dessous de plaque / sol = ", H_plaque, " mm"));
echo(str("Entretoises capteurs = ", entretoise_h, " mm"));
echo(str("Cale de roue folle = ", cale_h, " mm"));
echo(str("Capteurs IR devant l'axe = ", barre_y - axe_y, " mm"));

// ---------- Outils ----------
module plaque_arrondie(l, L, ep, r) {
    linear_extrude(ep) offset(r) square([l - 2 * r, L - 2 * r], center = true);
}
module oblong(l, w, h) {           // trou oblong le long de Y
    hull() for (s = [-1, 1]) translate([0, s * (l - w) / 2, 0]) cylinder(d = w, h = h);
}
module oblong_x(l, w, h) { rotate([0, 0, 90]) oblong(l, w, h); }

// ---------- Plaque principale ----------
module chassis() {
    rail_x = moteur_x - moteur_ep / 2 - 0.3;               // face intérieure du moteur
    difference() {
        union() {
            plaque_arrondie(plaque_l, plaque_L, plaque_ep, coin_r);
            for (s = [-1, 1]) {
                // Support vertical du moteur (vissé avec 2 vis M2)
                translate([s > 0 ? rail_x - 4 : -rail_x, moteur_y_av - moteur_L + 4, -moteur_h])
                    cube([4, moteur_L - 4, moteur_h]);
                // Butée avant
                translate([s > 0 ? rail_x - 4 : -plaque_l / 2, moteur_y_av, -8])
                    cube([moteur_ep + 4.3, 3, 8]);
            }
        }
        // Trous M2 du moteur dans le support (même position que les trous du moteur)
        for (s = [-1, 1]) for (dz = [-1, 1])
            translate([s * (rail_x - 6), trous_y, -moteur_h / 2 + dz * trous_entraxe / 2])
                rotate([0, 90, 0]) cylinder(d = trou_moteur_d, h = 12, center = true);
        // Fentes de serre-câbles (arrière du moteur, hors de la zone de la roue)
        for (s = [-1, 1]) for (y = [axe_y - roue_d / 2 - 5, moteur_y_av - moteur_L + 4]) {
            translate([s * (rail_x - 7), y, -1]) oblong(5, 2.8, plaque_ep + 2);
            translate([s * plaque_l / 2, y, plaque_ep / 2]) cube([3, 5, plaque_ep + 2], center = true);
        }
        // Grille M3 au pas de 10 mm (breadboard, batterie externe, matrice, serre-câbles)
        for (x = [-40 : 10 : 40]) for (y = [-60 : 10 : 60])
            translate([x, y, -1]) cylinder(d = m3, h = plaque_ep + 2);
        // Fixation de la barre capteurs
        for (p = barre_fix) translate([p[0], p[1], -1]) cylinder(d = m3, h = plaque_ep + 2);
        // Fixation du support HC-SR04
        for (x = [-18, 18]) translate([x, hc_fix_y, -1]) cylinder(d = m3, h = plaque_ep + 2);
        // Fixation de la cale de roue folle (2 vis M3 par le dessus)
        for (dy = [-9, 9]) translate([0, roulette_y + dy, -1]) cylinder(d = m3, h = plaque_ep + 2);
        // Passages de fils
        translate([0, plaque_L / 2 - 23, -1]) oblong_x(30, 8, plaque_ep + 2);
        for (s = [-1, 1]) translate([s * 47, axe_y + 22, -1]) oblong(16, 6, plaque_ep + 2);
    }
}

// ---------- Barre des capteurs ----------
// Les circuits sont vissés SOUS la barre, dos à plat, composants vers le sol.
// Broches vers l'arrière, capteur IR vers l'avant.
module barre() {
    y_min = barre_fix[0][1] - 7;
    y_max = barre_y + capt_ir + 2;
    difference() {
        translate([-58, y_min, 0]) cube([116, y_max - y_min, barre_ep]);
        for (p = barre_fix) translate([p[0], p[1], -1]) cylinder(d = m3, h = barre_ep + 2);
        for (i = [-2 : 2]) {
            x = i * capteur_pas;
            // 2 trous par capteur (trous oblongs : ±1,5 mm de réglage)
            for (t = [capt_trou1, capt_trou2]) {
                y = barre_y + capt_ir - (capt_L - t);
                translate([x, y, -1]) hull() for (dx = [-1.2, 1.2]) translate([dx, 0, 0]) cylinder(d = m3, h = barre_ep + 2);
            }
            // fenêtre au-dessus du potentiomètre de réglage (accès au tournevis)
            translate([x, barre_y + capt_ir - capt_L + 16, -1]) oblong(8, 6, barre_ep + 2);
        }
    }
}

module entretoise() {
    difference() { cylinder(d = 8, h = entretoise_h); translate([0, 0, -1]) cylinder(d = m3, h = entretoise_h + 2); }
}

// ---------- Support HC-SR04 ----------
hc_l = 50; hc_h = 32; hc_ep = 3; hc_base = 16;
module hcsr04() {
    zc = hc_ep + 14;                   // hauteur du centre des yeux
    difference() {
        union() {
            cube([hc_l, hc_ep, hc_h]);
            cube([hc_l, hc_base, hc_ep]);
            for (x = [0, hc_l - 3]) hull() {
                translate([x, 0, 0]) cube([3, hc_base, hc_ep]);
                translate([x, 0, 0]) cube([3, hc_ep, hc_h - 6]);
            }
        }
        for (s = [-1, 1]) translate([hc_l / 2 + s * hc_entraxe / 2, -1, zc]) rotate([-90, 0, 0]) cylinder(d = hc_trou_d, h = hc_ep + 2);
        // 4 petits trous pour les vis du circuit (M2) ou des serre-câbles
        for (sx = [-1, 1]) for (sz = [-1, 1])
            translate([hc_l / 2 + sx * hc_vis_L / 2, -1, zc + sz * hc_vis_H / 2]) rotate([-90, 0, 0]) cylinder(d = 2.2, h = hc_ep + 2);
        for (s = [-1, 1]) translate([hc_l / 2 + s * 18, hc_base / 2 + 2, -1]) cylinder(d = m3, h = hc_ep + 2);
    }
}

// ---------- Support de la matrice 8x8 (incliné à 60°) ----------
sm_l = mat_L + 8; sm_h = mat_W + 8; sm_ep = 3; sm_base = 22;
module support_matrice() {
    difference() {
        union() {
            cube([sm_l, sm_base, sm_ep]);                                     // semelle
            translate([0, sm_base, 0]) rotate([60, 0, 0]) cube([sm_l, sm_h, sm_ep]);  // face inclinée
            for (x = [0, sm_l - 3]) hull() {                                  // goussets
                translate([x, 0, 0]) cube([3, sm_base, sm_ep]);
                translate([x, sm_base, 0]) rotate([60, 0, 0]) cube([3, sm_h * 0.8, sm_ep]);
            }
        }
        // 2 paires de trous à 21,63 mm (horizontale et verticale) : selon l'orientation des trous de la matrice
        translate([0, sm_base, 0]) rotate([60, 0, 0]) {
            for (s = [-1, 1]) translate([sm_l / 2 + s * mat_entraxe / 2, sm_h / 2, -1]) cylinder(d = m3, h = sm_ep + 2);
            for (s = [-1, 1]) translate([sm_l / 2, sm_h / 2 + s * mat_entraxe / 2, -1]) cylinder(d = m3, h = sm_ep + 2);
        }
        // fixation à la grille (pas de 10 mm -> entraxe 40 mm)
        for (s = [-1, 1]) translate([sm_l / 2 + s * 20, 8, -1]) cylinder(d = m3, h = sm_ep + 2);
    }
}

// ---------- Cale de la roue folle ----------
module cale_roulette() {
    prof = min(10, cale_h / 2 - 1);
    difference() {
        translate([-(roulette_entraxe / 2 + 6), -14, 0]) cube([roulette_entraxe + 12, 28, cale_h]);
        // vis de la roue folle (par le dessous)
        for (s = [-1, 1]) translate([s * roulette_entraxe / 2, 0, -1]) cylinder(d = m3_pilote, h = prof + 1);
        // vis de fixation à la plaque (par le dessus)
        for (dy = [-9, 9]) translate([0, dy, cale_h - prof]) cylinder(d = m3_pilote, h = prof + 1);
    }
}

// ---------- Aperçu des composants (non imprimés) ----------
module fantomes() {
    for (s = [-1, 1]) {
        color("gold") translate([s * moteur_x - moteur_ep / 2, moteur_y_av - moteur_L, -moteur_h])
            cube([moteur_ep, moteur_L, moteur_h]);
        color("dimgray") translate([s * (plaque_l / 2 + 4 + roue_largeur / 2), axe_y, -moteur_h / 2])
            rotate([0, 90, 0]) cylinder(d = roue_d, h = roue_largeur, center = true);
    }
    color("silver") translate([0, roulette_y, -H_plaque + roulette_h / 2]) sphere(d = roulette_h * 0.8);
    color("white") translate([-41, 5, plaque_ep]) cube([82, 55, 9]);                          // breadboard
    color("teal")  translate([-9, 12, plaque_ep + 9]) cube([18, 45, 4]);                      // Nano ESP32
    color("darkgreen") for (i = [-2 : 2])
        translate([i * capteur_pas - capt_W / 2, barre_y + capt_ir - capt_L, -(H_plaque - barre_sol) - pcb_ep])
            cube([capt_W, capt_L, pcb_ep]);
}

// ---------- Sélection ----------
if (PART == "chassis") {
    rotate([180, 0, 0]) translate([0, 0, -plaque_ep]) chassis();
} else if (PART == "barre") {
    barre();
} else if (PART == "entretoise") {
    entretoise();
} else if (PART == "hcsr04") {
    rotate([90, 0, 0]) hcsr04();
} else if (PART == "support_matrice") {
    support_matrice();
} else if (PART == "cale_roulette") {
    cale_roulette();
} else {
    color("burlywood") chassis();
    color("tan") translate([0, 0, -(H_plaque - barre_sol)]) barre();
    color("tan") for (p = barre_fix) translate([p[0], p[1], -entretoise_h]) entretoise();
    color("tan") translate([hc_l / 2, hc_fix_y + hc_base / 2 + 2, plaque_ep]) rotate([0, 0, 180]) hcsr04();
    color("tan") translate([-sm_l / 2, -48, plaque_ep]) support_matrice();
    color("tan") translate([0, roulette_y, -cale_h]) cale_roulette();
    %fantomes();
}
