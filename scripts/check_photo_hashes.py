import os, json, re, hashlib

def hash_file(p):
    if not os.path.exists(p): return "MISSING"
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

from compare_cands_normalized import mapped, js_cands

# Let's map S.Chaitanya too
for jc in js_cands:
    if jc['fullName'] == 'S.Chaitanya':
        for root, dirs, files in os.walk('1docs/contestets/Hanuman house'):
            if 'chaintanya' in root.lower():
                imgs = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                mapped.append((jc, {
                    "folder_name": "S.Chaintanya",
                    "house_raw": "Hanuman house",
                    "img": imgs[0],
                    "img_path": os.path.join(root, imgs[0])
                }))

print(f"Total mapped pairs to verify: {len(mapped)}")

mismatches = []
for jc, dc in mapped:
    js_photo = jc.get('photoPath', '').replace('../', 'Houses/')
    doc_photo = dc['img_path']
    
    h_js = hash_file(js_photo)
    h_doc = hash_file(doc_photo)
    
    if h_js != h_doc:
        mismatches.append((jc['fullName'], jc['houseCode'], js_photo, doc_photo, h_js, h_doc))

print(f"\nTotal photo hash MISMATCHES: {len(mismatches)}")
for m in mismatches[:25]:
    print(f"Mismatch: {m[0]} ({m[1]})\n  JS photo: {m[2]} (hash: {m[4][:8]})\n  Doc photo: {m[3]} (hash: {m[5][:8]})")
