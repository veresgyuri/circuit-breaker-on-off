"""
Ez a kód a CircuitPython flash memória írását teszteli.
ESP32-S3-Zero modulon futtatva.
Version:
0v1 -- VSCode tisztázás 0/0
"""

import time
import storage

FILENAME = "/vd4.txt"

print("Flash teszt indul...")

try:
    storage.remount("/", False)
    with open(FILENAME, "a", encoding='utf-8') as f:
        f.write("Helló Gyuri! Ez egy új teszt sor.\n")
    storage.remount("/", True)
except OSError as e: # Vagy IOError
    print("❌ Fájlrendszer hiba:", e)

time.sleep(2)
