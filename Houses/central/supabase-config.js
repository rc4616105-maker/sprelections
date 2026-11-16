// House Portal — Pure Static JS Supabase Adapter (Direct REST/Storage or Netlify Env Proxy)
// Zero keys live in tracked code: reads Netlify Env Proxy (when deployed), gitignored supabase.local.json, or saved config.
(function () {
  const SB_CFG_KEY = "election_spr_2026_sb_cfg_v1";
  const DEFAULT_SB_URL = "https://rziptxcknaeuorekxwrl.supabase.co";
  const BUCKET = "voter-photos";
  const CHANNEL_NAME = "election_spr_2026_sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(CHANNEL_NAME) : null;

  try {
    localStorage.removeItem("election_spr_2026_store_v1");
    localStorage.removeItem("election_spr_2026_store_v2");
    localStorage.removeItem("election_spr_2026_store_v3");
    localStorage.removeItem("election_spr_2026_store_v4");
    localStorage.removeItem("election_spr_2026_store_v5");
  } catch (_) {}

  function statusKey(electionId, admissionNo, positionId) {
    return `${electionId}_${admissionNo}_${positionId}`;
  }

  const ROLE_VOTE_COLS = {
    CAPTAIN_BOY: "vote_10_boy",
    CAPTAIN_GIRL: "vote_10_girl",
    VICE_CAPTAIN_BOY: "vote_9_boy",
    VICE_CAPTAIN_GIRL: "vote_9_girl",
  };

  function getPositionsList() {
    return Array.isArray(window.HOUSE_DATA.positions) && window.HOUSE_DATA.positions.length
      ? window.HOUSE_DATA.positions
      : [{ id: window.HOUSE_DATA.positionId || "HOUSE_CAPTAIN", code: "Vote_10_Boy", title: "House Captain", subtitle: "Class 10" }];
  }

  function sbHeaders(key, extra = {}) {
    const h = { apikey: key, ...extra };
    if (String(key || "").startsWith("eyJ")) {
      h.Authorization = `Bearer ${key}`;
    }
    return h;
  }

  async function readBrowserSupabaseConfig() {
    try {
      const saved = JSON.parse(localStorage.getItem(SB_CFG_KEY) || "null");
      if (saved && saved.anonKey) {
        return { url: (saved.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: saved.anonKey.trim() };
      }
    } catch (_) {}

    for (const rel of ["../supabase.local.json", "./supabase.local.json"]) {
      try {
        const res = await fetch(rel, { cache: "no-store" });
        if (!res.ok) continue;
        const parsed = await res.json();
        const k = String(parsed.anonKey || parsed.key || "").trim();
        if (k && k !== "paste-your-supabase-key-here") {
          return { url: String(parsed.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: k };
        }
      } catch (_) {}
    }
    return { url: DEFAULT_SB_URL, key: "" };
  }

  const runtime = {
    transport: "offline",
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
      } catch (_) {}
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
    } catch (_) {}
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

  async function uploadPhotoToStorage(relPath, dataUrl) {
    const parts = String(dataUrl || "").split(",");
    if (parts.length < 2) return "";
    const b64 = parts[1];
    if (runtime.transport === "netlify") {
      const res = await fetch("/.netlify/functions/supabase?action=uploadPhoto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ relPath, base64: b64 }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.raw || err.error || `Storage upload failed (${res.status})`);
      }
      return relPath;
    }

    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
    const res = await fetch(`${runtime.url}/storage/v1/object/${BUCKET}/${relPath}`, {
      method: "POST",
      headers: sbHeaders(runtime.key, { "Content-Type": "image/jpeg", "x-upsert": "true" }),
      body: new Blob([bytes], { type: "image/jpeg" }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || `Supabase Storage photo upload failed (${res.status})`);
    }
    return relPath;
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

  window.ElectionBackend = {
    mode: "offline",
    backendError: null,
    _initPromise: null,
    _pollTimer: null,

    async init() {
      if (this._initPromise) return this._initPromise;
      this._initPromise = (async () => {
        if (window.location.protocol !== "file:") {
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
          } catch (_) {}

          const cfg = await readBrowserSupabaseConfig();
          if (cfg.key) {
            if (cfg.key.startsWith("sbp_")) {
              this.backendError = "Blocked sbp_ account token; use Publishable (sb_publishable_... or anon) key from Project Settings -> API Keys.";
            } else if (cfg.key.startsWith("sb_secret_")) {
              this.backendError = "Blocked sb_secret_ key in browser JS; use Publishable (anon) key or Netlify Env Vars.";
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
                this.backendError = `Run supabase/schema.sql in Supabase (${err.message || res.status})`;
              } catch (err) {
                this.backendError = err?.message || "Cannot reach Supabase";
              }
            }
          } else {
            this.backendError = "Connect Supabase key in Admin (Sync Roster to Supabase) first.";
          }
        }
        runtime.transport = "offline";
        this.mode = "offline";
        if (!this.backendError) {
          this.backendError = "Supabase is not connected. Open Admin -> Sync Roster to Supabase to connect.";
        }
        return "offline";
      })();
      return this._initPromise;
    },

    async verifyStudent(admissionNo, requestedHouseCode) {
      const cleanId = String(admissionNo || "").trim();
      if (!cleanId) {
        return { ok: false, code: "EMPTY_ID", title: "Voter ID Required", message: "Please scan a voter card or enter a valid Voter ID number." };
      }

      const { electionId, positionId, housesMeta, allStudents, houseConfig } = window.HOUSE_DATA;
      const positions = getPositionsList();

      // Special Demo User (0000) - Universal Access across ALL booths!
      if (cleanId === "0000") {
        const demoStudent = allStudents.find((s) => s.admissionNo === "0000") || {
          admissionNo: "0000",
          fullName: "Demo User",
          className: "Demo",
          section: "All",
          houseCode: "ALL",
          isActive: true,
        };
        return {
          ok: true,
          student: demoStudent,
          alreadyVoted: false,
          canVote: true,
          votedRoles: {},
          cancelledRoles: [],
          houseMeta: housesMeta[requestedHouseCode] || houseConfig,
          rolesStatus: positions.map((p) => ({ ...p, status: "open", candidateName: null })),
        };
      }

      // Step 1: Check Admission No. against the student roster
      const localMatch = allStudents.find((s) => s.admissionNo === cleanId) || null;
      if (!localMatch) {
        return {
          ok: false,
          code: "NOT_FOUND",
          title: "Not in Voter Roster",
          message: `Voter ID ${cleanId} was not found in the student roster.`,
        };
      }
      if (!localMatch.isActive) {
        return { ok: false, code: "INACTIVE", title: "Student Inactive", message: `Voter ID ${cleanId} is marked inactive for this election.` };
      }

      // School Cabinet Polling Booth Restriction: TEACHERS & FACULTY ONLY
      if (requestedHouseCode === "CENTRAL") {
        const isTeacher = localMatch.isStaff === true || localMatch.houseCode === "ALL" || cleanId === "0000";
        if (!isTeacher) {
          const registeredName = housesMeta[localMatch.houseCode]?.name || localMatch.houseCode;
          return {
            ok: false,
            code: "TEACHER_ONLY",
            title: "Teachers Only Polling Booth",
            message: `Voting for the School Cabinet is strictly reserved for Teachers and Faculty. Students must cast their votes in their respective House polling booths (${registeredName} House).`,
          };
        }
      }

      if (requestedHouseCode !== "CENTRAL" && localMatch.houseCode !== requestedHouseCode && localMatch.houseCode !== "ALL") {
        const registeredName = housesMeta[localMatch.houseCode]?.name || localMatch.houseCode;
        const requestedName = housesMeta[requestedHouseCode]?.name || requestedHouseCode;
        return {
          ok: false,
          code: "WRONG_HOUSE",
          title: "Does Not Belong to This House",
          message: `Voter ID ${cleanId} (${localMatch.fullName}) is registered in ${registeredName} House, not ${requestedName} House.`,
        };
      }

      // Step 2: Cross-check in Supabase Postgres (`voters` + `ballots`) or local store per role
      if (this.mode === "supabase") {
        const qAdm = encodeURIComponent(cleanId);
        const [vRows, bRows] = await Promise.all([
          sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`),
          sbRest("GET", `/rest/v1/ballots?admission_no=eq.${qAdm}&select=id,position_id,position_name,candidate_id,candidate_name,status,cast_at,cancelled_at&order=cast_at.desc`),
        ]);

        const votedRoles = {};
        const cancelledRoleIds = [];
        const hasAnyPerRole = bRows.some((b) => b.position_id);

        if (bRows.length === 0 && vRows.length > 0 && vRows[0].final_status === "Voted") {
          return {
            ok: false,
            code: "ALREADY_VOTED",
            title: "Vote Already Casted",
            message: `Voter ID ${cleanId} (${localMatch.fullName}) is already marked "Voted".`,
          };
        }

        positions.forEach((pos, idx) => {
          const acc = bRows.find((b) => {
            const bPos = b.position_id || (idx === 0 ? pos.id : "");
            return b.status === "accepted" && bPos === pos.id;
          });
          if (acc) {
            votedRoles[pos.id] = {
              ballotId: acc.id,
              positionId: pos.id,
              positionName: acc.position_name || pos.title,
              candidateId: acc.candidate_id,
              candidateName: acc.candidate_name,
              castAt: acc.cast_at,
            };
          } else {
            const hasCan = bRows.some((b) => {
              const bPos = b.position_id || (idx === 0 ? pos.id : "");
              return b.status === "cancelled" && bPos === pos.id;
            });
            if (hasCan || (!hasAnyPerRole && vRows.length > 0 && vRows[0].final_status === "Cancelled")) {
              cancelledRoleIds.push(pos.id);
            }
          }
        });

        const pendingRoleIds = positions.filter((p) => !votedRoles[p.id]).map((p) => p.id);
        if (pendingRoleIds.length === 0) {
          return {
            ok: false,
            code: "ALREADY_VOTED",
            title: "All Votes Already Casted",
            message: `Voter ID ${cleanId} (${localMatch.fullName}) has already voted for all ${positions.length} roles.`,
          };
        }

        const isPartial = Object.keys(votedRoles).length > 0;
        const isCancelled = cancelledRoleIds.length > 0;
        let verificationNote = "Not Voted";
        if (isCancelled && isPartial) {
          verificationNote = `Re-vote open for ${cancelledRoleIds.length} cancelled role(s); ${Object.keys(votedRoles).length} locked`;
        } else if (isCancelled) {
          verificationNote = "Previous vote cancelled";
        } else if (isPartial) {
          verificationNote = `${Object.keys(votedRoles).length}/${positions.length} role(s) recorded`;
        }

        return {
          ok: true,
          student: { ...localMatch, docId: cleanId },
          voterStatus: isCancelled ? "cancelled" : isPartial ? "partial" : "not_voted",
          pendingRoleIds,
          votedRoles,
          cancelledRoleIds,
          verificationNote,
        };
      }

      return {
        ok: false,
        code: "SUPABASE_REQUIRED",
        title: "Supabase Not Connected",
        message: `${this.backendError ? `${this.backendError} — ` : ""}Votes must save strictly to Supabase. Open Admin -> Sync Roster to Supabase and connect your Publishable key first.`,
      };
    },

    async getHouseCandidates(houseCode) {
      if (this.mode === "supabase") {
        try {
          const rows = await sbRest(
            "GET",
            `/rest/v1/candidates?house_code=eq.${encodeURIComponent(houseCode)}&is_approved=eq.true&select=*`
          );
          if (Array.isArray(rows) && rows.length > 0) {
            return rows.map((c) => ({
              id: c.id,
              admissionNo: c.admission_no,
              fullName: c.full_name,
              className: c.class_name,
              section: c.section,
              houseCode: c.house_code,
              positionId: c.position_id || "CAPTAIN_BOY",
              positionName: c.position_name || "Boys Captain",
              tagline: c.tagline || "",
              isApproved: c.is_approved !== false,
            }));
          }
        } catch (_) {}
        return window.HOUSE_DATA.houseCandidates;
      }
      return window.HOUSE_DATA.houseCandidates;
    },

    async getHouseSnapshot(houseCode) {
      if (this.mode === "supabase") {
        const { electionId, positionId, houseStudents } = window.HOUSE_DATA;
        const positions = getPositionsList();
        const qH = encodeURIComponent(houseCode);
        const [voterRows, ballotRows] = await Promise.all([
          sbFetchAll(`voters?house_code=eq.${qH}&select=*`),
          sbFetchAll(`ballots?house_code=eq.${qH}&select=*&order=cast_at.desc`),
        ]);

        const byAdm = new Map(houseStudents.map((s) => [s.admissionNo, { ...s }]));
        const voterStatus = {};
        const ballotsByAdmRole = new Map();

        ballotRows.forEach((b) => {
          const posId = b.position_id || positionId;
          const k = `${b.admission_no}::${posId}`;
          if (!ballotsByAdmRole.has(k)) ballotsByAdmRole.set(k, []);
          ballotsByAdmRole.get(k).push(b);
        });

        voterRows.forEach((v) => {
          if (!byAdm.has(v.admission_no)) {
            byAdm.set(v.admission_no, {
              admissionNo: v.admission_no,
              fullName: v.full_name || v.admission_no,
              className: v.class_name || "",
              section: v.section || "",
              houseCode,
              isActive: v.is_active !== false,
              isCandidate: false,
              positionName: null,
            });
          }
          let foundPerRole = false;
          positions.forEach((pos) => {
            const list = ballotsByAdmRole.get(`${v.admission_no}::${pos.id}`) || [];
            const acc = list.find((b) => b.status === "accepted");
            const can = list.find((b) => b.status === "cancelled");
            if (acc || can) {
              foundPerRole = true;
              const st = acc ? "voted" : "cancelled";
              voterStatus[statusKey(electionId, v.admission_no, pos.id)] = {
                electionId,
                admissionNo: v.admission_no,
                houseCode,
                positionId: pos.id,
                status: st,
                activeBallotId: acc ? acc.id : null,
                updatedAt: acc ? acc.cast_at : can.cancelled_at,
              };
            }
          });
          if (!foundPerRole && (v.final_status === "Voted" || v.final_status === "Cancelled")) {
            const st = v.final_status === "Voted" ? "voted" : "cancelled";
            const fallbackPosId = positions[0]?.id || positionId;
            voterStatus[statusKey(electionId, v.admission_no, fallbackPosId)] = {
              electionId,
              admissionNo: v.admission_no,
              houseCode,
              positionId: fallbackPosId,
              status: st,
              activeBallotId: st === "voted" ? v.ballot_id : null,
              updatedAt: st === "voted" ? v.cast_at : v.cancelled_at,
            };
          }
        });

        const uniquePaths = Array.from(new Set(ballotRows.map((b) => b.photo_path).filter(Boolean)));
        await Promise.all(uniquePaths.map((p) => resolveSignedPhotoUrl(p)));

        const ballots = await Promise.all(
          ballotRows.map(async (b) => {
            const stu = byAdm.get(b.admission_no) || {};
            const photoDataUrl = b.photo_path ? await resolveSignedPhotoUrl(b.photo_path) : "";
            const posId = b.position_id || positionId;
            return {
              id: b.id,
              electionId: b.election_id || electionId,
              admissionNo: b.admission_no,
              fullName: stu.fullName || b.admission_no,
              className: stu.className || "",
              section: stu.section || "",
              houseCode,
              positionId: posId,
              positionName: b.position_name || "House Captain",
              candidateId: b.candidate_id,
              candidateName: b.candidate_name,
              photoField: b.photo_field || "",
              photoDataUrl,
              status: b.status,
              castAt: b.cast_at,
              cancelledAt: b.cancelled_at,
              cancelReason: b.cancel_reason,
            };
          })
        );

        let houseCandidates = window.HOUSE_DATA.houseCandidates;
        try {
          const liveCands = await this.getHouseCandidates(houseCode);
          if (Array.isArray(liveCands) && liveCands.length > 0) {
            houseCandidates = liveCands;
          }
        } catch (_) {}

        return {
          students: Array.from(byAdm.values()),
          candidates: houseCandidates,
          voterStatus,
          ballots,
          auditLogs: [],
        };
      }
      return {
        students: window.HOUSE_DATA.houseStudents,
        candidates: window.HOUSE_DATA.houseCandidates,
        voterStatus: {},
        ballots: [],
        auditLogs: [],
      };
    },

    async castVote({ student, selections, candidate, photoDataUrl, boothName }) {
      const finalBooth = String(boothName || (typeof window.getRegisteredBooth === "function" && window.getRegisteredBooth()) || (typeof sessionStorage !== "undefined" && sessionStorage.getItem("election_booth_name")) || (typeof localStorage !== "undefined" && localStorage.getItem("last_registered_booth")) || "Booth 1").trim();
      const { electionId, positionId, positionName, houseConfig, allStudents, houseCandidates } = window.HOUSE_DATA;
      const positions = getPositionsList();
      const nowIso = new Date().toISOString();

      let rawSelections = [];
      if (Array.isArray(selections) && selections.length > 0) {
        rawSelections = selections;
      } else if (selections && typeof selections === "object") {
        rawSelections = Object.entries(selections)
          .filter(([, cand]) => Boolean(cand))
          .map(([pid, cand]) => ({ positionId: pid, candidate: cand }));
      } else if (candidate) {
        rawSelections = [{ positionId: candidate.positionId || positionId, candidate }];
      }
      if (rawSelections.length === 0) {
        throw new Error("Select a candidate for each open leadership role.");
      }

      const normalizedSels = rawSelections.map((sel) => {
        const cand = sel.candidate || sel;
        const pos = positions.find((p) => p.id === (sel.positionId || cand?.positionId));
        const posId = pos ? pos.id : sel.positionId || cand?.positionId || positionId;
        const posTitle = pos ? pos.title : cand?.positionName || positionName;
        const candDoc = houseCandidates.find((c) => c.id === cand?.id);
        if (!candDoc || !candDoc.isApproved) {
          throw new Error(`Selected candidate for ${posTitle} is not eligible for this house.`);
        }
        if (candDoc.positionId && candDoc.positionId !== posId) {
          throw new Error(`${candDoc.fullName} does not run for ${posTitle}.`);
        }
        return { positionId: posId, positionName: posTitle, candidate: candDoc };
      });

      if (this.mode === "supabase") {
        let stu = allStudents.find((s) => s.admissionNo === student.admissionNo);
        if (student.admissionNo === "0000" && !stu) {
          stu = { admissionNo: "0000", fullName: "Demo User", className: "Demo", section: "All", houseCode: "ALL", isActive: true };
        }
        if (!stu || !stu.isActive || (stu.houseCode !== houseConfig.code && stu.houseCode !== "ALL" && stu.admissionNo !== "0000" && houseConfig.code !== "CENTRAL")) {
          throw new Error("Student does not belong to this house roster.");
        }

        const qAdm = encodeURIComponent(stu.admissionNo);
        const existingRows = await sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`);
        let voterRow = existingRows[0] || null;
        if (!voterRow) {
          const created = await sbRest(
            "POST",
            "/rest/v1/voters",
            {
              admission_no: stu.admissionNo,
              full_name: stu.fullName,
              class_name: stu.className,
              section: stu.section,
              house_code: houseConfig.code,
              house_name: houseConfig.name,
              final_status: "Not Voted",
              voted_for: "",
              vote_10_boy: "",
              vote_10_girl: "",
              vote_9_boy: "",
              vote_9_girl: "",
              position_name: "4 Roles",
              photo_path: "",
              photos_history: [],
              is_active: true,
              updated_at: nowIso,
            },
            "resolution=ignore-duplicates,return=representation"
          );
          voterRow = Array.isArray(created) ? created[0] : created;
        }

        const priorBallots = await sbRest(
          "GET",
          `/rest/v1/ballots?admission_no=eq.${qAdm}&select=id,position_id,position_name,candidate_id,candidate_name,status,photo_field,photo_path,cast_at&order=cast_at.desc`
        );

        for (const sel of normalizedSels) {
          const dup = priorBallots.find((b) => b.status === "accepted" && (b.position_id || sel.positionId) === sel.positionId);
          if (dup && stu.admissionNo !== "0000") {
            throw new Error(`Vote already casted for ${sel.positionName} (${stu.admissionNo}).`);
          }
        }

        const existingHist = Array.isArray(voterRow?.photos_history) ? voterRow.photos_history : [];
        const priorPhotoBatches = new Set(priorBallots.map((b) => b.photo_field || b.cast_at).filter(Boolean)).size;
        const attemptNum = Math.max(priorPhotoBatches, existingHist.length) + 1;
        const photoField = attemptNum === 1 ? "Photo" : `Photo${attemptNum}`;
        const photoFile = attemptNum === 1 ? "photo.jpg" : `photo${attemptNum}.jpg`;
        const relPath = `${houseConfig.slug}/${stu.admissionNo}/${photoFile}`;
        const storedPath = photoDataUrl ? await uploadPhotoToStorage(relPath, photoDataUrl) : "";

        const tsBase = Date.now().toString(36).toUpperCase();
        const ballotsToInsert = normalizedSels.map((sel) => {
          const safeRole = sel.positionId.replace(/[^A-Z0-9]/g, "");
          return {
            id: `BLT-${tsBase}-${stu.admissionNo}-${safeRole}`,
            election_id: electionId,
            admission_no: stu.admissionNo,
            house_code: houseConfig.code,
            position_id: sel.positionId,
            position_name: sel.positionName,
            candidate_id: sel.candidate.id,
            candidate_name: sel.candidate.fullName,
            photo_field: photoField,
            photo_path: storedPath,
            status: "accepted",
            booth_name: finalBooth,
            cast_at: nowIso,
            cancelled_at: null,
            cancel_reason: null,
            cancelled_by: null,
          };
        });

        try {
          await sbRest("POST", "/rest/v1/ballots", ballotsToInsert);
        } catch (ballotErr) {
          if (String(ballotErr?.message || "").includes("booth_name")) {
            // Graceful fallback if booth_name column does not exist in ballots table
            const strippedBallots = ballotsToInsert.map(({ booth_name, ...rest }) => rest);
            await sbRest("POST", "/rest/v1/ballots", strippedBallots);
          } else {
            throw ballotErr;
          }
        }

        const acceptedByPos = new Map();
        priorBallots
          .filter((b) => b.status === "accepted" && b.position_id)
          .forEach((b) => acceptedByPos.set(b.position_id, { candidateName: b.candidate_name, candidateId: b.candidate_id }));
        normalizedSels.forEach((sel) => {
          acceptedByPos.set(sel.positionId, { candidateName: sel.candidate.fullName, candidateId: sel.candidate.id });
        });

        const voteColsPatch = {};
        const summaryParts = [];
        positions.forEach((pos) => {
          const col = ROLE_VOTE_COLS[pos.id];
          const chosen = acceptedByPos.get(pos.id);
          if (col) voteColsPatch[col] = chosen ? chosen.candidateName : "";
          if (chosen) summaryParts.push(`${pos.shortTitle || pos.title}: ${chosen.candidateName}`);
        });

        const allRolesAccepted = positions.every((p) => acceptedByPos.has(p.id));
        const lastBallot = ballotsToInsert[ballotsToInsert.length - 1];
        const nextHistory = [...existingHist];
        if (storedPath) {
          nextHistory.push({ field: photoField, path: storedPath, ballotId: lastBallot.id, castAt: nowIso });
        }

        await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${qAdm}`, {
          ...voteColsPatch,
          final_status: allRolesAccepted ? "Voted" : "Cancelled",
          voted_for: summaryParts.join(" | "),
          candidate_id: lastBallot.candidate_id,
          position_name: allRolesAccepted ? `All ${positions.length} Roles` : lastBallot.position_name,
          ballot_id: lastBallot.id,
          cast_at: nowIso,
          cancelled_at: null,
          active_photo_field: photoField,
          photo_path: storedPath,
          photos_history: nextHistory,
          updated_at: nowIso,
        });

        if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
        return { ok: true, ballotIds: ballotsToInsert.map((b) => b.id), ballotId: lastBallot.id };
      }

      throw new Error(this.backendError || "Supabase is not connected — votes must be saved strictly in Supabase, never locally.");
    },

    subscribeHouseUpdates(houseCode, onChange) {
      if (channel) {
        channel.addEventListener("message", () => onChange());
      }
      window.addEventListener("storage", (e) => {
        if (e.key === SB_CFG_KEY) onChange();
      });
      if (this.mode === "supabase" && !this._pollTimer) {
        this._pollTimer = setInterval(() => onChange(), 3000);
      }
    },
  };

  // Dedicated Pendrive / Local Folder Storage Engine (House-Isolated)
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
    } catch (_) {}
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
        `- **Voted For (Cancelled):** ${b.candidateName} (\`${b.candidateId || ""}\`)`,
        `- **Position:** ${b.positionName || window.HOUSE_DATA.positionName}`,
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

  function buildVoterMarkdown({ student, houseMeta, activeBallot, activeBallots, cancelledBallots, stageLabel, photoByBallotId }) {
    const cls = student ? `${student.className}-${student.section}` : "—";
    const list = Array.isArray(activeBallots) ? activeBallots : activeBallot ? [activeBallot] : [];
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
      const uniquePhotoFiles = Array.from(
        new Set(list.map((b) => (photoByBallotId && photoByBallotId.get(b.id)) || "photo.jpg"))
      );
      const latestCastAt = list.map((b) => b.castAt).filter(Boolean).sort().pop() || "";
      list.forEach((b) => {
        const posLabel = b.positionName || window.HOUSE_DATA.positionName;
        const pf = (photoByBallotId && photoByBallotId.get(b.id)) || "photo.jpg";
        lines.push(`- **${posLabel}:** ${b.candidateName} (\`${b.candidateId || ""}\` · \`${b.id}\` · \`${pf}\`)`);
      });
      lines.push(
        `- **Status:** Accepted (${list.length} role${list.length > 1 ? "s" : ""})`,
        `- **Cast Time:** ${formatLocalTime(latestCastAt)}`,
        `- **Photo File${uniquePhotoFiles.length > 1 ? "s" : ""}:** ${uniquePhotoFiles.map((f) => `\`${f}\``).join(", ")}`
      );
    } else {
      const position = (cancelledBallots && cancelledBallots[0]?.positionName) || "All 4 Leadership Roles";
      const statusText = stageLabel || "Voting Started (Verified — Selecting Candidates)";
      lines.push(
        `- **Voted For:** Pending Selection`,
        `- **Position:** ${position}`,
        `- **Status:** ${statusText}`,
        `- **Started At:** ${formatLocalTime(new Date().toISOString())}`
      );
    }

    return lines.join("\n") + "\n";
  }

  function buildHouseSummaryMarkdown(meta, students, candidates, ballots) {
    const eligible = students.filter((s) => s.isActive).length;
    const accepted = ballots.filter((b) => b.status === "accepted");
    const cancelled = ballots.filter((b) => b.status === "cancelled");
    const votedStudents = new Set(accepted.map((b) => b.admissionNo)).size;
    const pct = eligible ? Math.round((votedStudents / eligible) * 100) : 0;

    const lines = [
      `# ${meta.name} House — Local Backup Summary`,
      "",
      `- **Last Updated:** ${new Date().toISOString()}`,
      `- **Eligible Students:** ${eligible}`,
      `- **Voters With Accepted Votes:** ${votedStudents} (${pct}% turnout · ${accepted.length} role ballots)`,
      `- **Cancelled Ballots:** ${cancelled.length}`,
      `- **Remaining To Vote:** ${Math.max(0, eligible - votedStudents)}`,
      "",
      "## Candidate Tally (Accepted Votes)",
      "",
      "| Role | Candidate | Admission No | Class | Accepted Votes |",
      "| :--- | :--- | :--- | :--- | :---: |",
    ];

    candidates.forEach((c) => {
      const count = accepted.filter((b) => b.candidateId === c.id).length;
      lines.push(`| ${c.positionName || "Role"} | ${c.fullName} | \`${c.admissionNo}\` | ${c.className}-${c.section} | ${count} |`);
    });

    lines.push(
      "",
      "## Recorded Voter Folders",
      "",
      "| Folder | Student | Status | Voted For |",
      "| :--- | :--- | :--- | :--- |"
    );

    const byAdm = new Map();
    ballots.forEach((b) => {
      if (!byAdm.has(b.admissionNo)) byAdm.set(b.admissionNo, []);
      byAdm.get(b.admissionNo).push(b);
    });

    byAdm.forEach((list, admNo) => {
      const activeList = list.filter((b) => b.status === "accepted");
      const latest = activeList[0] || list[0];
      const folder = getVoterFolderName(admNo, latest.fullName);
      const summaryChoice = activeList.length
        ? activeList.map((b) => `${b.positionName}: ${b.candidateName}`).join(" ; ")
        : `${latest.positionName}: ${latest.candidateName}`;
      lines.push(
        `| \`${folder}/\` | ${latest.fullName} | ${activeList.length > 0 ? `Accepted (${activeList.length})` : "Cancelled"} | ${summaryChoice} |`
      );
    });

    return lines.join("\n") + "\n";
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
    scopeKey: null,
    houseMeta: null,
    getSnapshotFn: null,
    widgetEls: null,
    writtenPhotos: new Set(),
    boundPhotoNames: new Map(),
    activeStartedFolder: null,
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
    } catch (_) {}
  }

  async function resolvePhotoFilename(voterDir, folderName, ballot, attemptIdx, usedNames) {
    const ballotId = ballot?.id || ballot;
    const fieldMatch = String(ballot?.photoField || "").match(/^(?:Photo|photo)(\d*)$/);
    if (fieldMatch) {
      const num = fieldMatch[1];
      const exactName = !num || num === "1" ? "photo.jpg" : `photo${num}.jpg`;
      if (!usedNames || !usedNames.has(exactName)) {
        if (usedNames) usedNames.add(exactName);
        return exactName;
      }
    }
    const cacheKey = `${folderName}::${ballotId}`;
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
      w.statusBtn.title = `Saving ${pendriveState.houseMeta.name} House voter folders to "${pendriveState.dirHandle.name}" (click to change folder)`;
    } else {
      w.statusBtn.title = `Select pendrive folder for ${pendriveState.houseMeta?.name || "this"} House`;
    }
  }

  async function writeHouseBundleToDisk(snapshot) {
    const dir = pendriveState.dirHandle;
    const meta = pendriveState.houseMeta;
    if (!dir || !meta || !pendriveState.connected) return;

    const students = (snapshot.students || []).filter((s) => s.houseCode === meta.code);
    const candidates = (snapshot.candidates || []).filter((c) => c.houseCode === meta.code && c.isApproved);
    const ballots = (snapshot.ballots || []).filter((b) => b.houseCode === meta.code);

    await writeTextFile(
      dir,
      `${meta.code}_SUMMARY.md`,
      buildHouseSummaryMarkdown(meta, students, candidates, ballots)
    );

    if (ballots.length === 0) {
      pendriveState.writtenPhotos.clear();
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
      const voterDir = await dir.getDirectoryHandle(folderName, { create: true });

      const photoByBallotId = new Map();
      const usedNames = new Set();
      const seenCastTimes = new Map();
      for (let i = 0; i < ordered.length; i++) {
        const b = ordered[i];
        const batchKey = b.castAt || b.photoField || `i_${i}`;
        let fname = seenCastTimes.get(batchKey);
        if (!fname) {
          fname = await resolvePhotoFilename(voterDir, folderName, b, seenCastTimes.size, usedNames);
          seenCastTimes.set(batchKey, fname);
        }
        photoByBallotId.set(b.id, fname);
        if (b.photoDataUrl) {
          const photoKey = `${folderName}_${fname}`;
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
        const md = buildVoterMarkdown({
          student: stu,
          houseMeta: meta,
          activeBallots,
          cancelledBallots,
          photoByBallotId,
        });
        await writeTextFile(voterDir, "result.md", md);
      } else {
        await removeFileSafe(voterDir, "result.md");
      }
    }
  }

  function enqueuePendriveWrite(snapshot) {
    if (!pendriveState.connected || !pendriveState.dirHandle) return Promise.resolve(false);
    pendriveState.writeQueue = pendriveState.writeQueue
      .then(async () => {
        await writeHouseBundleToDisk(snapshot);
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
          id: pendriveState.scopeKey || "house_pendrive",
          mode: "readwrite",
        });
        let perm = await picked.queryPermission({ mode: "readwrite" });
        if (perm !== "granted") {
          perm = await picked.requestPermission({ mode: "readwrite" });
        }
        if (perm !== "granted") {
          return false;
        }
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

    async mount({ container, houseMeta, getSnapshot }) {
      if (!container) return;
      pendriveState.houseMeta = houseMeta;
      pendriveState.scopeKey = `house_${houseMeta.slug}`;
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
        } catch (_) {}
      }
      refreshWidgetUi();
    },

    async markVoterStarted(student) {
      if (!pendriveState.connected || !pendriveState.dirHandle || !pendriveState.houseMeta || !student) {
        return false;
      }
      const meta = pendriveState.houseMeta;
      if (student.houseCode !== meta.code && student.houseCode !== "ALL" && student.admissionNo !== "0000" && meta.code !== "CENTRAL") return false;
      const folderName = getVoterFolderName(student.admissionNo, student.fullName);
      pendriveState.writeQueue = pendriveState.writeQueue
        .then(async () => {
          const dir = pendriveState.dirHandle;
          let folderExisted = false;
          try {
            await dir.getDirectoryHandle(folderName, { create: false });
            folderExisted = true;
          } catch (_) {}
          const voterDir = await dir.getDirectoryHandle(folderName, { create: true });
          if (!folderExisted) {
            const md = buildVoterMarkdown({
              student,
              houseMeta: meta,
              activeBallots: [],
              cancelledBallots: [],
              stageLabel: "Voting Started (Verified — Selecting Candidates)",
            });
            await writeTextFile(voterDir, "result.md", md);
            pendriveState.activeStartedFolder = folderName;
          } else {
            pendriveState.activeStartedFolder = null;
          }
          return true;
        })
        .catch((err) => {
          console.warn("Pendrive start-folder write failed:", err);
          pendriveState.connected = false;
          pendriveState.dirHandle = null;
          refreshWidgetUi();
          return false;
        });
      return pendriveState.writeQueue;
    },

    async clearIncompleteStarted() {
      const folderToClean = pendriveState.activeStartedFolder;
      pendriveState.activeStartedFolder = null;
      if (!folderToClean || !pendriveState.connected || !pendriveState.dirHandle) return;
      const dir = pendriveState.dirHandle;
      pendriveState.writeQueue = pendriveState.writeQueue
        .then(async () => {
          if (typeof dir.removeEntry === "function") {
            await dir.removeEntry(folderToClean, { recursive: true });
          }
        })
        .catch(() => {});
      return pendriveState.writeQueue;
    },

    async syncNow() {
      pendriveState.activeStartedFolder = null;
      if (!pendriveState.connected || !pendriveState.dirHandle || !pendriveState.getSnapshotFn) {
        return false;
      }
      try {
        const snap = await pendriveState.getSnapshotFn();
        return await enqueuePendriveWrite(snap);
      } catch (err) {
        console.warn("Unable to fetch snapshot for pendrive backup:", err);
        return false;
      }
    },
  };

  if (channel) {
    channel.addEventListener("message", () => {
      if (pendriveState.connected) {
        window.PendriveStorage.syncNow();
      }
    });
  }
  window.addEventListener("storage", (e) => {
    if (e.key === SB_CFG_KEY && pendriveState.connected) {
      window.PendriveStorage.syncNow();
    }
  });
})();
