// Admin Console — Pure Static JS Supabase Adapter (Direct REST + Private Storage or Netlify Functions Proxy)
// Zero keys live in tracked code: reads Netlify Env Proxy (when deployed), gitignored supabase.local.json, or Admin setup modal.
(function () {
  const SB_CFG_KEY = "election_spr_2026_sb_cfg_v1";
  const DEFAULT_SB_URL = "https://rziptxcknaeuorekxwrl.supabase.co";
  const BUCKET = "voter-photos";
  const ELECTION_ID = window.ADMIN_DATA?.electionId || "spring-2026";
  const POSITION_ID = window.ADMIN_DATA?.positionId || "house_captain";
  const CHANNEL_NAME = "election_spr_2026_sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(CHANNEL_NAME) : null;

  try {
    localStorage.removeItem("election_spr_2026_store_v1");
    localStorage.removeItem("election_spr_2026_store_v2");
    localStorage.removeItem("election_spr_2026_store_v3");
    localStorage.removeItem("election_spr_2026_store_v4");
    localStorage.removeItem("election_spr_2026_store_v5");
  } catch (_) { }

  function sbHeaders(key, extra = {}) {
    const h = { apikey: key, ...extra };
    if (String(key || "").startsWith("eyJ")) {
      h.Authorization = `Bearer ${key}`;
    }
    return h;
  }

  async function readBrowserSupabaseConfig() {
    // 1. Browser saved config (e.g., entered in Admin Connect modal)
    try {
      const saved = JSON.parse(localStorage.getItem(SB_CFG_KEY) || "null");
      if (saved && saved.anonKey) {
        return { url: (saved.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: saved.anonKey.trim() };
      }
    } catch (_) { }

    // 2. Gitignored local file supabase.local.json (works on Live Server without exposing keys in git)
    for (const rel of ["./supabase.local.json", "../supabase.local.json", "../../supabase.local.json"]) {
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
    transport: "offline", // "netlify" | "direct" | "offline"
    url: DEFAULT_SB_URL,
    key: "",
    signedCache: new Map(),
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

  async function sbFetchAll(tableQuery) {
    const rows = [];
    let offset = 0;
    const limit = 1000;
    const sep = tableQuery.includes("?") ? "&" : "?";
    while (true) {
      const batch = await sbRest("GET", `/rest/v1/${tableQuery}${sep}limit=${limit}&offset=${offset}`);
      if (!Array.isArray(batch)) break;
      rows.push(...batch);
      if (batch.length < limit) break;
      offset += limit;
    }
    return rows;
  }

  async function resolveSignedPhotoUrl(photoPath) {
    const cleanPath = String(photoPath || "").trim();
    if (!cleanPath) return "";
    if (cleanPath.startsWith("data:") || cleanPath.startsWith("http")) return cleanPath;
    if (runtime.transport === "netlify") {
      return `/.netlify/functions/supabase?action=photo&path=${encodeURIComponent(cleanPath)}`;
    }
    const cached = runtime.signedCache.get(cleanPath);
    if (cached && cached.exp > Date.now()) {
      return cached.url;
    }
    try {
      const res = await fetch(`${runtime.url}/storage/v1/object/sign/${BUCKET}/${cleanPath}`, {
        method: "POST",
        headers: sbHeaders(runtime.key, { "Content-Type": "application/json" }),
        body: JSON.stringify({ expiresIn: 3600 }),
      });
      if (!res.ok) return "";
      const data = await res.json();
      const rawSigned = data.signedURL || data.signedUrl || "";
      if (!rawSigned) return "";
      const fullUrl = rawSigned.startsWith("http")
        ? rawSigned
        : `${runtime.url}/storage/v1${rawSigned.startsWith("/") ? "" : "/"}${rawSigned}`;
      runtime.signedCache.set(cleanPath, { url: fullUrl, exp: Date.now() + 3000 * 1000 });
      return fullUrl;
    } catch (_) {
      return "";
    }
  }

  async function deletePhotoFromStorage(relPath) {
    const cleanPath = String(relPath || "").trim();
    if (!cleanPath) return;
    runtime.signedCache.delete(cleanPath);
    try {
      if (runtime.transport === "netlify") {
        await fetch("/.netlify/functions/supabase?action=deletePhoto", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ relPath: cleanPath }),
        });
        return;
      }
      await fetch(`${runtime.url}/storage/v1/object/${BUCKET}/${cleanPath}`, {
        method: "DELETE",
        headers: sbHeaders(runtime.key),
      });
    } catch (_) { }
  }

  window.AdminBackend = {
    mode: "offline",
    backendError: null,
    _pollTimer: null,

    getDefaultUrl() {
      return DEFAULT_SB_URL;
    },

    hasStoredBrowserKey() {
      try {
        const s = JSON.parse(localStorage.getItem(SB_CFG_KEY) || "null");
        return Boolean(s && s.anonKey);
      } catch (_) {
        return false;
      }
    },

    async configureBrowserKey(urlInput, keyInput) {
      const url = String(urlInput || DEFAULT_SB_URL).trim().replace(/\/+$/, "");
      const key = String(keyInput || "").trim();
      if (!key) throw new Error("Paste your Supabase Publishable / anon key.");
      if (key.startsWith("sbp_")) {
        throw new Error(
          "An sbp_... token is your Supabase Account Personal Access Token, not a Project API key. In Supabase -> Project Settings -> API Keys, copy the Publishable key (sb_publishable_... or legacy anon eyJ...)."
        );
      }
      if (key.startsWith("sb_secret_")) {
        throw new Error(
          "Do NOT use an sb_secret_ key in browser JavaScript! Copy your Publishable (sb_publishable_... or anon) key from Supabase -> Project Settings -> API, OR set SUPABASE_KEY in Netlify Environment Variables."
        );
      }
      const res = await fetch(`${url}/rest/v1/voters?select=admission_no&limit=1`, {
        cache: "no-store",
        headers: sbHeaders(key),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(
          err.message ||
          `Supabase rejected key or schema (${res.status}). Make sure you ran supabase/schema.sql in Supabase SQL Editor.`
        );
      }
      localStorage.setItem(SB_CFG_KEY, JSON.stringify({ url, anonKey: key }));
      runtime.transport = "direct";
      runtime.url = url;
      runtime.key = key;
      this.mode = "supabase";
      this.backendError = null;
      return "supabase";
    },

    clearBrowserKey() {
      localStorage.removeItem(SB_CFG_KEY);
      runtime.transport = "offline";
      this.mode = "offline";
    },

    getKey() {
      return runtime.key || "";
    },

    async init() {
      if (window.location.protocol === "file:") {
        runtime.transport = "offline";
        this.mode = "offline";
        this.backendError = "Serve over http://127.0.0.1:5500 or Netlify to connect Supabase.";
        return "offline";
      }

      // 1. Try hidden-key Netlify Function first (only when hosted on Netlify, skip on localhost to avoid 1.4s 404 delay)
      const isLocalhost = typeof window !== "undefined" && (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost");
      if (!isLocalhost) {
        try {
          const ctl = new AbortController();
          const tid = setTimeout(() => ctl.abort(), 800);
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
            if (h.configured && h.error) {
              this.backendError = `Run supabase/schema.sql in Supabase SQL Editor (${h.error})`;
            }
          }
        } catch (_) { }
      }

      // 2. Direct browser client using gitignored supabase.local.json or saved Publishable key
      const cfg = await readBrowserSupabaseConfig();
      if (cfg.key) {
        if (cfg.key.startsWith("sbp_")) {
          this.backendError =
            "Blocked sbp_ account token! Copy the project's Publishable key (sb_publishable_... or anon eyJ...) from Project Settings -> API Keys.";
        } else if (cfg.key.startsWith("sb_secret_")) {
          this.backendError =
            "Blocked sb_secret_ key in browser! Use Publishable (anon / sb_publishable_) key in supabase.local.json or Netlify Env Vars.";
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
            this.backendError = `Run supabase/schema.sql in Supabase SQL Editor (${err.message || res.status})`;
          } catch (err) {
            this.backendError = err?.message || "Cannot reach Supabase";
          }
        }
      } else {
        this.backendError = "Add your Supabase Publishable/anon key to connect.";
      }

      runtime.transport = "offline";
      this.mode = "offline";
      return "offline";
    },

    async getSnapshot() {
      if (this.mode === "supabase") {
        const [voterRows, ballotRows, candRows, auditRows] = await Promise.all([
          sbFetchAll("voters?select=*"),
          sbFetchAll("ballots?select=*&order=cast_at.desc"),
          sbFetchAll("candidates?select=*"),
          sbFetchAll("audit_logs?select=*&order=created_at.desc").catch(() => []),
        ]);

        const byAdm = new Map(window.ADMIN_DATA.students.map((s) => [s.admissionNo, { ...s }]));
        (window.ADMIN_DATA.teachers || window.TEACHERS_DATA || []).forEach((t) => {
          if (!byAdm.has(t.admissionNo)) {
            byAdm.set(t.admissionNo, { ...t });
          } else {
            const ex = byAdm.get(t.admissionNo);
            ex.isStaff = true;
            if (!ex.subject && t.subject) ex.subject = t.subject;
            ex.houseCode = "ALL";
          }
        });
        const voterByAdm = new Map();
        voterRows.forEach((v) => {
          voterByAdm.set(v.admission_no, v);
          if (!byAdm.has(v.admission_no)) {
            const isStaff = v.class_name === "Staff" || v.section === "Faculty" || v.house_code === "ALL";
            byAdm.set(v.admission_no, {
              admissionNo: v.admission_no,
              fullName: v.full_name || v.admission_no,
              className: v.class_name || (isStaff ? "Staff" : ""),
              section: v.section || (isStaff ? "Faculty" : ""),
              subject: isStaff ? (v.class_name || "Faculty") : "",
              houseCode: v.house_code || (isStaff ? "ALL" : ""),
              isStaff,
              isActive: v.is_active !== false,
              isCandidate: false,
              positionName: null,
            });
          } else {
            const ex = byAdm.get(v.admission_no);
            if (v.class_name === "Staff" || v.section === "Faculty" || v.house_code === "ALL") {
              ex.isStaff = true;
              ex.houseCode = "ALL";
            }
          }
        });

        const positions = window.ADMIN_DATA.positions || [{ id: POSITION_ID, code: "Vote_10_Boy", title: "House Captain" }];
        const voterStatus = {};

        // Initialize any overall status from voters first, then derive authoritative per-role status from ballots
        const ballotsByRole = new Map();
        ballotRows.forEach((b) => {
          const posId = b.position_id || POSITION_ID;
          const rk = `${ELECTION_ID}_${b.admission_no}_${posId}`;
          if (!ballotsByRole.has(rk)) ballotsByRole.set(rk, []);
          ballotsByRole.get(rk).push(b);
        });

        ballotsByRole.forEach((rows, rk) => {
          const accepted = rows.find((b) => b.status === "accepted");
          const latest = accepted || rows[0];
          voterStatus[rk] = {
            electionId: ELECTION_ID,
            admissionNo: latest.admission_no,
            houseCode: latest.house_code,
            positionId: latest.position_id || POSITION_ID,
            status: accepted ? "voted" : "cancelled",
            activeBallotId: accepted ? accepted.id : null,
            updatedAt: accepted ? accepted.cast_at : latest.cancelled_at,
          };
        });

        const posTitleById = Object.fromEntries(positions.map((p) => [p.id, `${p.title} (${p.subtitle})`]));
        const ballots = ballotRows.map((b) => {
          const stu = byAdm.get(b.admission_no) || voterByAdm.get(b.admission_no) || {};
          const posId = b.position_id || POSITION_ID;
          const cachedPhotoUrl = b.photo_path ? (runtime.signedCache.get(b.photo_path)?.url || "") : "";
          return {
            id: b.id,
            electionId: b.election_id || ELECTION_ID,
            admissionNo: b.admission_no,
            fullName: stu.fullName || stu.full_name || b.admission_no,
            className: stu.className || stu.class_name || "",
            section: stu.section || "",
            houseCode: b.house_code,
            positionId: posId,
            positionName: b.position_name || posTitleById[posId] || "House Captain",
            candidateId: b.candidate_id,
            candidateName: b.candidate_name,
            photoField: b.photo_field || "",
            photoPath: b.photo_path || "",
            photoDataUrl: cachedPhotoUrl,
            status: b.status,
            boothName: b.booth_name || "Booth 1",
            castAt: b.cast_at,
            cancelledAt: b.cancelled_at,
            cancelReason: b.cancel_reason,
            cancelledBy: b.cancelled_by,
          };
        });

        // Resolve uncached photos asynchronously in background so table renders instantly without waiting
        const uncachedPaths = Array.from(new Set(ballotRows.map((b) => b.photo_path).filter((p) => p && !runtime.signedCache.has(p))));
        if (uncachedPaths.length > 0) {
          Promise.all(uncachedPaths.map((p) => resolveSignedPhotoUrl(p))).then(() => {
            ballots.forEach((b) => {
              if (b.photoPath && !b.photoDataUrl) {
                b.photoDataUrl = runtime.signedCache.get(b.photoPath)?.url || "";
              }
            });
          }).catch(() => {});
        }

        const baseCandidates = window.ADMIN_DATA.candidates || [];
        const candDbById = new Map((candRows || []).map((c) => [c.id, c]));
        const candDbByName = new Map((candRows || []).map((c) => [`${c.house_code}_${c.full_name}`.toLowerCase(), c]));
        const seenCandIds = new Set();
        const candidates = baseCandidates.map((c) => {
          seenCandIds.add(c.id);
          const db = candDbById.get(c.id) || candDbByName.get(`${c.houseCode}_${c.fullName}`.toLowerCase());
          if (!db) return { ...c };
          return {
            id: c.id,
            admissionNo: db.admission_no || c.admissionNo,
            fullName: db.full_name || c.fullName,
            className: db.class_name || c.className,
            section: db.section || c.section,
            houseCode: db.house_code || c.houseCode,
            positionId: db.position_id || c.positionId,
            positionName: db.position_name || c.positionName,
            tagline: db.tagline || c.tagline || "",
            isApproved: db.is_approved !== false,
          };
        });

        (candRows || []).forEach((db) => {
          if (!seenCandIds.has(db.id) && !seenCandIds.has(`${db.house_code}_${db.full_name}`.toLowerCase())) {
            seenCandIds.add(db.id);
            candidates.push({
              id: db.id,
              admissionNo: db.admission_no || "",
              fullName: db.full_name,
              className: db.class_name || "",
              section: db.section || "",
              houseCode: db.house_code,
              positionId: db.position_id,
              positionName: db.position_name,
              tagline: db.tagline || "",
              isApproved: db.is_approved !== false,
            });
          }
        });

        try {
          localStorage.setItem(
            "spr_admin_snapshot_cache",
            JSON.stringify({
              ballots,
              voterStatus,
              timestamp: Date.now(),
            })
          );
        } catch (_) {}

        return {
          students: Array.from(byAdm.values()),
          candidates,
          voterStatus,
          ballots,
          auditLogs: auditRows.map((a) => ({
            id: a.id,
            action: a.action,
            ballotId: a.ballot_id,
            admissionNo: a.admission_no,
            studentName: a.student_name,
            houseCode: a.house_code,
            reason: a.reason,
            actor: a.actor,
            createdAt: a.created_at,
          })),
        };
      }
      const baseRoster = [
        ...(window.ADMIN_DATA?.students || []),
        ...(window.ADMIN_DATA?.teachers || window.TEACHERS_DATA || []),
      ];
      const seenAdms = new Set();
      const initialStudents = [];
      baseRoster.forEach((s) => {
        if (!seenAdms.has(s.admissionNo)) {
          seenAdms.add(s.admissionNo);
          initialStudents.push({ ...s });
        }
      });
      return {
        students: initialStudents,
        candidates: window.ADMIN_DATA?.candidates || [],
        voterStatus: {},
        ballots: [],
        auditLogs: [],
      };
    },

    async cancelBallot(ballotId, reason, actorName) {
      const cleanReason = String(reason || "").trim() || "Cancelled by Admin";
      const nowIso = new Date().toISOString();

      if (this.mode === "supabase") {
        const rows = await sbRest("GET", `/rest/v1/ballots?id=eq.${encodeURIComponent(ballotId)}&select=*`);
        if (!Array.isArray(rows) || rows.length === 0) {
          throw new Error("Ballot not found in Supabase.");
        }
        const b = rows[0];
        if (b.status === "cancelled") {
          throw new Error("This ballot has already been cancelled.");
        }

        const effectiveActor = actorName && !actorName.includes("Principal")
          ? actorName
          : ((typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com");

        await sbRest(
          "PATCH",
          `/rest/v1/ballots?id=eq.${encodeURIComponent(ballotId)}&status=eq.accepted`,
          {
            status: "cancelled",
            cancelled_at: nowIso,
            cancel_reason: cleanReason,
            cancelled_by: effectiveActor,
          },
          "return=representation"
        );

        const roleColMap = {
          CAPTAIN_BOY: "vote_10_boy",
          CAPTAIN_GIRL: "vote_10_girl",
          VICE_CAPTAIN_BOY: "vote_9_boy",
          VICE_CAPTAIN_GIRL: "vote_9_girl",
        };
        const roleCol = roleColMap[b.position_id || ""];
        const voterPatch = {
          final_status: "Cancelled",
          voted_for: "",
          cancelled_at: nowIso,
          updated_at: nowIso,
        };
        if (roleCol) voterPatch[roleCol] = "";
        await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${encodeURIComponent(b.admission_no)}`, voterPatch);

        const stu = window.ADMIN_DATA.students.find((s) => s.admissionNo === b.admission_no);
        await sbRest("POST", "/rest/v1/audit_logs", {
          id: `AUD-${Date.now().toString(36).toUpperCase()}`,
          action: "VOTE_CANCELLED",
          ballot_id: ballotId,
          admission_no: b.admission_no,
          student_name: stu?.fullName || b.admission_no,
          house_code: b.house_code,
          reason: cleanReason,
          actor: effectiveActor,
          created_at: nowIso,
        });
        if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
        return;
      }

      throw new Error(this.backendError || "Supabase is not connected — connect Supabase first to cancel ballots.");
    },

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
    },

    async updateBallotChoice(ballotId, newCandidateId, newCandidateName, actorName) {
      if (this.mode !== "supabase") {
        throw new Error(this.backendError || "Supabase is not connected — connect Supabase first to edit ballots.");
      }
      const cleanId = String(ballotId || "").trim();
      const cleanCandId = String(newCandidateId || "").trim();
      const cleanCandName = String(newCandidateName || "").trim();
      if (!cleanId || !cleanCandName) {
        throw new Error("Ballot ID and Candidate Name are required to update vote choice.");
      }
      const nowIso = new Date().toISOString();

      const rows = await sbRest("GET", `/rest/v1/ballots?id=eq.${encodeURIComponent(cleanId)}&select=*`);
      if (!Array.isArray(rows) || rows.length === 0) {
        throw new Error("Ballot not found in Supabase.");
      }
      const b = rows[0];
      const oldCand = b.candidate_name || "Unknown";

      await sbRest(
        "PATCH",
        `/rest/v1/ballots?id=eq.${encodeURIComponent(cleanId)}`,
        {
          candidate_id: cleanCandId,
          candidate_name: cleanCandName,
        },
        "return=representation"
      );

      const roleColMap = {
        CAPTAIN_BOY: "vote_10_boy",
        CAPTAIN_GIRL: "vote_10_girl",
        VICE_CAPTAIN_BOY: "vote_9_boy",
        VICE_CAPTAIN_GIRL: "vote_9_girl",
      };
      const roleCol = roleColMap[b.position_id || ""];
      const voterPatch = { updated_at: nowIso };
      if (roleCol) voterPatch[roleCol] = cleanCandName;
      voterPatch.voted_for = cleanCandName;

      try {
        await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${encodeURIComponent(b.admission_no)}`, voterPatch);
      } catch (_) {}

      await sbRest("POST", "/rest/v1/audit_logs", {
        id: `AUD-${Date.now().toString(36).toUpperCase()}`,
        action: "VOTE_EDITED",
        ballot_id: cleanId,
        admission_no: b.admission_no,
        student_name: b.admission_no,
        house_code: b.house_code,
        reason: `Changed choice from "${oldCand}" to "${cleanCandName}"`,
        actor: actorName || "Principal / Admin",
        created_at: nowIso,
      });

      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
    },

    async clearStudentBallots(admissionNo, actorName) {
      if (this.mode !== "supabase") {
        throw new Error(this.backendError || "Supabase is not connected — connect Supabase first to delete ballots.");
      }
      const cleanAdm = String(admissionNo || "").trim();
      if (!cleanAdm) throw new Error("Voter ID is required.");

      const qAdm = encodeURIComponent(cleanAdm);
      const nowIso = new Date().toISOString();

      const [voterRows, priorBallots] = await Promise.all([
        sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`),
        sbRest("GET", `/rest/v1/ballots?admission_no=eq.${qAdm}&select=id,house_code,photo_path,status`),
      ]);
      const voterRow = Array.isArray(voterRows) && voterRows.length > 0 ? voterRows[0] : null;
      const ballotsList = Array.isArray(priorBallots) ? priorBallots : [];

      if (ballotsList.length > 0) {
        const deletedRows = await sbRest(
          "DELETE",
          `/rest/v1/ballots?admission_no=eq.${qAdm}`,
          null,
          "return=representation"
        );
        if (!Array.isArray(deletedRows) || deletedRows.length === 0) {
          throw new Error(
            "Supabase blocked deleting ballots — re-run supabase/schema.sql (ballots DELETE permission & policy) in Supabase SQL Editor."
          );
        }
      }

      if (voterRow) {
        await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${qAdm}`, {
          final_status: "Not Voted",
          voted_for: "",
          vote_10_boy: "",
          vote_10_girl: "",
          vote_9_boy: "",
          vote_9_girl: "",
          candidate_id: null,
          position_name: "4 Roles",
          ballot_id: null,
          cast_at: null,
          cancelled_at: null,
          active_photo_field: null,
          photo_path: "",
          photos_history: [],
          updated_at: nowIso,
        });
      }

      const photoPaths = new Set();
      ballotsList.forEach((b) => {
        if (b.photo_path) photoPaths.add(b.photo_path);
      });
      if (voterRow?.photo_path) photoPaths.add(voterRow.photo_path);
      if (Array.isArray(voterRow?.photos_history)) {
        voterRow.photos_history.forEach((h) => {
          if (h?.path) photoPaths.add(h.path);
        });
      }
      await Promise.all(Array.from(photoPaths).map((p) => deletePhotoFromStorage(p)));

      const effectiveActor = actorName && !actorName.includes("Principal")
        ? actorName
        : ((typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com");

      const stu = window.ADMIN_DATA.students.find((s) => s.admissionNo === cleanAdm);
      await sbRest("POST", "/rest/v1/audit_logs", {
        id: `AUD-${Date.now().toString(36).toUpperCase()}`,
        action: "BALLOTS_CLEARED",
        ballot_id: null,
        admission_no: cleanAdm,
        student_name: voterRow?.full_name || stu?.fullName || cleanAdm,
        house_code: voterRow?.house_code || stu?.houseCode || ballotsList[0]?.house_code || "",
        reason: `Cleared ${ballotsList.length} ballot(s) for Voter ID ${cleanAdm}`,
        actor: effectiveActor,
        created_at: nowIso,
      }).catch(() => {});

      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
      return { ok: true, deletedCount: ballotsList.length, admissionNo: cleanAdm };
    },

    async addCandidate({ fullName, className, section, houseCode, houseName, positionId, positionName, admissionNo, tagline }) {
      const cleanName = String(fullName || "").trim();
      if (!cleanName) throw new Error("Candidate full name is required.");
      const cleanHouse = String(houseCode || "BHEESHMA").toUpperCase().trim();
      const cleanPosId = String(positionId || "CAPTAIN_BOY").trim();
      const cleanClass = String(className || "").trim();
      const cleanSec = String(section || "").trim();
      const cleanAdm = String(admissionNo || "").trim() || `CAND-${Date.now().toString(36).toUpperCase()}`;
      const cleanTagline = String(tagline || "").trim();

      const candId = `CAND_${cleanHouse}_${cleanPosId}_${cleanName.replace(/[^A-Za-z0-9]/g, "_").toUpperCase()}`;
      const nowIso = new Date().toISOString();

      const newCandDoc = {
        id: candId,
        admission_no: cleanAdm,
        full_name: cleanName,
        class_name: cleanClass,
        section: cleanSec,
        house_code: cleanHouse,
        house_name: houseName || cleanHouse,
        position_id: cleanPosId,
        position_name: positionName || cleanPosId,
        tagline: cleanTagline,
        is_approved: true,
        created_at: nowIso,
      };

      if (this.mode === "supabase") {
        await sbRest("POST", "/rest/v1/candidates", [newCandDoc], "resolution=merge-duplicates,return=representation");
      }

      if (!window.ADMIN_DATA.candidates) window.ADMIN_DATA.candidates = [];
      const existingIdx = window.ADMIN_DATA.candidates.findIndex(
        (c) => c.id === candId || (c.houseCode === cleanHouse && c.fullName === cleanName && c.positionId === cleanPosId)
      );
      const candObj = {
        id: candId,
        admissionNo: cleanAdm,
        fullName: cleanName,
        className: cleanClass,
        section: cleanSec,
        houseCode: cleanHouse,
        positionId: cleanPosId,
        positionName: positionName || cleanPosId,
        tagline: cleanTagline,
        isApproved: true,
      };
      if (existingIdx >= 0) {
        window.ADMIN_DATA.candidates[existingIdx] = candObj;
      } else {
        window.ADMIN_DATA.candidates.push(candObj);
      }

      const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
      if (this.mode === "supabase") {
        await sbRest("POST", "/rest/v1/audit_logs", {
          id: `AUD-${Date.now().toString(36).toUpperCase()}`,
          action: "CANDIDATE_ADDED",
          ballot_id: null,
          admission_no: cleanAdm,
          student_name: cleanName,
          house_code: cleanHouse,
          reason: `Added candidate "${cleanName}" (${cleanClass}-${cleanSec}) for ${positionName} in ${houseName || cleanHouse}`,
          actor: actorName,
          created_at: nowIso,
        }).catch(() => {});
      }

      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
      return { ok: true, candidate: candObj };
    },

    async syncRosterToSupabase() {
      if (this.mode !== "supabase") {
        throw new Error(this.backendError || "Connect Supabase first.");
      }
      const { houses, students, candidates } = window.ADMIN_DATA;
      const houseNameByCode = Object.fromEntries(houses.map((h) => [h.code, h.name]));
      const existing = await sbFetchAll("voters?select=admission_no");
      const existingSet = new Set(existing.map((r) => r.admission_no));
      const nowIso = new Date().toISOString();

      const toInsert = students
        .filter((s) => !existingSet.has(s.admissionNo))
        .map((s) => ({
          admission_no: s.admissionNo,
          full_name: s.fullName,
          class_name: s.className,
          section: s.section,
          house_code: s.houseCode,
          house_name: houseNameByCode[s.houseCode] || s.houseCode,
          final_status: "Not Voted",
          voted_for: "",
          vote_10_boy: "",
          vote_10_girl: "",
          vote_9_boy: "",
          vote_9_girl: "",
          position_name: "House Captains & Vice Captains",
          photo_path: "",
          photos_history: [],
          is_active: s.isActive !== false,
          updated_at: nowIso,
        }));

      for (let i = 0; i < toInsert.length; i += 400) {
        await sbRest("POST", "/rest/v1/voters", toInsert.slice(i, i + 400), "resolution=ignore-duplicates");
      }

      const candRows = candidates.map((c) => ({
        id: c.id,
        admission_no: c.admissionNo,
        full_name: c.fullName,
        class_name: c.className,
        section: c.section,
        house_code: c.houseCode,
        house_name: houseNameByCode[c.houseCode] || c.houseCode,
        position_id: c.positionId,
        position_name: c.positionName,
        tagline: c.tagline,
        is_approved: c.isApproved !== false,
      }));
      await sbRest("POST", "/rest/v1/candidates", candRows, "resolution=merge-duplicates");

      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
      return { insertedVoters: toInsert.length, totalVoters: students.length, candidates: candRows.length };
    },

    resetLocalDemoData() {
      try {
        localStorage.removeItem("election_spr_2026_store_v5");
      } catch (_) {}
      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
    },

    subscribeUpdates(onChange) {
      if (channel) {
        channel.addEventListener("message", () => onChange());
      }
      window.addEventListener("storage", (e) => {
        if (e.key === SB_CFG_KEY) onChange();
      });
      if (this.mode === "supabase" && !this._pollTimer) {
        this._pollTimer = setInterval(() => onChange(), 2500);
      }
    },

    resolveSignedPhotoUrl,
  };

  // Dedicated Pendrive / Local Folder Storage Engine (House-Isolated + Per-Voter Subfolders)
  const FS_DB_NAME = "election_spr_2026_pendrive_v1";
  const FS_STORE = "handles";

  function openHandleDb() {
    return new Promise((resolve, reject) => {
      if (typeof indexedDB === "undefined") {
        reject(new Error("IndexedDB unavailable"));
        return;
      }
      const req = indexedDB.open(FS_DB_NAME, 1);
      req.onupgradeneeded = () => {
        if (!req.result.objectStoreNames.contains(FS_STORE)) {
          req.result.createObjectStore(FS_STORE);
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function idbGetHandle(key) {
    try {
      const db = await openHandleDb();
      return await new Promise((resolve) => {
        const tx = db.transaction(FS_STORE, "readonly");
        const req = tx.objectStore(FS_STORE).get(key);
        req.onsuccess = () => resolve(req.result || null);
        req.onerror = () => resolve(null);
      });
    } catch (_) {
      return null;
    }
  }

  async function idbSetHandle(key, value) {
    try {
      const db = await openHandleDb();
      await new Promise((resolve) => {
        const tx = db.transaction(FS_STORE, "readwrite");
        tx.objectStore(FS_STORE).put(value, key);
        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      });
    } catch (_) { }
  }

  async function photoSourceToBytes(photoSrc) {
    const src = String(photoSrc || "").trim();
    if (!src) return null;
    if (src.startsWith("data:")) {
      const parts = src.split(",");
      if (parts.length < 2) return null;
      const bin = atob(parts[1]);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) {
        bytes[i] = bin.charCodeAt(i);
      }
      return bytes;
    }
    try {
      const resp = await fetch(src, { cache: "no-store" });
      if (!resp.ok) return null;
      const buf = await resp.arrayBuffer();
      return new Uint8Array(buf);
    } catch (_) {
      return null;
    }
  }

  function getVoterFolderName(admissionNo, fullName) {
    const cleanId = String(admissionNo || "unknown").trim().replace(/[<>:"/\\|?*\x00-\x1f]/g, "_");
    const cleanName = String(fullName || "Student")
      .trim()
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, "_")
      .replace(/\s+/g, "_");
    return `${cleanId}_${cleanName}`;
  }

  function formatLocalTime(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString();
    } catch (_) {
      return iso;
    }
  }

  function buildCancelledMarkdown({ student, houseMeta, cancelledBallots, photoByBallotId }) {
    const cls = student ? `${student.className}-${student.section}` : "—";
    const lines = [
      `# Cancelled Ballot Record — ${student.fullName} (${student.admissionNo})`,
      "",
      "## Student Info",
      "",
      `- **Admission No:** \`${student.admissionNo}\``,
      `- **Student Name:** ${student.fullName}`,
      `- **Class & Section:** ${cls}`,
      `- **House:** ${houseMeta.name} House`,
      "",
      "",
      "## Cancelled Vote Details",
      "",
    ];

    cancelledBallots.forEach((b, idx) => {
      const cPhoto = (photoByBallotId && photoByBallotId.get(b.id)) || (idx === 0 ? "photo.jpg" : `photo${idx + 1}.jpg`);
      if (cancelledBallots.length > 1) {
        lines.push(`### Cancelled Attempt ${idx + 1}`, "");
      }
      lines.push(
        `- **Role:** ${b.positionName || "House Captain"}`,
        `- **Voted For (Cancelled):** ${b.candidateName} (\`${b.candidateId || ""}\`)`,
        `- **Status:** Cancelled`,
        `- **Ballot ID:** \`${b.id}\``,
        `- **Cast Time:** ${formatLocalTime(b.castAt)}`,
        `- **Cancelled Time:** ${formatLocalTime(b.cancelledAt)}`,
        `- **Reason:** ${b.cancelReason || "Cancelled by Admin"}`,
        `- **Photo File:** \`${cPhoto}\``,
        ""
      );
    });

    return lines.join("\n") + "\n";
  }

  function buildVoterMarkdown({ student, houseMeta, activeBallots, photoByBallotId }) {
    const cls = student ? `${student.className}-${student.section}` : "—";
    const list = Array.isArray(activeBallots) ? activeBallots : activeBallots ? [activeBallots] : [];
    const lines = [
      `# Voter Record — ${student.fullName} (${student.admissionNo})`,
      "",
      "## Student Info",
      "",
      `- **Admission No:** \`${student.admissionNo}\``,
      `- **Student Name:** ${student.fullName}`,
      `- **Class & Section:** ${cls}`,
      `- **House:** ${houseMeta.name} House`,
      "",
      "",
      "",
      "## Vote Details",
      "",
    ];

    if (list.length > 0) {
      const latestPhoto = (photoByBallotId && photoByBallotId.get(list[list.length - 1].id)) || "photo.jpg";
      list.forEach((b) => {
        lines.push(`- **${b.positionName || "House Role"}:** ${b.candidateName} (\`${b.id}\`)`);
      });
      lines.push(
        `- **Status:** Accepted (${list.length} role${list.length === 1 ? "" : "s"})`,
        `- **Cast Time:** ${formatLocalTime(list[list.length - 1].castAt)}`,
        `- **Photo File:** \`${latestPhoto}\``
      );
    }

    return lines.join("\n") + "\n";
  }

  function buildHouseSummaryMarkdown(meta, students, candidates, ballots) {
    const eligible = students.filter((s) => s.isActive).length;
    const accepted = ballots.filter((b) => b.status === "accepted");
    const votedAdms = new Set(accepted.map((b) => b.admissionNo));
    const cancelled = ballots.filter((b) => b.status === "cancelled");
    const pct = eligible ? Math.round((votedAdms.size / eligible) * 100) : 0;
    const nowLocal = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });

    const lines = [
      `# ${meta.name} House — Election Results`,
      "",
      `- **House:** ${meta.name} House`,
      `- **Last Updated:** ${nowLocal}`,
      `- **Total Eligible Voters:** ${eligible}`,
      `- **Total Voters Cast:** ${votedAdms.size} (${pct}% Turnout · ${accepted.length} accepted ballots)`,
      `- **Cancelled Ballots:** ${cancelled.length}`,
      "",
      "## Candidate Results & Winners",
      "",
      "| Role | Candidate | Admission No | Class | Votes Received | Result |",
      "| :--- | :--- | :--- | :--- | :---: | :---: |",
    ];

    const byRole = new Map();
    candidates.forEach((c) => {
      const roleName = c.positionName || c.positionId || "House Leadership";
      if (!byRole.has(roleName)) byRole.set(roleName, []);
      const count = accepted.filter((b) => b.candidateId === c.id).length;
      byRole.get(roleName).push({
        ...c,
        votes: count,
      });
    });

    byRole.forEach((candList, roleName) => {
      candList.sort((a, b) => b.votes - a.votes);
      const topVotes = candList[0] ? candList[0].votes : 0;
      const topCount = candList.filter((c) => c.votes === topVotes && c.votes > 0).length;

      candList.forEach((c) => {
        let status = "—";
        if (c.votes === 0 && topVotes === 0) {
          status = "No votes yet";
        } else if (c.votes === topVotes && c.votes > 0) {
          status = topCount > 1 ? "🤝 Tied (Leading)" : "🏆 WINNER";
        } else {
          status = "Runner-up";
        }
        lines.push(
          `| ${roleName} | **${c.fullName}** | \`${c.admissionNo}\` | ${c.className || ""}-${c.section || ""} | **${c.votes}** | ${status} |`
        );
      });
    });

    return lines.join("\n") + "\n";
  }

  async function getHouseDirectory(rootHandle, meta) {
    if (!rootHandle || !meta) return rootHandle;
    const rootName = (rootHandle.name || "").trim().toLowerCase();
    const houseSlug = (meta.slug || "").trim().toLowerCase();
    const houseName = (meta.name || "").trim().toLowerCase();
    if (rootName === houseSlug || rootName === `${houseSlug} house` || rootName === houseName || rootName === `${houseName} house`) {
      return rootHandle;
    }
    return await rootHandle.getDirectoryHandle(houseSlug, { create: true });
  }

  async function writeBinaryFile(dirHandle, filename, bytes) {
    const fileHandle = await dirHandle.getFileHandle(filename, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(bytes);
    await writable.close();
  }

  async function writeTextFile(dirHandle, filename, content) {
    const fileHandle = await dirHandle.getFileHandle(filename, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(content);
    await writable.close();
  }

  const pendriveState = {
    dirHandle: null,
    connected: false,
    scopeKey: "overview",
    houseMeta: null,
    getSnapshotFn: null,
    widgetEls: null,
    writtenPhotos: new Set(),
    boundPhotoNames: new Map(),
    writeQueue: Promise.resolve(),
  };

  async function readTextFileSafe(dirHandle, filename) {
    try {
      const fh = await dirHandle.getFileHandle(filename, { create: false });
      const file = await fh.getFile();
      return await file.text();
    } catch (_) {
      return null;
    }
  }

  async function fileExistsSafe(dirHandle, filename) {
    try {
      await dirHandle.getFileHandle(filename, { create: false });
      return true;
    } catch (_) {
      return false;
    }
  }

  async function removeFileSafe(dirHandle, filename) {
    try {
      if (typeof dirHandle.removeEntry === "function") {
        await dirHandle.removeEntry(filename);
      }
    } catch (_) { }
  }

  async function resolvePhotoFilename(voterDir, scopePrefix, ballot, attemptIdx, usedNames) {
    const ballotId = ballot?.id || ballot;
    const fieldMatch = String(ballot?.photoField || "").match(/^(?:Photo|photo)(\d*)$/);
    if (fieldMatch) {
      const num = fieldMatch[1];
      const exactName = !num || num === "1" ? "photo.jpg" : `photo${num}.jpg`;
      if (usedNames) usedNames.add(exactName);
      return exactName;
    }
    const cacheKey = `${scopePrefix}::${ballotId}`;
    if (pendriveState.boundPhotoNames.has(cacheKey)) {
      const cached = pendriveState.boundPhotoNames.get(cacheKey);
      if (!usedNames || !usedNames.has(cached)) {
        if (usedNames) usedNames.add(cached);
        return cached;
      }
    }
    const [resMd, canMd] = await Promise.all([
      readTextFileSafe(voterDir, "result.md"),
      readTextFileSafe(voterDir, "cancelled.md"),
    ]);
    const escapedId = String(ballotId || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const idRe = new RegExp("`" + escapedId + "`[^\\n]*(?:\\n[^\\n]*){0,6}?`(photo\\d*\\.jpg)`");
    for (const mdText of [canMd, resMd]) {
      if (!mdText) continue;
      const m = mdText.match(idRe);
      if (m && m[1] && (!usedNames || !usedNames.has(m[1]))) {
        pendriveState.boundPhotoNames.set(cacheKey, m[1]);
        if (usedNames) usedNames.add(m[1]);
        return m[1];
      }
    }
    let idx = attemptIdx;
    let candidateName = idx === 0 ? "photo.jpg" : `photo${idx + 1}.jpg`;
    while ((usedNames && usedNames.has(candidateName)) || (await fileExistsSafe(voterDir, candidateName))) {
      idx += 1;
      candidateName = `photo${idx + 1}.jpg`;
    }
    pendriveState.boundPhotoNames.set(cacheKey, candidateName);
    if (usedNames) usedNames.add(candidateName);
    return candidateName;
  }

  function refreshWidgetUi() {
    const w = pendriveState.widgetEls;
    if (!w) return;
    w.pill.classList.toggle("is-connected", pendriveState.connected);
    w.dot.classList.toggle("is-green", pendriveState.connected);
    w.dot.classList.toggle("is-red", !pendriveState.connected);
    w.selectBtn.hidden = pendriveState.connected;
    if (pendriveState.connected && pendriveState.dirHandle) {
      const scopeLabel = pendriveState.houseMeta ? `${pendriveState.houseMeta.name} House` : "per-house";
      w.statusBtn.title = `Saving ${scopeLabel} voter folders to "${pendriveState.dirHandle.name}" (click to change folder)`;
    } else {
      const scopeLabel = pendriveState.houseMeta ? `${pendriveState.houseMeta.name} House` : "local backup";
      w.statusBtn.title = `Select pendrive folder for ${scopeLabel} data`;
    }
  }

  async function writeSingleHouseToDir(targetDir, snapshot, meta) {
    const students = (snapshot.students || []).filter((s) => s.houseCode === meta.code);
    const candidates = (snapshot.candidates || []).filter((c) => c.houseCode === meta.code && c.isApproved);
    const ballots = (snapshot.ballots || []).filter((b) => b.houseCode === meta.code);

    const summaryMd = buildHouseSummaryMarkdown(meta, students, candidates, ballots);
    await writeTextFile(targetDir, "result.md", summaryMd);
    await writeTextFile(targetDir, `${meta.code}_SUMMARY.md`, summaryMd);

    if (ballots.length === 0) {
      Array.from(pendriveState.writtenPhotos).forEach((k) => {
        if (k.startsWith(`${meta.slug}_`)) pendriveState.writtenPhotos.delete(k);
      });
      return;
    }

    const byStudent = new Map();
    ballots.forEach((b) => {
      if (!byStudent.has(b.admissionNo)) byStudent.set(b.admissionNo, []);
      byStudent.get(b.admissionNo).push(b);
    });

    for (const [admNo, list] of byStudent.entries()) {
      const stu = students.find((s) => s.admissionNo === admNo) || list[0];
      const ordered = [...list].sort((a, b) => (a.castAt || "").localeCompare(b.castAt || ""));
      const activeBallots = ordered.filter((b) => b.status === "accepted");
      const cancelledBallots = ordered.filter((b) => b.status === "cancelled");
      const folderName = getVoterFolderName(admNo, stu.fullName);
      const voterDir = await targetDir.getDirectoryHandle(folderName, { create: true });

      const photoByBallotId = new Map();
      const usedNames = new Set();
      let distinctIdx = 0;
      const seenCastTimes = new Map();
      for (let i = 0; i < ordered.length; i++) {
        const b = ordered[i];
        let fname = seenCastTimes.get(b.castAt || `i_${i}`);
        if (!fname) {
          fname = await resolvePhotoFilename(voterDir, `${meta.slug}_${folderName}`, b, distinctIdx, usedNames);
          if (b.castAt) seenCastTimes.set(b.castAt, fname);
          distinctIdx += 1;
        }
        photoByBallotId.set(b.id, fname);
        if (b.photoDataUrl) {
          const photoKey = `${meta.slug}_${folderName}_${fname}`;
          if (!pendriveState.writtenPhotos.has(photoKey) && !(await fileExistsSafe(voterDir, fname))) {
            const bytes = await photoSourceToBytes(b.photoDataUrl);
            if (bytes) {
              await writeBinaryFile(voterDir, fname, bytes);
              pendriveState.writtenPhotos.add(photoKey);
            }
          } else {
            pendriveState.writtenPhotos.add(photoKey);
          }
        }
      }

      if (cancelledBallots.length > 0) {
        await writeTextFile(
          voterDir,
          "cancelled.md",
          buildCancelledMarkdown({ student: stu, houseMeta: meta, cancelledBallots, photoByBallotId })
        );
      } else {
        await removeFileSafe(voterDir, "cancelled.md");
      }

      if (activeBallots.length > 0) {
        await writeTextFile(
          voterDir,
          "result.md",
          buildVoterMarkdown({ student: stu, houseMeta: meta, activeBallots, photoByBallotId })
        );
      } else {
        await removeFileSafe(voterDir, "result.md");
      }
    }
  }

  async function writeSnapshotToDisk(snapshot) {
    const dir = pendriveState.dirHandle;
    if (!dir || !pendriveState.connected) return;

    if (pendriveState.houseMeta) {
      const houseDir = await getHouseDirectory(dir, pendriveState.houseMeta);
      await writeSingleHouseToDir(houseDir, snapshot, pendriveState.houseMeta);
      return;
    }

    const houses = window.ADMIN_DATA?.houses || [];
    for (const h of houses) {
      const subDir = await dir.getDirectoryHandle(h.slug, { create: true });
      await writeSingleHouseToDir(subDir, snapshot, h);
    }
  }

  function enqueuePendriveWrite(snapshot) {
    if (!pendriveState.connected || !pendriveState.dirHandle) return Promise.resolve(false);
    pendriveState.writeQueue = pendriveState.writeQueue
      .then(async () => {
        await writeSnapshotToDisk(snapshot);
        return true;
      })
      .catch((err) => {
        console.warn("Pendrive write failed; disconnecting storage status:", err);
        pendriveState.connected = false;
        pendriveState.dirHandle = null;
        refreshWidgetUi();
        return false;
      });
    return pendriveState.writeQueue;
  }

  window.PendriveStorage = {
    async selectFolder() {
      if (typeof window.showDirectoryPicker !== "function") {
        alert("Direct pendrive folder saving requires Chrome or Edge over http://localhost or https://.");
        return false;
      }
      try {
        const picked = await window.showDirectoryPicker({
          id: pendriveState.scopeKey || "election_pendrive",
          mode: "readwrite",
        });
        let perm = await picked.queryPermission({ mode: "readwrite" });
        if (perm !== "granted") {
          perm = await picked.requestPermission({ mode: "readwrite" });
        }
        if (perm !== "granted") return false;

        pendriveState.dirHandle = picked;
        pendriveState.connected = true;
        pendriveState.writtenPhotos.clear();
        await idbSetHandle(pendriveState.scopeKey, picked);
        refreshWidgetUi();
        await this.syncNow();
        return true;
      } catch (err) {
        if (err && err.name !== "AbortError") {
          console.warn("Unable to open local storage folder:", err);
          alert("Could not access the selected folder. Please choose a writable folder on your pendrive.");
        }
        return false;
      }
    },

    async mount({ container, houseMeta = null, getSnapshot }) {
      if (!container) return;
      pendriveState.houseMeta = houseMeta;
      pendriveState.scopeKey = houseMeta ? `house_${houseMeta.slug}` : "overview";
      pendriveState.getSnapshotFn = getSnapshot;

      container.innerHTML = `
        <div class="storage-pill" role="region" aria-label="Local pendrive storage status">
          <button type="button" class="storage-status-btn" title="Local storage folder not selected">
            <span class="storage-dot is-red" aria-hidden="true"></span>
            <span class="storage-label">Local Storage</span>
          </button>
          <button type="button" class="storage-select-btn">Select</button>
        </div>
      `;

      pendriveState.widgetEls = {
        pill: container.querySelector(".storage-pill"),
        statusBtn: container.querySelector(".storage-status-btn"),
        dot: container.querySelector(".storage-dot"),
        selectBtn: container.querySelector(".storage-select-btn"),
      };

      const onPick = () => this.selectFolder();
      pendriveState.widgetEls.selectBtn.addEventListener("click", onPick);
      pendriveState.widgetEls.statusBtn.addEventListener("click", onPick);

      const saved = await idbGetHandle(pendriveState.scopeKey);
      if (saved && typeof saved.queryPermission === "function") {
        try {
          const perm = await saved.queryPermission({ mode: "readwrite" });
          if (perm === "granted") {
            pendriveState.dirHandle = saved;
            pendriveState.connected = true;
            refreshWidgetUi();
            await this.syncNow();
            return;
          }
        } catch (_) { }
      }
      refreshWidgetUi();
    },

    async syncNow(snapshotOverride) {
      if (!pendriveState.connected || !pendriveState.dirHandle) return false;
      try {
        const snap = snapshotOverride || (pendriveState.getSnapshotFn ? await pendriveState.getSnapshotFn() : null);
        if (!snap) return false;
        return await enqueuePendriveWrite(snap);
      } catch (err) {
        console.warn("Unable to prepare pendrive snapshot:", err);
        return false;
      }
    },
  };
})();
