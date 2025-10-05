# code.py - Megszakító (BE/KI) pulzusgenerátor CircuitPython alatt


""" ************ KAPCSOLÁSI RAJZ ******************

 TÁPFESZÜLTSÉG
     REPL         
      ↓          GND
                   │
    USB-C         ┌┴┐ 
┌────┬──┬────┐    4.7k
│    └──┘    ├    └┬┘
│         IO1├─────┴──[1.0k]───→ BE
│            │  
│         IO2├─────┬──[1.0k]───→ KI   
│            │    ┌┴┐
│   ESP32    │    4.7k
│  S3-zero   │    └┬┘
│            │     │
│            │    GND
│    Pull up │   
│         I03├──────── RUGÓ FESZES
│            │
└────────────┘
        
"""

# ver 0.1 - 2025-10-02 minimál kód
# ver 0.2 - 2025-10-02 REPL bevezetése, soros monitorra írjuk a KI-BE eseményeket, ms időbélyeggel
# ver 0.22  2025-10-03 REPL kiegészítés impulzus hossz időkkel
# ver 0.3 - 2025-10-02 Rugó feszes bemenet
# ver 0.4 - Rugó feszes input nem kell (ZöldiZ.) + hibakezelés beépítése
# ver 0.45  REPL üzenet véglegesítés + GPIO deinit, tisztítás
# ver 0.5 - működés -ciklus- számláló beépítése
       # zsákutca, mert a rugó feszes jelzés figyelése nélkül nem tudjuk,
       # hogy valós működés zajlott-e (csak a mi KI-BE ciklusunkat számoljuk)
# ver 0.6 - Rugó feszes IO3 implementálás és a ciklus-számlálóhoz kötése
       # Az első BE-KI ciklus indulása nem függ a 'Rugó feszes' jelzés meglététől
       # ez az utolsó OOP - objektumorientált verzió, mert áttérünk a moduláris eljárásra

# ver 0.7 - 1st funkcionális változat, moduláris eljárásorientáltságra állás 2025-10-05
# ver 0.8 - rugó felhúzási idő mérése, logolása

import board
import digitalio
import time
import sys
import traceback

VERSION = "0.8 - motoridő mérés - 2025-10-05"

# PIN-ek
BE_PIN = board.IO1
KI_PIN = board.IO2
RUGO_FESZES_PIN = board.IO3

# Konstansok - időzítések (sec)
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 5.0
RUGO_FESZES_TIMEOUT = 20.0
DEBOUNCE_MS = 50 # ms, stabil állapot ideje
POLL_INTERVAL = 0.01 # sec, mintavételi intervallum
ENSURE_LAZA_TIMEOUT = 1.0  # max ennyit várunk, hogy LAZA legyen (sec)

# Logikai beállítások
RUGO_ACTIVE_LOW = True  # ha True, akkor LOW = FESZES

# Állapotok
be = ki = rugo = None
t0 = time.monotonic()
cycle_count = 0

def now_ms():
    return int((time.monotonic() - t0) * 1000)

def log(msg):
    print(f"[{now_ms()} ms] {msg}")

def init_pins():
    global be, ki, rugo
    be = digitalio.DigitalInOut(BE_PIN)
    be.direction = digitalio.Direction.OUTPUT
    be.value = False

    ki = digitalio.DigitalInOut(KI_PIN)
    ki.direction = digitalio.Direction.OUTPUT
    ki.value = False

    rugo = digitalio.DigitalInOut(RUGO_FESZES_PIN)
    rugo.direction = digitalio.Direction.INPUT
    rugo.pull = digitalio.Pull.UP

def deinit_pins():
    global be, ki, rugo
    try:
        if be is not None:
            be.value = False
            be.deinit()
        if ki is not None:
            ki.value = False
            ki.deinit()
        if rugo is not None:
            rugo.deinit()
    except Exception:
        # biztos tisztítás: csak logolunk
        print("Tisztítás közben hiba:", sys.exc_info()[0])

def pulse(pin_obj, duration):
    pin_obj.value = True
    time.sleep(duration)
    pin_obj.value = False

def rugo_feszes():
    # visszaadja True/False attól függően, hogy a jel aktív-e
    val = rugo.value
    return (not val) if RUGO_ACTIVE_LOW else val

def wait_for_feszes(timeout, debounce_ms=DEBOUNCE_MS):
    """Vár a FESZES (active) állapotra, csak ha az stabilan fennáll debounce_ms ideig."""
    start = time.monotonic()
    stable_needed = debounce_ms / 1000.0
    stable_start = None
    while time.monotonic() - start < timeout:
        cur = rugo_feszes()  # True = FESZES
        if cur:
            if stable_start is None:
                stable_start = time.monotonic()
            elif time.monotonic() - stable_start >= stable_needed:
                return True
        else:
            stable_start = None
        time.sleep(POLL_INTERVAL)
    return False

def measure_rugo_felhuzasi_ido(max_timeout):
    """
    Mér egy LAZA -> FESZES átmenetet: ha már FESZES -> 0.0, 
    ha nem történik meg max_timeout alatt -> None,
    különben visszaadja a felhúzási időt másodpercben.
    """
    # Ha már feszes, visszaadjuk 0.0 (azonnali)
    if rugo_feszes():
        return 0.0

    # Győződjünk meg róla, hogy LAZA állapotból indulunk (max ENSURE_LAZA_TIMEOUT)
    ensure_start = time.monotonic()
    while time.monotonic() - ensure_start < ENSURE_LAZA_TIMEOUT:
        if not rugo_feszes():  # LAZA
            break
        time.sleep(POLL_INTERVAL)

    # Start időpont (innen mérünk)
    t_start = time.monotonic()

    # Várjuk a debounce-olt FESZES állapotot
    if wait_for_feszes(max_timeout):
        return time.monotonic() - t_start
    return None

def main_loop():
    global cycle_count, t0
    # Nullpont újraindítása a loop elején (egységes ms méréshez)
    t0 = time.monotonic()

    log("Circuit-breaker tester")
    log(f"Version: {VERSION}")
    log(f"Első BE parancs {BOOT_DELAY} mp múlva")
    time.sleep(BOOT_DELAY)

    log("Stopper nullázva és elindítva")
    log(f"Rugó állapota induláskor: {'FESZES' if rugo_feszes() else 'LAZA'}")

    while True:
        # --- BE impulzus ---
        log("BE impulzus kiadva")
        pulse(be, PULSE)
        log("BE impulzus visszavéve")

        # --- Rugó felhúzási idő mérése (LAZA -> FESZES) ---
        log(f"Rugó felhúzási idő mérése (max {RUGO_FESZES_TIMEOUT} s)...")
        elapsed = measure_rugo_felhuzasi_ido(RUGO_FESZES_TIMEOUT)
        if elapsed is None:
            log(f"[HIBA] Időtúllépés! A LAZA -> FESZES átmenet nem történt meg {RUGO_FESZES_TIMEOUT} s alatt.")
            raise SystemExit("Rugófelhúzó egység hibás?")
        else:
            ms = int(elapsed * 1000)
            log(f"Rugó felhúzási idő: {ms} ms")
            cycle_count += 1

        # --- Várakozás BE után, majd KI impulzus ---
        log(f"KI impulzus {WAIT_AFTER_BE} mp múlva........")
        time.sleep(WAIT_AFTER_BE)

        log("KI impulzus kiadva")
        pulse(ki, PULSE)
        log("KI impulzus visszavéve")

        # --- Ciklus összegzés és várakozás a következő BE-ig ---
        log(f"===== BE-KI ciklus befejezve. Eddig {cycle_count} rugófelhúzás volt =====")
        log(f"BE impulzus {WAIT_AFTER_KI} mp múlva........")
        time.sleep(WAIT_AFTER_KI)


def wait_for_rugo(timeout):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if rugo_feszes():
            return True
        time.sleep(0.05)
    return False



if __name__ == "__main__":
    try:
        init_pins()
        main_loop()
    except KeyboardInterrupt:
        log("Program megszakítva a felhasználó által.")
    except SystemExit as e:
        log("Program leállítás indítva: " + str(e))
    except Exception as e:
        log("Váratlan hiba történt: " + repr(e))
        traceback.print_exc()
    finally:
        log("Memória és GPIO tisztítás...")
        deinit_pins()
        log("Program leállítva.")
