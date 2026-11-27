# main.py — Suivi de ligne + arrêt devant un obstacle.
# 5 capteurs IR + 2 moteurs + potentiomètre + capteur ultrason HC-SR04 + LED RVB d'état
# + matrice de DEL 8x8 Keyestudio (HT16K33) en I2C.
# Alimentation : batterie externe USB (5 V) branchée dans le port USB du Nano.
#
# Branchements :
#   Capteurs (gauche -> droite) : S1 -> A0, S2 -> A1, S3 -> A2, S4 -> A3, S5 -> A4
#                                 V -> 3V3 (rail +), G -> GND (rail -)
#   Potentiomètre : gauche -> 3V3, milieu -> A6, droite -> GND
#   HC-SR04 : VCC -> 3V3, GND -> GND, TRIG -> D10, ECHO -> D11
#   LED RVB (cathode commune) : R -> 220 Ω -> D1, G -> 100 Ω -> A7, B -> 100 Ω -> D6,
#                               patte la plus longue -> GND
#   Matrice 8x8 I2C : VCC -> 3V3 (ou VBUS 5 V), GND -> GND, SDA -> A5, SCL -> D12
#   TB6612 : VM -> VBUS (USB) ou batterie, VCC et STBY -> 3V3, GND -> GND
#            D3 -> PWMA, D4 -> AIN1, D5 -> AIN2 (moteur gauche sur AO1/AO2)
#            D9 -> PWMB, D7 -> BIN1, D8 -> BIN2 (moteur droit sur BO1/BO2)
# Ctrl+C pour arrêter.

from machine import Pin, PWM, ADC, I2C, time_pulse_us
from time import ticks_ms, ticks_diff, sleep_ms, sleep_us

# ---------- Broches (numéros GPIO) ----------
SENSOR_PINS = (1, 2, 3, 4, 11)  # A0, A1, A2, A3, A4 (de gauche à droite)
POT_PIN = 13                    # A6
TRIG_PIN = 21                   # D10
ECHO_PIN = 38                   # D11
LED_R, LED_G, LED_B = 43, 14, 9 # D1, A7, D6 (rouge déplacé de D13 vers D1)
I2C_SDA, I2C_SCL = 12, 47       # A5, D12
PWMA, AIN1, AIN2 = 6, 7, 8      # D3, D4, D5
PWMB, BIN1, BIN2 = 18, 10, 17   # D9, D7, D8

# ---------- Réglages ----------
WEIGHTS = (-2, -1, 0, 1, 2)     # poids de chaque capteur
KP = 22                         # force de la correction (à ajuster sur la piste)
MIN_SPEED = 25                  # % : sous cette valeur les moteurs TT calent (mesuré)
LINE_LOST_MS = 400              # temps de recherche avant d'arrêter
SEARCH_SPEED = 35               # % pendant la recherche de la ligne
LEFT_TRIM = 1.0                 # facteur du moteur gauche (baisser si trop rapide)
RIGHT_TRIM = 1.0                # facteur du moteur droit (baisser si trop rapide)

OBSTACLE_CM = 15                # on s'arrête sous cette distance
CLEAR_CM = 22                   # on repart au-dessus (hystérésis : évite les à-coups)
ULTRASONIC_PERIOD_MS = 60       # une mesure toutes les 60 ms
ECHO_TIMEOUT_US = 5000          # environ 85 cm : au-delà, la voie est libre
MAX_ECHO_FAILURES = 10          # mesures sans écho d'affilée = capteur débranché

PRINT_PERIOD_MS = 300
DISPLAY_PERIOD_MS = 300         # rafraîchissement de la matrice 8x8
MATRIX_ADDR = 0x70              # adresse I2C (interrupteurs A0-A2 à 0 = 0x70)
MATRIX_BRIGHTNESS = 5           # luminosité de 0 à 15
MATRIX_MIRROR = False           # True si les motifs s'affichent à l'envers (miroir)

# Couleur de la LED RVB et clignotement (ms, 0 = fixe) pour chaque état
LED_FOR_STATUS = {
    "SUIVI":        ("green", 0),
    "RECHERCHE":    ("orange", 0),
    "OBSTACLE":     ("orange", 0),
    "LIGNE PERDUE": ("orange", 250),
    "ARRÊT":        ("blue", 0),
    "ERREUR":       ("red", 150),
}


class Motor:
    def __init__(self, pwm_pin, in1_pin, in2_pin, trim=1.0):
        self.pwm = PWM(Pin(pwm_pin), freq=1000, duty_u16=0)
        self.in1 = Pin(in1_pin, Pin.OUT, value=0)
        self.in2 = Pin(in2_pin, Pin.OUT, value=0)
        self.trim = trim

    def set_speed(self, speed):
        """speed : -100 (arrière) à 100 (avant), 0 = arrêt"""
        speed = max(-100, min(100, int(speed * self.trim)))
        self.in1.value(1 if speed > 0 else 0)
        self.in2.value(1 if speed < 0 else 0)
        self.pwm.duty_u16(abs(speed) * 65535 // 100)

    def stop(self):
        self.set_speed(0)


class LineSensors:
    def __init__(self, pins):
        self.pins = [Pin(p, Pin.IN) for p in pins]
        self.states = [0] * len(pins)

    def read(self):
        self.states = [p.value() for p in self.pins]   # 1 = ligne noire
        return self.states

    def position(self):
        """-2 (ligne à gauche) à +2 (ligne à droite), None si aucune ligne vue."""
        active = sum(self.states)
        if active == 0:
            return None
        return sum(w for w, s in zip(WEIGHTS, self.states) if s) / active


class Potentiometer:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin), atten=ADC.ATTN_11DB)

    def percent(self):
        return self.adc.read_u16() * 100 // 65535


class Ultrasonic:
    """HC-SR04 : une mesure toutes les ULTRASONIC_PERIOD_MS (non bloquant entre les mesures)."""

    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT, value=0)
        self.echo = Pin(echo_pin, Pin.IN)
        self.distance = None        # cm ; None = rien de proche
        self.failures = 0
        self.last_measure = ticks_ms()

    def update(self, now):
        if ticks_diff(now, self.last_measure) < ULTRASONIC_PERIOD_MS:
            return
        self.last_measure = now
        self.trig.value(1)
        sleep_us(10)
        self.trig.value(0)
        duration = time_pulse_us(self.echo, 1, ECHO_TIMEOUT_US)   # bloque 5 ms au plus
        if duration == -2:          # l'écho n'a jamais commencé : capteur débranché ?
            self.failures += 1
            self.distance = None
        elif duration == -1:        # écho trop long : rien de proche, voie libre
            self.failures = 0
            self.distance = None
        else:
            self.failures = 0
            d = duration * 0.0343 / 2
            self.distance = d if 2 <= d <= 400 else None

    def missing(self):
        return self.failures >= MAX_ECHO_FAILURES


class RgbLed:
    """LED RGB à cathode commune : chaque couleur est allumée (1) ou éteinte (0)."""

    COLORS = {
        "off":    (0, 0, 0),
        "red":    (1, 0, 0),
        "green":  (0, 1, 0),
        "blue":   (0, 0, 1),
        "orange": (1, 1, 0),   # rouge + vert
    }

    def __init__(self, r_pin, g_pin, b_pin):
        self.r = Pin(r_pin, Pin.OUT, value=0)
        self.g = Pin(g_pin, Pin.OUT, value=0)
        self.b = Pin(b_pin, Pin.OUT, value=0)

    def show(self, color, now=0, blink_ms=0):
        if blink_ms and (now // blink_ms) % 2:   # moitié « éteinte » du clignotement
            color = "off"
        r, g, b = self.COLORS[color]
        self.r.value(r)
        self.g.value(g)
        self.b.value(b)


# Motifs 8x8 (une ligne = un octet, bit 7 = colonne de gauche)
PATTERNS = {
    "straight": (0b00011000, 0b00111100, 0b01111110, 0b11011011,
                 0b00011000, 0b00011000, 0b00011000, 0b00011000),   # flèche vers l'avant
    "left":     (0b00010000, 0b00110000, 0b01110000, 0b11111111,
                 0b11111111, 0b01110000, 0b00110000, 0b00010000),   # flèche à gauche
    "right":    (0b00001000, 0b00001100, 0b00001110, 0b11111111,
                 0b11111111, 0b00001110, 0b00001100, 0b00001000),   # flèche à droite
    "stop":     (0b10000001, 0b01000010, 0b00100100, 0b00011000,
                 0b00011000, 0b00100100, 0b01000010, 0b10000001),   # X (obstacle)
    "lost":     (0b00111100, 0b01100110, 0b00000110, 0b00001100,
                 0b00011000, 0b00011000, 0b00000000, 0b00011000),   # ?
    "pause":    (0b00000000, 0b01100110, 0b01100110, 0b01100110,
                 0b01100110, 0b01100110, 0b01100110, 0b00000000),   # || (arrêt)
    "error":    (0b00011000, 0b00011000, 0b00011000, 0b00011000,
                 0b00011000, 0b00000000, 0b00011000, 0b00011000),   # !
    "blank":    (0,) * 8,
}


class MatrixDisplay:
    """Matrice de DEL 8x8 Keyestudio (puce HT16K33) en I2C.
    Si la matrice est absente, le robot continue sans elle."""

    def __init__(self, sda_pin, scl_pin, addr):
        self.i2c = None
        self.addr = addr
        self.previous = None
        try:
            i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
            found = i2c.scan()
            print("Appareils I2C trouvés :", [hex(a) for a in found])
            if addr not in found:
                print("Matrice 8x8 introuvable à", hex(addr), ": vérifier SDA, SCL, VCC, GND et les interrupteurs d'adresse")
                return
            i2c.writeto(addr, bytes((0x21,)))                       # démarre l'oscillateur
            i2c.writeto(addr, bytes((0x81,)))                       # affichage allumé, sans clignotement
            i2c.writeto(addr, bytes((0xE0 | MATRIX_BRIGHTNESS,)))   # luminosité 0 à 15
            self.i2c = i2c
            self.draw("blank")
        except Exception as e:
            print("Matrice 8x8 indisponible :", e)
            self.i2c = None

    def draw(self, name):
        """Affiche un motif de PATTERNS (n'envoie rien si c'est déjà le même)."""
        if self.i2c is None or name == self.previous:
            return
        self.previous = name
        data = bytearray(17)            # adresse 0x00 + 8 lignes x 2 octets
        for row, bits in enumerate(PATTERNS[name]):
            if MATRIX_MIRROR:
                bits = int("{:08b}".format(bits)[::-1], 2)
            data[1 + 2 * row] = bits
        self.i2c.writeto(self.addr, data)

    def show(self, status, position):
        if status == "SUIVI":
            if position is not None and position <= -1:
                self.draw("left")
            elif position is not None and position >= 1:
                self.draw("right")
            else:
                self.draw("straight")
        elif status == "RECHERCHE":
            self.draw("lost")
        elif status == "OBSTACLE":
            self.draw("stop")
        elif status == "LIGNE PERDUE":
            self.draw("lost")
        elif status.startswith("ERREUR"):
            self.draw("error")
        else:
            self.draw("pause")

    def clear(self):
        self.draw("blank")


left = Motor(PWMA, AIN1, AIN2, LEFT_TRIM)
right = Motor(PWMB, BIN1, BIN2, RIGHT_TRIM)
sensors = LineSensors(SENSOR_PINS)
pot = Potentiometer(POT_PIN)
ultrasonic = Ultrasonic(TRIG_PIN, ECHO_PIN)
led = RgbLed(LED_R, LED_G, LED_B)
display = MatrixDisplay(I2C_SDA, I2C_SCL, MATRIX_ADDR)

last_position = 0
t_line_seen = ticks_ms()
t_print = ticks_ms()
t_display = ticks_ms()
line_stopped = False
obstacle = False

print("Suivi de ligne + obstacle : pose le robot sur la ligne (Ctrl+C pour arrêter)")

try:
    while True:
        now = ticks_ms()
        sensors.read()
        ultrasonic.update(now)
        position = sensors.position()
        pot_pct = pot.percent()
        base = 0 if pot_pct < 5 else max(MIN_SPEED, pot_pct)   # 0 % = robot arrêté

        # Obstacle avec hystérésis : arrêt sous 15 cm, reprise au-dessus de 22 cm
        d = ultrasonic.distance
        if d is not None and d < OBSTACLE_CM:
            obstacle = True
        elif d is None or d > CLEAR_CM:
            obstacle = False

        if position is not None:
            # Ligne vue : correction proportionnelle
            last_position = position
            t_line_seen = now
            line_stopped = False
            correction = KP * position
            left_speed = base + correction
            right_speed = base - correction
            status = "SUIVI"
        elif ticks_diff(now, t_line_seen) < LINE_LOST_MS and not line_stopped:
            # Ligne perdue depuis peu : on tourne du côté où on l'a vue en dernier
            if last_position < 0:
                left_speed, right_speed = -SEARCH_SPEED, SEARCH_SPEED
            elif last_position > 0:
                left_speed, right_speed = SEARCH_SPEED, -SEARCH_SPEED
            else:
                left_speed, right_speed = SEARCH_SPEED, SEARCH_SPEED
            status = "RECHERCHE"
        else:
            line_stopped = True
            left_speed = right_speed = 0
            status = "LIGNE PERDUE"

        # Les arrêts de sécurité passent avant le suivi
        if False and ultrasonic.missing():
            left_speed = right_speed = 0
            status = "ERREUR : HC-SR04 ne répond pas"
        elif obstacle:
            left_speed = right_speed = 0
            t_line_seen = now               # ne pas compter l'arrêt comme une ligne perdue
            status = "OBSTACLE"
        elif base == 0:
            left_speed = right_speed = 0
            status = "ARRÊT (potentiomètre à 0)"

        left.set_speed(left_speed)
        right.set_speed(right_speed)

        # LED RVB : couleur selon l'état (on prend le premier mot, ex. « ERREUR : ... » -> ERREUR)
        key = status.split(" :")[0].split(" (")[0]
        color, blink = LED_FOR_STATUS.get(key, ("off", 0))
        led.show(color, now, blink)

        if ticks_diff(now, t_display) >= DISPLAY_PERIOD_MS:
            t_display = now
            display.show(status, position)

        if ticks_diff(now, t_print) >= PRINT_PERIOD_MS:
            t_print = now
            print("capteurs={}  pos={:>5}  dist={:>6}  pot={:3d}%  G={:4d}%  D={:4d}%  {}".format(
                "".join(str(s) for s in sensors.states),
                "--" if position is None else "{:+.1f}".format(position),
                "--" if d is None else "{:.0f}cm".format(d),
                pot_pct, int(max(-100, min(100, left_speed))),
                int(max(-100, min(100, right_speed))), status))
        sleep_ms(5)
except KeyboardInterrupt:
    print("Arrêt demandé")
finally:
    left.stop()
    right.stop()
    led.show("off")
    display.clear()
    print("Moteurs arrêtés")
