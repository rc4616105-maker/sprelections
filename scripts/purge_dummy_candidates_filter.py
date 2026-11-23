import shutil

dummy_list = [
    "Arjun Verma", "Tushar Singhania", "Karthik Menon", "Ananya Iyer", "Shruti Deshpande", "Pallavi Rao",
    "Rohan Nair", "Aryan Gupta", "Prateek Joshi", "Sneha Reddy", "Ishani Sen", "Kritika Bhat",
    "Devrath Singh", "Harshavardhan Rao", "Manish Pandey", "Kavya Menon", "Sanya Malhotra", "Deepika Nair",
    "Kunal Joshi", "Nikhil Saxena", "Tanmay Kulkarni", "Meera Sen", "Rhea Pillai", "Anushka Varma",
    "Tejas Chawla", "Yuvraj Sharma", "Samar Chauhan", "Ishita Pillai", "Tara Nambiar", "Garima Saxena",
    "Dhruv Kapoor", "Akshay Mehra", "Naveen Reddy", "Avni Sharma", "Bhavya Nair", "Kareena Joseph",
    "Abhimanyu Das", "Raghav Vashisht", "Surya Prakash", "Tarini Mukherjee", "Priyanka Bose", "Aaradhya Sen",
    "Siddharth Jain", "Jayesh Patel", "Chetan Anand", "Roshni Paul", "Diya Sengupta", "Maya Nambiar",
    "Aditya Hegde", "Gautam Menon", "Pranav Joshi", "Pooja Kulkarni", "Nandita Rao", "Malavika Nair",
    "Varun Bhat", "Naveen Iyer", "Rahul Somani", "Tanvi Saxena", "Divya Kamath", "Swati Mishra",
    "Vikramaditya Roy", "Shaurya Singhal", "Anirudh Deshmukh", "Rhea Deshmukh", "Ayesha Khan", "Tanvi Sengupta",
    "Samarth Rao", "Vivan Kapoor", "Tejas Nambiar", "Pari Chopra", "Ananya Roy", "Sana Sheikh",
    "Kabir Mehta", "Ananya Sundaram", "Rishabh Tandon", "Manav Saxena", "Isha Nair", "Vivaan Goel",
    "Siddharth Varma", "Kavya Ramanathan", "Nirav Shah", "Aayush Rawat", "Tanvi Bhardwaj", "Arman Gill",
    "Zoya Akhtar", "Pranav Khandelwal", "Rhea Sengupta"
]

dummy_names_js = '[\n    ' + ',\n    '.join([f'"{name}"' for name in dummy_list]) + '\n  ]'

new_get_candidates = f'''    async getHouseCandidates(houseCode) {{
      const DUMMY_CANDIDATE_NAMES = new Set({dummy_names_js});

      const isDummyCand = (c) => {{
        if (!c) return false;
        const name = String(c.full_name || c.fullName || "").trim();
        const sec = String(c.section || "").trim();
        const tag = String(c.tagline || "").trim();
        const adm = String(c.admission_no || c.admissionNo || "").trim();
        return (
          DUMMY_CANDIDATE_NAMES.has(name) ||
          sec.includes("Option ") ||
          tag.includes("Option ") ||
          name.startsWith("Candidate ") ||
          adm.startsWith("DEMO-")
        );
      }};

      const localCands = (window.HOUSE_DATA?.houseCandidates || []).filter((c) => !isDummyCand(c));
      const localMap = new Map(localCands.map((c) => [c.id, c]));

      if (this.mode === "supabase") {{
        try {{
          const rows = await sbRest(
            "GET",
            `/rest/v1/candidates?house_code=eq.${{encodeURIComponent(houseCode)}}&is_approved=eq.true&select=*`
          );
          if (Array.isArray(rows) && rows.length > 0) {{
            // Permanently purge any dummy rows found in Supabase
            const dummyRows = rows.filter(isDummyCand);
            if (dummyRows.length > 0) {{
              dummyRows.forEach((dr) => {{
                sbRest("DELETE", `/rest/v1/candidates?id=eq.${{encodeURIComponent(dr.id)}}`).catch(() => {{}});
                if (dr.full_name) {{
                  sbRest("DELETE", `/rest/v1/candidates?full_name=eq.${{encodeURIComponent(dr.full_name)}}`).catch(() => {{}});
                }}
              }});
            }}

            // Valid candidates only
            const validRows = rows.filter((c) => !isDummyCand(c));
            if (validRows.length > 0) {{
              return validRows.map((c) => {{
                const loc = localMap.get(c.id) || {{}};
                return {{
                  id: c.id,
                  admissionNo: c.admission_no || loc.admissionNo,
                  fullName: c.full_name || loc.fullName,
                  className: c.class_name || loc.className,
                  section: c.section || loc.section,
                  houseCode: c.house_code || loc.houseCode,
                  positionId: c.position_id || loc.positionId || "CAPTAIN_BOY",
                  positionName: c.position_name || loc.positionName || "Boys Captain",
                  tagline: c.tagline || loc.tagline || "",
                  symbolObj: loc.symbolObj || (c.symbol_name ? {{ name: c.symbol_name, icon: c.symbol_icon, image: `../assets/symbols/${{(c.symbol_name||'star').toLowerCase().replace(/[\\s-]+/g, '_')}}.png`, imagePath: `../assets/symbols/${{(c.symbol_name||'star').toLowerCase().replace(/[\\s-]+/g, '_')}}.png` }} : null),
                  photoUrl: loc.photoUrl || c.photo_url || "",
                  photoPath: loc.photoPath || c.photo_url || "",
                  isApproved: c.is_approved !== false,
                }};
              }});
            }}
          }}
        }} catch (_) {{}}
      }}
      return localCands;
    }},'''

# Update bheeshma/supabase-config.js
with open('Houses/bheeshma/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find getHouseCandidates block
start_idx = text.find('async getHouseCandidates(houseCode) {')
end_idx = text.find('async getHouseSnapshot(houseCode) {')

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_get_candidates + '\n\n    ' + text[end_idx:]
    with open('Houses/bheeshma/supabase-config.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated Houses/bheeshma/supabase-config.js successfully!")
else:
    print("Could not find getHouseCandidates boundaries in bheeshma/supabase-config.js")

# Copy to all other houses
for h in ['gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']:
    target = f'Houses/{h}/supabase-config.js'
    shutil.copyfile('Houses/bheeshma/supabase-config.js', target)
    print(f"Copied to {target}")
