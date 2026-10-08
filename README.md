# CE Quiz

Oefen-app (PWA) voor één speler met ruim 1000 vragen over de minor Circulaire Economie: systeemdenken, circulariteit, ecologische grenzen, rapportage, business ethics en greenwashing.

- **App:** `app/`. Statische bestanden die via GitHub Pages worden gepubliceerd. De app werkt offline en is installeerbaar op je telefoon.
- **Vragen genereren:** `python tools/genereer.py` zet de kennisbank (`tools/kb/`) en de handgeschreven vragen (`tools/hand.json`) om naar `app/vragen.js`.
- **Iconen:** `python tools/iconen.py` (vereist Pillow).
- **Klassikale versie (4 spelers, beamer):** `extra/klassikale-battle.html`.

Verhoog na het wijzigen van de app `VERSIE` in `app/sw.js`.
