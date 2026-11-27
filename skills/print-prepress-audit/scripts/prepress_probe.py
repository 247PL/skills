#!/usr/bin/env python3
"""
Deterministic Prepress, Post-RIP & Spot-UV Audit Probe (print-prepress-audit v1.1)
Requires: pymupdf (fitz), Pillow, numpy

Subcommands:
  inspect       Inspect one or more PDFs (or an entire folder) for page boxes (mm/pt), visual pixel bleed,
                OutputIntents/PDF-X, AI private PieceInfo data, fonts/outlined text, image DPI/CMYK,
                vector RGB/K100 fills, safe-margin collisions, and batch consistency across a series.
  uv-align      Verify exact vector coordinate alignment (0.0000 pt) between a CMYK cover PDF and a spot UV mask PDF.
  diff-pdfs     Compare two PDFs page-by-page (supports --clip-trimbox for comparing files with/without crop marks).
  diff-split    Verify that a combined PDF (wszystko.pdf) matches split cover (okladka.pdf) + inside (srodek.pdf).
  match-pages   Deterministically match imposed RIP spread halves against source pages (identifies Side 1A vs 1B).
  uv-overlay    Generate a visual verification PDF overlaying a UV mask in glowing magenta onto a CMYK cover/RIP sheet.
"""

import argparse
import datetime
import glob
import io
import json
import os
import re
import sys

# Force UTF-8 stdout/stderr on Windows to prevent cp1250 crashes on ligatures (\ufb01, \ufb02)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # fallback for older PyMuPDF

from PIL import Image
import numpy as np

PT_TO_MM = 25.4 / 72.0


def check_visual_bleed(page, dpi=120):
    """Sample pixels 1.5mm outside vs 1.5mm inside TrimBox on all 4 edges to detect clipped/white bleeds."""
    trim = page.trimbox
    media = page.mediabox
    margin_l = (trim.x0 - media.x0) * PT_TO_MM
    margin_t = (trim.y0 - media.y0) * PT_TO_MM
    margin_r = (media.x1 - trim.x1) * PT_TO_MM
    margin_b = (media.y1 - trim.y1) * PT_TO_MM

    if min(margin_l, margin_t, margin_r, margin_b) < 1.5:
        return {
            "checked": False,
            "reason": "MediaBox has less than 1.5 mm area outside TrimBox",
            "empty_white_bleed_suspected": False,
        }

    s = dpi / 72.0
    pix = page.get_pixmap(dpi=dpi)
    arr = np.array(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    h, w = arr.shape[:2]

    tx0, ty0, tx1, ty1 = int(trim.x0 * s), int(trim.y0 * s), int(trim.x1 * s), int(trim.y1 * s)
    off = max(2, int(1.5 / PT_TO_MM * s))
    mid_x = max(20, min(w - 20, (tx0 + tx1) // 2))
    mid_y = max(20, min(h - 20, (ty0 + ty1) // 2))
    span = min(40, max(5, (tx1 - tx0) // 6))

    def mean_patch(y0, y1, x0, x1):
        y0, y1 = max(0, min(h - 1, y0)), max(1, min(h, y1))
        x0, x1 = max(0, min(w - 1, x0)), max(1, min(w, x1))
        if y1 <= y0 or x1 <= x0:
            return 255.0
        return round(float(arr[y0:y1, x0:x1].mean()), 1)

    outside = {
        "top": mean_patch(ty0 - off - 2, ty0 - off + 2, mid_x - span, mid_x + span),
        "bottom": mean_patch(ty1 + off - 2, ty1 + off + 2, mid_x - span, mid_x + span),
        "left": mean_patch(mid_y - span, mid_y + span, tx0 - off - 2, tx0 - off + 2),
        "right": mean_patch(mid_y - span, mid_y + span, tx1 + off - 2, tx1 + off + 2),
    }
    inside = {
        "top": mean_patch(ty0 + off, ty0 + off + 4, mid_x - span, mid_x + span),
        "bottom": mean_patch(ty1 - off - 4, ty1 - off, mid_x - span, mid_x + span),
        "left": mean_patch(mid_y - span, mid_y + span, tx0 + off, tx0 + off + 4),
        "right": mean_patch(mid_y - span, mid_y + span, tx1 - off - 4, tx1 - off),
    }

    clipped_edges = [
        side for side in ("top", "bottom", "left", "right")
        if inside[side] < 245.0 and outside[side] >= 252.0
    ]

    return {
        "checked": True,
        "outside_1_5mm_brightness": outside,
        "inside_1_5mm_brightness": inside,
        "clipped_edges": clipped_edges,
        "empty_white_bleed_suspected": len(clipped_edges) > 0,
    }


def inspect_single_pdf(pdf_path, safe_mm=3.5, min_dpi=250.0, visual_bleed=True):
    st = os.stat(pdf_path)
    mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    doc = fitz.open(pdf_path)
    safe_pt = safe_mm / PT_TO_MM

    cat_str = doc.xref_object(doc.pdf_catalog())
    has_output_intent = "/OutputIntents" in cat_str
    has_ai_private = ("/PieceInfo" in cat_str) or ("/Illustrator" in cat_str)

    report = {
        "file": os.path.abspath(pdf_path),
        "filename": os.path.basename(pdf_path),
        "size_bytes": st.st_size,
        "mtime": mtime,
        "pdf_version": doc.metadata.get("format", ""),
        "creator": doc.metadata.get("creator", ""),
        "has_output_intent": has_output_intent,
        "has_ai_private_data": has_ai_private,
        "page_count": len(doc),
        "divisible_by_4": (len(doc) % 4 == 0),
        "pages": [],
    }

    for i, page in enumerate(doc):
        if not report["has_ai_private_data"]:
            pg_str = doc.xref_object(page.xref)
            if "/PieceInfo" in pg_str or "/Illustrator" in pg_str:
                report["has_ai_private_data"] = True

        media = page.mediabox
        trim = page.trimbox
        bleed = page.bleedbox

        bleeds_mm = {
            "left": round((trim.x0 - bleed.x0) * PT_TO_MM, 2),
            "top": round((trim.y0 - bleed.y0) * PT_TO_MM, 2),
            "right": round((bleed.x1 - trim.x1) * PT_TO_MM, 2),
            "bottom": round((bleed.y1 - trim.y1) * PT_TO_MM, 2),
        }

        fonts = []
        for f in page.get_fonts():
            fonts.append(
                {
                    "xref": f[0],
                    "ext": f[1],
                    "type": f[2],
                    "basefont": f[3],
                    "embedded": (f[1] != "n/a"),
                }
            )

        images = []
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            w_px, h_px = img_info[2], img_info[3]
            cs_name = img_info[5]
            rects = page.get_image_rects(xref)
            for r in rects:
                if r.width > 0 and r.height > 0:
                    dpi_x = round(w_px / (r.width / 72.0), 1)
                    dpi_y = round(h_px / (r.height / 72.0), 1)
                else:
                    dpi_x, dpi_y = 0, 0
                images.append(
                    {
                        "xref": xref,
                        "width_px": w_px,
                        "height_px": h_px,
                        "colorspace": cs_name,
                        "dpi_x": dpi_x,
                        "dpi_y": dpi_y,
                        "low_dpi": min(dpi_x, dpi_y) < min_dpi,
                        "non_cmyk": cs_name not in ("DeviceCMYK", "Separation", "DeviceN", "Indexed"),
                    }
                )

        stream = page.read_contents().decode("latin1", errors="ignore")
        cmyk_fills = sorted(set(re.findall(r"([0-9.]+ [0-9.]+ [0-9.]+ [0-9.]+) k", stream)))
        rgb_fills = sorted(set(re.findall(r"([0-9.]+ [0-9.]+ [0-9.]+) rg", stream)))
        has_k100 = ("0 0 0 1" in cmyk_fills) or ("0 0 0 1 K" in stream)

        full_text = page.get_text().strip()
        drawings_count = len(page.get_drawings())
        text_outlined = (len(fonts) == 0) and (len(full_text) == 0) and (drawings_count > 10)

        safe_rect = fitz.Rect(
            trim.x0 + safe_pt,
            trim.y0 + safe_pt,
            trim.x1 - safe_pt,
            trim.y1 - safe_pt,
        )
        margin_warnings = []
        for b in page.get_text("blocks"):
            if b[6] != 0:
                continue
            r = fitz.Rect(b[:4])
            txt = b[4].strip().replace("\n", " ")
            if not txt or not r.intersects(trim):
                continue
            if (
                r.x0 < safe_rect.x0
                or r.y0 < safe_rect.y0
                or r.x1 > safe_rect.x1
                or r.y1 > safe_rect.y1
            ):
                dists_mm = {
                    "left_mm": round((r.x0 - trim.x0) * PT_TO_MM, 2),
                    "top_mm": round((r.y0 - trim.y0) * PT_TO_MM, 2),
                    "right_mm": round((trim.x1 - r.x1) * PT_TO_MM, 2),
                    "bottom_mm": round((trim.y1 - r.y1) * PT_TO_MM, 2),
                }
                margin_warnings.append(
                    {
                        "text_preview": txt[:80],
                        "distances_to_trim_mm": dists_mm,
                    }
                )

        page_entry = {
            "page": i + 1,
            "trim_size_mm": [
                round(trim.width * PT_TO_MM, 2),
                round(trim.height * PT_TO_MM, 2),
            ],
            "bleed_size_mm": [
                round(bleed.width * PT_TO_MM, 2),
                round(bleed.height * PT_TO_MM, 2),
            ],
            "media_size_mm": [
                round(media.width * PT_TO_MM, 2),
                round(media.height * PT_TO_MM, 2),
            ],
            "bleeds_mm": bleeds_mm,
            "fonts_count": len(fonts),
            "unembedded_fonts": [f["basefont"] for f in fonts if not f["embedded"]],
            "text_length": len(full_text),
            "text_outlined": text_outlined,
            "images_count": len(images),
            "low_dpi_images": [img for img in images if img["low_dpi"]],
            "non_cmyk_images": [img for img in images if img["non_cmyk"]],
            "drawings_count": drawings_count,
            "has_k100": has_k100,
            "vector_rgb_fills_count": len(rgb_fills),
            "margin_warnings": margin_warnings,
        }

        if visual_bleed:
            page_entry["visual_bleed_check"] = check_visual_bleed(page)

        report["pages"].append(page_entry)

    return report


def cmd_inspect(args):
    pdf_paths = []
    for target in args.targets:
        if os.path.isdir(target):
            pdf_paths.extend(sorted(glob.glob(os.path.join(target, "*.pdf"))))
        elif os.path.isfile(target):
            pdf_paths.append(target)
        else:
            pdf_paths.extend(sorted(glob.glob(target)))

    if not pdf_paths:
        print(json.dumps({"error": "No PDF files found for given target(s)."}, ensure_ascii=False))
        sys.exit(1)

    if len(pdf_paths) == 1:
        rep = inspect_single_pdf(
            pdf_paths[0],
            safe_mm=args.safe_mm,
            min_dpi=args.min_dpi,
            visual_bleed=not args.no_visual_bleed,
        )
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return

    reports = [
        inspect_single_pdf(
            p,
            safe_mm=args.safe_mm,
            min_dpi=args.min_dpi,
            visual_bleed=not args.no_visual_bleed,
        )
        for p in pdf_paths
    ]

    # Compute batch consistency checks across the series
    pdf_versions = sorted(set(r["pdf_version"] for r in reports))
    trim_sizes = sorted(set(tuple(r["pages"][0]["trim_size_mm"]) for r in reports if r["pages"]))
    bleed_sizes = sorted(set(tuple(r["pages"][0]["bleed_size_mm"]) for r in reports if r["pages"]))
    outlined_states = sorted(set(r["pages"][0]["text_outlined"] for r in reports if r["pages"]))
    clipped_bleed_files = [
        r["filename"]
        for r in reports
        if any(pg.get("visual_bleed_check", {}).get("empty_white_bleed_suspected") for pg in r["pages"])
    ]
    low_dpi_files = [
        r["filename"]
        for r in reports
        if any(len(pg["low_dpi_images"]) > 0 for pg in r["pages"])
    ]
    non_cmyk_files = [
        r["filename"]
        for r in reports
        if any(len(pg["non_cmyk_images"]) > 0 or pg["vector_rgb_fills_count"] > 0 for pg in r["pages"])
    ]
    ai_priv_files = [r["filename"] for r in reports if r["has_ai_private_data"]]

    batch_report = {
        "batch_count": len(reports),
        "batch_consistency": {
            "pdf_versions_found": pdf_versions,
            "pdf_version_consistent": len(pdf_versions) == 1,
            "trim_sizes_mm_found": [list(t) for t in trim_sizes],
            "trim_size_consistent": len(trim_sizes) == 1,
            "bleed_sizes_mm_found": [list(b) for b in bleed_sizes],
            "bleed_size_consistent": len(bleed_sizes) == 1,
            "text_outlined_states": outlined_states,
            "files_with_suspected_white_clipped_bleed": clipped_bleed_files,
            "files_with_low_dpi_images": low_dpi_files,
            "files_with_non_cmyk_or_rgb": non_cmyk_files,
            "files_with_ai_private_editing_data": ai_priv_files,
        },
        "files": reports,
    }
    print(json.dumps(batch_report, ensure_ascii=False, indent=2))


def cmd_uv_align(args):
    doc_cmyk = fitz.open(args.cmyk)
    doc_uv = fitz.open(args.uv)

    result = {
        "cmyk_file": os.path.abspath(args.cmyk),
        "uv_file": os.path.abspath(args.uv),
        "cmyk_pages": len(doc_cmyk),
        "uv_pages": len(doc_uv),
        "pages": [],
    }

    for i in range(min(len(doc_cmyk), len(doc_uv))):
        p_c = doc_cmyk[i]
        p_u = doc_uv[i]

        boxes_match = (
            p_c.trimbox == p_u.trimbox
            and p_c.bleedbox == p_u.bleedbox
            and p_c.mediabox == p_u.mediabox
        )

        c_rects = [d["rect"] for d in p_c.get_drawings() if d["rect"].width > 0.5 and d["rect"].height > 0.5]
        u_drawings = [d for d in p_u.get_drawings() if d["rect"].width > 0.5 and d["rect"].height > 0.5]

        # Separate filled UV varnish elements inside TrimBox from registration marks in slug
        trim = p_u.trimbox
        uv_items = []
        for idx, d in enumerate(u_drawings):
            r = d["rect"]
            in_trim = (d.get("fill") is not None) and trim.contains(r)
            min_diff = None
            for cr in c_rects:
                diff = max(
                    abs(r.x0 - cr.x0),
                    abs(r.y0 - cr.y0),
                    abs(r.x1 - cr.x1),
                    abs(r.y1 - cr.y1),
                )
                if min_diff is None or diff < min_diff:
                    min_diff = diff

            uv_items.append(
                {
                    "uv_index": idx,
                    "in_trim_area": in_trim,
                    "rect_pt": [round(r.x0, 4), round(r.y0, 4), round(r.x1, 4), round(r.y1, 4)],
                    "fill": d.get("fill"),
                    "closest_cmyk_vector_diff_pt": round(min_diff, 4) if min_diff is not None else None,
                }
            )

        result["pages"].append(
            {
                "page": i + 1,
                "boxes_match_exactly": boxes_match,
                "cmyk_mediabox_mm": [round(p_c.mediabox.width * PT_TO_MM, 2), round(p_c.mediabox.height * PT_TO_MM, 2)],
                "uv_mediabox_mm": [round(p_u.mediabox.width * PT_TO_MM, 2), round(p_u.mediabox.height * PT_TO_MM, 2)],
                "uv_elements_in_trim": sum(1 for item in uv_items if item["in_trim_area"]),
                "uv_items": uv_items,
            }
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))


def compare_two_pages(p_a, p_b, dpi=100, clip_trimbox=False):
    pix_a = p_a.get_pixmap(dpi=dpi, clip=p_a.trimbox if clip_trimbox else None)
    pix_b = p_b.get_pixmap(dpi=dpi, clip=p_b.trimbox if clip_trimbox else None)
    im_a = Image.frombytes("RGB", [pix_a.width, pix_a.height], pix_a.samples)
    im_b = Image.frombytes("RGB", [pix_b.width, pix_b.height], pix_b.samples)
    size_mismatch = (im_a.size != im_b.size)
    if size_mismatch:
        im_b = im_b.resize(im_a.size)
    arr_a = np.array(im_a, dtype=int)
    arr_b = np.array(im_b, dtype=int)
    diff = np.abs(arr_a - arr_b)
    return {
        "size_mismatch": size_mismatch,
        "mean_diff": round(float(diff.mean()), 2),
        "max_diff": int(diff.max()),
        "pct_pixels_over_50": round(float((diff > 50).any(axis=2).mean() * 100.0), 3),
    }


def cmd_diff_pdfs(args):
    doc_a = fitz.open(args.pdf_a)
    doc_b = fitz.open(args.pdf_b)
    res = {
        "pdf_a": os.path.abspath(args.pdf_a),
        "pdf_b": os.path.abspath(args.pdf_b),
        "clip_trimbox": args.clip_trimbox,
        "pages_a": len(doc_a),
        "pages_b": len(doc_b),
        "comparisons": [],
    }
    for i in range(min(len(doc_a), len(doc_b))):
        stats = compare_two_pages(doc_a[i], doc_b[i], dpi=args.dpi, clip_trimbox=args.clip_trimbox)
        stats["page"] = i + 1
        res["comparisons"].append(stats)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_diff_split(args):
    doc_cov = fitz.open(args.cover)
    doc_in = fitz.open(args.inside)
    doc_all = fitz.open(args.combined)

    expected_total = len(doc_cov) + len(doc_in)
    res = {
        "cover_pages": len(doc_cov),
        "inside_pages": len(doc_in),
        "combined_pages": len(doc_all),
        "page_count_matches": (len(doc_all) == expected_total),
        "mismatches": [],
    }

    if len(doc_cov) == 4 and len(doc_all) == expected_total:
        mapping = (
            [(0, "cover", 0), (1, "cover", 1)]
            + [(i + 2, "inside", i) for i in range(len(doc_in))]
            + [(len(doc_all) - 2, "cover", 2), (len(doc_all) - 1, "cover", 3)]
        )
        for all_idx, src_type, src_idx in mapping:
            p_all = doc_all[all_idx]
            p_src = doc_cov[src_idx] if src_type == "cover" else doc_in[src_idx]
            stats = compare_two_pages(p_all, p_src, dpi=100, clip_trimbox=args.clip_trimbox)
            if stats["mean_diff"] > 1.0 or stats["pct_pixels_over_50"] > 0.1:
                res["mismatches"].append(
                    {
                        "combined_page": all_idx + 1,
                        "source": f"{src_type} page {src_idx + 1}",
                        "stats": stats,
                    }
                )

    print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_match_pages(args):
    """Deterministically match left/right halves of imposed RIP sheets against source cover pages."""
    doc_rip = fitz.open(args.rip_cover)
    doc_src = fitz.open(args.source_cover)

    src_thumbs = {}
    for i, p in enumerate(doc_src):
        pix = p.get_pixmap(dpi=72)
        im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).resize((200, 140))
        src_thumbs[f"Source Cover Page {i + 1}"] = np.array(im, dtype=int)

    matches = []
    for r_idx, r_page in enumerate(doc_rip):
        pix = r_page.get_pixmap(dpi=72)
        im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        w, h = im.size
        y_end = h // 2 if args.two_up else h
        halves = {
            "Left Half": im.crop((int(w * 0.04), int(y_end * 0.08), int(w * 0.48), int(y_end * 0.92))),
            "Right Half": im.crop((int(w * 0.52), int(y_end * 0.08), int(w * 0.96), int(y_end * 0.92))),
        }
        page_report = {"rip_page": r_idx + 1, "halves": {}}
        for h_name, h_im in halves.items():
            h_arr = np.array(h_im.resize((200, 140)), dtype=int)
            best_name = None
            best_err = 999999.0
            for s_name, s_arr in src_thumbs.items():
                err = float(np.abs(h_arr - s_arr).mean())
                if err < best_err:
                    best_err = err
                    best_name = s_name
            page_report["halves"][h_name] = {
                "best_match": best_name,
                "mean_rgb_diff": round(best_err, 2),
            }
        matches.append(page_report)

    print(json.dumps(matches, ensure_ascii=False, indent=2))


def cmd_uv_overlay(args):
    """Render UV mask in glowing magenta over the CMYK page (aligned at top origin y=0)."""
    doc_cmyk = fitz.open(args.cmyk)
    doc_uv = fitz.open(args.uv)
    out_pdf = fitz.open()

    pages_to_render = min(len(doc_cmyk), len(doc_uv)) if args.all_pages else 1
    for i in range(pages_to_render):
        pix_c = doc_cmyk[i].get_pixmap(dpi=args.dpi)
        pix_u = doc_uv[i].get_pixmap(dpi=args.dpi)

        im_c = Image.frombytes("RGB", [pix_c.width, pix_c.height], pix_c.samples)
        im_u = Image.frombytes("RGB", [pix_u.width, pix_u.height], pix_u.samples)

        arr_c = np.array(im_c)
        arr_u = np.array(im_u)

        uv_mask = (arr_u < 120).any(axis=2)

        overlay = arr_c.copy()
        h_min = min(arr_c.shape[0], uv_mask.shape[0])
        w_min = min(arr_c.shape[1], uv_mask.shape[1])

        mask_pad = np.zeros((arr_c.shape[0], arr_c.shape[1]), dtype=bool)
        mask_pad[:h_min, :w_min] = uv_mask[:h_min, :w_min]

        overlay[mask_pad, 0] = np.clip(overlay[mask_pad, 0].astype(int) + 160, 0, 255)
        overlay[mask_pad, 1] = np.clip(overlay[mask_pad, 1].astype(int) // 3, 0, 255)
        overlay[mask_pad, 2] = np.clip(overlay[mask_pad, 2].astype(int) + 160, 0, 255)

        out_page = out_pdf.new_page(
            width=doc_cmyk[i].rect.width,
            height=doc_cmyk[i].rect.height,
        )
        buf = io.BytesIO()
        Image.fromarray(overlay).save(buf, format="JPEG", quality=92)
        out_page.insert_image(out_page.rect, stream=buf.getvalue())

    out_pdf.save(args.output)
    print(f"Saved visual UV registration proof to: {os.path.abspath(args.output)}")


def main():
    parser = argparse.ArgumentParser(description="Deterministic Print & Prepress DTP Probe (v1.1)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ins = sub.add_parser("inspect", help="Inspect one or more PDFs (or a folder) for prepress health & batch consistency")
    p_ins.add_argument("targets", nargs="+", help="PDF file path(s), glob pattern, or directory containing PDFs")
    p_ins.add_argument("--safe-mm", type=float, default=3.5, help="Safe margin inside TrimBox in mm (default: 3.5)")
    p_ins.add_argument("--min-dpi", type=float, default=250.0, help="Minimum effective image DPI threshold (default: 250)")
    p_ins.add_argument("--no-visual-bleed", action="store_true", help="Skip raster pixel sampling outside TrimBox")
    p_ins.set_defaults(func=cmd_inspect)

    p_uv = sub.add_parser("uv-align", help="Compare vector coordinates between CMYK PDF and UV mask PDF")
    p_uv.add_argument("cmyk", help="Path to CMYK cover/artwork PDF")
    p_uv.add_argument("uv", help="Path to UV spot mask PDF")
    p_uv.set_defaults(func=cmd_uv_align)

    p_diff = sub.add_parser("diff-pdfs", help="Compare two PDFs page-by-page (e.g. source vs RIP proof)")
    p_diff.add_argument("pdf_a", help="First PDF file")
    p_diff.add_argument("pdf_b", help="Second PDF file")
    p_diff.add_argument("--dpi", type=int, default=100, help="Comparison render DPI (default: 100)")
    p_diff.add_argument("--clip-trimbox", action="store_true", help="Clip both pages to TrimBox before comparing (ignores crop marks/slugs)")
    p_diff.set_defaults(func=cmd_diff_pdfs)

    p_split = sub.add_parser("diff-split", help="Verify combined wszystko.pdf matches cover + inside PDFs")
    p_split.add_argument("cover", help="Cover PDF (4 pages)")
    p_split.add_argument("inside", help="Inside body PDF (N pages)")
    p_split.add_argument("combined", help="Combined PDF (N+4 pages)")
    p_split.add_argument("--clip-trimbox", action="store_true", help="Clip pages to TrimBox before comparing")
    p_split.set_defaults(func=cmd_diff_split)

    p_match = sub.add_parser("match-pages", help="Match imposed RIP spread halves against source cover pages")
    p_match.add_argument("rip_cover", help="Imposed RIP cover PDF")
    p_match.add_argument("source_cover", help="4-page source cover PDF")
    p_match.add_argument("--two-up", action="store_true", default=True, help="2-up vertical imposition on sheet")
    p_match.set_defaults(func=cmd_match_pages)

    p_ov = sub.add_parser("uv-overlay", help="Generate visual PDF with UV mask in glowing magenta over CMYK")
    p_ov.add_argument("cmyk", help="CMYK cover or RIP sheet PDF")
    p_ov.add_argument("uv", help="UV mask PDF")
    p_ov.add_argument("output", help="Output overlay PDF path")
    p_ov.add_argument("--dpi", type=int, default=150, help="Render DPI (default: 150)")
    p_ov.add_argument("--all-pages", action="store_true", help="Overlay all pages instead of Page 1 only")
    p_ov.set_defaults(func=cmd_uv_overlay)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
