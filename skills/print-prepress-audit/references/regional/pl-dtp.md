# Regional DTP & Editorial Rules: Polish (`pl-dtp`)

Apply this checklist automatically whenever auditing Polish-language catalogs, brochures, leaflets, calendars, posters, or packaging.

---

## 1. Polish Syllabification & Line-End Hyphenation (*Dzielenie wyrazów*)

When reviewing line-end word breaks in narrow columns, product cards, or justified paragraphs:

- **Open-Syllable Rule (*Sylaby otwarte*)**:
  - Standard Polish syllabification prefers breaking after a vowel (open syllable), moving the single intervocalic consonant to the next line.
  - **Important False-Positive Guard**: Words like *banerów* divide phonetically and orthographically into **`ba-ne-rów`** (so both `ba-nerów` and `bane-rów` are valid line breaks!). Never flag a valid open-syllable break (`CV-CV-CVC`) as an error; always verify the full syllable chain before reporting a hyphenation mistake.
- **True Hyphenation Errors to Flag**:
  - Breaking monosyllabic words (e.g. *wstrząs*, *zjazd*, *krzyż*).
  - Leaving a single letter at the end or start of a line (e.g. `o-raz`, `u-rząd`).
  - Separating two vowels that do not form separate syllables or splitting digraphs (`ch`, `cz`, `dz`, `dż`, `dź`, `rz`, `sz`).
  - Awkward breaks in short proper names, brand names, or section headers (e.g. breaking `Kon-takt` in a footer heading or splitting product codes like `Q-NSK`, `SENSO-WAY` when avoidable).
  - Double hyphens / stray hard hyphens left inside a line after text reflow (e.g. `wypo- sażone` in the middle of a line).

---

## 2. Hanging Conjunctions, Prepositions & Non-Breaking Spaces (*Wiszące spójniki i skróty*)

- **Single-Letter Prepositions & Conjunctions (*Sierotki / wiszące spójniki*)**:
  - Single-letter words (**`a, i, o, u, w, z`** — both lowercase and uppercase) must **never** be left at the end of a line. Bind them to the following word with a non-breaking space (`\u00A0`).
  - In technical or tight DTP layouts, also check two-letter prepositions (`do, na, od, po, we, za, ze`) in large display headings.
- **Abbreviations Requiring Non-Breaking Spaces**:
  - Bind abbreviations to their following noun/number so they never split across lines:
    - `ds.␣Narkomanii`, `im.␣...`, `św.␣...`
    - `ul.␣...`, `al.␣...`, `pl.␣...`, `os.␣...`
    - `nr␣...`, `pkt␣...`, `str.␣...` / `s.␣...`, `rys.␣...`, `tab.␣...`, `ust.␣...`, `art.␣...`
  - Bind numbers to units and currency symbols at the end of a clause:
    - `2026␣r.`, `30␣lat`, `100␣mm`, `300␣DPI`, `4 550␣zł`, `23%␣VAT`.

---

## 3. Dashes, Hyphens & Quotation Marks (*Myślniki i cudzysłowy*)

- **Hyphen / Dywiz (`-`, U+002D) vs En-Dash / Półpauza (`–`, U+2013) vs Em-Dash / Pauza (`—`, U+2014)**:
  - **Dywiz (`-`)**: used *without spaces* inside compound words (`biało-czerwony`, `produktowo-systemowy`, `roll-up`, `Q-NSK`, `on-line`).
  - **Półpauza (`–`)**: standard in Polish DTP for sentence pauses (*myślnik* with spaces: `␣–␣`, e.g. `form wsparcia – prawnych`) and numeric/time ranges (*without spaces*: `10–15`, `9:30–12:30`, `str. 4–7`).
  - **Inconsistency Trap**: Flag sentences or documents that mix a hyphen with spaces (` - `), an en-dash (` – `), and an em-dash (` — `) in the same text block or series of leaflets.
- **Polish Quotation Marks (*Cudzysłowy drukarskie*)**:
  - Standard Polish quotes use lower opening **`„`** (U+201E) and upper closing **`”`** (U+201D) — never straight typewriter quotes (`"..."`) or English upper opening quotes (`“...”`).
  - Inner nested quotes in Polish DTP use guillemets (`«...»` or `»...«`).
  - Always check that every opened `„` has a matching closing `”`.

---

## 4. Capitalization, Headings & Table of Contents Consistency

- **Polish Sentence Case vs English Title Case**:
  - In Polish typography, section headings and Table of Contents entries use **sentence case** (only the first word and proper nouns/acronyms capitalized, e.g. *„Najważniejsze funkcje DINE”*, *„Elektroniczna tablica ogłoszeń ETO”*, *„System zarządzania treścią – DINE”*).
  - Flag inconsistent capitalization between the Table of Contents and body headings (e.g. `"Najważniejsze Funkcje DINE"` in TOC vs `"Najważniejsze funkcje DINE"` on p. 19, or mixing `"Funkcje"` and `"funkcje"` in adjacent lines of the same TOC).
- **Common Typos & Inflection Traps in Polish Catalogs**:
  - Verbal noun typos in system names: e.g. *„System Zarządzania Treścią”* vs erroneous *„System Zarządzenia Treścią”* (*zarządzania* = continuous management; *zarządzenia* = issuing a single decree).
  - Missing diacritics (`ą, ć, ę, ł, ń, ó, ś, ź, ż`), especially on uppercase letters (`Ś, Ć, Ź, Ż, Ł, Ó`).
  - Accidental double spaces, missing spaces before opening parentheses, or stray characters at the end of imported `.docx` paragraphs (e.g. `uporządkowania.v` or `do kontaktu.Kod QR` without a paragraph break).

---

## 5. Contact Blocks, Phone Numbers & Justified Text Rivers

- **Phone Number & Separator Formatting**:
  - Use consistent spacing across all pages/variants in a series: standard Polish 9-digit grouping `+48 123 456 789` (mobile) or `+48 33 851 44 30` (landline with area code).
  - Flag inconsistent prefixes across a series (e.g. `tel. +48...` on leaflet v01, `tel. 33...` without `+48` on v03, and no `tel.` label on v02/v04).
  - Inspect list/phone separators carefully: watch for a misplaced Polish overdot diacritic **`˙`** (U+02D9) or semicolon `;` used instead of a middle dot **`·`** (U+00B7, `punkt środkowy`).
- **Rivers in Justified Text (*Rozstrzelone wiersze / korytarze w justowaniu*)**:
  - In narrow columns (such as DL trifold panels or 2-column catalog cards), flag lines with excessive word spacing caused by long unhyphenated Polish words (*„Osoba doświadczająca przemocy może”*, *„psychologiczne, psychoterapię indywidualną”*). Recommend manual soft-hyphen (`\u00AD`) insertion or subtle tracking adjustment (`-5` to `-15`).
- **Unicode Ligatures in PDF Text Extraction**:
  - Polish PDFs exported from InDesign/Illustrator frequently encode `fi` and `fl` as Unicode ligatures (`\ufb01`, `\ufb02`). Ensure all Python extraction scripts run with UTF-8 encoding (`sys.stdout.reconfigure(encoding='utf-8')`) so console output never crashes on Windows `cp1250` charmaps.
