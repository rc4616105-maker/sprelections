import re, json

with open("Houses/admin/teachers.js", "r", encoding="utf-8") as f:
    t_js = f.read()
with open("Houses/admin/data.js", "r", encoding="utf-8") as f:
    d_js = f.read()

print("--- TEACHERS DEMO SEARCH ---")
for m in re.finditer(r'\{[^{}]*?"admissionNo":\s*"([^"]+)"[^{}]*?\}', t_js):
    block = m.group(0)
    if "demo" in block.lower() or "0000" in block:
        print("Teacher:", block)

print("--- DATA.JS DEMO SEARCH ---")
for m in re.finditer(r'\{[^{}]*?"admissionNo":\s*"([^"]+)"[^{}]*?\}', d_js):
    block = m.group(0)
    if "demo" in block.lower() or "0000" in block or "facul" in block.lower():
        adm = re.search(r'"admissionNo":\s*"([^"]+)"', block)
        name = re.search(r'"fullName":\s*"([^"]+)"', block)
        print("Data:", adm.group(1) if adm else "?", name.group(1) if name else "?")
