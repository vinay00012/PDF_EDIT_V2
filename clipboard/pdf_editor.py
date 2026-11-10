"""
PDF Text Editor - Direct In-Place Text Replacement Engine
Preserves font family, font size, baseline alignment, and text color.
"""

import os
import re
import sys
import argparse
from typing import Optional, Tuple, Dict, Any, List
import pymupdf


def normalize_font_name(font_name: str) -> str:
    """Removes PDF subset prefixes (e.g., 'AAOCRQ+Roboto-Regular' -> 'Roboto-Regular')."""
    return re.sub(r"^[A-Z]{6}\+", "", font_name)


def resolve_font_file(font_name: str, flags: int = 0) -> Optional[str]:
    """
    Finds matching TTF/OTF font file:
    1. Checks local ./fonts folder for bundled fonts (Roboto-Black, Roboto-Bold, Roboto-Medium, Roboto-Regular, Roboto-Light).
    2. Checks Windows system fonts (C:\\Windows\\Fonts).
    3. Falls back to bundled TrueType font with matching weight so Linux/Vercel embeds real glyphs.
    Accurately detects black, bold, medium, light, and italic weights.
    """
    clean = normalize_font_name(font_name).lower()
    
    # Weight & style detection
    is_black = any(k in clean for k in ["black", "heavy", "ultrabold", "extra-bold", "extrabold", "900", "800"])
    is_bold = bool(flags & 16 or any(k in clean for k in ["bold", "700"]))
    is_medium = any(k in clean for k in ["medium", "semibold", "semi-bold", "demi", "600", "500"])
    is_light = any(k in clean for k in ["light", "thin", "hairline", "300", "200", "100"])
    is_italic = bool(flags & 2 or any(k in clean for k in ["italic", "oblique"]))

    # 1. Search local ./fonts folder
    local_fonts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts"))
    if os.path.isdir(local_fonts_dir):
        # Specific weight matching for bundled Roboto fonts
        if is_black and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Black.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Black.ttf")
        if (is_bold or (flags & 16)) and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Bold.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Bold.ttf")
        if is_medium and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Medium.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Medium.ttf")
        if is_light and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Light.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Light.ttf")
        if any(k in clean for k in ["roboto", "sans", "helvetica", "arial"]) and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Regular.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Regular.ttf")

        # Generic name search in fonts folder
        for fname in os.listdir(local_fonts_dir):
            if fname.lower().endswith((".ttf", ".otf")):
                name_part = os.path.splitext(fname)[0].lower()
                if name_part in clean or clean in name_part:
                    return os.path.join(local_fonts_dir, fname)

    # 2. Search Windows system fonts
    fonts_dir = os.environ.get("WINDIR", r"C:\Windows") + r"\Fonts"
    if os.path.isdir(fonts_dir):
        font_family_map = {
            "arial": ("arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"),
            "calibri": ("calibri.ttf", "calibrib.ttf", "calibrii.ttf", "calibriz.ttf"),
            "times": ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"),
            "timesnewroman": ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"),
            "segoe": ("segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf", "segoeuez.ttf"),
            "segoeui": ("segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf", "segoeuez.ttf"),
            "verdana": ("verdana.ttf", "verdanab.ttf", "verdanai.ttf", "verdanaz.ttf"),
            "georgia": ("georgia.ttf", "georgiab.ttf", "georgiai.ttf", "georgiaz.ttf"),
            "tahoma": ("tahoma.ttf", "tahomabd.ttf", "tahoma.ttf", "tahomabd.ttf"),
            "consolas": ("consola.ttf", "consolab.ttf", "consolai.ttf", "consolaz.ttf"),
            "courier": ("cour.ttf", "courbd.ttf", "couri.ttf", "courbi.ttf"),
            "trebuchet": ("trebuc.ttf", "trebucbd.ttf", "trebucit.ttf", "trebucbi.ttf"),
            "cambria": ("cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf"),
        }

        for key, variants in font_family_map.items():
            if key in clean:
                idx = 0
                if (is_bold or is_black) and is_italic:
                    idx = 3
                elif is_bold or is_black or is_medium:
                    idx = 1
                elif is_italic:
                    idx = 2
                candidate = os.path.join(fonts_dir, variants[idx])
                if os.path.isfile(candidate):
                    return candidate
                candidate_reg = os.path.join(fonts_dir, variants[0])
                if os.path.isfile(candidate_reg):
                    return candidate_reg

    # 3. Universal Fallback: Use bundled Roboto matching the weight for Linux/Vercel embedding
    if os.path.isdir(local_fonts_dir):
        if is_black and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Black.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Black.ttf")
        if (is_bold or (flags & 16)) and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Bold.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Bold.ttf")
        if is_medium and os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Medium.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Medium.ttf")
        if os.path.isfile(os.path.join(local_fonts_dir, "Roboto-Regular.ttf")):
            return os.path.join(local_fonts_dir, "Roboto-Regular.ttf")

    return None


def int_to_rgb(color_int: int) -> Tuple[float, float, float]:
    """Converts PyMuPDF integer color to RGB float tuple (0.0 - 1.0)."""
    r = ((color_int >> 16) & 255) / 255.0
    g = ((color_int >> 8) & 255) / 255.0
    b = (color_int & 255) / 255.0
    return (r, g, b)


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """Converts RGB floats to hex string #RRGGBB."""
    return f"#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}"


def get_base14_fallback(font_name: str, flags: int = 0) -> str:
    """Returns the closest Base-14 PDF standard font identifier."""
    clean = normalize_font_name(font_name).lower()
    is_bold = bool(flags & 16 or any(k in clean for k in ["bold", "black", "heavy", "medium"]))
    is_italic = bool(flags & 2 or any(k in clean for k in ["italic", "oblique"]))

    if any(k in clean for k in ["times", "serif", "roman", "georgia", "cambria"]):
        if is_bold and is_italic:
            return "tibi"
        if is_bold:
            return "tibo"
        if is_italic:
            return "tiit"
        return "tiro"

    if any(k in clean for k in ["courier", "mono", "consolas", "code"]):
        if is_bold and is_italic:
            return "cobi"
        if is_bold:
            return "cobo"
        if is_italic:
            return "coit"
        return "cour"

    # Default Sans-Serif (Helvetica / Arial / Roboto)
    if is_bold and is_italic:
        return "hebi"
    if is_bold:
        return "hebo"
    if is_italic:
        return "heit"
    return "helv"


def register_page_font(page: pymupdf.Page, font_name: str, flags: int, font_cache: dict) -> Tuple[str, Optional[str]]:
    """
    Registers the font on the page with a weight-specific alias.
    Ensures font is present in the page dictionary even after redaction resets it.
    """
    font_file = resolve_font_file(font_name, flags)

    if font_file and os.path.isfile(font_file):
        base = re.sub(r"[^a-zA-Z0-9]", "", os.path.splitext(os.path.basename(font_file))[0])
        alias = f"f_{base}"
        
        try:
            page.insert_font(fontname=alias, fontfile=font_file)
            return alias, font_file
        except Exception:
            try:
                unique_alias = f"f_{base}_{len(page.get_fonts()) + 1}"
                page.insert_font(fontname=unique_alias, fontfile=font_file)
                return unique_alias, font_file
            except Exception:
                pass

    fallback_alias = get_base14_fallback(font_name, flags)
    return fallback_alias, None


def replace_exact_span(
    page: pymupdf.Page,
    bbox: Tuple[float, float, float, float],
    origin: Tuple[float, float],
    font_name: str,
    font_size: float,
    color_val: Any,
    flags: int,
    new_text: str,
    auto_shrink: bool = False,
    bg_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    font_cache: Optional[dict] = None,
    orig_width: Optional[float] = None,
) -> bool:
    """
    Directly replaces an exact text span at its bounding box and baseline coordinates.
    Preserves exact font, size, and color.
    Supports reference orig_width to prevent sticky shrinking on multiple edits.
    """
    if font_cache is None:
        font_cache = {}

    target_rect = pymupdf.Rect(bbox)
    
    # 1. Resolve color
    if isinstance(color_val, int):
        color_rgb = int_to_rgb(color_val)
    elif isinstance(color_val, (list, tuple)) and len(color_val) == 3:
        color_rgb = tuple(color_val)
    else:
        color_rgb = (0.0, 0.0, 0.0)

    # 2. Compute final font size (auto-shrink if enabled and text overflows reference width)
    final_size = font_size
    reference_width = orig_width if (orig_width and orig_width > 0) else target_rect.width

    if auto_shrink:
        try:
            font_file = resolve_font_file(font_name, flags)
            if font_file and os.path.isfile(font_file):
                f_obj = pymupdf.Font(fontfile=font_file)
            else:
                f_obj = pymupdf.Font(get_base14_fallback(font_name, flags))

            new_width = f_obj.text_length(new_text, fontsize=font_size)
            if new_width > reference_width and reference_width > 0:
                scale = reference_width / new_width
                final_size = round(font_size * scale, 2)
            else:
                # Text fits inside reference boundary - restore to full target font_size!
                final_size = font_size
        except Exception:
            final_size = font_size

    # 3. Cleanly redact the old text FIRST (this resets the page resource dictionary)
    page.add_redact_annot(target_rect, fill=bg_color)
    page.apply_redactions()

    # 4. Register the font on the page AFTER redaction with unique weight-specific alias
    registered_name, font_file = register_page_font(page, font_name, flags, font_cache)

    # 5. Insert new text at the exact baseline origin
    page.insert_text(
        origin,
        new_text,
        fontname=registered_name,
        fontfile=font_file,
        fontsize=final_size,
        color=color_rgb,
    )
    return True


def replace_text(
    input_path: str,
    output_path: str,
    find_str: str,
    replace_str: str,
    page_num: Optional[int] = None,
    auto_shrink: bool = False,
    bg_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> int:
    """
    Finds and replaces all occurrences of text directly on the PDF,
    preserving font, size, and color.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    doc = pymupdf.open(input_path)
    total_pages = len(doc)
    pages = [page_num - 1] if page_num is not None else range(total_pages)
    total_replaced = 0
    font_cache = {}

    for pno in pages:
        if pno < 0 or pno >= total_pages:
            continue
        page = doc[pno]
        matches = page.search_for(find_str)
        if not matches:
            continue

        page_dict = page.get_text("dict")
        spans = []
        for b in page_dict.get("blocks", []):
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    spans.append(s)

        for match_rect in matches:
            target_rect = pymupdf.Rect(match_rect)

            best_span = None
            best_overlap = 0.0
            for s in spans:
                s_rect = pymupdf.Rect(s["bbox"])
                overlap_rect = target_rect & s_rect
                overlap = overlap_rect.get_area() if not overlap_rect.is_empty else 0.0
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_span = s

            font_name = best_span["font"] if best_span else "helv"
            font_size = best_span["size"] if best_span else 12.0
            color = best_span["color"] if best_span else 0
            flags = best_span.get("flags", 0) if best_span else 0
            
            origin_x = target_rect.x0
            origin_y = best_span["origin"][1] if best_span else target_rect.y1 - 1.5

            replace_exact_span(
                page=page,
                bbox=tuple(target_rect),
                origin=(origin_x, origin_y),
                font_name=font_name,
                font_size=font_size,
                color_val=color,
                flags=flags,
                new_text=replace_str,
                auto_shrink=auto_shrink,
                bg_color=bg_color,
                font_cache=font_cache,
                orig_width=target_rect.width,
            )
            total_replaced += 1

    # Atomic write to support output_path == input_path
    if os.path.abspath(output_path) == os.path.abspath(input_path):
        pdf_bytes = doc.tobytes(deflate=True, garbage=3)
        doc.close()
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
    else:
        doc.save(output_path)
        doc.close()

    return total_replaced


def inspect_pdf(pdf_path: str, page_num: Optional[int] = None):
    """Prints extracted text with font, size, color, and bounding box details."""
    if not os.path.isfile(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    print(f"\nDocument: {pdf_path} ({total_pages} page{'s' if total_pages != 1 else ''})\n" + "=" * 60)

    pages = [page_num - 1] if page_num is not None else range(total_pages)

    for pno in pages:
        if pno < 0 or pno >= total_pages:
            print(f"Warning: Page {pno + 1} is out of bounds (1-{total_pages}).")
            continue

        page = doc[pno]
        print(f"\n--- PAGE {pno + 1} ---")
        blocks = page.get_text("dict")["blocks"]
        count = 0

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue
                    font = span["font"]
                    size = round(span["size"], 1)
                    color_rgb = int_to_rgb(span["color"])
                    color_hex = rgb_to_hex(*color_rgb)
                    bbox = [round(v, 1) for v in span["bbox"]]
                    origin = [round(v, 1) for v in span["origin"]]
                    print(
                        f"  [{origin[0]}, {origin[1]}] '{text}'\n"
                        f"      Font: {font} | Size: {size} pt | Color: {color_hex} | BBox: {bbox}"
                    )
                    count += 1

        if count == 0:
            print("  (No extractable text found on this page)")

    doc.close()


def main():
    parser = argparse.ArgumentParser(
        description="PDF Direct Text Editor - Edit text in PDF preserving font, size, and styling."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect text, font, size, and positions in a PDF.")
    inspect_parser.add_argument("pdf_path", help="Path to input PDF file.")
    inspect_parser.add_argument("--page", type=int, default=None, help="Specific page number (1-indexed).")

    # Replace command
    replace_parser = subparsers.add_parser("replace", help="Find and replace text directly on a PDF.")
    replace_parser.add_argument("pdf_path", help="Path to input PDF file.")
    replace_parser.add_argument("--find", required=True, help="Text string to find.")
    replace_parser.add_argument("--replace", required=True, help="Replacement text.")
    replace_parser.add_argument("-o", "--output", required=True, help="Path for the output edited PDF.")
    replace_parser.add_argument("--page", type=int, default=None, help="Target specific page (1-indexed).")
    replace_parser.add_argument(
        "--auto-shrink",
        action="store_true",
        help="Slightly adjust font size if new text exceeds original width.",
    )

    args = parser.parse_args()

    if args.command == "inspect":
        inspect_pdf(args.pdf_path, args.page)
    elif args.command == "replace":
        count = replace_text(
            input_path=args.pdf_path,
            output_path=args.output,
            find_str=args.find,
            replace_str=args.replace,
            page_num=args.page,
            auto_shrink=args.auto_shrink,
        )
        if count > 0:
            print(f"Success: Replaced {count} occurrence{'s' if count != 1 else ''}. Saved to '{args.output}'.")
        else:
            print(f"No occurrences of '{args.find}' were found in '{args.pdf_path}'.")


if __name__ == "__main__":
    main()
