"""Check the physical Atlas chapter composition against the immutable PDF.

This is deliberately a structural check. It never approves scientific content,
the work of the right margin, source interpretation or a chapter for publication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError as exc:
    raise SystemExit("PyMuPDF is required: python3 -m pip install PyMuPDF") from exc


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROFILE = json.loads((HERE / "reference_profile.json").read_text(encoding="utf-8"))
REFERENCE = ROOT / PROFILE["reference_path_from_repo"]
TOLERANCE = 1.5


def near(actual: float, expected: float, tolerance: float = TOLERANCE) -> bool:
    return abs(actual - expected) <= tolerance


def drawings(page):
    return [item["rect"] for item in page.get_drawings()]


def horizontal(rects, x0, x1, y):
    return any(
        near(r.x0, x0) and near(r.x1, x1) and near(r.y0, y) and near(r.y1, y)
        for r in rects
    )


def vertical(rects, x, minimum_length):
    return any(near(r.x0, x) and near(r.x1, x) and r.height >= minimum_length
               for r in rects)


def spans(page):
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            yield from line["spans"]


def font_chars(items, name, size, zone=None):
    return sum(
        len(s["text"]) for s in items
        if s["font"] == name and near(s["size"], size, 0.35)
        and (zone is None or zone(s["bbox"]))
    )


def check_pdf(path: Path, units: int) -> dict:
    g = PROFILE["article_geometry_pt"]
    b = PROFILE["bibliography_geometry_pt"]
    issues = []

    def issue(code, page, detail):
        issues.append({"code": code, "page": page, "detail": detail})

    doc = fitz.open(path)
    expected_pages = units * 3
    if len(doc) != expected_pages:
        issue("page_count", None, f"Expected {expected_pages} pages, found {len(doc)}")

    for index, page in enumerate(doc):
        number = index + 1
        role = index % 3
        rects = drawings(page)
        items = list(spans(page))
        text = page.get_text()
        width, height = PROFILE["page_size_pt"]
        if not near(page.rect.width, width, 0.5) or not near(page.rect.height, height, 0.5):
            issue("page_size", number, "Page is not the reference A4 size")
        if any(780 < s["bbox"][1] < 800 and s["text"].strip() for s in items):
            issue("body_footer_overlap", number, "Text intrudes into the footer reserve")
        footer_numbers = [
            s for s in items
            if s["text"].strip() == str(number) and s["bbox"][1] > 790
        ]
        expected_x = 294 if role == 2 else 541
        if not any(abs(s["bbox"][0] - expected_x) < 8 for s in footer_numbers):
            issue("page_number", number, "Page number is not in the reference position")

        if role != 2:
            if "БИБЛИОГРАФИЯ" in text:
                issue("wrong_page_role", number, "Bibliography appears on an article page")
            if not vertical(rects, g["left_rule_x"], 700):
                issue("left_rule", number, "Missing full-height thin left rule")
            if not horizontal(rects, g["main_text_x"], g["content_right_x"], g["top_rule_y"]):
                issue("header_rule", number, "Header rule differs from reference")
            if not horizontal(rects, g["main_text_x"], g["content_right_x"], g["bottom_rule_y"]):
                issue("footer_rule", number, "Footer rule differs from reference")
            if not vertical(rects, g["sidebar_rule_x"], 180):
                issue("column_rule", number, "Missing divider at x≈404.2 pt")
            main = lambda box: box[0] < 400 and box[1] < 780
            side = lambda box: 410 < box[0] < 550 and box[1] < 780
            if font_chars(items, "SourceSerif4-Regular", 10.5, main) < 350:
                issue("article_body_font", number, "Main serif text missing or wrong size")
            if font_chars(items, "NimbusSans-Regular", 9.0, side) < 90:
                issue("sidebar_font", number, "Right sans-serif explanation missing or wrong size")
            if not any(link.get("uri") for link in page.get_links()):
                issue("article_citation_links", number, "No clickable external source in the article")
            large_titles = [s for s in items
                            if s["bbox"][0] < 400 and s["size"] >= 18 and s["bbox"][1] < 160]
            if role == 0:
                if not large_titles:
                    issue("first_page_title", number, "First article page lacks a large title")
                if font_chars(items, "SourceSerif4-Regular", 11.5, main) < 70:
                    issue("lead", number, "Topic lead is absent or has the wrong style")
            elif large_titles:
                issue("repeated_large_title", number, "Second article page repeats a large title")
        else:
            if "БИБЛИОГРАФИЯ" not in text:
                issue("bibliography_title", number, "No full-width bibliography page")
            if vertical(rects, g["left_rule_x"], 700) or vertical(rects, g["sidebar_rule_x"], 180):
                issue("bibliography_columns", number, "Article rules intrude into bibliography")
            if not horizontal(rects, b["rule_x0"], b["rule_x1"], b["rule_y"]):
                issue("bibliography_rule", number, "Centered title rule differs from reference")
            if not any("БИБЛИОГРАФИЯ" in s["text"] and near(s["size"], 14, 0.7)
                       for s in items):
                issue("bibliography_heading_style", number, "Heading style differs")
            records = [int(n) for n in re.findall(r"(?m)^\s*(\d+)\.\s+", text)]
            if len(records) < 2 or records != list(range(1, len(records) + 1)):
                issue("local_numbering", number, f"Local source numbers are {records}")
            if text.count("Что читать.") != len(records):
                issue("reading_instructions", number, "Each source needs a specific reading pointer")
            if text.count("Порядок чтения.") != 1:
                issue("reading_route", number, "A single reading route is required at the end")
            if "ВВОДНЫЕ РАБОТЫ" not in text:
                issue("introductory_group", number, "Introductory group is absent")
            if font_chars(items, "SourceSerif4-It", 10.5) < 20:
                issue("italic_titles", number, "Linked original titles should be italic")
            unique_urls = {link["uri"] for link in page.get_links() if link.get("uri")}
            if len(unique_urls) < len(records):
                issue("source_links", number, "Fewer distinct source URLs than local entries")

    if len(doc):
        targets = [link.get("page") for link in doc[0].get_links()
                   if link.get("page") is not None]
        expected_targets = [3 * i for i in range(1, units)]
        if targets != expected_targets:
            issue("intro_navigation", 1,
                  f"Expected links to page indices {expected_targets}, found {targets}")
    return {
        "file": str(path),
        "pages": len(doc),
        "units_expected": units,
        "structural_result": "pass" if not issues else "fail",
        "issues": issues,
        "editorial_result": "not_determined_by_structural_check",
        "user_approval": "not_determined_by_structural_check",
        "accepted": None
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--units", type=int, default=PROFILE["units"])
    parser.add_argument("--reference", action="store_true",
                        help="Verify that the input is the immutable approved source")
    parser.add_argument("--report", type=Path, help="Write the structural result as JSON")
    args = parser.parse_args()
    if args.units < 1:
        parser.error("--units must be positive")
    if not args.pdf.is_file():
        parser.error(f"File not found: {args.pdf}")
    if not REFERENCE.is_file():
        parser.error(f"Canonical reference missing: {REFERENCE}")
    sha = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    if sha != PROFILE["reference_sha256"]:
        raise SystemExit("Canonical reference has changed: stop and restore the approved PDF")
    if args.reference:
        input_sha = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
        if input_sha != sha:
            raise SystemExit("Input differs from the approved reference SHA-256")
    result = check_pdf(args.pdf, args.units)
    if args.reference:
        result["reference_verified"] = True
        result["editorial_result"] = "reference_document_only"
        result["user_approval"] = "original_reference_approved"
        result["accepted"] = not result["issues"]
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(f"СТРУКТУРА: {result['structural_result'].upper()} "
          f"({len(result['issues'])} замечаний; {result['pages']} страниц).")
    for item in result["issues"]:
        location = f"с. {item['page']}" if item["page"] is not None else "документ"
        print(f"  {location}: {item['code']}: {item['detail']}")
    if args.reference:
        print("ИСХОДНЫЙ ЭТАЛОН: SHA-256 подтверждён.")
    else:
        print("ЭТО ТОЛЬКО СТРУКТУРНАЯ ПРОВЕРКА. Редакторский и пользовательский "
              "вердикты определяются отдельно; код 2 не означает отклонение.")
    if result["issues"]:
        return 1
    return 0 if args.reference else 2


if __name__ == "__main__":
    sys.exit(main())
