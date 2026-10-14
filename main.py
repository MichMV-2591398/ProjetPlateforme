from machine import Pin, time_pulse_us
from time import sleep_ms, sleep_us
 
trig = Pin(5, Pin.OUT)   # D2 = GPIO5
echo = Pin(6, Pin.IN)    # D3 = GPIO6
 
 
def mesure_cm():
    """Une mesure en cm, ou None si pas d'écho."""
    trig.value(0)
    sleep_us(5)
    trig.value(1)
    sleep_us(10)
    trig.value(0)
 
    duree = time_pulse_us(echo, 1, 30000)  # timeout 30 ms
    if duree < 0:
        return None
    return duree * 0.0343 / 2
 
 
def mesure_moyenne(n=5):
    """Moyenne de n mesures valides, ou None si aucune."""
    valeurs = []
    for _ in range(n):
        d = mesure_cm()
        if d is not None:
            valeurs.append(d)
        sleep_ms(60)  # laisse l'écho précédent s'éteindre
    if not valeurs:
        return None
    return sum(valeurs) / len(valeurs)
 
 
while True:
    d = mesure_moyenne()
    if d is None:
        print("Pas d'écho (hors portée ou problème de câblage/alimentation)")
    else:
        print("Distance : {:.1f} cm".format(d))
    sleep_ms(300)
 