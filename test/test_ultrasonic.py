# test_ultrasonic.py — Test du capteur ultrason HC-SR04.
# Branchements : VCC -> 3V3, GND -> GND, TRIG -> D10, ECHO -> D11.
# Place ta main ou un livre à 10 cm, 30 cm puis 100 cm et compare avec une règle.

from machine import Pin, time_pulse_us
from time import sleep_ms, sleep_us

TRIG_PIN = 21   # D10
ECHO_PIN = 38   # D11

trig = Pin(TRIG_PIN, Pin.OUT, value=0)
echo = Pin(ECHO_PIN, Pin.IN)

print("Test du HC-SR04 (Ctrl+C pour arrêter)")
while True:
    trig.value(1)
    sleep_us(10)
    trig.value(0)
    duration = time_pulse_us(echo, 1, 30000)   # 30 ms max (environ 5 m)
    if duration == -2:
        print("Aucun écho : vérifie VCC, GND et le fil ECHO")
    elif duration == -1:
        print("Rien devant (hors de portée)")
    else:
        print("Distance : {:.1f} cm".format(duration * 0.0343 / 2))
    sleep_ms(200)
