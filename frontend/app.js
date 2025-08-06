(function () {
  const qs = (sel) => document.querySelector(sel);
  const $apiBase = qs("#apiBase");
  const $health = qs("#healthStatus");
  const $db = qs("#dbPath");
  const $query = qs("#query");
  const $max = qs("#maxAttempts");
  const $includeSchema = qs("#includeSchema");
  const $btnHealth = qs("#btnHealth");
  const $btnRun = qs("#btnRun");
  const $resp = qs("#response");

  function safeUrl(base, path) {
    const b = base.replace(/\/+$/, "");
    const p = path.startsWith("/") ? path : `/${path}`;
    return `${b}${p}`;
  }

  async function jsonFetch(url, opts) {
    const res = await fetch(url, {
      method: "GET",
      ...opts,
      headers: {
        "Content-Type": "application/json",
        ...(opts && opts.headers ? opts.headers : {}),
      },
    });
    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = { raw: text }; }
    return { status: res.status, ok: res.ok, data };
  }

  function setBusy(busy) {
    $btnRun.disabled = busy;
    $btnHealth.disabled = busy;
  }

  function show(obj) {
    $resp.textContent = JSON.stringify(obj, null, 2);
  }

  $btnHealth.addEventListener("click", async () => {
    setBusy(true);
    $health.textContent = "…";
    try {
      const url = safeUrl($apiBase.value, "/health");
      const res = await jsonFetch(url);
      if (res.ok) {
        $health.textContent = "OK";
      } else {
        $health.textContent = `Error ${res.status}`;
      }
      show({ endpoint: "/health", ...res });
    } catch (e) {
      $health.textContent = "Network error";
      show({ error: String(e) });
    } finally {
      setBusy(false);
    }
  });

  $btnRun.addEventListener("click", async () => {
    setBusy(true);
    try {
      const url = safeUrl($apiBase.value, "/query");
      const payload = {
        natural_query: $query.value || "",
        max_debug_attempts: $max.value ? Number($max.value) : undefined,
        db_path: $db.value || undefined,
        include_schema: $includeSchema.checked,
      };
      const res = await jsonFetch(url, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      show({ endpoint: "/query", ...res });
    } catch (e) {
      show({ error: String(e) });
    } finally {
      setBusy(false);
    }
  });
})();
