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

import board
import digitalio
import time

VERSION = "0.5 - 2025-10-03"

# --- GPIO PIN ---
BE_PIN = board.IO1   # megszakító BE
KI_PIN = board.IO2   # megszakító KI

# --- Times [sec] ---
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

# --- Kiírjuk a verziót induláskor ---
print("Circuit-breaker tester\n")
print("VERSION:", VERSION)

# --- pin inicializálás ---
be = None # Kezdetben None
ki = None # Kezdetben None

# --- CIKLUSSZÁMLÁLÓ INICIALIZÁLÁSA ---
cycle_count = 0

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
        # BE impulzus kezdete — kiírás ms pontossággal
        print("[{0} ms] BE impulzus kiadva".format(now_ms()))
        be.value = True
        time.sleep(PULSE)
        be.value = False
        print("[{0} ms] BE impulzus visszavéve".format(now_ms()))
        print("      [{0} ms] KI impulzus {1} mp múlva........".format(now_ms(), WAIT_AFTER_BE))


        # 20 s csönd (mindkettő GPIO inaktív)
        time.sleep(WAIT_AFTER_BE)

        # KI impulzus kezdete — kiírás ms pontossággal
        print("[{0} ms] KI impulzus kiadva".format(now_ms()))
        ki.value = True
        time.sleep(PULSE)
        ki.value = False
        print("[{0} ms] KI impulzus visszavéve".format(now_ms()))
        
        # --- CIKLUSSZÁMLÁLÓ NÖVELÉSE ÉS KIÍRÁSA ---
        cycle_count += 1
        print("\n===== [{0} ms] Ciklus befejezve. Eddig {1} motorfelhúzás volt =====\n".format(now_ms(), cycle_count))
        print("      [{0} ms] BE impulzus {1} mp múlva........".format(now_ms(), WAIT_AFTER_KI))

        # 10 s csönd
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