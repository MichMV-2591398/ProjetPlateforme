# test_rgb_led.py — Test de la LED RVB d'état (cathode commune).
# Branchements : rouge -> 220 Ω -> D1, vert -> 100 Ω -> A7, bleu -> 100 Ω -> D6,
#                patte la plus longue (cathode) -> GND.
# Chaque couleur s'allume pendant 1,5 s.

from machine import Pin
from time import sleep_ms

RED_PIN = 43     # D1 (D13 ne fonctionne pas sur notre carte)
GREEN_PIN = 14   # A7
BLUE_PIN = 9     # D6

r = Pin(RED_PIN, Pin.OUT, value=0)
g = Pin(GREEN_PIN, Pin.OUT, value=0)
b = Pin(BLUE_PIN, Pin.OUT, value=0)

COLORS = (
    ("Rouge (arrêt)", 1, 0, 0),
    ("Vert (suivi)", 0, 1, 0),
    ("Bleu (attente)", 0, 0, 1),
    ("Rouge + vert (problème)", 1, 1, 0),
    ("Blanc (les 3)", 1, 1, 1),
    ("Éteint", 0, 0, 0),
)

def show(red, green, blue):
    r.value(red)
    g.value(green)
    b.value(blue)

try:
    for name, red, green, blue in COLORS:
        print(name)
        show(red, green, blue)
        sleep_ms(1500)
    print("Clignotement rouge (batterie faible)")
    for _ in range(6):
        show(1, 0, 0)
        sleep_ms(250)
        show(0, 0, 0)
        sleep_ms(250)
    print("Test terminé")
finally:
    show(0, 0, 0)
