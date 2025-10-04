# ver 0.1 - 2025-10-02 minimál
# ver 0.2 - 2025-10-02 REPL bevezetése
# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt
import board
import digitalio
import time

VERSION = "0.2 - 2025-10-02"

# --- GPIO PIN ---
BE_PIN = board.GPIO1   # megszakító BE
KI_PIN = board.GPIO2   # megszakító KI

# Times [sec]
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

# Kiírjuk a verziót induláskor
print("Circuit-breaker tester")
print("VERSION:", VERSION)

# --- pin inicializálás ---
be = digitalio.DigitalInOut(BE_PIN)
be.direction = digitalio.Direction.OUTPUT
be.value = False

ki = digitalio.DigitalInOut(KI_PIN)
ki.direction = digitalio.Direction.OUTPUT
ki.value = False

time.sleep(BOOT_DELAY)  # adunk egy kis időt boot után

# Nullapont beállítása (ms felbontás alapja)
t0 = time.monotonic()
print("t0 set")

def now_ms():
    return int((time.monotonic() - t0) * 1000)

# --- végtelen ciklus ---
while True:
    # BE impulzus kezdete — kiírás ms pontossággal
    print("[{0} ms] BE pulse start".format(now_ms()))
    be.value = True
    time.sleep(PULSE)
    be.value = False

    # 20 s csönd (mindkettő inaktív)
    time.sleep(WAIT_AFTER_BE)

    # KI impulzus kezdete — kiírás ms pontossággal
    print("[{0} ms] KI pulse start".format(now_ms()))
    ki.value = True
    time.sleep(PULSE)
    ki.value = False

    # 10 s csönd
    time.sleep(WAIT_AFTER_KI)
