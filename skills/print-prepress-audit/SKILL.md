---
name: print-prepress-audit
description: >-
  Runs a comprehensive DTP, prepress, post-RIP, spot-finish (UV varnish, white
  underbase, die-cut), and editorial/typographic quality audit on print-ready
  PDFs (catalogs, brochures, leaflets, calendars, posters, labels, packaging).
  Supports three modes (preflight, post-rip, re-audit), deterministic PyMuPDF
  vector/raster probes, visual UV-on-CMYK overlay generation, cross-file
  synchronization (cover + inside vs combined PDF, or source DOCX/MD vs PDF),
  and regional typography rules (e.g. Polish DTP). Use whenever the user asks
  to check files for print, verify a catalog or brochure before sending to the
  print house, check post-RIP proofs, verify if a UV mask aligns, or audit
  text/TOC in a PDF (e.g. "sprawdź pliki do druku", "sprawdź katalog po ripie",
  "czy UV się pokrywa", "preflight PDF", "audit prepress", "sprawdź ulotkę").
---

# Print & Prepress DTP Audit (`print-prepress-audit`)

Perform an evidence-backed technical prepress, visual DTP, spot-finish registration, and editorial/typographic audit of print-ready PDF files before press sign-off or after receiving print-house RIP proofs.

## Modes

Select the mode that matches the stage of production. Default to **`preflight`** when given production PDFs, **`post-rip`** when given rasterized RIP proofs or imposition sheets (e.g. files in a `rip/` folder or named `screen-RIP*`), and **`re-audit`** when verifying fixes after an earlier round.

### 1. Preflight Mode (`preflight`) — *Default*
Complete pre-press audit before sending files to the print house:
- **Structure & Binding Math**: Verify page counts across split files (`okladka.pdf` + `srodek.pdf` vs combined `wszystko.pdf`), check divisibility by 4 for saddle-stitch (*oprawa zeszytowa*) or signature requirements for perfect binding (*oprawa klejona*), and scan for accidental duplicate or missing pages.
- **Page Boxes & Bleeds**: Inspect `TrimBox`, `BleedBox`, `CropBox`, and `MediaBox` in millimeters ($1\text{ pt} = 25.4 / 72\text{ mm}$). Confirm uniform bleed (typically $3\text{ mm}$ or $5\text{ mm}$) and verify that background artwork actually extends to the `BleedBox` edge.
- **Safe Zone & Margin Collisions**: Flag text, folios (page numbers), tables, or logos positioned closer than $3\text{–}5\text{ mm}$ to the `TrimBox` edge or spine fold.
- **Spot Finishes (`UV`, `Spot White`, `Die-Cut`)**: Verify vector alignment ($0.0000\text{ pt}$ tolerance) between the spot mask PDF (`*_UV.pdf`) and the CMYK artwork PDF, confirm $100\%\text{ K}$ (`0 0 0 1 k`) or proper `/Separation` channel usage, inspect knockouts (*wybrania*), and confirm inside covers (pp. II & III) are clean when only outside covers receive varnish.
- **Color, Effective DPI, AI Assets & Fonts**: Check embedded images for effective resolution ($\ge 250\text{–}300\text{ DPI}$) and `DeviceCMYK` color space, inspect AI-generated/composited images for artifacts, and verify all fonts are embedded or outlined.
- **Editorial, TOC & Typography**: Cross-check Table of Contents (*Spis treści*) titles, casing, and page numbers against body headings; compare against source `.docx`/`.md` copy if provided; apply regional DTP rules (e.g. [references/regional/pl-dtp.md](./references/regional/pl-dtp.md)).

### 2. Post-RIP & Imposition Mode (`post-rip`)
Final sign-off audit of proofs returned by the print house (`do akceptacji po ripie`):
- **Imposition & Sheet Layout**: Identify multi-up imposition layouts (e.g. 2-up B2 sheet $640 \times 450\text{ mm}$ with outer spread `1 A` and inner spread `1 B`).
- **Page Order & Side Matching**: Match each RIP page against source cover/inside pages by visual pixel comparison (`scripts/prepress_probe.py match-pages`)—never assume 0-based vs 1-based page order without verifying which page holds Side A (Front + Back, pp. IV + I) vs Side B (Inside, pp. II + III).
- **Gripper Margin Compensation**: Print houses often add a technological gripper margin (*pas technologiczny na chwytaki*, e.g. $14\text{ mm}$ at the bottom of the CMYK sheet: $640 \times 464\text{ mm}$ CMYK vs $640 \times 450\text{ mm}$ UV). Because PDF viewers center pages in the viewport, tabbing between CMYK and UV makes the image "jump" vertically. Always verify registration from the common origin ($y = 0\text{ pt}$), spine fold line, and registration marks rather than viewer window centering.
- **UV / Spot Registration Proof**: Generate a visual overlay PDF (`PODGLAD_PASOWANIA_LAKIERU_UV.pdf`) highlighting the UV mask in glowing magenta directly over the CMYK RIP sheet so the user can visually confirm 1:1 registration.
- **Body Pages RIP Diff**: Compare all rasterized `screen-RIP` body pages against the approved source PDF to confirm zero dropped glyphs, font substitutions, clipped bleeds, or outdated file versions.

### 3. Re-Audit Mode (`re-audit`)
Verification of DTP fixes after an earlier audit round:
- **Timestamp & File Sync Check**: Check modification timestamps across all deliverables (`okladka`, `srodek`, `wszystko`, `UV`, or multi-variant leaflets `v01..v04`) to immediately spot files that were not re-exported.
- **Delta Verification**: Re-test every prior finding and classify as `FIXED`, `OPEN`, `PARTIAL`, or `REGRESSION`.
- **Full-File Synchronization**: Confirm that fixes applied to `srodek.pdf` or `okladka.pdf` were also propagated to the combined `wszystko.pdf` (and vice versa) via pixel-diff verification.

## Execution Workflow

1. **Be Transparent About Verification Methods**:
   - State the exact deterministic methods used: PDF box geometry extraction, vector path bounding-box comparison (`0.0000 pt`), embedded image XObject inspection, text/glyph extraction, and raster pixel-diffing via PyMuPDF (`pymupdf`) + Pillow/NumPy.
   - Never claim external commercial GUI tools (such as Adobe Acrobat Pro Preflight or Enfocus PitStop) were executed unless actually invoked.
2. **Run the Deterministic Prepress Probe Script**:
   - Use [scripts/prepress_probe.py](./scripts/prepress_probe.py) to extract exact JSON/console facts for page boxes, fonts, image DPI/colorspace, margin collisions, vector UV alignment, page-to-page pixel diffs, and visual UV overlays.
   - Always force UTF-8 output (`PYTHONIOENCODING=utf-8` or explicit UTF-8 file writes) to avoid Windows `cp1250` crashes on typographic ligatures (`\ufb01` `fi`, `\ufb02` `fl`).
3. **Apply Regional Typography & Copy Rules**:
   - For Polish-language publications, automatically load [references/regional/pl-dtp.md](./references/regional/pl-dtp.md) (syllable division rules such as open-syllable `ba-ne-rów`, hyphen `-` vs en-dash `–`, hanging single-letter prepositions, non-breaking spaces after abbreviations like `ds.`, phone/address formatting, and justified text rivers).
4. **Respect Intentional Client & Production Decisions**:
   - If the user or project notes specify mandatory client constraints (e.g. keeping `"TREŚCI ZOSTAŁY WYGENEROWANE Z AI"` disclaimers, intentional non-standard contrast on brand colors, or preserving source schedule timestamps), log them as `ACKNOWLEDGED / INTENTIONAL` rather than flagging them as errors.
5. **Preserve Existing Files**:
   - Never overwrite the user's original production PDFs. Save generated visual overlays (e.g. `PODGLAD_PASOWANIA_LAKIERU_UV.pdf`), diff crops, or JSON QC reports as separate verification files.

## Report Format & Deliverables

- **Default Output**: Deliver a clear, structured report in the **user's language**, organized into:
  1. **Verdict / Print Readiness Summary** (`READY FOR PRINT`, `READY WITH MINOR NOTES`, or `BLOCKED — FIXES REQUIRED`)
  2. **Blocking Prepress / Geometry / Spot-Finish Issues**
  3. **Editorial, TOC & Typographic Issues** (with exact page numbers and quoted text)
  4. **Verified Parameters** (TrimBox, BleedBox, page count, effective DPI, color space, UV registration accuracy in `pt`/`mm`)
  5. **Ready-to-Send Note for the Print House** (when relevant, e.g. for RIP sign-off or specialty ink handling)
- **File Export (on request)**: Use [templates/report-template.md](./templates/report-template.md) for Markdown reports or save a structured `qc.json` / `preflight.json` manifest alongside the deliverables.
- **Reference Materials**:
  - Full technical checklist: [references/checklist.md](./references/checklist.md)
  - Polish DTP & editorial rules: [references/regional/pl-dtp.md](./references/regional/pl-dtp.md)
  - Sample multi-stage audit report: [examples/sample-report.md](./examples/sample-report.md)
