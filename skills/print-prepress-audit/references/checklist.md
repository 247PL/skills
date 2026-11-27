# Core Print & Prepress DTP Audit Checklist

Use every applicable category below during **`preflight`**, **`post-rip`**, and **`re-audit`** workflows. For Polish-language publications, also load [regional/pl-dtp.md](./regional/pl-dtp.md).

---

## 1. Multi-File Delivery & Pagination Structure (Catalogs, Brochures, Leaflets)

- **File Timestamp & Active Directory Verification**:
  - Verify you are auditing the active working folder (e.g. active Syncthing/production directory rather than an outdated backup copy) and log exact file modification timestamps and byte sizes.
  - When auditing multi-variant sets (e.g. leaflets `v01..v04` or packaging variants `1A, 1B, 2A, 2B`), flag any file whose timestamp did not change since the previous round.
- **Page Count & Binding Math**:
  - **Saddle-Stitch (*Oprawa zeszytowa*)**: Total inside pages (`srodek`) + 4 cover pages (`okladka`) must be divisible by `4`. If `srodek` has 42 or 43 pages, flag the binding error immediately and look for accidental blank or duplicated pages.
  - **Perfect Binding (*Oprawa klejona*)**: Check spine width allowance on the cover spread and confirm page count matches the print house quote.
  - **Folded Leaflets (*Ulotki składane DL / C-fold / Z-fold*)**: Verify panel widths (e.g. $97 + 100 + 100\text{ mm}$ for roll-fold where the inner flap is $2\text{–}3\text{ mm}$ narrower, or $99 + 99 + 99\text{ mm}$ for Z-fold) and confirm outer (`s. 1`: flap | back | front) vs inner (`s. 2`: left | center | right) panel alignment.
- **Cross-File Pixel Synchronization**:
  - When a project delivers both split files (`okladka.pdf` + `srodek.pdf`) and a combined preview (`wszystko.pdf`), run a page-by-page pixel diff (`prepress_probe.py diff-split`) to ensure:
    - `wszystko[0..1]` == `okladka[0..1]` (Cover I & II)
    - `wszystko[2..N+1]` == `srodek[0..N-1]` (Body pages)
    - `wszystko[N+2..N+3]` == `okladka[2..3]` (Cover III & IV)
  - Scan for accidental duplicate pages (e.g. two identical consecutive pages at the end of a catalog).

---

## 2. Geometry, Page Boxes, Bleeds & Safe Margins

- **PDF Page Boxes**:
  - Extract `MediaBox`, `CropBox`, `BleedBox`, `TrimBox`, and `ArtBox` for every page ($1\text{ pt} = 25.4 / 72\text{ mm}$).
  - Flag pages with inconsistent `TrimBox` dimensions within the same document.
- **Bleed Verification (*Spady*)**:
  - Confirm uniform bleed around the `TrimBox`: typically **$3.0\text{ mm}$** ($8.504\text{ pt}$) per side for catalogs, brochures, labels, and calendars, or **$5.0\text{ mm}$** ($14.173\text{ pt}$) for large-format posters/boards.
  - Verify that full-bleed background photos, gradients, and color blocks actually reach the `BleedBox` boundary (watch for artwork clipped cleanly at the `TrimBox` while the `BleedBox` metadata is set to $+3\text{ mm}$ of empty white paper).
- **Safe Margins (*Marginesy wewnętrzne / strefa bezpieczeństwa*)**:
  - All live text, page numbers (folios), footnotes, logos, and QR codes must stay at least **$3\text{–}5\text{ mm}$** ($8.5\text{–}14.2\text{ pt}$) inside the `TrimBox` (and away from the spine fold/gutter).
  - Run `prepress_probe.py inspect` to detect text bounding boxes or drawn objects encroaching on the trim edge.
- **Brand Logo Clearance & Protective Zones**:
  - When brand guidelines or project specs specify a minimum protective zone around a logo (e.g. clearance $\ge 0.5\times$ the width of a lettermark from surrounding ornaments or edges), measure exact vector distances in millimeters.

---

## 3. Spot Finishes: Selective UV Varnish (`Lakier UV`), Spot White & Die-Cuts

- **Exact Vector Registration (`0.0000 pt` Tolerance)**:
  - Compare vector path bounding boxes in the spot mask PDF (`*_UV.pdf`) against the corresponding elements in the CMYK cover/artwork PDF (`prepress_probe.py uv-align`).
  - Confirm `TrimBox`, `BleedBox`, `MediaBox`, and `/Separation /All` registration marks match identically across both files.
- **Knockouts (*Wybrania*) vs Direct Varnish**:
  - Inspect how compound logos and display typography are constructed on the UV plate:
    - *Background block varnished + white letters knocked out (`0% K`)*: the colored/dark logo box receives gloss UV while white letters/icons remain matte.
    - *Direct text varnish (`100% K`)*: headlines (e.g. cover titles) receive raised/gloss UV directly over the letters.
  - Report clearly to the user which elements are varnished and which are knocked out so they can confirm creative intent.
- **Separation Hygiene**:
  - Spot UV masks must be pure vector **$100\%\text{ K}$ (`0 0 0 1 k`)** or a dedicated named spot separation (`/Separation /Lakier_UV` or `/Spot`), with zero stray CMY tint and zero rasterized JPEG compression halos.
  - For 4-page cover UV files where only the outside cover (pp. 1 & 4) is varnished, confirm inside cover pages (pp. 2 & 3) are completely empty inside the `TrimBox` (only slug registration marks allowed).
- **Specialty Ink & Mockup Separation (Packaging, Bags, Apparel, Labels)**:
  - Separate client presentation mockups (`*-wizualizacja-EDYTOWALNA.pdf` with background photos/fabric textures) from production print files (`*-nadruk-*.pdf` with transparent/no background).
  - When white ink is part of the design on colored substrates (e.g. gift bags, dark labels, screen print / DTF transfers), explicitly state whether `Spot White` is separated or represented as vector white, and remind the user to confirm white underbase / minimum line thickness with the print house.

---

## 4. Color Spaces, Effective Image DPI, AI Assets & Fonts

- **Effective Image Resolution**:
  - Calculate effective DPI for every placed raster image XObject based on its pixel width/height and its placed bounding box on the page:
    $$\text{Effective DPI} = \frac{\text{Image Pixels}}{\text{Placed Size in Points} / 72}$$
  - **Thresholds**:
    - Standard offset / digital print (catalogs, brochures, leaflets, labels): **$\ge 250\text{–}300\text{ DPI}$** (flag $< 200\text{ DPI}$ as `WARNING` and $< 150\text{ DPI}$ as `CRITICAL`).
    - Large-format posters / boards ($A1, B1$, roll-ups viewed from distance): **$\ge 150\text{–}200\text{ DPI}$**.
- **Color Spaces & Ink**:
  - Verify production print files use **`DeviceCMYK`** (or required spot separations). Flag leftover `DeviceRGB` images or unflattened RGB transparency groups unless the workflow explicitly uses a calibrated RGB-to-PDF/X print pipeline.
  - Check small body copy and barcodes/QR codes: should be pure **$100\%\text{ K}$** (`0 0 0 1 k`) rather than 4-color rich black to prevent registration blur on press.
- **AI-Generated & Composited Product Imagery**:
  - Inspect AI-generated environments and product composites (e.g. infokiosks, totems, devices composited into hospital/office scenes) for:
    - Incomplete upscaling or jagged mask edges around hardware bezels.
    - Garbled AI-generated background text on wall signs or screens (while respecting intentional client "AI-generated content" disclaimers when mandated).
    - Tonal/shadow consistency in CMYK gamut (deep blues and neon cyans shifting dull in CMYK).
- **Font Embedding & Outlines**:
  - Verify every font in the PDF is either **embedded** (subset `TrueType` / `Type1` / `CIDFont`) or **converted to curves/outlines**.
  - Flag unembedded CFF/OTF fonts (common in automated PPTX/IDML exporters) that require local installation or outline conversion before sending to press.

---

## 5. Post-RIP & Imposition Proof Verification (`rip/` Folder)

When auditing files returned by the print house's RIP software (e.g. `screen-RIP___* - 300 dpi.pdf` and `*_okladka_* LAKIER UV.pdf`):

1. **Identify Imposition Topology**:
   - Determine whether the RIP proof is single-page (e.g. 40 body pages in `srodek`) or an imposed press sheet (e.g. 2-up cover spreads stacked vertically on a B2 sheet $640 \times 450\text{ mm}$).
2. **Verify Page Order (`1 A` vs `1 B`) Deterministically**:
   - Never guess which page of a 2-page RIP PDF is the outer cover vs inner cover. Match the left and right halves of each RIP page against the source cover pages (`Page 1 Front`, `Page 2 Inside Front`, `Page 3 Inside Back`, `Page 4 Back`) via pixel diff (`prepress_probe.py match-pages`).
   - Confirm that **Page 1 of the CMYK RIP** corresponds to **Page 1 of the UV RIP** (typically Side `1 A` = Outer Cover spread: Back p. 4 on left + Spine + Front p. 1 on right; Side `1 B` = Inner Cover spread: p. 2 on left + Spine + p. 3 on right, with empty UV). If the page order differs between CMYK and UV, flag it immediately for the platemaker.
3. **Account for Gripper Margins (*Pas technologiczny na chwytaki*)**:
   - Print houses frequently add a gripper margin at the bottom of the CMYK proof (e.g. CMYK sheet height $464\text{ mm} = 1315.27\text{ pt}$ vs UV sheet height $450\text{ mm} = 1275.59\text{ pt}$, a $14\text{ mm}$ difference).
   - Explain to the user why switching tabs in a PDF viewer causes a visual vertical jump (viewer auto-centering), and verify mathematical alignment from the top sheet origin ($y = 0.00\text{ pt}$), spine marks ($x = 907.09\text{ pt}$), and crop marks.
4. **Generate a Visual UV Registration Proof (`PODGLAD_PASOWANIA_LAKIERU_UV.pdf`)**:
   - Run `prepress_probe.py uv-overlay` to render the UV mask in high-contrast glowing magenta directly over the CMYK RIP sheet and save it in the `rip/` folder so the user can zoom in and inspect registration visually.
5. **Audit All Rasterized Body Pages Against Source**:
   - Run `prepress_probe.py diff-pdfs` comparing the 300 DPI `screen-RIP` body PDF against the approved source `srodek.pdf` to confirm no text shifted, no glyphs dropped during RIP font interpretation, and the latest file version was RIPped.

---

## 6. Editorial, Table of Contents (TOC) & Cross-Document Copy Consistency

- **Table of Contents (*Spis treści*) Audit**:
  - Compare every TOC line against the actual page heading and folio in the body:
    - Exact page number match (watch for $+1/-1$ shifts after adding/removing pages).
    - Word-for-word title match and consistent capitalization (e.g. `"Najważniejsze funkcje DINE"` vs `"Najważniejsze Funkcje DINE"`).
    - Consistent leader dots and separator dashes (`-` vs `–`).
- **Source Copy (`.docx` / `.md`) vs PDF Verification**:
  - When source text documents are available, compare sentence-by-sentence against the PDF text layer.
  - Watch for copy-paste leftovers from another variant/template (e.g. a headline from leaflet `v01` left inside leaflet `v04`).
- **Schedules, Tables & Data Integrity**:
  - In agendas, catalogs, and technical spec tables, check chronological time intervals, row/column completeness, unit consistency, and intentional vs accidental gaps.
