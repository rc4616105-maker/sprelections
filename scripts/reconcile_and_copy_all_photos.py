import os, json, re, shutil, hashlib

def hash_file(p):
    if not os.path.exists(p): return None
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

with open('scripts/extracted_contestants.json', 'r', encoding='utf-8') as f:
    docs = json.load(f)

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
js_cands = json.loads(m.group(1))

# Symbols map
SYMBOL_MAP = {
    "ashoka chakra": {"name": "Ashoka Chakra", "icon": "☸️", "slug": "ashoka_chakra", "image": "../assets/symbols/ashoka_chakra.png"},
    "ashok chakra": {"name": "Ashoka Chakra", "icon": "☸️", "slug": "ashoka_chakra", "image": "../assets/symbols/ashoka_chakra.png"},
    "peacock": {"name": "Peacock", "icon": "🦚", "slug": "peacock", "image": "../assets/symbols/peacock.png"},
    "banyan tree": {"name": "Banyan Tree", "icon": "🌳", "slug": "banyan_tree", "image": "../assets/symbols/banyan_tree.png"},
    "tree": {"name": "Banyan Tree", "icon": "🌳", "slug": "banyan_tree", "image": "../assets/symbols/banyan_tree.png"},
    "mango": {"name": "Mango", "icon": "🥭", "slug": "mango", "image": "../assets/symbols/mango.png"},
    "hockey stick": {"name": "Hockey Stick", "icon": "🏑", "slug": "hockey_stick", "image": "../assets/symbols/hockey_stick.png"},
    "dolphin": {"name": "Dolphin", "icon": "🐬", "slug": "dolphin", "image": "../assets/symbols/dolphin.png"},
    "royal bengal tiger": {"name": "Royal Bengal Tiger", "icon": "🐅", "slug": "royal_bengal_tiger", "image": "../assets/symbols/royal_bengal_tiger.png"},
    "bengal tiger": {"name": "Royal Bengal Tiger", "icon": "🐅", "slug": "royal_bengal_tiger", "image": "../assets/symbols/royal_bengal_tiger.png"},
    "tiger": {"name": "Royal Bengal Tiger", "icon": "🐅", "slug": "royal_bengal_tiger", "image": "../assets/symbols/royal_bengal_tiger.png"},
    "ganga river": {"name": "River", "icon": "🌊", "slug": "river", "image": "../assets/symbols/river.png"},
    "river": {"name": "River", "icon": "🌊", "slug": "river", "image": "../assets/symbols/river.png"},
    "konark wheel": {"name": "Konark Wheel", "icon": "☸️", "slug": "konark_wheel", "image": "../assets/symbols/konark_wheel.png"},
    "star": {"name": "Star", "icon": "⭐", "slug": "star", "image": "../assets/symbols/star.png"},
    "torch": {"name": "Torch", "icon": "🔥", "slug": "torch", "image": "../assets/symbols/torch.png"},
    "shield": {"name": "Shield", "icon": "🛡️", "slug": "shield", "image": "../assets/symbols/shield.png"},
    "rising sun": {"name": "Rising Sun", "icon": "🌅", "slug": "rising_sun", "image": "../assets/symbols/rising_sun.png"},
    "book": {"name": "Book", "icon": "📖", "slug": "book", "image": "../assets/symbols/book.png"},
    "trophy": {"name": "Trophy", "icon": "🏆", "slug": "trophy", "image": "../assets/symbols/trophy.png"},
    "compass": {"name": "Compass", "icon": "🧭", "slug": "compass", "image": "../assets/symbols/compass.png"},
    "rocket": {"name": "Rocket", "icon": "🚀", "slug": "rocket", "image": "../assets/symbols/rocket.png"},
    "bell": {"name": "Bell", "icon": "🔔", "slug": "bell", "image": "../assets/symbols/bell.png"},
    "elephant": {"name": "Elephant", "icon": "🐘", "slug": "elephant", "image": "../assets/symbols/elephant.png"},
    "pumpkin": {"name": "Pumpkin", "icon": "🎃", "slug": "pumpkin", "image": "../assets/symbols/pumpkin.png"}
}

def resolve_symbol(raw_txt, fallback_sym):
    txt = raw_txt.lower()
    for k in ["ashoka chakra", "ashok chakra", "royal bengal tiger", "bengal tiger", "tiger", "hockey stick", "banyan tree", "peacock", "mango", "dolphin", "ganga river", "river", "konark wheel", "rising sun", "star", "torch", "shield", "book", "trophy", "compass", "rocket", "bell", "elephant", "pumpkin"]:
        if k in txt:
            return SYMBOL_MAP[k]
    return fallback_sym

from compare_cands_normalized import norm_name, norm_house

# Build complete reconciliation
final_roster = []
for jc in js_cands:
    jname = norm_name(jc['fullName'])
    jhouse = norm_house(jc['houseCode'])
    
    # find in docs
    doc_match = None
    for d in docs:
        dname = norm_name(d['folder'])
        dhouse = norm_house(d['house'])
        if jhouse == dhouse:
            if jname == dname or jname in dname or dname in jname or jname in norm_name(d['parsed']['name']) or (jname == "schaitanya" and dname == "schaintanya"):
                doc_match = d
                break
                
    if not doc_match:
        print(f"FAILED TO MATCH: {jc['fullName']} ({jc['houseCode']})")
        continue
        
    orig_img_path = doc_match['img_path']
    if not orig_img_path or not os.path.exists(orig_img_path):
        print(f"NO ORIGINAL IMAGE: {jc['fullName']} at {orig_img_path}")
        continue
        
    # Target filename in assets/candidates
    photo_rel = jc['photoPath'].replace('../assets/candidates/', '')
    dst_houses = os.path.join("Houses/assets/candidates", photo_rel)
    dst_result = os.path.join("Result declaration/assets/candidates", photo_rel)
    
    # Copy from 1docs directly!
    shutil.copy2(orig_img_path, dst_houses)
    shutil.copy2(orig_img_path, dst_result)
    
    # Check symbol
    raw_doc_txt = doc_match['parsed'].get('raw_text', '')
    correct_sym = resolve_symbol(raw_doc_txt, jc['symbolObj'])
    
    jc_updated = dict(jc)
    jc_updated['symbolObj'] = {
        "name": correct_sym["name"],
        "icon": correct_sym["icon"],
        "slug": correct_sym["slug"],
        "image": correct_sym["image"],
        "imagePath": correct_sym["image"]
    }
    final_roster.append(jc_updated)

print(f"Successfully reconciled, copied photos and resolved symbols for {len(final_roster)} / {len(js_cands)} candidates!")
