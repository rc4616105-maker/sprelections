// Polling Booth Session Management
// Persists the registered booth & presiding officer per browser tab (sessionStorage).
// When the tab is closed and reopened, it asks again.
// While the tab stays open across voting navigation, it remembers the booth and officer.
(function () {
  const SESSION_KEY = "election_booth_name";
  const LOCAL_KEY = "last_registered_booth";
  const SESSION_OFFICER_KEY = "election_officer_name";
  const LOCAL_OFFICER_KEY = "last_registered_officer";

  function getRegisteredBooth() {
    try {
      const b = sessionStorage.getItem(SESSION_KEY);
      return b && b.trim() ? b.trim() : "";
    } catch (_) {
      return "";
    }
  }

  function setRegisteredBooth(name) {
    const clean = String(name || "").trim() || "Booth 1";
    try {
      sessionStorage.setItem(SESSION_KEY, clean);
    } catch (_) {}
    try {
      localStorage.setItem(LOCAL_KEY, clean);
    } catch (_) {}
    return clean;
  }

  function getLastKnownBooth() {
    try {
      const b = localStorage.getItem(LOCAL_KEY);
      return b && b.trim() ? b.trim() : "Booth 1";
    } catch (_) {
      return "Booth 1";
    }
  }

  function getRegisteredOfficer() {
    try {
      const o = sessionStorage.getItem(SESSION_OFFICER_KEY);
      return o && o.trim() ? o.trim() : "";
    } catch (_) {
      return "";
    }
  }

  function setRegisteredOfficer(name) {
    const clean = String(name || "").trim();
    try {
      sessionStorage.setItem(SESSION_OFFICER_KEY, clean);
    } catch (_) {}
    try {
      localStorage.setItem(LOCAL_OFFICER_KEY, clean);
    } catch (_) {}
    return clean;
  }

  function getLastKnownOfficer() {
    try {
      const o = localStorage.getItem(LOCAL_OFFICER_KEY);
      return o && o.trim() ? o.trim() : "";
    } catch (_) {
      return "";
    }
  }

  window.getRegisteredBooth = getRegisteredBooth;
  window.setRegisteredBooth = setRegisteredBooth;
  window.getLastKnownBooth = getLastKnownBooth;
  window.getRegisteredOfficer = getRegisteredOfficer;
  window.setRegisteredOfficer = setRegisteredOfficer;
  window.getLastKnownOfficer = getLastKnownOfficer;
})();
