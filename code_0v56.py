# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt
# ver 0.1 - 2025-10-02 minimál
# ver 0.2 - 2025-10-02 REPL bevezetése
# soros monitorra írjuk a KI-BE eseményeket, ms időbélyeggel
# ver 0.22 - 2025-10-03 REPL kiegészítés impulzus hossz időkkel
# ver 0.3 - 2025-10-02 Rugó feszes bemenet
# ver 0.4 -- Rugó feszes input nem kell (ZöldiZ.) + hibakezelés beépítése
# ver 0.45 - REPL üzenet véglegesítés + GPIO deinit, tisztítás
# ver 0.5 -- működés -ciklus- számláló beépítése

# zsákutca, mert a rugó feszes jelzés figyelése nélkül nem tudjuk,
# hogy valós működés zajlott-e (csak a mi KI-BE ciklusunkat számoljuk

# ver 0.55 - 2025-11-06 számláló mentés flash-be (vd4.txt) - save_cycle_count()
# ver 0.56 - 2025-11-07 import strorage

import board
import digitalio
import time
import os
import storage

VERSION = "0.56 - 2025-11-07"

# --- GPIO PIN ---
BE_PIN = board.IO1   # megszakító BE
KI_PIN = board.IO2   # megszakító KI

# --- Times [sec] ---
PULSE = 1.0
WAIT_AFTER_BE = 10.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

# --- Kiírjuk a verziót induláskor ---
print("Circuit-breaker tester\n")
print("VERSION:", VERSION)

# --- fájlnevek ---
COUNT_FILE = "/vd4.txt"

# --- függvények ---

def load_cycle_count():
    """Korábbi számláló érték beolvasása flash-ből."""
    try:
        with open(COUNT_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0  # ha nincs fájl, vagy hiba volt

def save_cycle_count(n):
    """Számláló biztonságos mentése flash-be."""
    tmp = COUNT_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            f.write(str(n) + "\n")
            f.flush()
        try:
            os.sync()  # ha a build támogatja
        except Exception:
            pass
        os.rename(tmp, COUNT_FILE)  # atomikus csere
    except OSError as e:
        print("[HIBA] Mentés sikertelen:", e)


# --- pin inicializálás ---
be = None
ki = None

# --- CIKLUSSZÁMLÁLÓ INICIALIZÁLÁSA ---
cycle_count = load_cycle_count()
print(f"[INFO] Korábbi számláló érték: {cycle_count}")

try:
    be = digitalio.DigitalInOut(BE_PIN)
    be.direction = digitalio.Direction.OUTPUT
    be.value = False

    ki = digitalio.DigitalInOut(KI_PIN)
    ki.direction = digitalio.Direction.OUTPUT
    ki.value = False

    time.sleep(BOOT_DELAY)

    # --- Nullapont beállítása (ms felbontás alapja) ---
    t0 = time.monotonic()
    print("\nidőzítő nullázva és elindítva")

    def now_ms():
        return int((time.monotonic() - t0) * 1000)

    # --- végtelen ciklus ---
    while True:
        # BE impulzus
        print("[{0} ms] BE impulzus kiadva".format(now_ms()))
        be.value = True
        time.sleep(PULSE)
        be.value = False
        print("[{0} ms] BE impulzus visszavéve".format(now_ms()))
        print("      [{0} ms] KI impulzus {1} mp múlva........".format(now_ms(), WAIT_AFTER_BE))

        time.sleep(WAIT_AFTER_BE)

        # KI impulzus
        print("[{0} ms] KI impulzus kiadva".format(now_ms()))
        ki.value = True
        time.sleep(PULSE)
        ki.value = False
        print("[{0} ms] KI impulzus visszavéve".format(now_ms()))

        # --- CIKLUSSZÁMLÁLÓ NÖVELÉSE ÉS KIÍRÁSA ---
        cycle_count += 1
        print("\n===== [{0} ms] Ciklus befejezve. Eddig {1} motorfelhúzás volt =====\n".format(now_ms(), cycle_count))
        save_cycle_count(cycle_count)
        print("[INFO] Számláló mentve flash-be.")

        print("      [{0} ms] BE impulzus {1} mp múlva........".format(now_ms(), WAIT_AFTER_KI))
        time.sleep(WAIT_AFTER_KI)

except KeyboardInterrupt:
    print("\n[INFO] Program megszakítva a felhasználó által.")
except Exception as e:
    print(f"\n[HIBA] Váratlan hiba történt: {e}")
    print("[HIBA] Kérjük, ellenőrizze a kódot és a hardverkapcsolatokat.")
finally:
    print("[INFO] Tisztító műveletek végrehajtása...")
    if be is not None:
        be.value = False
        be.deinit()
    if ki is not None:
        ki.value = False
        ki.deinit()
    print("[INFO] Program leállítva.")