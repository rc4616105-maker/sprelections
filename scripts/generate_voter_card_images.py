"""
SPR School of Excellence — Official House Elections 2026
Voter Identity Card & Barcode Image Generator (New Format)

Generates high-resolution, print-ready PNG voter cards with scannable Code 128 barcodes.
NEW FORMAT:
  - Header: School Name & Election Header (with house/staff badge)
  - Student / Teacher Details: Name, Class/Subject, Section/Contact, Voter ID
  - Code 128 Barcode: Crisp, high-contrast, scannable lines WITHOUT duplicate text underneath
  - Polling booth instructions / authorization in footer
"""

import os
import sys
import json
import argparse
from pathlib import Path
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "scripts"))
from parse_roster import parse_xlsx, XLSX_PATH, HOUSES

# Official House Design Theme
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
    "BHISHMA": {
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


def render_voter_card(person: dict, output_path: Path):
    """Renders a single 850x560 print-ready voter card PNG with NO repeated ID below barcode."""
    W, H = 850, 560
    card = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(card)

    is_staff = person.get("isStaff", False) or person.get("className") == "Staff"
    house_code = person.get("houseCode", "HANUMAN").upper()
    is_demo = False  # Render full authentic student identity on all cards

    if is_staff:
        theme = HOUSE_THEMES["STAFF"]
    elif is_demo:
        theme = HOUSE_THEMES["ALL"]
    else:
        theme = HOUSE_THEMES.get(house_code, HOUSE_THEMES["ALL"])

    # Fonts
    font_school = load_font("segoeuib.ttf", 26)
    font_sub = load_font("segoeui.ttf", 15)
    font_house = load_font("segoeuib.ttf", 17)
    font_details = load_font("segoeui.ttf", 18)
    font_label = load_font("segoeuib.ttf", 15)
    font_footer = load_font("segoeui.ttf", 13)
    font_voter_id = load_font("segoeuib.ttf", 24)

    # Dynamic name font sizing
    name = person.get("fullName", "").strip().upper()
    name_size = 28
    if len(name) > 28:
        name_size = 22
    elif len(name) > 22:
        name_size = 25
    font_name = load_font("segoeuib.ttf", name_size)

    # 1. Outer card border
    draw.rounded_rectangle([10, 10, W - 10, H - 10], radius=16, outline="#cbd5e1", width=2)

    # 2. Header banner
    draw.rounded_rectangle([12, 12, W - 12, 86], radius=14, fill=theme["primary"])
    draw.rectangle([12, 50, W - 12, 86], fill=theme["primary"])

    # Header texts
    draw.text((32, 20), "SPR SCHOOL OF EXCELLENCE", fill="#ffffff", font=font_school)
    if is_staff:
        draw.text((32, 55), "OFFICIAL ELECTIONS 2026 • TEACHING STAFF VOTER CARD", fill="#ffffff", font=font_sub)
    elif is_demo:
        draw.text((32, 55), "OFFICIAL ELECTIONS 2026 • UNIVERSAL DEMO VOTER CARD", fill="#ffffff", font=font_sub)
    else:
        draw.text((32, 55), "OFFICIAL HOUSE ELECTIONS 2026 • VOTER IDENTITY CARD", fill="#ffffff", font=font_sub)

    # House / Role badge pill
    if is_staff:
        badge_text = "TEACHING STAFF / ALL"
    elif is_demo or house_code == "ALL":
        badge_text = "ALL HOUSES"
    else:
        badge_text = f"{theme['name'].upper()} HOUSE"

    badge_box_w = 230 if not is_staff else 250
    draw.rounded_rectangle([W - badge_box_w, 24, W - 28, 68], radius=8, fill=theme["badge_bg"])
    badge_bbox = draw.textbbox((0, 0), badge_text, font=font_house)
    badge_w = badge_bbox[2] - badge_bbox[0]
    badge_x = (W - badge_box_w) + ((badge_box_w - 28 - badge_w) // 2)
    draw.text((badge_x, 34), badge_text, fill=theme["badge_text"], font=font_house)

    # 3. Person details box
    draw.rounded_rectangle([28, 102, W - 28, 240], radius=12, fill=theme["bg"], outline=theme["border"], width=1)

    if is_staff:
        draw.text((48, 116), "TEACHING STAFF / FACULTY", fill=theme["label"], font=font_label)
    elif is_demo:
        draw.text((48, 116), "UNIVERSAL DEMO VOTER", fill=theme["label"], font=font_label)
    else:
        draw.text((48, 116), "STUDENT VOTER", fill=theme["label"], font=font_label)
    draw.text((48, 140), name, fill="#0f172a", font=font_name)

    details_y = 192
    voter_id = str(person.get("admissionNo", "0000"))

    if is_staff:
        subj_str = str(person.get("subject", "FACULTY")).strip().upper()
        phone_str = str(person.get("contact", "")).strip()
        draw.text((48, details_y), "SUBJECT:", fill="#64748b", font=font_label)
        draw.text((125, details_y), subj_str, fill="#0f172a", font=font_details)
        if phone_str and phone_str != "—":
            draw.text((330, details_y), "CONTACT:", fill="#64748b", font=font_label)
            draw.text((410, details_y), phone_str, fill="#0f172a", font=font_details)
        draw.text((W - 240, details_y), "VOTER ID:", fill="#64748b", font=font_label)
        draw.text((W - 145, details_y - 4), voter_id, fill=theme["primary"], font=font_voter_id)
    else:
        cls_str = str(person.get("className", ""))
        sec_str = str(person.get("section", "—"))
        draw.text((48, details_y), "CLASS:", fill="#64748b", font=font_label)
        draw.text((112, details_y), cls_str, fill="#0f172a", font=font_details)
        draw.text((200, details_y), "SECTION:", fill="#64748b", font=font_label)
        draw.text((285, details_y), sec_str, fill="#0f172a", font=font_details)
        draw.text((W - 230, details_y), "VOTER ID:", fill="#64748b", font=font_label)
        draw.text((W - 135, details_y - 3), voter_id, fill=theme["primary"], font=font_voter_id)

    # 4. Generate Code 128 Barcode (NEW FORMAT: No ID numbers printed underneath!)
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
    foot_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    foot_w = foot_bbox[2] - foot_bbox[0]
    draw.text(((W - foot_w) // 2, H - 32), footer_text, fill="#94a3b8", font=font_footer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(output_path, "PNG", dpi=(300, 300))
    return output_path


def generate_a4_sheets(roster: list, output_dir: Path, title_prefix="Official Voter Cards"):
    """
    Arranges cards into standard A4 sheets (2 columns x 4 rows = 8 cards per page)
    ready to print directly on any printer.
    A4 at 300 DPI: 2480 x 3508 pixels.
    """
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

            # Render card in memory
            temp_card_path = output_dir / f"_temp_{s['admissionNo']}.png"
            render_voter_card(s, temp_card_path)
            card_img = Image.open(temp_card_path).resize((card_w, card_h), Image.Resampling.LANCZOS)
            page.paste(card_img, (x, y))

            # Light cut guideline
            draw.rectangle([x - 2, y - 2, x + card_w + 2, y + card_h + 2], outline="#e2e8f0", width=1)
            temp_card_path.unlink(missing_ok=True)

        # Footer page number
        font_page = load_font("segoeui.ttf", 32)
        page_str = f"SPR School of Excellence — {title_prefix} • Sheet {page_num} of {total_pages}"
        pbbox = draw.textbbox((0, 0), page_str, font=font_page)
        draw.text(((A4_W - (pbbox[2] - pbbox[0])) // 2, A4_H - 80), page_str, fill="#94a3b8", font=font_page)

        page_file = output_dir / f"A4_Sheet_{page_num:03d}.png"
        page.save(page_file, "PNG", dpi=(300, 300))
        print(f"Saved A4 sheet {page_num}/{total_pages}: {page_file.name}")
        page_num += 1


def load_teachers_roster():
    json_path = ROOT / "Houses" / "admin" / "teachers.json"
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return []


def main():
    parser = argparse.ArgumentParser(description="Generate Voter Card Images")
    parser.add_argument("--demo", action="store_true", help="Generate official Universal Demo User (0000) and Teacher Demo cards in sample_cards")
    parser.add_argument("--teacher-demo", action="store_true", help="Generate official Universal Teacher Demo card in sample_cards")
    parser.add_argument("--teachers", action="store_true", help="Generate all teaching staff cards and A4 sheets")
    parser.add_argument("--sample", action="store_true", help="Generate sample cards for each house")
    parser.add_argument("--all", action="store_true", help="Generate all individual student cards")
    parser.add_argument("--id", type=str, help="Generate card for a specific voter ID / admission number")
    parser.add_argument("--sheets", action="store_true", help="Generate A4 printable 8-card sheet PNGs for students")
    args = parser.parse_args()

    if args.demo or args.teacher_demo:
        out_dirs = [
            ROOT / "Houses" / "sample_cards",
            ROOT / "sample_cards"
        ]
        demo_st_6char = {
            "admissionNo": "1C8492",
            "fullName": "Aditya Vikram",
            "className": "10",
            "section": "CS (Chatrapathi Shivaji)",
            "houseCode": "BHEESHMA",
        }
        demo_st = {
            "admissionNo": "0000",
            "fullName": "Aditya Vikram",
            "className": "10",
            "section": "CS (Chatrapathi Shivaji)",
            "houseCode": "BHEESHMA",
        }
        demo_teacher = {
            "admissionNo": "0000",
            "fullName": "Dr. Rajesh Sharma (Demo Faculty)",
            "subject": "SENIOR FACULTY / DEMO",
            "contact": "9876543210",
            "houseCode": "BHEESHMA",
            "className": "Staff",
            "section": "Faculty",
            "isStaff": True,
        }
        demo_teacher_6000 = {
            "admissionNo": "6000",
            "fullName": "Dr. Rajesh Sharma (Demo Faculty)",
            "subject": "SENIOR FACULTY / DEMO",
            "contact": "9876543210",
            "houseCode": "BHEESHMA",
            "className": "Staff",
            "section": "Faculty",
            "isStaff": True,
        }
        for od in out_dirs:
            od.mkdir(parents=True, exist_ok=True)
            if args.demo:
                out_path_6char = od / "1C8492_Demo_User.png"
                render_voter_card(demo_st_6char, out_path_6char)
                print(f"Created 6-Character Format Demo Card (1C8492): {out_path_6char}")

                out_path_student = od / "0000_Demo_User.png"
                render_voter_card(demo_st, out_path_student)
                print(f"Created clean New Format Universal Student Demo Card: {out_path_student}")

                out_path_alias = od / "demo_voter_card.png"
                render_voter_card(demo_st_6char, out_path_alias)
                print(f"Created default demo voter card: {out_path_alias}")
            
            # Generate Teacher Demo Cards
            out_path_t0 = od / "0000_Demo_Teacher.png"
            render_voter_card(demo_teacher, out_path_t0)
            print(f"Created clean New Format Universal Teacher Demo Card (0000): {out_path_t0}")

            out_path_t6 = od / "6000_Demo_Teacher.png"
            render_voter_card(demo_teacher_6000, out_path_t6)
            print(f"Created clean New Format Universal Teacher Demo Card (6000): {out_path_t6}")

            out_path_t_alias = od / "teacher_demo_card.png"
            render_voter_card(demo_teacher, out_path_t_alias)
            print(f"Created Teacher Demo Card alias: {out_path_t_alias}")

            # Also refresh sample_verified_6001_teacher.png to New Format
            sample_6001 = {
                "admissionNo": "6001",
                "fullName": "MARUTHI KOMIREDDY",
                "subject": "CORRESPONDENT",
                "contact": "9908899987",
                "houseCode": "BHEESHMA",
                "className": "Staff",
                "section": "Faculty",
                "isStaff": True,
            }
            out_6001 = od / "sample_verified_6001_teacher.png"
            render_voter_card(sample_6001, out_6001)
            print(f"Refreshed sample teacher card (6001): {out_6001}")
        return

    if args.teachers:
        teachers = load_teachers_roster()
        if not teachers:
            print("Error: Houses/admin/teachers.json not found! Run generate_teachers_files.py first.")
            sys.exit(1)
        
        cards_dir = ROOT / "voter_cards" / "teachers"
        cards_dir.mkdir(parents=True, exist_ok=True)
        print(f"Generating cards for {len(teachers)} Teaching Staff members...")
        for t in teachers:
            clean_name = "".join(c if c.isalnum() else "_" for c in t["fullName"])
            out_file = cards_dir / f"{t['admissionNo']}_{clean_name}.png"
            render_voter_card(t, out_file)
        print(f"Successfully generated {len(teachers)} teacher cards in {cards_dir}!")

        # A4 printable sheets
        sheets_dir = ROOT / "voter_cards" / "teachers" / "a4_sheets"
        print(f"Generating A4 printable sheets for Teaching Staff...")
        generate_a4_sheets(teachers, sheets_dir, title_prefix="Official Teaching Staff Voter Cards")
        print(f"Completed all Teaching Staff A4 sheets in {sheets_dir}!")
        return

    # Student-based commands
    students, _, _ = parse_xlsx(XLSX_PATH)
    print(f"Loaded {len(students)} students from roster.")

    if args.id:
        # Check students first, then teachers
        st = next((s for s in students if str(s["admissionNo"]) == args.id), None)
        if not st:
            teachers = load_teachers_roster()
            st = next((t for t in teachers if str(t["admissionNo"]) == args.id), None)
        if not st:
            print(f"Error: Voter ID {args.id} not found!")
            sys.exit(1)
        out = ROOT / "sample_cards" / f"voter_{args.id}.png"
        render_voter_card(st, out)
        print(f"Created card: {out}")
        return

    if args.sample:
        out_dir = ROOT / "Houses" / "sample_cards"
        for house in ["BHEESHMA", "GURUDRONA", "HANUMAN", "KARNA", "VASISTHA", "VISHWAMITHRA"]:
            st = next((s for s in students if s["houseCode"] == house and s["admissionNo"] != "0000"), None)
            if not st:
                st = next(s for s in students if s["houseCode"] == house)
            out = out_dir / f"{house.lower()}_{st['admissionNo']}_{st['fullName'].replace(' ', '_')}.png"
            render_voter_card(st, out)
            print(f"Created sample [{house}]: {out.name}")
        return

    if args.all:
        out_dir = ROOT / "voter_cards" / "students"
        print(f"Generating all {len(students)} voter cards into {out_dir}...")
        for i, s in enumerate(students):
            house_slug = s["houseCode"].lower()
            safe_name = "".join(c if c.isalnum() else "_" for c in s["fullName"])[:30]
            out = out_dir / house_slug / f"{s['admissionNo']}_{safe_name}.png"
            render_voter_card(s, out)
            if (i + 1) % 100 == 0 or (i + 1) == len(students):
                print(f"Progress: {i + 1}/{len(students)} cards generated.")
        print("Completed generating all student cards!")

    if args.sheets:
        out_dir = ROOT / "voter_cards" / "students" / "a4_sheets"
        print(f"Generating A4 printable sheets (8 cards per page) into {out_dir}...")
        generate_a4_sheets(students, out_dir, title_prefix="Official Student Voter Cards")
        print(f"All A4 sheets generated in {out_dir}!")


if __name__ == "__main__":
    main()
