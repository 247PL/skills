# Przykładowy Raport Audytu Prepress & Post-RIP — Katalog A4 (44 str. + Lakier UV)

- **Data audytu:** `2026-11-13`
- **Tryb:** `re-audit` + `post-rip` (weryfikacja poprawionych plików produkcyjnych oraz impozycji drukarni po RIP-ie)
- **Sprawdzone pliki:**
  - `katalog_okladka.pdf` (4 str., A4 poziom) + `katalog_okladka_UV.pdf` (4 str., maska lakieru wybiórczego UV)
  - `katalog_srodek.pdf` (40 str., A4 poziom) + `katalog_wszystko.pdf` (44 str., podgląd łączony)
  - `rip/screen-RIP___okladka.pdf - 300 dpi.pdf` (2 str., montaż 2-użytkowy B2)
  - `rip/okladka_LAKIER_UV.pdf` (2 str., montaż 2-użytkowy B2)
  - `rip/screen-RIP___srodek.pdf - 300 dpi.pdf` (40 str., raster po RIP-ie 300 DPI)
- **Metoda weryfikacji:** Ekstrakcja `TrimBox`/`BleedBox`/`MediaBox`, matematyczne porównanie współrzędnych krzywych wektorowych ($0{,}0000\text{ pt}$), kontrola synchronizacji pikselowej 1:1 oraz wygenerowanie wizualnego nakładu kontrolnego UV na CMYK (`PODGLAD_PASOWANIA_LAKIERU_UV.pdf`).

---

## 1. Werdykt

> **Status:** **GOTOWE DO DRUKU (100% ZGODNOŚCI)**

Wszystkie błędy z poprzedniej rundy (rozbieżność liczby stron 40 vs 44, zdublowana strona 43, brakujące spady $3\text{ mm}$, kolizja tekstu z linią cięcia na str. 30 oraz niespójności wielkości liter i paginacji w spisie treści) zostały w pełni wyeliminowane. Pliki po RIP-ie oraz montaż lakieru wybiórczego UV pasują z dokładnością do $0{,}0000\text{ pt}$ (w wektorze) oraz $\le 1\text{ px}$ przy $150\text{ DPI}$ (w rastrze RIP).

---

## 2. Parametry techniczne (Prepress & Geometria)

| Parametr | Plik / Część | Wartość oczekiwana | Wartość w pliku | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Format netto (`TrimBox`)** | Okładka i Środek | $297{,}0 \times 210{,}0\text{ mm}$ | $297{,}0 \times 210{,}0\text{ mm}$ | **PASS** |
| **Format ze spadami (`BleedBox`)** | Okładka i Środek | $303{,}0 \times 216{,}0\text{ mm}$ ($3\text{ mm}$) | $303{,}0 \times 216{,}0\text{ mm}$ ($3\text{ mm}$) | **PASS** |
| **Objętość i podzielność** | Środek + Okładka | $40 + 4 = 44\text{ str.}$ ($\div 4$) | $40 + 4 = 44\text{ str.}$ | **PASS** |
| **Synchronizacja plików** | `okladka` + `srodek` vs `wszystko` | 1:1 co do piksela | `0.00` średniej różnicy RGB | **PASS** |
| **Pasowanie maski UV (źródło)** | `okladka.pdf` vs `okladka_UV.pdf` | Różnica $0{,}0000\text{ pt}$, $100\%\text{ K}$ | Max diff: $0{,}0000\text{ pt}$ | **PASS** |
| **Pasowanie maski UV (po RIP)** | Montaż B2 ($640 \times 450/464\text{ mm}$) | Wspólna baza od $y = 0\text{ pt}$ | Oś grzbietu $x = 907{,}09\text{ pt}$, pasery 1:1 | **PASS** |

---

## 3. Szczegóły weryfikacji maski lakieru UV i impozycji po RIP-ie

1. **Elementy objęte lakierem wybiórczym UV ($100\%\text{ K}$):**
   - **I strona okładki (front):**
     - Napis tytułowy *„URZĄDZENIA I OPROGRAMOWANIE”* — lakier bezpośrednio na literach.
     - Logo — polakierowane oba prostokątne bloki tła logotypu, natomiast sam sygnet i litery są wybrane ($0\%\text{ K}$, pozostają matowe).
   - **IV strona okładki (tył):**
     - Logo na dole strony — bloki tła lakierowane, litery i sygnet wybrane.
   - **II i III strona okładki (wnętrze):**
     - Czyste w obszarze netto (brak lakieru).
2. **Wyjaśnienie różnicy wysokości arkusza w podglądzie po RIP-ie ($464\text{ mm}$ vs $450\text{ mm}$):**
   - Plik UV po RIP-ie ma wymiar $640 \times 450\text{ mm}$ ($1814{,}17 \times 1275{,}59\text{ pt}$), natomiast plik CMYK ma $640 \times 464\text{ mm}$ ($1814{,}17 \times 1315{,}27\text{ pt}$).
   - Dodatkowe $14\text{ mm}$ na dole arkusza CMYK to pas technologiczny drukarni na chwytaki maszyny. Punkt bazowy od góry ($y = 0{,}00\text{ pt}$), znaczniki łamania grzbietu ($x = 907{,}09\text{ pt}$) oraz obrysy obu użytków pokrywają się w 100%.
   - Wygenerowano plik kontrolny `rip/PODGLAD_PASOWANIA_LAKIERU_UV.pdf` z nałożoną maską UV w kolorze jaskrawej magenty na arkusz CMYK.

---

## 4. Status poprawek z poprzedniej rundy (`re-audit`)

| Lp. | Zgłoszenie z poprzedniej rundy | Lokalizacja | Status | Komentarz weryfikacyjny |
| :--- | :--- | :--- | :--- | :--- |
| 1. | Rozbieżność liczby stron (`srodek` 42 str. vs `wszystko` 44 str.) i zdublowana str. 43 | Cały dokument | **`FIXED`** | `srodek.pdf` ma dokładnie 40 str., `wszystko.pdf` 44 str. |
| 2. | Brak spadów $3\text{ mm}$ w pliku środka | `srodek.pdf` | **`FIXED`** | `BleedBox` wynosi $303 \times 216\text{ mm}$ na wszystkich 40 stronach. |
| 3. | Kolizja tekstu ze spadem / linią cięcia | `str. 30` | **`FIXED`** | Tekst odsunięty na bezpieczny margines wewnętrzny. |
| 4. | Niespójna wielkość liter w spisie treści (*Funkcje* vs *funkcje*) oraz literówka *Zarządzenia* | `okladka str. 2` (Spis treści) | **`FIXED`** | Ujednolicono na *„Najważniejsze funkcje...”* oraz *„System Zarządzania Treścią”*. |
| 5. | Podział wyrazu `bane- rów` na końcu wiersza | `srodek str. 38` (`wszystko str. 40`) | **`ACKNOWLEDGED`** | Podział `ba-ne-rów` (sylaba otwarta) jest poprawny słownikowo. |
| 6. | Stopka `TREŚCI ZOSTAŁY WYGENEROWANE Z AI` | `srodek str. 3–4` | **`INTENTIONAL`** | Pozostawiono zgodnie z wyraźnym wymogiem klienta. |
