# main.py — Test simple des 2 moteurs TT (TB6612FNG), sans autre fichier.
# Broches selon le plan électrique. STBY du TB6612 doit être relié au 3V3.
# Surélève le robot : les roues ne doivent pas toucher la table.

from machine import Pin, PWM
from time import sleep_ms

# Moteur gauche : PWMA = D3, AIN1 = D4, AIN2 = D5
# Moteur droit  : PWMB = D9, BIN1 = D7, BIN2 = D8
PWMA, AIN1, AIN2 = 6, 7, 8
PWMB, BIN1, BIN2 = 18, 10, 17


class Motor:
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm = PWM(Pin(pwm_pin), freq=1000, duty_u16=0)
        self.in1 = Pin(in1_pin, Pin.OUT, value=0)
        self.in2 = Pin(in2_pin, Pin.OUT, value=0)

    def set_speed(self, speed):
        """speed de -100 (arrière) à 100 (avant), 0 = arrêt."""
        speed = max(-100, min(100, speed))
        self.in1.value(1 if speed > 0 else 0)
        self.in2.value(1 if speed < 0 else 0)
        self.pwm.duty_u16(abs(speed) * 65535 // 100)

    def stop(self):
        self.set_speed(0)


left = Motor(PWMA, AIN1, AIN2)
right = Motor(PWMB, BIN1, BIN2)


def run(left_speed, right_speed, duration_ms, label):
    print("{:<22} gauche={:>4}%  droit={:>4}%".format(label, left_speed, right_speed))
    left.set_speed(left_speed)
    right.set_speed(right_speed)
    sleep_ms(duration_ms)
    left.stop()
    right.stop()
    sleep_ms(1000)


try:
    run(100, 0, 2000, "Gauche, avant")
    run(-100, 0, 2000, "Gauche, arrière")
    run(0, 100, 2000, "Droit, avant")
    run(0, -100, 2000, "Droit, arrière")
    run(40, 40, 2000, "Les deux, avant")
    run(-40, -40, 2000, "Les deux, arrière")
    print("Test terminé.")
finally:
    left.stop()
    right.stop()
