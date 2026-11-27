# test_matrix.py — Test de la matrice de DEL 8x8 Keyestudio (puce HT16K33) en I2C.
# Branchements : VCC -> 3V3 (ou VBUS 5 V si trop faible), GND -> GND, SDA -> A5, SCL -> D12.
# Attendu : l'adresse 0x70, puis un coeur, une flèche, un X et un balayage des 64 DEL.

from machine import Pin, I2C
from time import sleep_ms

SDA_PIN = 12    # A5
SCL_PIN = 47    # D12
ADDR = 0x70     # interrupteurs d'adresse A0, A1, A2 tous à 0

HEART = (0b00000000, 0b01100110, 0b11111111, 0b11111111,
         0b11111111, 0b01111110, 0b00111100, 0b00011000)
ARROW = (0b00011000, 0b00111100, 0b01111110, 0b11011011,
         0b00011000, 0b00011000, 0b00011000, 0b00011000)
CROSS = (0b10000001, 0b01000010, 0b00100100, 0b00011000,
         0b00011000, 0b00100100, 0b01000010, 0b10000001)

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400000)
found = i2c.scan()
print("Appareils I2C trouvés :", [hex(a) for a in found])


def show(rows):
    data = bytearray(17)
    for r, bits in enumerate(rows):
        data[1 + 2 * r] = bits
    i2c.writeto(ADDR, data)


if ADDR not in found:
    print("Matrice introuvable à 0x70.")
    print("- Aucune adresse : vérifie VCC, GND, SDA (A5) et SCL (D12), ou essaie VCC sur VBUS (5 V).")
    print("- Une autre adresse entre 0x70 et 0x77 : change ADDR (interrupteurs d'adresse).")
else:
    i2c.writeto(ADDR, bytes((0x21,)))         # oscillateur
    i2c.writeto(ADDR, bytes((0x81,)))         # affichage allumé
    i2c.writeto(ADDR, bytes((0xE0 | 8,)))     # luminosité moyenne
    for name, pattern in (("Coeur", HEART), ("Flèche", ARROW), ("X", CROSS)):
        print(name)
        show(pattern)
        sleep_ms(1500)
    print("Balayage des 64 DEL")
    for r in range(8):
        for c in range(8):
            rows = [0] * 8
            rows[r] = 0b10000000 >> c
            show(rows)
            sleep_ms(40)
    show([0] * 8)
    print("Test terminé. Si les motifs sont à l'envers, mets MATRIX_MIRROR = True dans main.py.")
