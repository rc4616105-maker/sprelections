import json
import re

with open('scripts/school_cabinet_contestants_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

reg_json = json.dumps(registry, indent=2)

with open('Houses/central/supabase-config.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert const SCHOOL_CABINET_REGISTRY after DEMO_ACCOUNTS
registry_decl = f"\n  const SCHOOL_CABINET_REGISTRY = {reg_json};\n"
if "const SCHOOL_CABINET_REGISTRY" not in content:
    content = content.replace("  const DEMO_ACCOUNTS = {", registry_decl + "\n  const DEMO_ACCOUNTS = {")

# 2. In verifyStudent, if not localMatch, check SCHOOL_CABINET_REGISTRY fallback
fallback_block = """      if (!localMatch) {
        const cabReg = SCHOOL_CABINET_REGISTRY.find((e) =>
          e.candidateAdm.toUpperCase() === cleanId.toUpperCase() ||
          e.voterId.toUpperCase() === cleanId.toUpperCase()
        );
        if (cabReg) {
          localMatch = {
            admissionNo: cleanId,
            fullName: cabReg.candidateName,
            fatherName: "",
            gender: "Student",
            className: cabReg.classSec.includes("10") ? "10" : "9",
            section: cabReg.classSec,
            houseCode: cabReg.houseCode,
            isActive: true,
            isCabinetContestant: true,
            registeredHouseCode: cabReg.houseCode,
            registeredHouseTitle: cabReg.houseTitle,
            constituency: cabReg.constituency,
            winnerRoleTitle: `Cabinet Contestant · ${cabReg.roleTitle}`,
            winnerHouseName: cabReg.houseTitle,
            classSec: cabReg.classSec
          };
        }
      }
      if (!localMatch) {"""

content = re.sub(r'if \(!localMatch\) \{\s*return \{\s*ok: false,\s*code: "NOT_FOUND"', fallback_block + '\n        return {\n          ok: false,\n          code: "NOT_FOUND"', content, count=1)

# 3. Update isElectedHouseCaptainOrWinner to check SCHOOL_CABINET_REGISTRY first
registry_check = """        // Check 0: Official School Cabinet Contestants Registry
        const vName = voter && voter.fullName ? voter.fullName.trim().toLowerCase() : "";
        const regEntry = SCHOOL_CABINET_REGISTRY.find((entry) => {
          const cAdm = String(entry.candidateAdm || "").trim().toUpperCase();
          const vId = String(entry.voterId || "").trim().toUpperCase();
          const eName = String(entry.candidateName || "").trim().toLowerCase();
          return (
            (cAdm && cAdm === idNorm) ||
            (vId && vId === idNorm) ||
            (vName && eName && (vName === eName || vName.includes(eName) || eName.includes(vName)))
          );
        });

        if (regEntry) {
          return {
            isWinner: true,
            isCabinetContestant: true,
            roleTitle: `Cabinet Contestant · ${regEntry.roleTitle}`,
            houseCode: regEntry.houseCode,
            houseTitle: regEntry.houseTitle,
            houseName: regEntry.houseTitle,
            constituency: regEntry.constituency,
            classSec: regEntry.classSec,
          };
        }
"""

content = re.sub(
    r'// Check 0: School Cabinet Contestants.*?(?=// Check 1: Declared winners list)',
    registry_check + '\n        ',
    content,
    flags=re.DOTALL
)

# 4. Attach registeredHouseCode and registeredHouseTitle to localMatch
attach_fields = """          isElectedCaptain = true;
          localMatch.isElectedWinner = true;
          localMatch.isCabinetContestant = Boolean(winnerCheck.isCabinetContestant);
          localMatch.winnerRoleTitle = winnerCheck.roleTitle;
          localMatch.winnerHouseName = winnerCheck.houseTitle || winnerCheck.houseName;
          localMatch.registeredHouseCode = winnerCheck.houseCode || localMatch.houseCode;
          localMatch.registeredHouseTitle = winnerCheck.houseTitle || `${winnerCheck.houseCode} House`;
          localMatch.constituency = winnerCheck.constituency || "";
          localMatch.classSec = winnerCheck.classSec || `Class ${localMatch.className}-${localMatch.section}`;"""

content = re.sub(
    r'isElectedCaptain = true;\s*localMatch\.isElectedWinner = true;\s*localMatch\.isCabinetContestant = Boolean\(winnerCheck\.isCabinetContestant\);\s*localMatch\.winnerRoleTitle = winnerCheck\.roleTitle;\s*localMatch\.winnerHouseName = winnerCheck\.houseName;',
    attach_fields,
    content
)

with open('Houses/central/supabase-config.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Houses/central/supabase-config.js successfully!")
