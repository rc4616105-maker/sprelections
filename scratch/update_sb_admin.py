with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Check if cancelStudentBallots is already present
if 'cancelStudentBallots' not in text:
    idx = text.find('async cancelBallot(')
    idx_end = text.find('throw new Error(this.backendError || "Supabase is not connected', idx)
    idx_block_end = text.find('},', idx_end) + 2

    new_method = """

    async cancelStudentBallots(admissionNo, reason, actorName) {
      const cleanAdm = String(admissionNo || "").trim();
      if (!cleanAdm) throw new Error("Voter ID is required.");
      const cleanReason = String(reason || "").trim() || "Cancelled by Admin";
      const nowIso = new Date().toISOString();

      if (this.mode === "supabase") {
        const effectiveActor = actorName && !actorName.includes("Principal")
          ? actorName
          : ((typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com");

        const qAdm = encodeURIComponent(cleanAdm);
        const rows = await sbRest("GET", `/rest/v1/ballots?admission_no=eq.${qAdm}&select=*`);
        if (!Array.isArray(rows) || rows.length === 0) {
          throw new Error("No ballots found for this voter.");
        }

        await sbRest(
          "PATCH",
          `/rest/v1/ballots?admission_no=eq.${qAdm}&status=eq.accepted`,
          {
            status: "cancelled",
            cancelled_at: nowIso,
            cancel_reason: cleanReason,
            cancelled_by: effectiveActor,
          },
          "return=representation"
        );

        const voterPatch = {
          final_status: "Cancelled",
          voted_for: "",
          cancelled_at: nowIso,
          updated_at: nowIso,
        };
        await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${qAdm}`, voterPatch).catch(() => {});

        const stu = window.ADMIN_DATA.students.find((s) => s.admissionNo === cleanAdm);
        await sbRest("POST", "/rest/v1/audit_logs", {
          id: `AUD-${Date.now().toString(36).toUpperCase()}`,
          action: "ALL_VOTES_CANCELLED",
          admission_no: cleanAdm,
          student_name: stu?.fullName || cleanAdm,
          reason: cleanReason,
          actor: effectiveActor,
          created_at: nowIso,
        }).catch(() => {});

        if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
        return;
      }

      throw new Error(this.backendError || "Supabase is not connected — connect Supabase first to cancel ballots.");
    },"""

    text = text[:idx_block_end] + new_method + text[idx_block_end:]
    with open('Houses/admin/supabase-config.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added cancelStudentBallots to Houses/admin/supabase-config.js successfully!")
else:
    print("cancelStudentBallots already exists.")
