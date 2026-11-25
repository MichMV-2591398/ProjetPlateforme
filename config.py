# config.py — Toutes les constantes du robot (broches, seuils, vitesses).
# Pour ajuster le comportement, on modifie seulement ce fichier.

from pins import Pins

# ---------------- Capteurs de ligne (de gauche à droite) ----------------
LINE_PINS = (Pins.A0, Pins.A1, Pins.A2, Pins.A3, Pins.A4)
LINE_BLACK = 1                   # valeur lue quand le capteur est au-dessus de la ligne noire
LINE_WEIGHTS = (-2, -1, 0, 1, 2) # poids de chaque capteur pour calculer la position
ALL_BLACK_MS = 300               # 5 capteurs « noirs » plus longtemps que ça = robot soulevé

# ---------------- Moteurs (TB6612FNG, STBY relié au 3V3) ----------------
PWMA, AIN1, AIN2 = Pins.D3, Pins.D4, Pins.D5   # moteur gauche
PWMB, BIN1, BIN2 = Pins.D9, Pins.D7, Pins.D8   # moteur droit
PWM_FREQ = 1000                  # Hz
INVERT_LEFT = False              # mettre True si le moteur tourne à l'envers
INVERT_RIGHT = False
MAX_RAMP = 8                     # variation max de vitesse (%) par mise à jour : évite les chutes de tension
MOTORS_PERIOD_MS = 10

# ---------------- Capteur ultrason HC-SR04 ----------------
TRIG, ECHO = Pins.D10, Pins.D11
ULTRASONIC_PERIOD_MS = 60        # le HC-SR04 a besoin d'environ 60 ms entre deux mesures
ECHO_TIMEOUT_US = 5000           # environ 85 cm : au-delà, la voie est considérée libre
OBSTACLE_DIST_CM = 15            # on s'arrête sous cette distance
CLEAR_DIST_CM = 22               # on repart au-dessus de cette distance (hystérésis)
RESUME_DELAY_MS = 300            # la voie doit rester libre ce temps avant de repartir
MAX_ULTRASONIC_FAILURES = 10     # mesures sans aucun écho d'affilée = capteur débranché

# ---------------- Batterie (diviseur 20 kΩ / 10 kΩ) ----------------
BATTERY_PIN = Pins.A5
DIVIDER_RATIO = 3.0              # (20 k + 10 k) / 10 k
LOW_BATTERY_V = 6.6              # 3,3 V par cellule
NO_BATTERY_V = 1.0               # sous cette valeur : pas de batterie (alimenté par USB)
LOW_BATTERY_DELAY_MS = 2000      # la tension doit rester basse ce temps (évite les fausses alertes)
BATTERY_PERIOD_MS = 200
BATTERY_AVERAGE_COUNT = 10       # moyenne glissante sur 10 mesures
REQUIRE_BATTERY = True           # False : permet de tester sur USB sans batterie (les moteurs restent immobiles)

# ---------------- Potentiomètre (vitesse) ----------------
POT_PIN = Pins.A6
MIN_SPEED = 25                   # % ; en dessous, les moteurs TT calent
MAX_SPEED = 100
POT_DEAD_ZONE = 3                # % ; ignore les petites variations du potentiomètre

# ---------------- Bouton ----------------
BUTTON_PIN = Pins.D2
DEBOUNCE_MS = 50
LONG_PRESS_MS = 1500

# ---------------- LED RVB (cathode commune) ----------------
LED_R, LED_G, LED_B = Pins.D13, Pins.A7, Pins.D6

# ---------------- Barre WS2812B ----------------
STRIP_PIN = Pins.D12
STRIP_COUNT = 8
STRIP_BRIGHTNESS = 0.15          # 15 % : limite le courant sur le rail 3V3

# ---------------- Suivi de ligne ----------------
KP = 22                          # correction (%) par unité de position (-2 à +2)
LINE_LOST_MS = 400               # temps de recherche avant de déclarer la ligne perdue
SEARCH_SPEED = 35                # % pendant la courte recherche de la ligne

# ---------------- Affichage et débogage ----------------
DISPLAY_PERIOD_MS = 50
DEBUG_PERIOD_MS = 500
REFUSED_SIGNAL_MS = 1000         # durée du signal orange quand un démarrage est refusé
