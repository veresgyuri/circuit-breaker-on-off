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
        # hogy valós működés zajlott-e (csak a mi KI-BE ciklusunkat számoljuk)
# ver 0.6 -- Rugó feszes IO3 implementálás és a ciklus-számlálóhoz kötése
        # Az első BE-KI ciklus indulása nem függ a 'Rugó feszes' jelzés meglététől
# ez az utolsó OOP - objektumorientált verzió, mert áttérünk a moduláris eljárásra

# ver 0.7 - refactor - funkcionális változat, moduláris eljárásorientáltságra állás

import board
import digitalio
import time
import sys
import traceback

VERSION = "0.70 - refactor - 2025-10-05"

# PIN-ek
BE_PIN = board.IO1
KI_PIN = board.IO2
RUGO_FESZES_PIN = board.IO3

# Időzítések (sec)
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 5.0
RUGO_FESZES_TIMEOUT = 20.0

# Logikai beállítások
RUGO_ACTIVE_LOW = True  # ha True, akkor LOW = FESZES

# állapotok
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

def rugo_is_feszes():
    # visszaadja True/False attól függően, hogy a jel aktív-e
    val = rugo.value
    return (not val) if RUGO_ACTIVE_LOW else val

def wait_for_rugo(timeout):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if rugo_is_feszes():
            return True
        time.sleep(0.05)
    return False

def main_loop():
    global cycle_count
    log("Circuit-breaker tester")
    log(f"Version: {VERSION}")
    log(f"Első BE parancs {BOOT_DELAY} mp múlva")
    time.sleep(BOOT_DELAY)

    log("Stopper nullázva és elindítva")
    log(f"Rugó állapota induláskor: {'FESZES' if rugo_is_feszes() else 'LAZA'}")

    while True:
        # BE
        log("BE impulzus kiadva")
        pulse(be, PULSE)
        log("BE impulzus visszavéve")

        log(f"Várakozás a 'rugó feszes' jelzésre (max {RUGO_FESZES_TIMEOUT} mp)...")
        if wait_for_rugo(RUGO_FESZES_TIMEOUT):
            log("'Rugó feszes' jelzés megérkezett. Rugó felhúzva.")
            cycle_count += 1
        else:
            log(f"[HIBA] Időtúllépés! A 'rugó feszes' jelzés nem érkezett {RUGO_FESZES_TIMEOUT} mp alatt.")
            raise SystemExit("Rugófelhúzó egység hibás?")

        log(f"KI impulzus {WAIT_AFTER_BE} mp múlva........")
        time.sleep(WAIT_AFTER_BE)

        # KI
        log("KI impulzus kiadva")
        pulse(ki, PULSE)
        log("KI impulzus visszavéve")

        log(f"===== BE-KI ciklus befejezve. Eddig {cycle_count} rugófelhúzás volt =====")
        log(f"BE impulzus {WAIT_AFTER_KI} mp múlva........")
        time.sleep(WAIT_AFTER_KI)

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
