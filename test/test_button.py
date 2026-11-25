# test_button.py — Test du bouton poussoir (anti-rebond, appui court et long).
# Branchements : une patte -> D2, l'autre patte -> GND (pull-up interne activé).
# Fais des appuis courts puis tiens le bouton plus de 1,5 s.

from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms

BUTTON_PIN = 5      # D2
DEBOUNCE_MS = 50
LONG_PRESS_MS = 1500

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
stable = 1
change_start = ticks_ms()
press_start = 0
long_reported = False
count = 0

print("Test du bouton (Ctrl+C pour arrêter). Valeur au repos :", button.value(), "(attendu : 1)")
while True:
    now = ticks_ms()
    raw = button.value()

    if raw == stable:
        change_start = now
    elif ticks_diff(now, change_start) >= DEBOUNCE_MS:
        stable = raw
        if raw == 0:
            press_start = now
            long_reported = False
            print("Appuyé")
        else:
            if not long_reported:
                count += 1
                print("Relâché -> APPUI COURT n°", count)
            else:
                print("Relâché")

    if stable == 0 and not long_reported and ticks_diff(now, press_start) >= LONG_PRESS_MS:
        long_reported = True
        print("APPUI LONG détecté")

    sleep_ms(5)
