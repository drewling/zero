/* inbox-keeper panel logic. Vanilla, no dependencies. Reads the cached state
   artifact, renders four views, and drives keeper/undo jobs via the local API. */
"use strict";

const $ = (sel, root = document) => root.querySelector(sel);
const viewEl = $("#view");
const navEl = $("#nav");
const stripEl = $("#accounts-strip");
const actionEl = $("#actionbar");
const panelEl = $(".panel");

let STATE = null;
const _VIEWS = ["loops", "accounts", "undo", "policy"];
let VIEW = _VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : "loops";
let JOB_POLL = null;

/* ---------- helpers ---------- */
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function relTime(epoch) {
  if (!epoch) return "";
  const s = Math.max(0, Math.floor(Date.now() / 1000) - epoch);
  if (s < 90) return "now";
  const m = Math.floor(s / 60);
  if (m < 60) return m + "m";
  const h = Math.floor(m / 60);
  if (h < 24) return h + "h";
  const d = Math.floor(h / 24);
  if (d < 7) return d + "d";
  const w = Math.floor(d / 7);
  if (w < 5) return w + "w";
  return Math.floor(d / 30) + "mo";
}

const acctBySlug = (slug) => (STATE?.accounts || []).find((a) => a.slug === slug);

function gmailUrl(acct, threadId) {
  const who = encodeURIComponent(acct?.email || "");
  return `https://mail.google.com/mail/?authuser=${who}#all/${threadId}`;
}

async function api(path, opts) {
  try {
    const r = await fetch(path, opts);
    const ct = r.headers.get("content-type") || "";
    const data = ct.includes("json") ? await r.json() : await r.text();
    return { ok: r.ok, status: r.status, data };
  } catch (e) {
    return { ok: false, status: 0, data: null };  // server unreachable
  }
}

let toastTimer = null;
function toast(msg) {
  let t = $(".toast", panelEl);
  if (!t) { t = document.createElement("div"); t.className = "toast"; panelEl.appendChild(t); }
  t.textContent = msg;
  requestAnimationFrame(() => t.classList.add("show"));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2600);
}

/* ---------- data ---------- */
async function loadState() {
  const { data } = await api("/api/state");
  if (!data) {                       // server unreachable: keep last good state
    toast("Can’t reach the keeper server");
    return;
  }
  STATE = data;
  renderStrip();
  render();
}

/* ---------- top strip ---------- */
function renderStrip() {
  const accts = STATE?.accounts || [];
  stripEl.innerHTML = accts.map((a) => {
    const badge = a.inbox_threads > 0
      ? `<span class="badge">${a.inbox_threads > 99 ? "99+" : a.inbox_threads}</span>` : "";
    return `<span class="acct-dot${a.ok ? "" : " err"}" style="background:${esc(a.color)}"
                  title="${esc(a.email)}${a.ok ? "" : " — needs attention"}">${esc(a.short)}${badge}</span>`;
  }).join("");
}

/* ---------- views ---------- */
function loopRows() {
  const rows = [];
  for (const a of STATE.accounts || []) {
    for (const l of a.loops || []) rows.push({ ...l, _acct: a });
  }
  rows.sort((x, y) => (y.epoch || 0) - (x.epoch || 0));
  return rows;
}

function failureBanner() {
  const failed = (STATE.accounts || []).filter((a) => !a.ok);
  const partial = (STATE.accounts || []).filter((a) => a.ok && a.partial > 0);
  if (failed.length) {
    const names = failed.map((a) => a.short).join(", ");
    return `<div class="banner banner-err" role="alert">
      Couldn’t read ${failed.length === 1 ? "an account" : failed.length + " accounts"}
      (${esc(names)}). Counts below may be incomplete.</div>`;
  }
  if (partial.length) {
    const n = partial.reduce((s, a) => s + a.partial, 0);
    return `<div class="banner" role="status">${n} ${n === 1 ? "thread" : "threads"} couldn’t be loaded; the list may be short.</div>`;
  }
  return "";
}

function renderLoops() {
  if (!STATE || STATE.needs_build) return skeleton();
  const rows = loopRows();
  const total = STATE.total_loops ?? rows.length;
  const anyFailed = (STATE.accounts || []).some((a) => !a.ok);

  // Never show the calm "all clear" state while an account is unreachable —
  // a transient Gmail/auth failure must not read as "you're caught up".
  if (total === 0 && anyFailed) {
    const failed = (STATE.accounts || []).filter((a) => !a.ok);
    return `<div class="empty">
      <div class="mark warn">${alertSvg()}</div>
      <h2>Couldn’t check your inboxes</h2>
      <p>${failed.length === 1 ? "An account" : failed.length + " accounts"} didn’t
         respond, so this isn’t a real "all clear". ${esc(failed[0].error || "")}</p>
    </div>`;
  }

  if (total === 0) {
    return `<div class="empty">
      <div class="mark">${checkSvg()}</div>
      <h2>Your inboxes are clear</h2>
      <p>Nothing is waiting on you across ${(STATE.accounts || []).length} accounts.
         Everything else was set aside, reversibly.</p>
    </div>`;
  }

  const word = total === 1 ? "thing" : "things";
  const hero = `<div class="hero">
      <div class="count">${total}</div>
      <div class="lede">${total === 1 ? "thing still needs you" : word + " still need you"}</div>
      <div class="sub">Across ${(STATE.accounts || []).length} accounts. Tap any to open it in Gmail.</div>
    </div>`;

  const list = rows.map((r) => {
    const a = r._acct;
    return `<button class="row" data-thread="${esc(r.thread_id)}" data-slug="${esc(a.slug)}">
      <span class="mono" style="background:${esc(a.color)}">${esc(a.short)}</span>
      <span class="body">
        <span class="sender">${esc(r.sender)}</span>
        <span class="ask">${esc(r.subject)}</span>
      </span>
      <span class="meta">
        <span class="when">${esc(relTime(r.epoch))}</span>
      </span>
    </button>`;
  }).join("");

  return failureBanner() + hero +
    `<div class="section-label">Waiting on you</div><ul class="rows">${list}</ul>`;
}

function renderAccounts() {
  if (!STATE) return skeleton();
  const cards = (STATE.accounts || []).map((a) => {
    const undoN = (a.undo_points || []).reduce((n, u) => n + (u.count || 0), 0);
    const bits = [`${a.unread} unread`];
    if (undoN) bits.push(`${undoN} archived`);
    const stat = a.ok ? bits.join(" · ") : "Couldn’t reach this account";
    return `<li class="acct-card">
      <span class="avatar" style="background:${esc(a.color)}">${esc(a.short)}</span>
      <span class="acct-meta">
        <span class="email">${esc(a.email)}</span>
        <span class="stat${a.ok ? "" : " err"}"${a.ok ? "" : ` title="${esc(a.error || "")}"`}>${esc(stat)}</span>
      </span>
      <span class="num"><b>${a.ok ? a.inbox_threads : "—"}</b><span>open</span></span>
    </li>`;
  }).join("");
  return `<ul class="acct-list">${cards}</ul>`;
}

function renderUndo() {
  if (!STATE) return skeleton();
  const items = [];
  for (const a of STATE.accounts || []) {
    for (const u of a.undo_points || []) items.push({ ...u, _acct: a });
  }
  items.sort((x, y) => (y.date || "").localeCompare(x.date || ""));

  if (!items.length) {
    return `<div class="empty">
      <div class="mark">${checkSvg()}</div>
      <h2>Nothing to undo</h2>
      <p>Archived mail is grouped by the day it was set aside. Restore points appear here.</p>
    </div>`;
  }

  const intro = `<p class="undo-intro">Nothing is ever deleted. Each point restores a day’s
    archived threads back to the inbox in one tap.</p>`;
  const list = items.map((u, i) => `<li class="undo-item">
      <span>
        <span class="what">${u.count} ${u.count === 1 ? "thread" : "threads"} set aside</span>
        <span class="who">${esc(u._acct.email)} · ${esc(u.date)}</span>
      </span>
      <button class="btn btn-restore" data-restore="${i}"
              data-slug="${esc(u._acct.slug)}" data-label="${esc(u.label)}">Restore</button>
    </li>`).join("");
  return intro + `<ul class="undo-list">${list}</ul>`;
}

function renderPolicy() {
  const text = STATE?.policy || "";
  return `<div class="policy-wrap">
    <p class="policy-note">The <b>only</b> thing you configure. Describe what counts as
      “still needs me” in plain English. The agent reads each thread and enforces it.</p>
    <textarea class="policy-edit" id="policy-edit" spellcheck="false"
              aria-label="Keep policy">${esc(text)}</textarea>
  </div>`;
}

function skeleton() {
  const r = `<div class="sk-row"><div class="sk" style="width:26px;height:26px;border-radius:7px"></div>
    <div style="flex:1"><div class="sk sk-line" style="width:42%"></div>
    <div class="sk sk-line" style="width:74%;margin-top:7px"></div></div></div>`;
  return `<div style="padding-top:18px">${r.repeat(6)}</div>`;
}

const VIEWS = { loops: renderLoops, accounts: renderAccounts, undo: renderUndo, policy: renderPolicy };

function checkSvg() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>`;
}
function alertSvg() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>`;
}
function runSvg() {
  return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 4v5h-5"/></svg>`;
}

/* ---------- action bar (per view) ---------- */
function renderAction() {
  const running = JOB_POLL !== null;
  if (VIEW === "policy") {
    actionEl.innerHTML = `<span class="status" id="status"></span>
      <button class="btn btn-ghost" id="policy-save">Save policy</button>`;
    $("#policy-save").onclick = savePolicy;
    return;
  }
  const label = running ? "Keeping…" : "Run keeper now";
  actionEl.innerHTML = `<span class="status${running ? " run" : ""}" id="status">${running ? "" : "Tidies every inbox to only what needs you."}</span>
    <button class="btn btn-primary" id="run" ${running ? "disabled" : ""}>
      ${running ? `<span class="spinner"></span>` : runSvg()}<span>${label}</span></button>`;
  $("#run").onclick = runKeeper;
}

function setStatus(msg, run) {
  const s = $("#status");
  if (s) { s.textContent = msg; s.classList.toggle("run", !!run); }
}

/* ---------- render ---------- */
function render() {
  viewEl.innerHTML = (VIEWS[VIEW] || renderLoops)();
  viewEl.classList.remove("view-enter");
  void viewEl.offsetWidth;
  viewEl.classList.add("view-enter");
  renderAction();
  navEl.querySelectorAll(".seg").forEach((b) =>
    b.setAttribute("aria-selected", String(b.dataset.view === VIEW)));
  wireView();
}

function wireView() {
  viewEl.querySelectorAll(".row").forEach((row) => {
    row.onclick = () => {
      const a = acctBySlug(row.dataset.slug);
      window.open(gmailUrl(a, row.dataset.thread), "_blank");
    };
  });
  viewEl.querySelectorAll("[data-restore]").forEach((btn) => {
    btn.onclick = () => doUndo(btn.dataset.slug, btn.dataset.label, btn);
  });
}

/* ---------- jobs ---------- */
async function startJob(path, body) {
  const { ok, status } = await api(path, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  if (status === 409) { toast("A keeper run is already going"); return false; }
  if (!ok) { toast("Couldn’t start — check the server"); return false; }
  pollJob();
  return true;
}

function pollJob() {
  if (JOB_POLL) return;
  renderAction();
  JOB_POLL = setInterval(async () => {
    const { data } = await api("/api/job");
    if (!data) return;               // transient unreachable; keep polling
    if (data.message) setStatus(data.message, true);
    if (data.state === "done") {
      stopPoll();
      await loadState();
      toast("Inbox updated");
    } else if (data.state === "error") {
      stopPoll();
      toast("Run failed: " + (data.error || "unknown"));
      await loadState();
    }
  }, 900);
}
function stopPoll() { clearInterval(JOB_POLL); JOB_POLL = null; renderAction(); }

async function runKeeper() {
  setStatus("Starting…", true);
  await startJob("/api/run", { grace_days: 2 });
}

async function doUndo(slug, label, btn) {
  btn.disabled = true; btn.textContent = "Restoring…";
  await startJob("/api/undo", { slug, label });
}

async function savePolicy() {
  const text = $("#policy-edit").value;
  const btn = $("#policy-save");
  btn.disabled = true; btn.textContent = "Saving…";
  const { ok } = await api("/api/policy", {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy: text }),
  });
  btn.disabled = false; btn.textContent = "Save policy";
  toast(ok ? "Policy saved" : "Couldn’t save policy");
  if (ok && STATE) STATE.policy = text;
}

/* ---------- nav ---------- */
navEl.addEventListener("click", (e) => {
  const seg = e.target.closest(".seg");
  if (!seg) return;
  VIEW = seg.dataset.view;
  history.replaceState(null, "", "#" + VIEW);
  render();
  viewEl.scrollTop = 0;
});

/* ---------- boot ---------- */
loadState();
// If state was missing on boot, the server builds it; refetch shortly after.
setTimeout(() => { if (!STATE || STATE.needs_build) loadState(); }, 2500);
