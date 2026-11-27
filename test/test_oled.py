# test_oled.py — Test de l'écran OLED SSD1306 en I2C.
# Branchements : VCC -> 3V3, GND -> GND, SDA -> A5, SCL -> D12.
# Nécessite ssd1306.py à la racine de la carte.
# Attendu : la liste des adresses I2C (0x3c pour l'OLED), puis du texte et une barre qui se remplit.

from machine import Pin, I2C
from time import sleep_ms

SDA_PIN = 12    # A5
SCL_PIN = 47    # D12

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400000)
found = i2c.scan()
print("Appareils I2C trouvés :", [hex(a) for a in found])

if not found:
    print("Aucun appareil : vérifie VCC, GND, SDA (A5) et SCL (D12)")
elif 0x3C not in found and 0x3D not in found:
    print("Pas d'OLED SSD1306 (0x3c/0x3d). Adresse 0x27 ou 0x3f = écran LCD 16x2, pas un OLED.")
else:
    from ssd1306 import SSD1306_I2C
    oled = SSD1306_I2C(128, 64, i2c, 0x3C if 0x3C in found else 0x3D)
    oled.fill(0)
    oled.text("Test OLED", 0, 0)
    oled.text("Fast line", 0, 16)
    oled.text("tracker!", 0, 28)
    oled.show()
    sleep_ms(1500)
    for pct in range(0, 101, 10):
        oled.fill_rect(0, 48, 128, 12, 0)
        oled.rect(0, 48, 128, 12, 1)
        oled.fill_rect(0, 48, 128 * pct // 100, 12, 1)
        oled.show()
        print("Barre :", pct, "%")
        sleep_ms(300)
    print("Test terminé : l'écran fonctionne")
