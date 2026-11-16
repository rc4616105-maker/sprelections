import sys
import os
import json
import shutil
from pathlib import Path
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "scripts"))
from parse_roster import parse_xlsx, XLSX_PATH, HOUSES

# Load Teachers
TEACHERS_PATH = ROOT / "Houses" / "admin" / "teachers.json"
TEACHERS = json.loads(TEACHERS_PATH.read_text(encoding="utf-8"))

HOUSE_THEMES = {
    "BHEESHMA": {
        "name": "Bheeshma",
        "primary": "#ca8a04",
        "bg": "#fefce8",
        "border": "#fef08a",
        "badge_bg": "#ffffff",
        "badge_text": "#854d0e",
        "label": "#854d0e",
    },
    "GURUDRONA": {
        "name": "Gurudrona",
        "primary": "#1d4ed8",
        "bg": "#eff6ff",
        "border": "#bfdbfe",
        "badge_bg": "#ffffff",
        "badge_text": "#1e40af",
        "label": "#1e40af",
    },
    "HANUMAN": {
        "name": "Hanuman",
        "primary": "#ea580c",
        "bg": "#fff7ed",
        "border": "#fed7aa",
        "badge_bg": "#ffffff",
        "badge_text": "#9a3412",
        "label": "#9a3412",
    },
    "KARNA": {
        "name": "Karna",
        "primary": "#b91c1c",
        "bg": "#fef2f2",
        "border": "#fecaca",
        "badge_bg": "#ffffff",
        "badge_text": "#991b1b",
        "label": "#991b1b",
    },
    "VASISTHA": {
        "name": "Vasistha",
        "primary": "#db2777",
        "bg": "#fdf2f8",
        "border": "#fbcfe8",
        "badge_bg": "#ffffff",
        "badge_text": "#9d174d",
        "label": "#9d174d",
    },
    "VISHWAMITHRA": {
        "name": "Vishwamithra",
        "primary": "#7c3aed",
        "bg": "#faf5ff",
        "border": "#e9d5ff",
        "badge_bg": "#ffffff",
        "badge_text": "#6b21a8",
        "label": "#6b21a8",
    },
    "ALL": {
        "name": "All Houses",
        "primary": "#059669",
        "bg": "#ecfdf5",
        "border": "#a7f3d0",
        "badge_bg": "#ffffff",
        "badge_text": "#065f46",
        "label": "#065f46",
    },
    "STAFF": {
        "name": "Teaching Staff",
        "primary": "#059669",
        "bg": "#ecfdf5",
        "border": "#a7f3d0",
        "badge_bg": "#ffffff",
        "badge_text": "#065f46",
        "label": "#065f46",
    },
}

def load_font(name: str, size: int):
    try:
        return ImageFont.truetype(name, size)
    except Exception:
        return ImageFont.load_default()

# Pre-cache common fonts
FONTS = {
    "school": load_font("segoeuib.ttf", 26),
    "sub": load_font("segoeui.ttf", 15),
    "house": load_font("segoeuib.ttf", 17),
    "details": load_font("segoeui.ttf", 18),
    "label": load_font("segoeuib.ttf", 15),
    "footer": load_font("segoeui.ttf", 13),
    "voter_id": load_font("segoeuib.ttf", 24),
    "page": load_font("segoeui.ttf", 32),
}

def create_card_image(person: dict) -> Image.Image:
    """Renders a single 850x560 print-ready voter card with NO numbers below barcode."""
    W, H = 850, 560
    card = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(card)

    is_staff = person.get("isStaff", False) or person.get("className") == "Staff"
    house_code = person.get("houseCode", "HANUMAN").upper()
    is_demo = str(person.get("admissionNo")) == "0000" or (house_code == "ALL" and not is_staff)

    if is_staff:
        theme = HOUSE_THEMES["STAFF"]
    elif is_demo:
        theme = HOUSE_THEMES["ALL"]
    else:
        theme = HOUSE_THEMES.get(house_code, HOUSE_THEMES["ALL"])

    # Dynamic name sizing
    name = person.get("fullName", "").strip().upper()
    name_size = 28
    if len(name) > 28:
        name_size = 22
    elif len(name) > 22:
        name_size = 25
    font_name = load_font("segoeuib.ttf", name_size)

    # 1. Border
    draw.rounded_rectangle([10, 10, W - 10, H - 10], radius=16, outline="#cbd5e1", width=2)

    # 2. Header
    draw.rounded_rectangle([12, 12, W - 12, 86], radius=14, fill=theme["primary"])
    draw.rectangle([12, 50, W - 12, 86], fill=theme["primary"])

    draw.text((32, 20), "SPR SCHOOL OF EXCELLENCE", fill="#ffffff", font=FONTS["school"])
    if is_staff:
        draw.text((32, 55), "OFFICIAL ELECTIONS 2026 • TEACHING STAFF VOTER CARD", fill="#ffffff", font=FONTS["sub"])
    elif is_demo:
        draw.text((32, 55), "OFFICIAL ELECTIONS 2026 • UNIVERSAL DEMO VOTER CARD", fill="#ffffff", font=FONTS["sub"])
    else:
        draw.text((32, 55), "OFFICIAL HOUSE ELECTIONS 2026 • VOTER IDENTITY CARD", fill="#ffffff", font=FONTS["sub"])

    # Badge pill
    if is_staff:
        badge_text = "TEACHING STAFF / ALL"
    elif is_demo or house_code == "ALL":
        badge_text = "ALL HOUSES"
    else:
        badge_text = f"{theme['name'].upper()} HOUSE"

    badge_box_w = 230 if not is_staff else 250
    draw.rounded_rectangle([W - badge_box_w, 24, W - 28, 68], radius=8, fill=theme["badge_bg"])
    badge_bbox = draw.textbbox((0, 0), badge_text, font=FONTS["house"])
    badge_w = badge_bbox[2] - badge_bbox[0]
    badge_x = (W - badge_box_w) + ((badge_box_w - 28 - badge_w) // 2)
    draw.text((badge_x, 34), badge_text, fill=theme["badge_text"], font=FONTS["house"])

    # 3. Details box
    draw.rounded_rectangle([28, 102, W - 28, 240], radius=12, fill=theme["bg"], outline=theme["border"], width=1)

    if is_staff:
        draw.text((48, 116), "TEACHING STAFF / FACULTY", fill=theme["label"], font=FONTS["label"])
    elif is_demo:
        draw.text((48, 116), "UNIVERSAL DEMO VOTER", fill=theme["label"], font=FONTS["label"])
    else:
        draw.text((48, 116), "STUDENT VOTER", fill=theme["label"], font=FONTS["label"])
    draw.text((48, 140), name, fill="#0f172a", font=font_name)

    details_y = 192
    voter_id = str(person.get("admissionNo", "0000"))

    if is_staff:
        subj_str = str(person.get("subject", "FACULTY")).strip().upper()
        phone_str = str(person.get("contact", "")).strip()
        draw.text((48, details_y), "SUBJECT:", fill="#64748b", font=FONTS["label"])
        draw.text((125, details_y), subj_str, fill="#0f172a", font=FONTS["details"])
        if phone_str and phone_str != "—":
            draw.text((330, details_y), "CONTACT:", fill="#64748b", font=FONTS["label"])
            draw.text((410, details_y), phone_str, fill="#0f172a", font=FONTS["details"])
        draw.text((W - 240, details_y), "VOTER ID:", fill="#64748b", font=FONTS["label"])
        draw.text((W - 145, details_y - 4), voter_id, fill=theme["primary"], font=FONTS["voter_id"])
    else:
        cls_str = str(person.get("className", ""))
        sec_str = str(person.get("section", "—"))
        draw.text((48, details_y), "CLASS:", fill="#64748b", font=FONTS["label"])
        draw.text((112, details_y), cls_str, fill="#0f172a", font=FONTS["details"])
        draw.text((200, details_y), "SECTION:", fill="#64748b", font=FONTS["label"])
        draw.text((285, details_y), sec_str, fill="#0f172a", font=FONTS["details"])
        draw.text((W - 230, details_y), "VOTER ID:", fill="#64748b", font=FONTS["label"])
        draw.text((W - 135, details_y - 3), voter_id, fill=theme["primary"], font=FONTS["voter_id"])

    # 4. Code 128 Barcode — STRICTLY NO NUMBERS/TEXT BELOW BARCODE
    code128 = barcode.get_barcode_class("code128")
    writer = ImageWriter()
    writer_opts = {
        "module_width": 0.45,
        "module_height": 18.0,
        "quiet_zone": 4.0,
        "write_text": False,
    }
    bc = code128(voter_id, writer=writer)
    bc_img = bc.render(writer_options=writer_opts)
    bc_x = (W - bc_img.width) // 2
    bc_y = 250 + ((265 - bc_img.height) // 2)
    card.paste(bc_img, (bc_x, bc_y))

    # 5. Footer notice
    if is_staff:
        footer_text = "Universal Faculty Card — Authorized for all House & Cabinet polling booths."
    elif is_demo:
        footer_text = "Universal Demo Card — Authorized for all House & Cabinet polling booths."
    else:
        footer_text = f"Present this card at the {theme['name']} House polling booth to cast your vote."
    foot_bbox = draw.textbbox((0, 0), footer_text, font=FONTS["footer"])
    foot_w = foot_bbox[2] - foot_bbox[0]
    draw.text(((W - foot_w) // 2, H - 32), footer_text, fill="#94a3b8", font=FONTS["footer"])

    return card

def render_voter_card_to_file(person: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    card = create_card_image(person)
    card.save(output_path, "PNG", dpi=(300, 300))
    return output_path

def generate_a4_sheets_for_roster(roster: list, output_dir: Path, title_prefix="Official Voter Cards", sheet_file_prefix="A4_Sheet"):
    output_dir.mkdir(parents=True, exist_ok=True)
    A4_W, A4_H = 2480, 3508
    margin_x = 100
    margin_y = 120
    card_w = 1100
    card_h = 740
    gap_x = 80
    gap_y = 80

    page_num = 1
    total = len(roster)
    total_pages = (total + 7) // 8

    for start_idx in range(0, total, 8):
        page = Image.new("RGB", (A4_W, A4_H), "#ffffff")
        draw = ImageDraw.Draw(page)

        chunk = roster[start_idx : start_idx + 8]
        for i, s in enumerate(chunk):
            row = i // 2
            col = i % 2
            x = margin_x + col * (card_w + gap_x)
            y = margin_y + row * (card_h + gap_y)

            card_img = create_card_image(s).resize((card_w, card_h), Image.Resampling.LANCZOS)
            page.paste(card_img, (x, y))
            draw.rectangle([x - 2, y - 2, x + card_w + 2, y + card_h + 2], outline="#e2e8f0", width=1)

        page_str = f"SPR School of Excellence — {title_prefix} • Sheet {page_num} of {total_pages}"
        pbbox = draw.textbbox((0, 0), page_str, font=FONTS["page"])
        draw.text(((A4_W - (pbbox[2] - pbbox[0])) // 2, A4_H - 80), page_str, fill="#94a3b8", font=FONTS["page"])

        page_file = output_dir / f"{sheet_file_prefix}_{page_num:03d}.png"
        page.save(page_file, "PNG", dpi=(300, 300))
        page_num += 1

    print(f"Generated {total_pages} sheets in {output_dir.name}")
