# test_potentiometer.py — Test du potentiomètre de vitesse.
# Branchements : patte gauche -> 3V3, patte du milieu -> A6, patte droite -> GND.
# Tourne le bouton d'un bout à l'autre : la valeur doit aller de 0 % à 100 %.

from machine import Pin, ADC
from time import sleep_ms

POT_PIN = 13    # A6
MIN_SPEED = 25
MAX_SPEED = 100

adc = ADC(Pin(POT_PIN), atten=ADC.ATTN_11DB)

print("Test du potentiomètre (Ctrl+C pour arrêter)")
while True:
    raw = adc.read_u16()
    percent = raw * 100 // 65535
    speed = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * percent // 100
    bar = "#" * (percent // 5)
    print("Brut : {:5d}   {:3d} %   vitesse robot : {:3d} %   {}".format(raw, percent, speed, bar))
    sleep_ms(200)
