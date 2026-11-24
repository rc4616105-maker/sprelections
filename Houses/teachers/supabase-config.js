// Teacher Universal Polling Booth — Pure Static JS Supabase Adapter
// Enables teachers to cast ballots for School Cabinet + All 6 Houses in a single session.
(function () {
  const SB_CFG_KEY = "election_spr_2026_sb_cfg_v1";
  const DEFAULT_SB_URL = "https://rziptxcknaeuorekxwrl.supabase.co";
  const DEFAULT_SB_KEY = "sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ";
  const BUCKET = "voter-photos";
  const ELECTION_ID = "ELECTION_2026";
  const CHANNEL_NAME = "election_spr_2026_sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(CHANNEL_NAME) : null;

  function sbHeaders(key, extra = {}) {
    const h = { apikey: key, ...extra };
    if (String(key || "").startsWith("eyJ") || String(key || "").startsWith("sb_secret_") || String(key || "").startsWith("sb_publishable_")) {
      h.Authorization = `Bearer ${key}`;
    }
    return h;
  }

  async function readBrowserSupabaseConfig() {
    if (DEFAULT_SB_KEY && DEFAULT_SB_KEY.trim() && DEFAULT_SB_KEY !== "paste-your-supabase-key-here") {
      return { url: DEFAULT_SB_URL.replace(/\/+$/, ""), key: DEFAULT_SB_KEY.trim() };
    }

    try {
      const saved = JSON.parse(localStorage.getItem(SB_CFG_KEY) || "null");
      if (saved && (saved.anonKey || saved.secretKey || saved.key)) {
        const k = (saved.anonKey || saved.secretKey || saved.key || "").trim();
        return { url: (saved.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: k };
      }
    } catch (_) { }

    for (const rel of [
      "./supabase.local.json",
      "../supabase.local.json",
      "../../supabase.local.json",
      "/supabase.local.json",
      "/Houses/supabase.local.json",
      "/1supabase/supabase.local.json",
      "../../1supabase/supabase.local.json",
      "../1supabase/supabase.local.json"
    ]) {
      try {
        const res = await fetch(rel, { cache: "no-store" });
        if (!res.ok) continue;
        const parsed = await res.json();
        const k = String(parsed.anonKey || parsed.key || "").trim();
        if (k && k !== "paste-your-supabase-key-here") {
          return { url: String(parsed.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: k };
        }
      } catch (_) { }
    }
    return { url: DEFAULT_SB_URL, key: "" };
  }

  const runtime = {
    transport: "offline",
    url: DEFAULT_SB_URL,
    key: "",
  };

  async function sbRest(method, path, body = null, prefer = "") {
    if (runtime.transport === "netlify") {
      const res = await fetch("/.netlify/functions/supabase?action=rest", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method, path, jsonBody: body, prefer }),
      });
      const txt = await res.text();
      let parsed = {};
      try {
        parsed = txt ? JSON.parse(txt) : {};
      } catch (_) { }
      if (!res.ok) throw new Error(parsed.message || parsed.error || `Supabase HTTP ${res.status}`);
      return parsed;
    }

    const headers = sbHeaders(runtime.key);
    if (body !== null) headers["Content-Type"] = "application/json";
    if (prefer) headers.Prefer = prefer;
    const res = await fetch(`${runtime.url}${path}`, {
      method,
      cache: "no-store",
      headers,
      body: body !== null ? JSON.stringify(body) : undefined,
    });
    const txt = await res.text();
    let parsed = {};
    try {
      parsed = txt ? JSON.parse(txt) : {};
    } catch (_) { }
    if (!res.ok) {
      throw new Error(parsed.message || parsed.error || parsed.hint || `Supabase HTTP ${res.status}`);
    }
    return parsed;
  }

  async function uploadPhotoToStorage(relPath, base64Jpg) {
    if (!base64Jpg || !base64Jpg.startsWith("data:")) return "";
    try {
      if (runtime.transport === "netlify") {
        const res = await fetch("/.netlify/functions/supabase?action=upload", {
          method: "POST",
          cache: "no-store",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path: relPath, base64Data: base64Jpg }),
        });
        if (res.ok) return relPath;
      }

      const base64Data = base64Jpg.split(",")[1];
      const binStr = atob(base64Data);
      const len = binStr.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binStr.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "image/jpeg" });
      const res = await fetch(`${runtime.url}/storage/v1/object/${BUCKET}/${relPath}`, {
        method: "POST",
        cache: "no-store",
        headers: sbHeaders(runtime.key, {
          "Content-Type": "image/jpeg",
          "x-upsert": "true",
        }),
        body: blob,
      });
      if (!res.ok) {
        console.warn("Storage upload warn:", res.status);
      }
    } catch (e) {
      console.warn("Storage upload exception:", e);
    }
    return relPath;
  }

  window.TeacherBackend = {
    mode: "offline",
    backendError: null,
    _initPromise: null,

    async init() {
      if (this._initPromise) return this._initPromise;
      this._initPromise = (async () => {
        if (window.location.protocol === "file:") {
          this.mode = "offline";
          this.backendError = "Serve over http://127.0.0.1:5500 to connect Supabase.";
          return "offline";
        }

        // 1. Check Netlify function proxy first if deployed
        try {
          const ctl = new AbortController();
          const tid = setTimeout(() => ctl.abort(), 1400);
          const res = await fetch("/.netlify/functions/supabase?action=health", { cache: "no-store", signal: ctl.signal });
          clearTimeout(tid);
          if (res.ok) {
            const h = await res.json();
            if (h.backend === "supabase") {
              runtime.transport = "netlify";
              this.mode = "supabase";
              this.backendError = null;
              return "supabase";
            }
          }
        } catch (_) { }

        // 2. Read browser / local config
        const cfg = await readBrowserSupabaseConfig();
        if (cfg.key) {
          if (cfg.key.startsWith("sbp_")) {
            this.backendError = "Blocked sbp_ account token; use Publishable key from Project Settings -> API Keys.";
          } else {
            try {
              const res = await fetch(`${cfg.url}/rest/v1/voters?select=admission_no&limit=1`, {
                cache: "no-store",
                headers: sbHeaders(cfg.key),
              });
              if (res.ok) {
                runtime.transport = "direct";
                runtime.url = cfg.url;
                runtime.key = cfg.key;
                this.mode = "supabase";
                this.backendError = null;
                return "supabase";
              }
              const err = await res.json().catch(() => ({}));
              this.backendError = `Supabase Error (${err.message || res.status})`;
            } catch (err) {
              this.backendError = err?.message || "Cannot reach Supabase";
            }
          }
        } else {
          this.backendError = "Supabase Publishable anon key not found.";
        }

        runtime.transport = "offline";
        this.mode = "offline";
        return "offline";
      })();
      return this._initPromise;
    },

    async verifyTeacher(inputTeacherId) {
      let cleanId = String(inputTeacherId || "").trim().toUpperCase();
      if (cleanId === "SPRENG203") cleanId = "SPRPRE203";
      if (!cleanId) {
        return { ok: false, code: "EMPTY_ID", message: "Please scan or enter your Teacher Voter ID." };
      }

      await this.init();

      const allTeachers = window.TEACHER_BOOTH_DATA?.teachers || [];
      let teacher = allTeachers.find((t) => String(t.admissionNo).trim().toUpperCase() === cleanId);

        // Support universal test accounts
        if ((cleanId === "0000" || cleanId === "6000" || cleanId === "SPRFAC100") && !teacher) {
          teacher = {
            admissionNo: cleanId,
            fullName: "Dr. Rajesh Sharma",
            subject: "Senior Faculty",
            className: "Staff",
            section: "Faculty",
            houseCode: "ALL",
            houseName: "All Houses & Cabinet",
            isStaff: true,
            isActive: true,
            photoUrl: "../assets/candidates/teacher_demo.jpg",
          };
        }

        // If not in local cache, query Supabase voters table directly!
        if (!teacher && this.mode === "supabase") {
          try {
            const qAdm = encodeURIComponent(cleanId);
            const vRows = await sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`);
            if (Array.isArray(vRows) && vRows.length > 0) {
              const r = vRows[0];
              if (r.house_code === "ALL" || r.class_name === "Staff" || String(r.admission_no).toUpperCase().startsWith("SPR")) {
                teacher = {
                  admissionNo: r.admission_no,
                  fullName: r.full_name,
                  subject: r.section || "Faculty",
                  className: "Staff",
                  section: r.section || "Faculty",
                  houseCode: "ALL",
                  houseName: "All Houses & Cabinet",
                  isStaff: true,
                  isActive: true,
                  photoUrl: "../assets/candidates/teacher_demo.jpg"
                };
              }
            }
          } catch (_) { }
        }

        if (!teacher) {
          return {
            ok: false,
            code: "NOT_A_TEACHER",
            message: `ID "${cleanId}" is not recognized as a registered Teacher or Faculty member. Please use your Teacher Voter Card.`,
          };
        }

        // If connected to Supabase, query both voters and ballots for this teacher
        const votedRolesMap = {};
        if (this.mode === "supabase") {
          try {
            const qAdm = encodeURIComponent(cleanId);
            const [vRows, ballots] = await Promise.all([
              sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`),
              sbRest("GET", `/rest/v1/ballots?admission_no=eq.${qAdm}&select=id,position_id,position_name,candidate_id,candidate_name,status,house_code,cast_at`),
            ]);

            const hasAcceptedBallots = Array.isArray(ballots) && ballots.some((b) => b.status === "accepted");
            const hasCancelledBallots = Array.isArray(ballots) && ballots.some((b) => b.status === "cancelled");
            const isVoterMarkedVoted = Array.isArray(vRows) && vRows.length > 0 && vRows[0].final_status === "Voted";

            // Strict Double-Voting Block for Teacher Universal Polling Booth:
            if ((isVoterMarkedVoted || hasAcceptedBallots) && !hasCancelledBallots) {
              return {
                ok: false,
                code: "ALREADY_VOTED",
                title: "Already Voted",
                message: `Teacher ${teacher.fullName} (ID ${teacher.admissionNo}) has already cast their universal ballot in this election. Duplicate voting is strictly blocked.`,
              };
            }

            if (Array.isArray(ballots)) {
              ballots.forEach((b) => {
                if (b.status === "accepted") {
                  const rk = `${b.house_code}_${b.position_id}`;
                  votedRolesMap[rk] = {
                    id: b.id,
                    houseCode: b.house_code,
                    positionId: b.position_id,
                    candidateId: b.candidate_id,
                    candidateName: b.candidate_name,
                    castAt: b.cast_at,
                  };
                }
              });
            }
          } catch (e) {
            console.warn("Could not check prior teacher ballots:", e);
          }
        }

        // Calculate total available roles across all houses
        const allHouses = window.TEACHER_BOOTH_DATA?.houses || [];
        const totalRoles = allHouses.reduce((sum, h) => sum + (h.positions?.length || 0), 0);
        const votedCount = Object.keys(votedRolesMap).length;

        // Allow 0000 and 6000 demo testing to re-vote freely
        if (cleanId !== "0000" && cleanId !== "6000" && votedCount >= totalRoles && totalRoles > 0) {
          return {
            ok: false,
            code: "ALREADY_VOTED",
            message: `Teacher ${teacher.fullName} (ID ${teacher.admissionNo}) has already cast all ${totalRoles} ballots across School Cabinet and all 6 Houses.`,
          };
        }

        return {
          ok: true,
          teacher,
          votedRolesMap,
          votedCount,
          totalRoles,
        };
      },

    async castUniversalBallot({ teacher, selections, photoDataUrl, boothName }) {
        const finalBooth = String(
          boothName ||
          (typeof window.getRegisteredBooth === "function" && window.getRegisteredBooth()) ||
          sessionStorage.getItem("election_booth_name") ||
          localStorage.getItem("last_registered_booth") ||
          "Teacher Station"
        ).trim();

        const nowIso = new Date().toISOString();
        const cleanAdm = String(teacher.admissionNo || "").trim();

        if (!Array.isArray(selections) || selections.length === 0) {
          throw new Error("No candidate selections provided.");
        }

        if (this.mode === "supabase") {
          // 1. Upload verification snapshot to storage
          let photoRelPath = "";
          if (photoDataUrl && photoDataUrl.startsWith("data:")) {
            try {
              const timeSlug = Date.now();
              photoRelPath = `teachers/${cleanAdm}/${timeSlug}.jpg`;
              await uploadPhotoToStorage(photoRelPath, photoDataUrl);
            } catch (e) {
              console.warn("Storage upload warning:", e);
            }
          }

          // 2. Build ballot records for each selected position with guaranteed unique IDs across houses
          const ballotDocs = selections.map((sel) => ({
            id: `BLT-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}-${cleanAdm}-${sel.houseCode}-${sel.positionId}`,
            election_id: ELECTION_ID,
            admission_no: cleanAdm,
            house_code: sel.houseCode,
            position_id: sel.positionId,
            position_name: sel.positionName,
            candidate_id: sel.candidate.id,
            candidate_name: sel.candidate.fullName,
            photo_path: photoRelPath,
            photo_field: "photo_path",
            status: "accepted",
            booth_name: finalBooth,
            cast_at: nowIso,
          }));

          // Batch insert ballots with fallback if table schema differs (e.g. booth_name column)
          try {
            await sbRest("POST", "/rest/v1/ballots", ballotDocs);
          } catch (ballotErr) {
            const errMsg = String(ballotErr?.message || "");
            if (errMsg.includes("booth_name")) {
              const strippedBallots = ballotDocs.map(({ booth_name, ...rest }) => rest);
              await sbRest("POST", "/rest/v1/ballots", strippedBallots);
            } else if (errMsg.includes("ballots_one_accepted_per_voter_role_idx")) {
              throw new Error(`Duplicate vote blocked: Faculty ${cleanAdm} already has accepted ballots.`);
            } else {
              console.error("Ballot insert error:", ballotErr);
              throw ballotErr;
            }
          }

          // 3. Upsert / update teacher voter record to Voted
          const qAdm = encodeURIComponent(cleanAdm);
          try {
            const existingRows = await sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`);
            if (!existingRows || existingRows.length === 0) {
              await sbRest("POST", "/rest/v1/voters", {
                admission_no: cleanAdm,
                full_name: teacher.fullName,
                class_name: teacher.className || "Staff",
                section: teacher.section || "Faculty",
                house_code: "ALL",
                house_name: "All Houses & Cabinet",
                final_status: "Voted",
                voted_for: `${ballotDocs.length} Roles Cast`,
                position_name: "Universal Teacher Ballot",
                cast_at: nowIso,
                photo_path: photoRelPath,
                is_active: true,
                updated_at: nowIso,
              }).catch((postErr) => {
                console.warn("Voter insert note:", postErr);
              });
            } else {
              await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${qAdm}`, {
                final_status: "Voted",
                voted_for: `${ballotDocs.length} Roles Cast`,
                cast_at: nowIso,
                photo_path: photoRelPath || existingRows[0].photo_path,
                updated_at: nowIso,
              }).catch((patchErr) => {
                console.warn("Voter patch note:", patchErr);
              });
            }
          } catch (vErr) {
            console.warn("Voter status update note:", vErr);
          }

          // 4. Log non-repudiable audit entry
          try {
            await sbRest("POST", "/rest/v1/audit_logs", {
              id: `AUD-${Date.now().toString(36).toUpperCase()}`,
              action: "TEACHER_UNIVERSAL_BALLOT_CAST",
              admission_no: cleanAdm,
              student_name: teacher.fullName,
              house_code: "ALL",
              reason: `Cast ${ballotDocs.length} ballots across School Cabinet and all student houses`,
              actor: finalBooth,
              created_at: nowIso,
            });
          } catch (_) { }

          // 5. Broadcast to cross-tab synchronizer
          if (channel) {
            channel.postMessage({ type: "store_updated", at: Date.now() });
          }

          return {
            ok: true,
            count: ballotDocs.length,
            teacherName: teacher.fullName,
            castAt: nowIso,
          };
        }

        // Offline mock fallback
        return {
          ok: true,
          count: selections.length,
          teacherName: teacher.fullName,
          castAt: nowIso,
        };
      },
    };

    // Re-evaluate backend if Supabase credentials updated in another tab
    window.addEventListener("storage", (e) => {
      if (e.key === SB_CFG_KEY) {
        if (window.TeacherBackend) {
          window.TeacherBackend._initPromise = null;
          window.TeacherBackend.init();
        }
      }
    });
  }) ();

