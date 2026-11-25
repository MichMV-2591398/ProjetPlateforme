# test_motors.py — Test des 2 moteurs TT avec le TB6612FNG.
# Branchements : VM -> VBUS (test USB) ou batterie, VCC et STBY -> 3V3, GND -> GND.
#   Moteur gauche : D3 -> PWMA, D4 -> AIN1, D5 -> AIN2, moteur sur AO1/AO2
#   Moteur droit  : D9 -> PWMB, D7 -> BIN1, D8 -> BIN2, moteur sur BO1/BO2
# Surélève le robot : les roues doivent tourner dans le vide.

from machine import Pin, PWM
from time import sleep

PWMA, AIN1, AIN2 = 6, 7, 8      # D3, D4, D5
PWMB, BIN1, BIN2 = 18, 10, 17   # D9, D7, D8
SPEED = 60                      # % ; baisser à 40 si le Nano redémarre sur USB


class Motor:
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm = PWM(Pin(pwm_pin), freq=1000, duty_u16=0)
        self.in1 = Pin(in1_pin, Pin.OUT, value=0)
        self.in2 = Pin(in2_pin, Pin.OUT, value=0)

    def set_speed(self, speed):
        speed = max(-100, min(100, speed))
        self.in1.value(1 if speed > 0 else 0)
        self.in2.value(1 if speed < 0 else 0)
        self.pwm.duty_u16(abs(speed) * 65535 // 100)

    def stop(self):
        self.set_speed(0)


left = Motor(PWMA, AIN1, AIN2)
right = Motor(PWMB, BIN1, BIN2)


def run(left_speed, right_speed, label):
    print(label)
    left.set_speed(left_speed)
    right.set_speed(right_speed)
    sleep(2)
    left.stop()
    right.stop()
    sleep(1)


try:
    run(SPEED, 0, "Moteur gauche : avant")
    run(-SPEED, 0, "Moteur gauche : arrière")
    run(0, SPEED, "Moteur droit : avant")
    run(0, -SPEED, "Moteur droit : arrière")
    run(SPEED, SPEED, "Les deux : avant")
    run(-SPEED, -SPEED, "Les deux : arrière")
    print("Test terminé")
finally:
    left.stop()
    right.stop()
