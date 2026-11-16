// Optional Netlify Function for completely hiding Supabase credentials in Netlify Environment Variables.
// Env vars on Netlify: SUPABASE_URL, SUPABASE_KEY (anon or secret), SUPABASE_PHOTO_BUCKET (default: voter-photos).

function supabaseHeaders(key, extra = {}) {
  const h = { apikey: key, ...extra };
  if (String(key).startsWith("eyJ")) {
    h.Authorization = `Bearer ${key}`;
  }
  return h;
}

async function sbJson(baseUrl, key, path, init = {}) {
  const resp = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: supabaseHeaders(key, init.headers || {}),
  });
  const txt = await resp.text();
  let data = null;
  try {
    data = txt ? JSON.parse(txt) : null;
  } catch (_) {
    data = { message: txt };
  }
  return { ok: resp.ok, status: resp.status, data };
}

export default async (req) => {
  const url = (process.env.SUPABASE_URL || "").replace(/\/+$/, "");
  const key = process.env.SUPABASE_KEY || "";
  const bucket = process.env.SUPABASE_PHOTO_BUCKET || "voter-photos";

  if (!url || !key) {
    return Response.json(
      { ok: false, configured: false, error: "Set SUPABASE_URL and SUPABASE_KEY in Netlify Environment Variables." },
      { status: 503 }
    );
  }

  try {
    const reqUrl = new URL(req.url);
    const action = reqUrl.searchParams.get("action") || "health";

    if (action === "health") {
      const res = await sbJson(url, key, "/rest/v1/voters?select=admission_no&limit=1");
      return Response.json({
        ok: res.ok,
        configured: true,
        backend: res.ok ? "supabase" : "offline",
        error: res.ok ? null : res.data?.message || `HTTP ${res.status}`,
      });
    }

    if (action === "photo") {
      const rel = reqUrl.searchParams.get("path") || "";
      if (!/^[a-z0-9_-]+\/[A-Za-z0-9_-]+\/photo[0-9]*\.jpg$/.test(rel)) {
        return new Response("Invalid path", { status: 400 });
      }
      const upstream = await fetch(`${url}/storage/v1/object/${bucket}/${rel}`, {
        headers: supabaseHeaders(key),
      });
      if (!upstream.ok) return new Response("Not found", { status: 404 });
      return new Response(upstream.body, {
        status: 200,
        headers: {
          "Content-Type": upstream.headers.get("Content-Type") || "image/jpeg",
          "Cache-Control": "private, max-age=300",
        },
      });
    }

    if (req.method !== "POST") {
      return Response.json({ error: "POST required" }, { status: 405 });
    }
    const body = await req.json();

    if (action === "rest") {
      const { method = "GET", path = "", jsonBody = null, prefer = "" } = body;
      if (!path.startsWith("/rest/v1/")) {
        return Response.json({ error: "Invalid path" }, { status: 400 });
      }
      const headers = {};
      if (jsonBody !== null) headers["Content-Type"] = "application/json";
      if (prefer) headers["Prefer"] = prefer;
      const res = await sbJson(url, key, path, {
        method,
        headers,
        body: jsonBody !== null ? JSON.stringify(jsonBody) : undefined,
      });
      return Response.json(res.data ?? {}, { status: res.status });
    }

    if (action === "uploadPhoto") {
      const { relPath = "", base64 = "" } = body;
      if (!/^[a-z0-9_-]+\/[A-Za-z0-9_-]+\/photo[0-9]*\.jpg$/.test(relPath) || !base64) {
        return Response.json({ error: "Invalid photo upload payload" }, { status: 400 });
      }
      const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
      const res = await fetch(`${url}/storage/v1/object/${bucket}/${relPath}`, {
        method: "POST",
        headers: supabaseHeaders(key, { "Content-Type": "image/jpeg", "x-upsert": "true" }),
        body: bytes,
      });
      const txt = await res.text();
      return Response.json({ ok: res.ok, raw: txt }, { status: res.status });
    }

    if (action === "deletePhoto") {
      const { relPath = "" } = body;
      if (!/^[a-z0-9_-]+\/[A-Za-z0-9_-]+\/photo[0-9]*\.jpg$/.test(relPath)) {
        return Response.json({ error: "Invalid photo path" }, { status: 400 });
      }
      const res = await fetch(`${url}/storage/v1/object/${bucket}/${relPath}`, {
        method: "DELETE",
        headers: supabaseHeaders(key),
      });
      const txt = await res.text();
      return Response.json({ ok: res.ok, raw: txt }, { status: res.status });
    }

    return Response.json({ error: "Unknown action" }, { status: 400 });
  } catch (err) {
    return Response.json({ error: err?.message || "Server error" }, { status: 500 });
  }
};

