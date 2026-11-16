import sys
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "scripts"))

from card_engine import (
    create_card_image,
    render_voter_card_to_file,
    generate_a4_sheets_for_roster,
    TEACHERS,
    HOUSES,
    parse_xlsx,
    XLSX_PATH,
)

def main():
    start_time = time.time()
    print("=== STARTING FULL VOTER CARDS REGENERATION (NEW FORMAT: NO NUMBER BELOW BARCODE) ===")

    # 1. Target Directories
    voter_cards_dir = ROOT / "voter_cards"
    houses_voter_cards_dir = ROOT / "Houses" / "2voter_cards"

    # Backup Demo Card
    demo_src = ROOT / "Houses" / "sample_cards" / "0000_Demo_User.png"
    demo_card_img = None
    demo_person = {
        "admissionNo": "0000",
        "fullName": "Demo User",
        "className": "Demo",
        "section": "All",
        "houseCode": "ALL",
    }
    demo_card_img = create_card_image(demo_person)

    # 2. Clean out old cards
    for d in [voter_cards_dir, houses_voter_cards_dir]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    print("Cleaned out old card directories.")

    # 3. Save Demo Card in sample_cards, Houses/sample_cards, and voter_cards
    demo_dirs = [
        ROOT / "Houses" / "sample_cards",
        ROOT / "sample_cards",
        voter_cards_dir,
        houses_voter_cards_dir
    ]
    for dd in demo_dirs:
        dd.mkdir(parents=True, exist_ok=True)
        demo_card_img.save(dd / "0000_Demo_User.png", "PNG", dpi=(300, 300))
    print("Saved clean New Format Demo User card (0000_Demo_User.png).")

    # 4. Generate Teachers Cards & A4 Sheets
    print(f"\nGenerating {len(TEACHERS)} Teaching Staff cards...")
    teachers_card_dir = voter_cards_dir / "teachers"
    teachers_card_dir.mkdir(parents=True, exist_ok=True)
    for t in TEACHERS:
        safe_name = "".join(c if c.isalnum() else "_" for c in t["fullName"])
        out_f = teachers_card_dir / f"{t['admissionNo']}_{safe_name}.png"
        render_voter_card_to_file(t, out_f)

    teachers_a4_dir = voter_cards_dir / "a4_sheets" / "teachers"
    generate_a4_sheets_for_roster(
        TEACHERS,
        teachers_a4_dir,
        title_prefix="Teaching Staff Voter Cards",
        sheet_file_prefix="Teacher_A4_Sheet"
    )
    print("Completed Teaching Staff cards and A4 sheets.")

    # 5. Load Students from Roster
    students, _, _ = parse_xlsx(XLSX_PATH)
    print(f"\nLoaded {len(students)} students from {XLSX_PATH.name}.")

    # 6. Generate House-Wise Cards & A4 Sheets
    house_counts = {}
    for h in HOUSES:
        code = h["code"]
        name = h["name"]
        slug = h["slug"]

        house_students = [s for s in students if s["houseCode"] == code]
        house_counts[code] = len(house_students)
        print(f"\nGenerating {len(house_students)} cards for {name} House...")

        house_card_dir = voter_cards_dir / slug
        house_card_dir.mkdir(parents=True, exist_ok=True)
        for s in house_students:
            safe_name = "".join(c if c.isalnum() else "_" for c in s["fullName"])[:30]
            out_f = house_card_dir / f"{s['admissionNo']}_{safe_name}.png"
            render_voter_card_to_file(s, out_f)

        house_a4_dir = voter_cards_dir / "a4_sheets" / slug
        generate_a4_sheets_for_roster(
            house_students,
            house_a4_dir,
            title_prefix=f"{name} House Voter Cards",
            sheet_file_prefix=f"{name}_A4_Sheet"
        )

    # 7. Mirror to Houses/2voter_cards
    print("\nMirroring to Houses/2voter_cards...")
    for item in voter_cards_dir.iterdir():
        dest = houses_voter_cards_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    elapsed = round(time.time() - start_time, 1)
    print(f"\n=== COMPLETED IN {elapsed}s ===")
    print(f"Total Teachers: {len(TEACHERS)}")
    print(f"Total Students: {len(students)} {house_counts}")
    print(f"Directory: {voter_cards_dir}")

if __name__ == "__main__":
    main()
