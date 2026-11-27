# Raport Audytu Prepress / DTP — `{{PROJECT_NAME}}`

- **Data audytu:** `{{DATE}}`
- **Tryb:** `{{MODE}}` (`preflight` / `post-rip` / `re-audit`)
- **Sprawdzone pliki:**
  - `{{FILE_1}}` *(rozmiar, data modyfikacji, liczba stron)*
  - `{{FILE_2}}`
- **Metoda weryfikacji:** Ekstrakcja geometrii (`TrimBox` / `BleedBox` / `MediaBox`), porównanie ścieżek wektorowych ($0{,}0000\text{ pt}$), kontrola fontów i rozdzielczości XObject, weryfikacja tekstowa/typograficzna oraz porównanie pikselowe (`PyMuPDF` + `Pillow`/`NumPy`).

---

## 1. Werdykt

> **Status:** `{{STATUS}}` *(GOTOWE DO DRUKU / GOTOWE Z DROBNYMI UWAGAMI / WYMAGA POPRAWEK PRZED DRUKIEM)*

{{EXECUTIVE_SUMMARY}}

---

## 2. Parametry techniczne (Prepress & Geometria)

| Parametr | Plik / Część | Wartość oczekiwana | Wartość w pliku | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Format netto (`TrimBox`)** | Okładka / Środek | `{{EXPECTED_TRIM}}` | `{{ACTUAL_TRIM}}` | {{TRIM_STATUS}} |
| **Format ze spadami (`BleedBox`)** | Okładka / Środek | `{{EXPECTED_BLEED}}` | `{{ACTUAL_BLEED}}` | {{BLEED_STATUS}} |
| **Liczba stron i podzielność** | Środek + Okładka | `{{EXPECTED_PAGES}}` | `{{ACTUAL_PAGES}}` | {{PAGES_STATUS}} |
| **Przestrzeń barwna i DPI** | Obrazy rastrowe | CMYK, $\ge 250\text{–}300\text{ DPI}$ | `{{ACTUAL_COLOR_DPI}}` | {{DPI_STATUS}} |
| **Fonty** | Wszystkie strony | Osadzone lub krzywe | `{{ACTUAL_FONTS}}` | {{FONTS_STATUS}} |
| **Pasowanie maski UV / Wykrojnika** | `{{UV_FILE}}` | Różnica $0{,}0000\text{ pt}$, $100\%\text{ K}$ | `{{ACTUAL_UV_DIFF}}` | {{UV_STATUS}} |

---

## 3. Błędy blokujące druk (Prepress / Geometria / Pasowanie)

- [ ] **{{ISSUE_1_LOCATION}}:** {{ISSUE_1_DESCRIPTION}}
- [ ] **{{ISSUE_2_LOCATION}}:** {{ISSUE_2_DESCRIPTION}}

*(Jeśli brak błędów blokujących: **Brak — wszystkie parametry techniczne i pasowanie w normie.**)*

---

## 4. Korekta treści, Spis treści i Typografia

- [ ] **Spis treści (`str. X`):** {{TOC_FINDINGS}}
- [ ] **Tekst i interpunkcja (`str. Y`):** {{COPY_FINDINGS}}
- [ ] **Marginesy bezpieczeństwa (`str. Z`):** {{MARGIN_FINDINGS}}

---

## 5. Status poprawek (tylko w trybie `re-audit`)

| Lp. | Zgłoszenie z poprzedniej rundy | Lokalizacja | Status | Komentarz weryfikacyjny |
| :--- | :--- | :--- | :--- | :--- |
| 1. | {{PRIOR_ITEM_1}} | `str. X` | `FIXED` / `OPEN` | {{VERIFY_NOTE_1}} |

---

## 6. Notatka dla drukarni (opcjonalnie)

```text
{{PRINTER_NOTE}}
```
