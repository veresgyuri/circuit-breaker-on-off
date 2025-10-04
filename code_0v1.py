# ver 0.1 - 2025-10-02
# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt
import board
import digitalio
import time

# --- CSERÉLD KI A KÖVETKEZŐKET a saját boardod PIN NEVEIRE ---
BE_PIN = board.GP1   # <- ide írd a tényleges "BE" kimenet pin-jét
KI_PIN = board.GP2   # <- ide írd a tényleges "KI" kimenet pin-jét

# Idők másodpercben
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

# --- pin inicializálás ---
be = digitalio.DigitalInOut(BE_PIN)
be.direction = digitalio.Direction.OUTPUT
be.value = False

ki = digitalio.DigitalInOut(KI_PIN)
ki.direction = digitalio.Direction.OUTPUT
ki.value = False

time.sleep(BOOT_DELAY)  # adunk egy kis időt boot után

# --- végtelen ciklus ---
while True:
    # BE impulzus 1 s
    be.value = True
    time.sleep(PULSE)
    be.value = False

    # 20 s csönd (mindkettő inaktív)
    time.sleep(WAIT_AFTER_BE)

    # KI impulzus 1 s
    ki.value = True
    time.sleep(PULSE)
    ki.value = False

    # 10 s csönd
    time.sleep(WAIT_AFTER_KI)
