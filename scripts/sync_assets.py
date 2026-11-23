import os, shutil

src_cand = 'Houses/assets/candidates'
dst_cand = 'Result declaration/assets/candidates'
for f in os.listdir(src_cand):
    src_f = os.path.join(src_cand, f)
    dst_f = os.path.join(dst_cand, f)
    if os.path.isfile(src_f) and not os.path.exists(dst_f):
        shutil.copy2(src_f, dst_f)

src_sym = 'Houses/assets/symbols'
dst_sym = 'Result declaration/assets/symbols'
for f in os.listdir(src_sym):
    src_f = os.path.join(src_sym, f)
    dst_f = os.path.join(dst_sym, f)
    if os.path.isfile(src_f) and not os.path.exists(dst_f):
        shutil.copy2(src_f, dst_f)

print("Synchronized real candidate photos and symbols to Result declaration/assets!")
