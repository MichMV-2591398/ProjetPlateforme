# test_line_sensors.py — Test des 5 capteurs de ligne Keyestudio.
# Branchements : S1..S5 -> A0..A4, V -> 3V3, G -> GND.
# Passe une feuille avec du ruban noir sous les capteurs.
# Attendu : 1 au-dessus du noir, 0 sur le blanc (et la DEL du capteur s'allume sur le noir).

from machine import Pin
from time import sleep_ms

# A0, A1, A2, A3, A4  ->  GPIO 1, 2, 3, 4, 11 (de gauche à droite)
SENSOR_PINS = (1, 2, 3, 4, 11)
WEIGHTS = (-2, -1, 0, 1, 2)

sensors = [Pin(p, Pin.IN) for p in SENSOR_PINS]

print("Test des capteurs de ligne (Ctrl+C pour arrêter)")
print("S1 S2 S3 S4 S5   position")
while True:
    states = [s.value() for s in sensors]
    active = sum(states)
    if active == 0:
        position = "ligne non vue"
    elif active == 5:
        position = "tous noirs (intersection ou robot soulevé)"
    else:
        position = sum(w for w, s in zip(WEIGHTS, states) if s) / active
    print(" {}  {}  {}  {}  {}    {}".format(*states, position))
    sleep_ms(200)
