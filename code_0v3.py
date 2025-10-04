# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt
# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt
# ver 0.1 - 2025-10-02 minimál
# ver 0.2 - 2025-10-02 REPL bevezetése
# soros monitorra írjuk a KI-BE eseményeket, ms időbélyeggel
# ver 0.22 - 2025-10-03 REPL kiegészítés impulzus hossz időkkel
# ver 0.3 - 2025-10-02 Rugó feszes bemenet

import board
import digitalio
import time

VERSION = "0.3 - 2025-10-02"

# --- GPIO PIN ---
BE_PIN = board.GPIO1   # megszakító BE
KI_PIN = board.GPIO2   # megszakító KI
RUGO_PIN = board.GPIO3 # rugó feszes bemenet

# --- Times [sec] ---
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

#  --- Kiírjuk a verziót induláskor ---
print("Circuit-breaker tester")
print("VERSION:", VERSION)

# --- pin inicializálás ---
be = digitalio.DigitalInOut(BE_PIN)
be.direction = digitalio.Direction.OUTPUT
be.value = False

ki = digitalio.DigitalInOut(KI_PIN)
ki.direction = digitalio.Direction.OUTPUT
ki.value = False

# Rugó bemenet inicializálása
rugo = digitalio.DigitalInOut(RUGO_PIN)
rugo.direction = digitalio.Direction.INPUT
# Állítsd Pull.UP vagy Pull.DOWN szerint, itt alap: Pull.DOWN (aktív = True)
rugo.pull = digitalio.Pull.DOWN

time.sleep(BOOT_DELAY)  # adunk egy kis időt boot után

# Nullapont beállítása (ms felbontás alapja)
t0 = time.monotonic()
print("t0 set")

def now_ms():
    return int((time.monotonic() - t0) * 1000)

# Rugo él-észleléshez állapot tárolása
last_rugo = rugo.value

# Segédfüggvény: várakozás, de közben gyakran ellenőrzi a RUGO bemenetet
def wait_with_rugo(duration, sample_interval=0.05):
    global last_rugo
    end = time.monotonic() + duration
    while time.monotonic() < end:
        cur = rugo.value
        # Rising edge = rugó feszes jel
        if cur and not last_rugo:
            print("[{0} ms] RUGO ASSERTED".format(now_ms()))
        # (opcionális) Falling edge - feloldás
        if not cur and last_rugo:
            print("[{0} ms] RUGO RELEASED".format(now_ms()))
        last_rugo = cur
        # rövid alvás, de ne legyen túl hosszú, hogy ne hagyjunk ki eseményt
        time.sleep(sample_interval)

# --- végtelen ciklus ---
while True:
    # BE impulzus kezdete — kiírás ms pontossággal
    print("[{0} ms] BE pulse start".format(now_ms()))
    be.value = True
    wait_with_rugo(PULSE)   # 1 s alatt is figyelünk a RUGO-ra
    be.value = False

    # 20 s csönd (mindkettő inaktív) — közben RUGO figyelés
    wait_with_rugo(WAIT_AFTER_BE)

    # KI impulzus kezdete — kiírás ms pontossággal
    print("[{0} ms] KI pulse start".format(now_ms()))
    ki.value = True
    wait_with_rugo(PULSE)
    ki.value = False

    # 10 s csönd
    wait_with_rugo(WAIT_AFTER_KI)
