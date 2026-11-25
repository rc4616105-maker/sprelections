import json, re

pdf_data = [
    # PRESIDENT (5)
    ("PRESIDENT", "M. Vaishnavi", "Banyan Tree"),
    ("PRESIDENT", "S. Harini Reddy", "Hockey Stick"),
    ("PRESIDENT", "M. Rithvik", "Mango"),
    ("PRESIDENT", "V. Janaki Koushik", "Peacock"),
    ("PRESIDENT", "Y. Srinith", "Konark Wheel"),

    # VICE_PRESIDENT (11)
    ("VICE_PRESIDENT", "G. Srunith Goud", "Konark Wheel"),
    ("VICE_PRESIDENT", "J. Sampath Kumar", "Elephant"),
    ("VICE_PRESIDENT", "K. Ambika", "Pumpkin"),
    ("VICE_PRESIDENT", "G. Badrinath", "Banyan Tree"),
    ("VICE_PRESIDENT", "N. Enrique Iglesias", "Mango"),
    ("VICE_PRESIDENT", "M. Vivekananda Rao", "Hockey Stick"),
    ("VICE_PRESIDENT", "M. Anvitha Sharma", "Dolphin"),
    ("VICE_PRESIDENT", "K. Hadvitha", "Ganga River"),
    ("VICE_PRESIDENT", "K. Ishwarya", "Indian Currency"),
    ("VICE_PRESIDENT", "G. Aadhya", "Peacock"),
    ("VICE_PRESIDENT", "V. Ananya Reddy", "Royal Bengal Tiger"),

    # SPORTS_SECRETARY (7)
    ("SPORTS_SECRETARY", "Ch. Kowshik", "Hockey Stick"),
    ("SPORTS_SECRETARY", "S. Rithvik Reddy", "Mango"),
    ("SPORTS_SECRETARY", "Ch. Bala Thrusha Datta", "Pumpkin"),
    ("SPORTS_SECRETARY", "R. Srikshith", "Banyan Tree"),
    ("SPORTS_SECRETARY", "Shubhi Patel", "Royal Bengal Tiger"),
    ("SPORTS_SECRETARY", "K. Krithika", "Konark Wheel"),
    ("SPORTS_SECRETARY", "S. Sahasra", "Peacock"),

    # LITERARY_SECRETARY (7)
    ("LITERARY_SECRETARY", "Indu Priya", "Konark Wheel"),
    ("LITERARY_SECRETARY", "Balla Raga Sri", "Pumpkin"),
    ("LITERARY_SECRETARY", "M. Srivaishnavi", "Royal Bengal Tiger"),
    ("LITERARY_SECRETARY", "Y. Bhagya Sri", "Peacock"),
    ("LITERARY_SECRETARY", "D. Samanvitha", "Banyan Tree"),
    ("LITERARY_SECRETARY", "N. Malala", "Dolphin"),
    ("LITERARY_SECRETARY", "G. Harsha Vardhan Rao", "Hockey Stick"),

    # SOCIAL_CULTURAL_SECRETARY (8)
    ("SOCIAL_CULTURAL_SECRETARY", "V. Himavardhan", "Mango"),
    ("SOCIAL_CULTURAL_SECRETARY", "G. Ashwath", "Peacock"),
    ("SOCIAL_CULTURAL_SECRETARY", "P. Divija", "Hockey Stick"),
    ("SOCIAL_CULTURAL_SECRETARY", "K. Rasagna", "Pumpkin"),
    ("SOCIAL_CULTURAL_SECRETARY", "K. Akshara", "Konark Wheel"),
    ("SOCIAL_CULTURAL_SECRETARY", "V. Chaithra", "Royal Bengal Tiger"),
    ("SOCIAL_CULTURAL_SECRETARY", "Nithya Sree. Y", "Dolphin"),
    ("SOCIAL_CULTURAL_SECRETARY", "P. Meghana", "Banyan Tree")
]

with open('Houses/central/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find houseCandidates
m = re.search(r'houseCandidates:\s*(\[.*?\])\s*,\s*classes:', text, re.DOTALL)
if not m:
    # try at the end
    m = re.search(r'houseCandidates:\s*(\[.*?\])\s*\}\s*;', text, re.DOTALL)

central_cands = json.loads(m.group(1)) if m else []
print(f"Total candidates in central data.js: {len(central_cands)}")

def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())

all_ok = True
for pos, name, sym in pdf_data:
    found = None
    for c in central_cands:
        if c['positionId'] == pos and norm(name) in norm(c['fullName']):
            found = c
            break
    if not found:
        print(f"MISSING: {pos} - {name} ({sym})")
        all_ok = False
    else:
        c_sym = found.get('symbolObj', {}).get('name')
        if norm(c_sym) != norm(sym):
            print(f"SYMBOL MISMATCH for {name}: PDF={sym}, central={c_sym}")
            all_ok = False
        else:
            print(f"OK: [{pos}] {found['fullName']} -> Symbol: {c_sym}")

if all_ok:
    print("\nALL 38 CANDIDATES AND SYMBOLS MATCH THE OFFICIAL PDF 100%!")
