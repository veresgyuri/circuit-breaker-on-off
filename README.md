# circuit-breaker-on-off
CircuitPython test code for a spring charging motor of the high-voltage circuit breaker

**Disclaimer:**  
This is an independent, non-manufacturer document.  
See [SAFETY_AND_LEGAL.md](SAFETY_AND_LEGAL.md) for full legal and safety information.

Sorry folks, this repo comes with Hungarian comments only 🙂

# --- KÖF megszakító – felhúzómotor tesztelése ---

**Jogi figyelmeztetés:**  
Ez egy független, nem gyártói anyag.  
A teljes jogi és biztonsági információkat [itt olvashatod](SAFETY_AND_LEGAL.md).

**Az alapprobléma:**  
A rugófelhúzó egységben, idővel elreped az egyik fröccsöntött fogaskerék.

<img src="images/vd4_motorblokk_repedt_kerek_kozeli.jpg" alt="Elrepedt" width="200">

**Egy lehetséges megoldás:**  
3D nyomtatott műanyag fogaskerékre cseréljük a hibás alkatrészt.

**Tesztelés:**  
Folyamatos KI-BE kapcsolásokkal nyúzzuk a rugóerőtároló egység felhúzó motorját.

# A cél annak kiderítése, hogy a 3D nyomtatott fogaskerék anyagválasztása sikeres volt-e.

Hardver: ESP32-S3-Zero mikrovezérló

Szoftver: CircuitPython 10.x

A CircuitPython jelenleg a legdinamikusabban fejlődő programozási nyelv a DIY kategóriában (2025. okt.)

Ebben a repóban a tesztelő szoftver életútjáról is találsz verziókövető leírásokat.
Ha ötleted van, vagy hibát találsz, bátran jelezd!

---
Egy kis vizuális betekintés

<img src="images/vd4_motorblokk_repedt_kerek.png" alt="Elrepedt" width="400">

<img src="images/rugofelhuzo_motorblokk.jpg" alt="Motorblokk" width="400">

<img src="images/fogaskerek_egyuttes.jpg" alt="Fogaskerekek" width="400">

<img src="images/nyomtatott_fogaskerek_kozeli.jpg" alt="Új kerék" width="400">

<img src="images/test_aramkor.jpg" alt="0v9 áramkör" width="400">

<img src="images/diagram2.png" alt="kapcsolási rajz-2" width="400">

<img src="images/teljes_teszt_aramkor1.jpg" alt="4 relés megoldás AC-DC" width="400">

<img src="images/20251125_masodik_teszt.jpg" alt="Indul a tesztelés..." width="400">
