import json

target_files = [
    'Houses/teachers/data.js',
    'Houses/assets/all-candidates.js',
    'Result declaration/js/candidates-data.js'
]

dup_str = """        "isApproved": true
    },
      "photoUrl": "../assets/candidates/cabinet_b_ragasri.jpg",
      "photoPath": "../assets/candidates/cabinet_b_ragasri.jpg",
      "isApproved": true
    },"""

dup_str2 = """    "isApproved": true
  },
    "photoUrl": "../assets/candidates/cabinet_b_ragasri.jpg",
    "photoPath": "../assets/candidates/cabinet_b_ragasri.jpg",
    "isApproved": true
  },"""

for fp in target_files:
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()

    orig = text
    if dup_str in text:
        text = text.replace(dup_str, '        "isApproved": true\n    },')
    if dup_str2 in text:
        text = text.replace(dup_str2, '    "isApproved": true\n  },')

    if text != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Fixed duplicate in {fp}")
    else:
        print(f"Did not find exact string in {fp}, searching regex...")
        import re
        # Search for b_ragasri followed by duplicate photoUrl
        pattern = r'("photoUrl":\s*"[^"]*cabinet_b_ragasri\.jpg",\s*"photoPath":\s*"[^"]*cabinet_b_ragasri\.jpg",\s*"isApproved":\s*true\s*\},?\s*)+("photoUrl":\s*"[^"]*cabinet_b_ragasri\.jpg",\s*"photoPath":\s*"[^"]*cabinet_b_ragasri\.jpg",\s*"isApproved":\s*true\s*\},)'
        text = re.sub(pattern, r'\1', text)
        if text != orig:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Regex fixed {fp}")
