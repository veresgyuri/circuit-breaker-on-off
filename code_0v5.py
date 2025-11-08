"""code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt"""
# ver 0.1 - 2025-10-02 minimál
# ver 0.2 - 2025-10-02 REPL bevezetése
# soros monitorra írjuk a KI-BE eseményeket, ms időbélyeggel
# ver 0.22 - 2025-10-03 REPL kiegészítés impulzus hossz időkkel
# ver 0.3 - 2025-10-02 Rugó feszes bemenet
# ver 0.4 -- Rugó feszes input nem kell (ZöldiZ.) + hibakezelés beépítése
# ver 0.45 - REPL üzenet véglegesítés + GPIO deinit, tisztítás
# ver 0.5 -- működés -ciklus- számláló beépítése -- VSCode javítással

# vakrepülés, mert a rugó feszes jelzés figyelése nélkül nem tudjuk,
# hogy valós működés zajlott-e (csak a mi KI-BE ciklusunkat számoljuk)

import time
import board
import digitalio

VERSION = "0.5 - 2025-10-03"

# --- GPIO Pin ---
BE_PIN = board.IO1   # megszakító BE
KI_PIN = board.IO2   # megszakító KI

# --- Times [sec] ---
PULSE = 1.0   # KI és BE impulzus hossza
WAIT_AFTER_BE = 10.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

# --- Kiírjuk a verziót induláskor ---
print("Circuit-breaker tester\n")
print("VERSION:", VERSION)

# --- Pin inicializálás ---
BE = None # Kezdetben None
KI = None # Kezdetben None

# --- Ciklusszámláló inicializálása ---
CYCLE_COUNT = 0

try:
    BE = digitalio.DigitalInOut(BE_PIN)
    BE.direction = digitalio.Direction.OUTPUT
    BE.value = False

    KI = digitalio.DigitalInOut(KI_PIN)
    KI.direction = digitalio.Direction.OUTPUT
    KI.value = False

    time.sleep(BOOT_DELAY)

    # --- Nullapont beállítása (ms felbontás alapja) ---
    t0 = time.monotonic()
    print("\nidőzítő nullázva és elindítva")

    def now_ms():
        """stopper indítás, nullázása - ms időbélyeghez"""
        return int((time.monotonic() - t0) * 1000)

    # --- Végtelen ciklus ---
    while True:
        # BE impulzus kezdete — kiírás ms pontossággal
        print(f"[{now_ms()} ms] BE impulzus kiadva")
        BE.value = True
        time.sleep(PULSE)
        BE.value = False
        print(f"[{now_ms()} ms] BE impulzus visszavéve")
        print(f"     [{now_ms()} ms] KI impulzus {WAIT_AFTER_BE} mp múlva........")

        # Csönd (mindkettő GPIO inaktív)
        time.sleep(WAIT_AFTER_BE)

        # KI impulzus kezdete — kiírás ms pontossággal
        print(f"[{now_ms()} ms] KI impulzus kiadva")
        KI.value = True
        time.sleep(PULSE)
        KI.value = False
        print(f"[{now_ms()} ms] KI impulzus visszavéve")

        # --- Ciklusszámláló növelése és kiírása ---
        CYCLE_COUNT += 1
        print(f"\n==== [{now_ms()} ms] Ciklus vége. Eddig {CYCLE_COUNT} motorfelhúzás volt ====\n")
        print(f"     [{now_ms()} ms] BE impulzus {WAIT_AFTER_KI} mp múlva........")

        # Csönd (mindkettő GPIO inaktív)
        time.sleep(WAIT_AFTER_KI)

except KeyboardInterrupt:
    print("\n[INFO] Program megszakítva a felhasználó által.")
except Exception as e:
    print(f"\n[HIBA] Váratlan hiba történt: {e}")
    print("[HIBA] Kérjük, ellenőrizze a kódot és a hardverkapcsolatokat.")

finally:
    print("[INFO] Tisztító műveletek végrehajtása...")
    if BE is not None:
        BE.value = False
        BE.deinit()
    if KI is not None:
        KI.value = False
        KI.deinit()
    print("[INFO] Program leállítva.")
