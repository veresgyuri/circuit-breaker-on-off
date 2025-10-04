# ver 0.1 -- 2025-10-02 minimál
# ver 0.2 -- 2025-10-02 REPL bevezetése
# ver 0.22 - 2025-10-03 REPL kiegészítés imp. időkkel
# ver 0.4 -- 2025-10-02 Rugó feszes input beépítése, de nem kell (ZöldiZ.)
# ver 0.4 -- hibakezelésel beépítése
# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt
import board
import digitalio
import time

VERSION = "0.4 - 2025-10-03" # Frissítettem a verziót, ahogy te is tetted

# --- GPIO PIN ---
BE_PIN = board.GPIO1   # megszakító BE
KI_PIN = board.GPIO2   # megszakító KI

# --- Times [sec] ---
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után

# --- Kiírjuk a verziót induláskor ---
print("Circuit-breaker tester")
print("VERSION:", VERSION)

# --- pin inicializálás ---
be = digitalio.DigitalInOut(BE_PIN)
be.direction = digitalio.Direction.OUTPUT # JAVÍTVA ITT
be.value = False

ki = digitalio.DigitalInOut(KI_PIN)
ki.direction = digitalio.Direction.OUTPUT # JAVÍTVA ITT
ki.value = False

time.sleep(BOOT_DELAY)  # adunk egy kis időt boot után

# --- Nullapont beállítása (ms felbontás alapja) ---
t0 = time.monotonic()
print("időzítő nullázva és elindítva")

def now_ms():
    return int((time.monotonic() - t0) * 1000)

# --- EZ A RÉSZ KEZELI A KEYBOARDINTERRUPT-OT ---
try:
    # --- végtelen ciklus ---
    while True:
        # BE impulzus kezdete — kiírás ms pontossággal
        print("[{0} ms] BE impulzus kiadva".format(now_ms()))
        be.value = True
        time.sleep(PULSE)
        be.value = False
        print("[{0} ms] BE impulzus visszavéve".format(now_ms()))
        print("      [{0} ms] KI impulzus {1} mp múlva".format(now_ms(), WAIT_AFTER_BE))


        # 20 s csönd (mindkettő GPIO inaktív)
        time.sleep(WAIT_AFTER_BE)

        # KI impulzus kezdete — kiírás ms pontossággal
        print("[{0} ms] KI impulzus kiadva".format(now_ms()))
        ki.value = True
        time.sleep(PULSE)
        ki.value = False
        print("[{0} ms] KI impulzus visszavéve".format(now_ms()))
        print("      [{0} ms] BE impulzus {1} mp múlva".format(now_ms(), WAIT_AFTER_KI))

        # 10 s csönd
        time.sleep(WAIT_AFTER_KI)

except KeyboardInterrupt:
    # Ez a blokk akkor fut le, ha a felhasználó Ctrl+C-vel megszakítja a programot
    print("\n[INFO] Program megszakítva a felhasználó által.")

finally:
    # Ez a blokk MINDIG lefut, akár volt KeyboardInterrupt, akár nem (pl. más hiba)
    # Ide kerülnek a "tisztító" lépések
    print("[INFO] GPIO pin-ek alapállapotba állítása...")
    be.value = False
    ki.value = False
    # Ha használjuk a deinit-et, akkor itt szabadíthatjuk fel a pin-eket:
    # be.deinit()
    # ki.deinit()
    print("[INFO] Program leállítva.")