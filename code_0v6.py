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
# ver 0.6 -- Rugó feszes IO3 implementálás és ciklushoz kötése

# code.py - egyszerű megszakító (BE/KI) pulzusgenerátor CircuitPython alatt

import board
import digitalio
import time

VERSION = "0.6 - 2025-10-03" # Verziószám frissítése

# --- GPIO PIN-ek ---
BE_PIN = board.IO1   # megszakító BE parancs
KI_PIN = board.IO2   # megszakító KI parancs
RUGO_FESZES_PIN = board.IO3 # Rugó feszes állapot jelzése (bemenet)

# --- Időzítések [sec] ---
PULSE = 1.0
WAIT_AFTER_BE = 20.0
WAIT_AFTER_KI = 10.0
BOOT_DELAY = 0.5  # rövid várakozás boot után
RUGO_FESZES_TIMEOUT = 20.0 # Ennyi ideig vár a "rugó feszes" jelzésre BE impulzus után

# --- Kiírjuk a verziót induláskor ---
print("Circuit-breaker tester\n")
print("Version:", VERSION)

# --- pin inicializálás ---
be = None
ki = None
rugo_feszes_input = None # Bemeneti pin inicializálása

# --- CIKLUSSZÁMLÁLÓ INICIALIZÁLÁSA ---
cycle_count = 0

try:
    be = digitalio.DigitalInOut(BE_PIN)
    be.direction = digitalio.Direction.OUTPUT
    be.value = False

    ki = digitalio.DigitalInOut(KI_PIN)
    ki.direction = digitalio.Direction.OUTPUT
    ki.value = False

    # Rugó feszes bemeneti pin inicializálása
    rugo_feszes_input = digitalio.DigitalInOut(RUGO_FESZES_PIN)
    rugo_feszes_input.direction = digitalio.Direction.INPUT
    rugo_feszes_input.pull = digitalio.Pull.UP # Belső felhúzó ellenállás aktiválása

    time.sleep(BOOT_DELAY)

    # --- Nullapont beállítása (ms felbontás alapja) ---
    t0 = time.monotonic()
    
    def now_ms():
        return int((time.monotonic() - t0) * 1000)

    print("időzítő nullázva és elindítva")
    print(f"[{now_ms()} ms] Rugó állapota induláskor: {'FESZES' if not rugo_feszes_input.value else 'LAZA'}")
    # IO3 alacsony = FESZES, IO3 magas = LAZA
  
    # --- végtelen ciklus ---
    while True:
        # BE impulzus kezdete — kiírás ms pontossággal
        print("[{0} ms] BE impulzus kiadva".format(now_ms()))
        be.value = True
        time.sleep(PULSE)
        be.value = False
        print("[{0} ms] BE impulzus visszavéve".format(now_ms()))

        # Várjuk a "rugó feszes" jelzést
        start_wait_time = time.monotonic()
        rugo_feszes_jelzes_megerkezett = False

        print(f"      [{now_ms()} ms] Várakozás a 'rugó feszes' jelzésre (max {RUGO_FESZES_TIMEOUT} mp)...")

        # A "rugó feszes" jelzés várhatóan ALACSONY lesz, ha feszes a rugó.
        # Feltételezzük, hogy kezdetben LAZA a rugó (HIGH), majd FESZES lesz (LOW).
        while time.monotonic() - start_wait_time < RUGO_FESZES_TIMEOUT:
            if not rugo_feszes_input.value: # Ha a pin ALACSONY (rugó feszes)
                rugo_feszes_jelzes_megerkezett = True
                break
            time.sleep(0.05) # Rövid várakozás, hogy ne pörögjön a CPU feleslegesen

        if rugo_feszes_jelzes_megerkezett:
            print(f"      [{now_ms()} ms] 'Rugó feszes' jelzés megérkezett. Rugó sikeresen felhúzva.")
            cycle_count += 1 # Csak itt növeljük a ciklusszámlálót
        else:
            print(f"\n[HIBA] [{now_ms()} ms] Időtúllépés! A 'rugó feszes' jelzés nem érkezett meg {RUGO_FESZES_TIMEOUT} mp alatt.")
            print("[HIBA] A program leáll, mert a rugófelhúzó motor valószínűleg hibás.")
            raise SystemExit # Program leállítása hibaüzenettel

        print("      [{0} ms] KI impulzus {1} mp múlva........".format(now_ms(), WAIT_AFTER_BE))

        # 20 s csönd (mindkettő GPIO inaktív)
        time.sleep(WAIT_AFTER_BE)

        # KI impulzus kezdete — kiírás ms pontossággal
        print("[{0} ms] KI impulzus kiadva".format(now_ms()))
        ki.value = True
        time.sleep(PULSE)
        ki.value = False
        print("[{0} ms] KI impulzus visszavéve".format(now_ms()))
        
        # --- CIKLUS ÖSSZEGZÉS ---
        print("\n===== [{0} ms] BE-KI ciklus befejezve. Eddig {1} rugófelhúzás volt =====\n".format(now_ms(), cycle_count))
        
        print("      [{0} ms] BE impulzus {1} mp múlva........".format(now_ms(), WAIT_AFTER_KI))

        # 10 s csönd
        time.sleep(WAIT_AFTER_KI)

except KeyboardInterrupt:
    print("\n[INFO] Program megszakítva a felhasználó által.")
except SystemExit: # Ezt a kivételt mi dobjuk, ha a rugófelhúzó hiba miatt áll le
    print("[INFO] Program leállítva a rugófelhúzó motor hibája miatt.")
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
    if rugo_feszes_input is not None:
        rugo_feszes_input.deinit() # Bemeneti pin felszabadítása is
    print("[INFO] Program leállítva.")