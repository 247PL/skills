# print-prepress-audit

An AI agent skill for running deterministic DTP, prepress, post-RIP imposition, spot-finish (`Lakier UV`, `Spot White`, die-cut), and editorial/typographic audits on print-ready PDFs (catalogs, brochures, folded leaflets, calendars, posters, labels, and packaging).

## Audit Modes

| Mode | Stage | Scope | Best For |
| :--- | :--- | :--- | :--- |
| **`preflight`** *(default)* | Pre-press (before sending to print house) | Page count & binding math ($\div 4$), `TrimBox`/`BleedBox` ($3\text{–}5\text{ mm}$), safe margin collisions, effective image DPI & CMYK check, font embedding, vector UV mask alignment ($0.0000\text{ pt}$), TOC sync, and full copy/typography review | Final quality gate before exporting/sending production PDFs to a print house |
| **`post-rip`** | Print house RIP proofs (`rip/` folder) | Rasterized `screen-RIP` 300 DPI proofs, 2-up B2 sheet imposition, outer (`1 A`) vs inner (`1 B`) side matching, gripper margin offset compensation, visual magenta UV-on-CMYK overlay PDF generation, and page-by-page diff against source PDFs | Approving print house RIP proofs (`do akceptacji po ripie`) with 100% confidence |
| **`re-audit`** | Post-fix verification | File modification timestamp check, delta verification (`FIXED` / `OPEN` / `PARTIAL` / `REGRESSION`), split-vs-combined PDF pixel synchronization (`okladka` + `srodek` vs `wszystko`), and DOCX-to-PDF copy comparison | Verifying designer DTP corrections after an earlier review round |

## Key Capabilities

- **Deterministic PyMuPDF Probe Script** (`scripts/prepress_probe.py`) — 6 CLI subcommands (`inspect`, `uv-align`, `diff-pdfs`, `diff-split`, `match-pages`, `uv-overlay`) providing mathematical verification instead of visual guesswork:
  - Extracts `TrimBox`, `BleedBox`, `CropBox`, and `MediaBox` in millimeters and checks safe-zone margin collisions.
  - Computes effective placed DPI and color space (`DeviceCMYK` vs `DeviceRGB`) for every embedded raster XObject.
  - Compares spot UV / die-cut vector paths against CMYK artwork paths down to **`0.0000 pt`** and identifies knockouts (*wybrania*).
  - Deterministically matches left/right halves of imposed RIP press sheets against source cover pages and compensates for printer gripper margins (*pas technologiczny na chwytaki*).
  - Generates a standalone visual proof PDF (`PODGLAD_PASOWANIA_LAKIERU_UV.pdf`) overlaying the spot UV plate in glowing magenta directly onto the CMYK cover or RIP sheet.
- **Multi-File & Source-Copy Synchronization** — cross-checks split production files (`okladka.pdf` + `srodek.pdf`) against combined preview PDFs (`wszystko.pdf`), synchronizes Table of Contents (*Spis treści*) headings and folios against body pages, and diffs `.docx`/`.md` source copy sentence-by-sentence against PDF text layers.
- **Polish DTP & Typography Pack** (`references/regional/pl-dtp.md`) — built-in rules for Polish syllabification (including open-syllable false-positive guards like `ba-ne-rów`), hanging single-letter prepositions (`a, i, o, u, w, z`), non-breaking spaces after abbreviations (`ds.`, `ul.`, `nr`, `str.`), hyphen (`-`) vs en-dash (`–`) consistency, Polish quotation marks (`„...”`), phone separators (`·` vs `˙`), and justified text rivers.

## Installation

### Using `skills` CLI

```bash
npx skills add 247PL/skills --skill print-prepress-audit
```

### Manual Installation

Clone or link this folder into your agent's skills directory:

| Agent | Global Path | Workspace / Project Path |
| :--- | :--- | :--- |
| **Universal / Cross-Agent** | `~/.agents/skills/print-prepress-audit` | `<project>/.agents/skills/print-prepress-audit` |
| **Claude Code** | `~/.claude/skills/print-prepress-audit` | `<project>/.claude/skills/print-prepress-audit` |
| **Codex** | `~/.codex/skills/print-prepress-audit` | `<project>/.codex/skills/print-prepress-audit` |
| **Hermes Agent** | `~/.hermes/skills/print-prepress-audit` | *or add `<repo>/skills` to `skills.external_dirs` in `~/.hermes/config.yaml`* |
| **Antigravity** | `~/.gemini/config/skills/print-prepress-audit` | `<project>/.agents/skills/print-prepress-audit` |
| **Cursor** | `~/.cursor/skills/print-prepress-audit` | `<project>/.cursor/skills/print-prepress-audit` |

> **Prerequisite:** Python 3 with `pymupdf` (`pip install pymupdf pillow numpy`).

## Quick CLI Usage (`scripts/prepress_probe.py`)

```bash
# 1. Inspect page boxes, bleeds (mm), fonts, image DPI/CMYK, and safe-margin collisions
python scripts/prepress_probe.py inspect katalog_srodek.pdf --safe-mm 3.5 --min-dpi 250

# 2. Verify exact vector alignment (0.0000 pt) between CMYK cover and spot UV mask
python scripts/prepress_probe.py uv-align katalog_okladka.pdf katalog_okladka_UV.pdf

# 3. Verify combined preview PDF matches split cover + inside PDFs 1:1
python scripts/prepress_probe.py diff-split katalog_okladka.pdf katalog_srodek.pdf katalog_wszystko.pdf

# 4. Match imposed 2-up RIP cover sheet halves against 4-page source cover
python scripts/prepress_probe.py match-pages "rip/screen-RIP___okladka.pdf" katalog_okladka.pdf --two-up

# 5. Generate a visual magenta UV-on-CMYK registration overlay PDF
python scripts/prepress_probe.py uv-overlay "rip/screen-RIP___okladka.pdf" "rip/okladka_LAKIER_UV.pdf" "rip/PODGLAD_PASOWANIA_LAKIERU_UV.pdf"
```

## Example Prompts

- **Full pre-press catalog audit**:
  > Sprawdź pliki katalogu (`okladka.pdf`, `okladka_UV.pdf`, `srodek.pdf`, `wszystko.pdf`) przed wysłaniem do drukarni — szczególnie spady, marginesy, pasowanie lakieru UV, spis treści i błędy w tekście.
- **Post-RIP verification**:
  > Sprawdź pliki do akceptacji (po ripie) w folderze `rip/` i zweryfikuj, czy lakier UV pokrywa się z okładką.
- **Leaflet / brochure re-audit against DOCX copy**:
  > Porównaj zaktualizowane ulotki DL w folderze `gotowe/` z plikami `.docx` i sprawdź, co zostało poprawione od poprzedniego raportu.

## Repository Structure

```text
print-prepress-audit/
├── SKILL.md                          # Main skill instructions & workflow
├── scripts/
│   └── prepress_probe.py             # Deterministic PyMuPDF/Pillow/NumPy prepress & RIP probe
├── references/
│   ├── checklist.md                  # Core DTP, geometry, spot UV, RIP & copy checklist
│   └── regional/
│       └── pl-dtp.md                 # Polish DTP typography, syllabification & copy rules
├── templates/
│   └── report-template.md            # Structured Markdown prepress audit report template
├── examples/
│   └── sample-report.md              # Full sample multi-stage catalog & post-RIP audit report
└── README.md
```

## License

MIT
