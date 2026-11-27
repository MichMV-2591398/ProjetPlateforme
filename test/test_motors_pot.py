# test_motors_pot.py — Le potentiomètre contrôle la vitesse des 2 moteurs.
# La vitesse est affichée dans la console.
#
# Branchements :
#   Potentiomètre : patte gauche -> 3V3, patte du milieu -> A6, patte droite -> GND
#   TB6612 : VM -> VBUS (test USB) ou batterie, VCC et STBY -> 3V3, GND -> GND
#   Moteur gauche : D3 -> PWMA, D4 -> AIN1, D5 -> AIN2, moteur sur AO1/AO2
#   Moteur droit  : D9 -> PWMB, D7 -> BIN1, D8 -> BIN2, moteur sur BO1/BO2
# Surélève le robot : les roues doivent tourner dans le vide. Ctrl+C pour arrêter.

from machine import Pin, PWM, ADC
from time import ticks_ms, ticks_diff, sleep_ms

POT_PIN = 13                    # A6
PWMA, AIN1, AIN2 = 6, 7, 8      # D3, D4, D5
PWMB, BIN1, BIN2 = 18, 10, 17   # D9, D7, D8

DEAD_ZONE = 5          # % : en dessous, les moteurs restent arrêtés
STALL_SPEED = 25       # % : en dessous, les moteurs TT risquent de ne pas tourner
PRINT_PERIOD_MS = 300


class Motor:
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm = PWM(Pin(pwm_pin), freq=1000, duty_u16=0)
        self.in1 = Pin(in1_pin, Pin.OUT, value=0)
        self.in2 = Pin(in2_pin, Pin.OUT, value=0)

    def set_speed(self, speed):
        """speed : -100 (arrière) à 100 (avant), 0 = arrêt"""
        speed = max(-100, min(100, speed))
        self.in1.value(1 if speed > 0 else 0)
        self.in2.value(1 if speed < 0 else 0)
        self.pwm.duty_u16(abs(speed) * 65535 // 100)

    def stop(self):
        self.set_speed(0)


class Potentiometer:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin), atten=ADC.ATTN_11DB)   # 0 à environ 3,1 V
        self.samples = []

    def percent(self):
        """Moyenne des 5 dernières lectures, de 0 à 100 %."""
        self.samples.append(self.adc.read_u16())
        if len(self.samples) > 5:
            self.samples.pop(0)
        average = sum(self.samples) // len(self.samples)
        return average * 100 // 65535


left = Motor(PWMA, AIN1, AIN2)
right = Motor(PWMB, BIN1, BIN2)
pot = Potentiometer(POT_PIN)

print("Tourne le potentiomètre pour changer la vitesse (Ctrl+C pour arrêter)")
last_print = ticks_ms()

try:
    while True:
        percent = pot.percent()
        speed = 0 if percent < DEAD_ZONE else percent
        left.set_speed(speed)
        right.set_speed(speed)

        now = ticks_ms()
        if ticks_diff(now, last_print) >= PRINT_PERIOD_MS:
            last_print = now
            bar = "#" * (speed // 5)
            if speed == 0:
                note = "(arrêt)"
            elif speed < STALL_SPEED:
                note = "(trop lent : les roues peuvent ne pas tourner)"
            else:
                note = ""
            print("Potentiomètre : {:3d} %  ->  vitesse moteurs : {:3d} %  {:<20} {}".format(
                percent, speed, bar, note))
        sleep_ms(20)
except KeyboardInterrupt:
    print("Arrêt demandé")
finally:
    left.stop()
    right.stop()
    print("Moteurs arrêtés")
