
from machine import Pin
from time import sleep

# A0 du Nano ESP32 = GPIO1
capteur = Pin(1, Pin.IN)

while True:
    valeur = capteur.value()

    print("Valeur :", valeur)

    sleep(0.5)
