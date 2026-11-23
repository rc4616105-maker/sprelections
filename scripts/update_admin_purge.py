with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'await sbRest("POST", "/rest/v1/candidates", candRows, "resolution=merge-duplicates");'

replacement = '''// Purge dummy candidates from Supabase
      const dummyCandidatesSet = [
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
      ];
      for (const dName of dummyCandidatesSet) {
        sbRest("DELETE", `/rest/v1/candidates?full_name=eq.${encodeURIComponent(dName)}`).catch(() => {});
      }
      sbRest("DELETE", `/rest/v1/candidates?section=like.*Option*`).catch(() => {});
      sbRest("DELETE", `/rest/v1/candidates?tagline=like.*Option*`).catch(() => {});
      
      const cleanCandRows = candRows.filter(c => !dummyCandidatesSet.includes(c.full_name) && !(c.section || "").includes("Option "));
      await sbRest("POST", "/rest/v1/candidates", cleanCandRows, "resolution=merge-duplicates");'''

if target in text:
    text = text.replace(target, replacement)
    with open('Houses/admin/supabase-config.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated Houses/admin/supabase-config.js!")
else:
    print("Target not found in Houses/admin/supabase-config.js")
