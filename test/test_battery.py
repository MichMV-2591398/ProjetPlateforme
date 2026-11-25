# test_battery.py — Test de la mesure de tension de la batterie.
# Branchements : batterie + (après l'interrupteur) -> 20 kΩ -> A5 -> 10 kΩ -> GND.
# Compare la tension affichée avec celle du multimètre aux bornes de la batterie.
# Sans batterie (USB seulement), la tension affichée doit être proche de 0 V.

from machine import Pin, ADC
from time import sleep_ms

BATTERY_PIN = 12      # A5
DIVIDER_RATIO = 3.0   # (20 k + 10 k) / 10 k
LOW_BATTERY_V = 6.6

adc = ADC(Pin(BATTERY_PIN), atten=ADC.ATTN_11DB)
samples = []

print("Test de la batterie (Ctrl+C pour arrêter)")
while True:
    pin_v = adc.read_uv() / 1000000
    samples.append(pin_v * DIVIDER_RATIO)
    if len(samples) > 10:
        samples.pop(0)
    average = sum(samples) / len(samples)

    if average < 1.0:
        status = "pas de batterie détectée"
    elif average < LOW_BATTERY_V:
        status = "BATTERIE FAIBLE"
    else:
        status = "OK"
    print("Broche A5 : {:.2f} V   Batterie : {:.2f} V (moyenne)   {}".format(pin_v, average, status))
    sleep_ms(300)
