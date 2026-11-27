# test_line_follow.py — Suivi de ligne simple : 5 capteurs IR + 2 moteurs + potentiomètre.
# Le potentiomètre règle la vitesse de base, les capteurs corrigent la direction.
#
# Branchements :
#   Capteurs (gauche -> droite) : S1 -> A0, S2 -> A1, S3 -> A2, S4 -> A3, S5 -> A4
#                                 V -> 3V3 (rail +), G -> GND (rail -)
#   Potentiomètre : gauche -> 3V3, milieu -> A6, droite -> GND
#   TB6612 : VM -> VBUS (USB) ou batterie, VCC et STBY -> 3V3, GND -> GND
#            D3 -> PWMA, D4 -> AIN1, D5 -> AIN2 (moteur gauche sur AO1/AO2)
#            D9 -> PWMB, D7 -> BIN1, D8 -> BIN2 (moteur droit sur BO1/BO2)
# Ctrl+C pour arrêter.

from machine import Pin, PWM, ADC
from time import ticks_ms, ticks_diff, sleep_ms

# ---------- Broches (numéros GPIO) ----------
SENSOR_PINS = (1, 2, 3, 4, 11)  # A0, A1, A2, A3, A4 (de gauche à droite)
POT_PIN = 13                    # A6
PWMA, AIN1, AIN2 = 6, 7, 8      # D3, D4, D5
PWMB, BIN1, BIN2 = 18, 10, 17   # D9, D7, D8

# ---------- Réglages ----------
WEIGHTS = (-2, -1, 0, 1, 2)     # poids de chaque capteur
KP = 22                         # force de la correction (à ajuster sur la piste)
MIN_SPEED = 25                  # % : sous cette valeur les moteurs TT calent
LINE_LOST_MS = 400              # temps de recherche avant d'arrêter
SEARCH_SPEED = 35               # % pendant la recherche de la ligne
PRINT_PERIOD_MS = 300


class Motor:
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm = PWM(Pin(pwm_pin), freq=1000, duty_u16=0)
        self.in1 = Pin(in1_pin, Pin.OUT, value=0)
        self.in2 = Pin(in2_pin, Pin.OUT, value=0)

    def set_speed(self, speed):
        """speed : -100 (arrière) à 100 (avant), 0 = arrêt"""
        speed = max(-100, min(100, int(speed)))
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


left = Motor(PWMA, AIN1, AIN2)
right = Motor(PWMB, BIN1, BIN2)
sensors = LineSensors(SENSOR_PINS)
pot = Potentiometer(POT_PIN)

last_position = 0
t_line_seen = ticks_ms()
t_print = ticks_ms()
stopped = False

print("Suivi de ligne : pose le robot sur la ligne (Ctrl+C pour arrêter)")

try:
    while True:
        now = ticks_ms()
        sensors.read()
        position = sensors.position()
        pot_pct = pot.percent()
        base = 0 if pot_pct < 5 else max(MIN_SPEED, pot_pct)   # 0 % = robot arrêté

        if position is not None:
            # Ligne vue : correction proportionnelle
            last_position = position
            t_line_seen = now
            stopped = False
            correction = KP * position
            left_speed = base + correction
            right_speed = base - correction
            status = "SUIVI"
        elif ticks_diff(now, t_line_seen) < LINE_LOST_MS and not stopped:
            # Ligne perdue depuis peu : on tourne du côté où on l'a vue en dernier
            if last_position < 0:
                left_speed, right_speed = -SEARCH_SPEED, SEARCH_SPEED
            elif last_position > 0:
                left_speed, right_speed = SEARCH_SPEED, -SEARCH_SPEED
            else:
                left_speed, right_speed = SEARCH_SPEED, SEARCH_SPEED
            status = "RECHERCHE"
        else:
            # Ligne perdue trop longtemps : arrêt
            stopped = True
            left_speed = right_speed = 0
            status = "LIGNE PERDUE"

        if base == 0:
            left_speed = right_speed = 0
            status = "ARRÊT (potentiomètre à 0)"

        left.set_speed(left_speed)
        right.set_speed(right_speed)

        if ticks_diff(now, t_print) >= PRINT_PERIOD_MS:
            t_print = now
            print("capteurs={}  pos={:>5}  pot={:3d}%  G={:4d}%  D={:4d}%  {}".format(
                "".join(str(s) for s in sensors.states),
                "--" if position is None else "{:+.1f}".format(position),
                pot_pct, int(max(-100, min(100, left_speed))),
                int(max(-100, min(100, right_speed))), status))
        sleep_ms(5)
except KeyboardInterrupt:
    print("Arrêt demandé")
finally:
    left.stop()
    right.stop()
    print("Moteurs arrêtés")
