# test_led_strip.py — Test de la barre de 8 DEL WS2812B.
# Branchements : DIN -> 330 Ω -> D12, 5V/VCC -> 3V3, GND -> GND.
# Attendu : chaque couleur, puis un bargraphe de 0 à 8 DEL, puis un clignotement.

from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

STRIP_PIN = 47      # D12
COUNT = 8
BRIGHTNESS = 0.15   # 15 % : limite le courant sur le 3V3

strip = NeoPixel(Pin(STRIP_PIN), COUNT)

def dim(color):
    return tuple(int(c * BRIGHTNESS) for c in color)

def fill(color):
    for i in range(COUNT):
        strip[i] = dim(color)
    strip.write()

def bar(n, color):
    for i in range(COUNT):
        strip[i] = dim(color) if i < n else (0, 0, 0)
    strip.write()

try:
    for name, color in (("Rouge", (255, 0, 0)), ("Vert", (0, 255, 0)),
                        ("Bleu", (0, 0, 255)), ("Orange", (255, 80, 0)),
                        ("Blanc", (255, 255, 255))):
        print(name)
        fill(color)
        sleep_ms(1000)

    print("Bargraphe 0 -> 8 DEL (vitesse)")
    for n in range(COUNT + 1):
        bar(n, (0, 255, 0))
        sleep_ms(300)

    print("Clignotement orange (ligne perdue)")
    for _ in range(6):
        fill((255, 80, 0))
        sleep_ms(250)
        fill((0, 0, 0))
        sleep_ms(250)
    print("Test terminé")
finally:
    fill((0, 0, 0))
