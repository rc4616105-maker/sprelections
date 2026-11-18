/**
 * Supabase Live Results Sync for Result Declaration Ceremony
 * Connects to live Supabase backend to fetch accepted ballots and compute real winners
 * across all 6 Houses (4 roles each) and Central School Cabinet (5 roles).
 */
(function () {
  const SB_CFG_KEY = "election_spr_2026_sb_cfg_v1";
  const DEFAULT_SB_URL = "https://rziptxcknaeuorekxwrl.supabase.co";

  const ROLE_MAP = [
    { key: "boys_captain", positionId: "CAPTAIN_BOY", code: "Vote_10_Boy", title: "Boys Captain", gradeDefault: "Grade 10" },
    { key: "girls_captain", positionId: "CAPTAIN_GIRL", code: "Vote_10_Girl", title: "Girls Captain", gradeDefault: "Grade 10" },
    { key: "boys_vc", positionId: "VICE_CAPTAIN_BOY", code: "Vote_9_Boy", title: "Boys Vice-Captain", gradeDefault: "Grade 9" },
    { key: "girls_vc", positionId: "VICE_CAPTAIN_GIRL", code: "Vote_9_Girl", title: "Girls Vice-Captain", gradeDefault: "Grade 9" }
  ];

  const CENTRAL_ROLES = [
    { id: "PRESIDENT", code: "Vote_President", title: "School President", subtitle: "Class 10" },
    { id: "VICE_PRESIDENT", code: "Vote_Vice_President", title: "School Vice President", subtitle: "Class 9" },
    { id: "LITERARY_SECRETARY", code: "Vote_Literary_Sec", title: "Literary Secretary", subtitle: "Class 9" },
    { id: "SPORTS_SECRETARY", code: "Vote_Sports_Sec", title: "Sports Secretary", subtitle: "Class 9" },
    { id: "SOCIAL_CULTURAL_SECRETARY", code: "Vote_Social_Cultural_Sec", title: "Social & Cultural Sec", subtitle: "Class 9" }
  ];

  function getSavedSupabaseCredentials() {
    try {
      const saved = JSON.parse(localStorage.getItem(SB_CFG_KEY) || "null");
      if (saved && saved.anonKey) {
        return {
          url: (saved.url || DEFAULT_SB_URL).replace(/\/+$/, ""),
          key: saved.anonKey.trim()
        };
      }
    } catch (_) {}
    return null;
  }

  async function sbFetch(url, key, endpoint) {
    const headers = {
      apikey: key,
      "Content-Type": "application/json"
    };
    if (String(key).startsWith("eyJ") || String(key).startsWith("sb_secret_")) {
      headers.Authorization = `Bearer ${key}`;
    }
    const res = await fetch(`${url}/rest/v1/${endpoint}`, { headers, cache: "no-store" });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return res.json();
  }

  function cleanGradeLabel(className, section) {
    let cls = className ? (String(className).toLowerCase().startsWith("class") || String(className).toLowerCase().startsWith("grade") ? className : `Grade ${className}`) : "";
    let sec = section || "";
    if (sec.includes("· Option")) {
      sec = sec.split("· Option").pop().trim();
      sec = `Opt ${sec}`;
    } else if (sec.startsWith("Class ")) {
      sec = "";
    }
    if (cls && sec) return `${cls}-${sec}`;
    return cls || sec || "Grade 10";
  }

  window.SupabaseResultsSync = {
    connected: false,
    totalBallots: 0,
    centralWinners: [],

    async fetchLiveResults(baseHouses) {
      const creds = getSavedSupabaseCredentials();
      const templateHouses = baseHouses || (typeof DEFAULT_HOUSES !== "undefined" ? JSON.parse(JSON.stringify(DEFAULT_HOUSES)) : []);

      if (!creds || !creds.key) {
        console.info("[SupabaseResultsSync] No active Supabase session in localStorage. Using default/preset data.");
        this.updateBadge(false, "Offline / Preset Mode");
        return templateHouses;
      }

      try {
        const [ballots, candidates] = await Promise.all([
          sbFetch(creds.url, creds.key, "ballots?status=eq.accepted&select=*"),
          sbFetch(creds.url, creds.key, "candidates?is_approved=eq.true&select=*")
        ]);

        this.connected = true;
        this.totalBallots = Array.isArray(ballots) ? ballots.length : 0;
        console.info(`[SupabaseResultsSync] Connected to Supabase: ${this.totalBallots} accepted ballots loaded.`);
        this.updateBadge(true, `Live Supabase Sync (${this.totalBallots} Votes)`);

        const clonedHouses = JSON.parse(JSON.stringify(templateHouses));

        // Tally 6 Houses
        clonedHouses.forEach((house) => {
          const houseCodeUpper = house.id.toUpperCase();
          const houseBallots = (ballots || []).filter(
            (b) => (b.house_code || "").toUpperCase() === houseCodeUpper
          );
          const houseCandidates = (candidates || []).filter(
            (c) => (c.house_code || "").toUpperCase() === houseCodeUpper
          );

          if (!house.candidates) house.candidates = {};

          ROLE_MAP.forEach((roleDef) => {
            const roleCands = houseCandidates.filter(
              (c) => c.position_id === roleDef.positionId || c.position_id === roleDef.code
            );

            // Tally votes for each candidate in this role
            const candsWithVotes = roleCands.map((c) => {
              const votes = houseBallots.filter(
                (b) => b.candidate_id === c.id || b.candidate_name === c.full_name
              ).length;
              return {
                id: c.id,
                fullName: c.full_name,
                className: c.class_name,
                section: c.section,
                photoUrl: c.photo_url || "",
                tagline: c.tagline || "",
                votes
              };
            });

            candsWithVotes.sort((a, b) => b.votes - a.votes || a.fullName.localeCompare(b.fullName));

            const totalVotes = candsWithVotes.reduce((sum, c) => sum + c.votes, 0);
            const winner = candsWithVotes[0];
            const fallbackCard = house.candidates[roleDef.key] || {};

            if (winner && totalVotes > 0) {
              const topVotes = winner.votes;
              const isTied = candsWithVotes.filter((c) => c.votes === topVotes).length > 1;
              const grade = cleanGradeLabel(winner.className, winner.section);
              const quote = isTied
                ? `🤝 Tied Winner with ${winner.votes} votes`
                : winner.tagline || `Elected with ${winner.votes} vote${winner.votes > 1 ? "s" : ""}`;

              house.candidates[roleDef.key] = {
                postTitle: roleDef.title,
                name: winner.fullName,
                grade: grade || roleDef.gradeDefault,
                photo: winner.photoUrl || fallbackCard.photo || "",
                quote: quote,
                votes: winner.votes,
                isTied: isTied
              };
            } else if (winner) {
              // 0 votes cast yet: show candidate name from approved roster
              const grade = cleanGradeLabel(winner.className, winner.section);
              house.candidates[roleDef.key] = {
                postTitle: roleDef.title,
                name: winner.fullName,
                grade: grade || fallbackCard.grade || roleDef.gradeDefault,
                photo: winner.photoUrl || fallbackCard.photo || "",
                quote: winner.tagline || fallbackCard.quote || "Awaiting Polling Results",
                votes: 0,
                isTied: false
              };
            }
          });
        });

        // Tally Central (School Cabinet)
        const centralBallots = (ballots || []).filter(
          (b) => (b.house_code || "").toUpperCase() === "CENTRAL"
        );
        const centralCandidates = (candidates || []).filter(
          (c) => (c.house_code || "").toUpperCase() === "CENTRAL"
        );

        const baseCabinet = (typeof DEFAULT_CABINET_POSTS !== "undefined" ? DEFAULT_CABINET_POSTS : CENTRAL_ROLES);
        this.centralWinners = baseCabinet.map((cp) => {
          const roleCands = centralCandidates.filter(
            (c) => c.position_id === cp.id || c.position_id === cp.code
          );
          const candsWithVotes = roleCands.map((c) => {
            const votes = centralBallots.filter(
              (b) => b.candidate_id === c.id || b.candidate_name === c.full_name
            ).length;
            return {
              id: c.id,
              fullName: c.full_name,
              className: c.class_name,
              section: c.section,
              photoUrl: c.photo_url || "",
              tagline: c.tagline || "",
              votes
            };
          });
          candsWithVotes.sort((a, b) => b.votes - a.votes || a.fullName.localeCompare(b.fullName));
          const winner = candsWithVotes[0];
          const grade = winner ? cleanGradeLabel(winner.className, winner.section) : (cp.grade || cp.subtitle);
          const quote = winner ? (winner.tagline || (winner.votes > 0 ? `Elected with ${winner.votes} vote${winner.votes > 1 ? "s" : ""}` : "Apex Leadership")) : "Apex Leadership";
          return {
            ...cp,
            postTitle: cp.postTitle || cp.fullName || cp.title,
            subtitle: cp.subtitle || cp.grade,
            winnerName: winner ? winner.fullName : (cp.candidate?.name || "Awaiting Result"),
            grade: grade,
            votes: winner ? winner.votes : 0,
            candidate: {
              name: winner ? winner.fullName : (cp.candidate?.name || "Awaiting Result"),
              grade: grade,
              photo: (winner && winner.photoUrl) || cp.candidate?.photo || "",
              quote: quote,
              votes: winner ? winner.votes : 0
            }
          };
        });

        return clonedHouses;
      } catch (err) {
        console.warn("[SupabaseResultsSync] Could not fetch live tallies, using fallback:", err);
        this.updateBadge(false, "Supabase Offline / Local Mode");
        return templateHouses;
      }
    },

    updateBadge(isLive, labelText) {
      const badge = document.getElementById("sbSyncBadge");
      const text = document.getElementById("sbSyncText");
      if (badge && text) {
        badge.classList.toggle("is-live", isLive);
        badge.classList.toggle("is-offline", !isLive);
        text.textContent = labelText;
      }
    }
  };
})();
