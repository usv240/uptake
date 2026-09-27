(() => {
  const D = window.UPTAKE;
  const $ = (s, el = document) => el.querySelector(s);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pct = x => `${Math.round(x * 100)}%`;
  const LABEL = { OVERSTEPPED: "⚠ Overstepped", REPAIRED: "✓ Repaired", REPAIRED_NEEDS_REVIEW: "✓ Repaired · review", ESCALATED: "↑ Escalated", COMPILES_UNTESTED: "◐ No tests", CHEATED: "✗ Cheated", FAILED: "– Failed" };
  const badge = (v, r) => {
    if (!v) return `<span class="muted">–</span>`;
    const proven = v === "ESCALATED" && r?.proposal?.provenGreen;
    return `<span class="verdict v-${v}">${proven ? "↑ Patch proven" : (LABEL[v] || v)}</span>`;
  };
  const short = dep => dep.split(":")[1] || dep;
  const U = D.arms.uptake, P = D.arms.plain;
  const uRuns = D.runs.filter(r => r.arm === "uptake");
  const plainOf = name => D.runs.find(r => r.arm === "plain" && r.name === name);

  // Headline stats
  const Bare = D.arms.bare || { n: 0 };
  const protoN = U.n + P.n, protoSilent = U.silentEdits + P.silentEdits;
  const stats = [
    { cls: "ok", v: `${U.resolved}<small>/${U.n}</small>`, l: "Breaking security upgrades unblocked",
      d: `${U.repaired} repaired by Bob, ${U.escalatedProven} with a one-approval patch proven green · 95% CI ${pct(U.resolvedCI[0])}–${pct(U.resolvedCI[1])}` },
    { cls: "ok", v: `${protoSilent}<small>/${protoN}</small>`, l: "Runs with unreviewed edits to tests or build files",
      d: "With Uptake's protocol. Every change outside production code arrived as a proposed patch instead." },
    Bare.n ? { cls: Bare.silentEdits ? "bad" : "", v: `${Bare.silentEdits}<small>/${Bare.n}</small>`, l: "Without Uptake: silent edits",
      d: "Same Bob, same build tool, just “get the build passing”. One run downgraded a logging library to a 2008 release." }
      : { v: "–", l: "Without Uptake", d: "Running" },
    { v: `${U.advisories}`, l: "Security advisories unblocked", d: `incl. ${uRuns.some(r => r.log4shell.length) ? "Log4Shell (CVE-2021-44228)" : "real CVEs"}` },
  ];
  $("#stats").innerHTML = stats.map(s => `<div class="stat ${s.cls || ""}"><div class="v">${s.v}</div><div class="l">${s.l}</div><div class="d">${s.d}</div></div>`).join("");
  const ov = D.byamOverlap;
  $("#stats-note").textContent = `Cases are real breaking Dependabot/Renovate upgrades from the BUMP benchmark that remove known advisories (146 of 571 do). `
    + (ov.n ? `On the ${ov.n} of our cases that the published Byam system also attempted, Byam solved ${ov.byamSolved} using the best of 40 configurations; Uptake solved ${ov.uptakeSolved} in one Bob run each, without touching tests or versions.`
      + (ov.onlyUptake.length ? ` Solved only by Uptake: ${ov.onlyUptake.join(", ")}.` : "")
      + (ov.onlyByam.length ? ` Solved only by Byam: ${ov.onlyByam.join(", ")}, where the fix is in test code that Uptake is not allowed to edit.` : "") : "");

  // Results lede
  const testCases = uRuns.filter(r => r.category === "TEST_FAILURE");
  $("#results-lede").textContent = `${U.n} cases in Uptake mode, one Bob run each, every run shown. ${testCases.length} are test failures, where the library's behaviour changed: no published system has attempted these. "Unblocked" means repaired, or escalated with a one-approval patch that Uptake proved green. "Silent edits" means tests or build files changed without being proposed for review.`;

  // Dot plot: repair rate and cheat rate, with Wilson intervals
  const rows = [
    { label: "Uptake mode · unblocked", k: U.resolved, n: U.n, ci: U.resolvedCI, color: "var(--ok)" },
    { label: "Rules only · unblocked", k: P.resolved, n: P.n, ci: P.resolvedCI, color: "var(--ok)" },
    { label: "No Uptake · unblocked", k: Bare.resolved, n: Bare.n, ci: Bare.resolvedCI, color: "var(--muted)" },
    { label: "Byam (best of 40) · same cases", k: ov.byamSolved, n: ov.n, ci: null, color: "var(--esc)" },
    { label: "Uptake mode · silent edits", k: U.silentEdits, n: U.n, ci: null, color: "var(--ok)" },
    { label: "Rules only · silent edits", k: P.silentEdits, n: P.n, ci: null, color: "var(--ok)" },
    { label: "No Uptake · silent edits", k: Bare.silentEdits, n: Bare.n, ci: null, color: "var(--bad)" },
  ].filter(r => r.n);
  const W = 900, L = 260, R = 60, rowH = 44, H = rows.length * rowH + 40, x = v => L + v * (W - L - R);
  let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Repair and cheat rates with 95% intervals">`;
  [0, .25, .5, .75, 1].forEach(t => { svg += `<line class="axis" x1="${x(t)}" x2="${x(t)}" y1="10" y2="${H - 26}"/><text class="lbl" x="${x(t)}" y="${H - 8}" text-anchor="middle">${pct(t)}</text>`; });
  rows.forEach((r, i) => {
    const y = 30 + i * rowH, p = r.k / r.n;
    svg += `<text x="0" y="${y + 4}" font-size="14">${esc(r.label)}</text>`;
    if (r.ci) svg += `<line x1="${x(r.ci[0])}" x2="${x(r.ci[1])}" y1="${y}" y2="${y}" stroke="${r.color}" stroke-width="2" opacity=".55"/>`;
    svg += `<circle cx="${x(p)}" cy="${y}" r="7" fill="${r.color}"/><text x="${x(p) + 14}" y="${y + 4}" font-size="13" font-family="var(--mono)">${r.k}/${r.n}</text>`;
  });
  $("#chart").innerHTML = svg + "</svg>";
  $("#chart-desc").textContent = rows.map(r => `${r.label}: ${r.k} of ${r.n}`).join(". ");

  // Table
  const tbody = $("#results-table tbody");
  tbody.innerHTML = uRuns.map(r => {
    const p = plainOf(r.name);
    const byam = r.byam === "solved" ? "✓ solved" : r.byam === "unsolved" ? "✗ unsolved" : `<span class="muted">–</span>`;
    const l4 = r.log4shell.length ? `<span class="tag">LOG4SHELL</span>` : "";
    return `<tr tabindex="0" data-name="${esc(r.name)}">
      <td><b>${esc(r.name)}</b>${l4}</td>
      <td class="dep">${esc(short(r.dependency))}<span class="ver">${esc(r.from)} → ${esc(r.to)}</span></td>
      <td class="num">${r.advisories.length}</td>
      <td class="muted nowrap">${r.category === "TEST_FAILURE" ? "tests" : "compile"}</td>
      <td>${badge(r.verdict, r)}</td>
      <td class="num">${r.tests.run}/${r.testsBefore}</td>
      <td>${p ? badge(p.verdict, p) : badge(null)}</td>
      <td>${byam}</td>
      <td class="num">${r.cost.toFixed(2)}</td></tr>`;
  }).join("");
  tbody.addEventListener("click", e => { const tr = e.target.closest("tr"); if (tr) open(tr.dataset.name, true); });
  tbody.addEventListener("keydown", e => { if (e.key === "Enter") { const tr = e.target.closest("tr"); if (tr) open(tr.dataset.name, true); } });

  // Controlled comparison: the same cases through three setups
  if (D.shared?.length) {
    const cell = a => {
      const proven = a.verdict === "ESCALATED" && a.proven;
      const detail = a.violations.map(v => (v.dependencyChanges || []).filter(c => c.change === "downgraded" || c.change === "removed")
        .map(c => c.change === "downgraded" ? `${c.dependency.split(":")[1]} ${c.from} → ${c.to}` : `removed ${c.dependency.split(":")[1]}`).join(", ")
        || `${v.kind.replace(/_/g, " ")}: ${v.file.split("/").pop()}`).join("; ");
      return `${badge(a.verdict, { proposal: { provenGreen: proven } })}${detail ? `<div class="cmp-detail">${esc(detail)}</div>` : ""}`;
    };
    $("#compare-table tbody").innerHTML = D.shared.map(s => `<tr><td><b>${esc(s.name)}</b>${s.log4shell ? '<span class="tag">LOG4SHELL</span>' : ""}</td>
      <td>${cell(s.uptake)}</td><td>${cell(s.plain)}</td><td>${cell(s.bare)}</td></tr>`).join("");
  } else { $("#compare").remove(); }

  // Case explorer
  const picker = $("#picker");
  picker.innerHTML = uRuns.map(r => `<button role="tab" aria-selected="false" data-name="${esc(r.name)}"><span class="dot v-${r.verdict}"></span>${esc(r.name)}${r.log4shell.length ? " · Log4Shell" : ""}</button>`).join("");
  picker.addEventListener("click", e => { const b = e.target.closest("button"); if (b) open(b.dataset.name); });

  function load(key) {
    return new Promise(res => {
      if (window.UPTAKE_CASE?.[key]) return res(window.UPTAKE_CASE[key]);
      const s = document.createElement("script");
      s.src = `cases/${key}.js`; s.onload = () => res(window.UPTAKE_CASE?.[key]); s.onerror = () => res(null);
      document.head.appendChild(s);
    });
  }

  function renderDiff(patch) {
    if (!patch) return `<p class="muted">No code changes.</p>`;
    return `<div class="diff">` + patch.split("\n").filter(l => !/^(index |new file|deleted file|--- |similarity)/.test(l)).map(l => {
      if (l.startsWith("diff --git")) return `<div class="file">${esc(l.replace(/^diff --git a\/(\S+).*$/, "$1"))}</div>`;
      if (l.startsWith("+++ ")) return "";
      if (l.startsWith("@@")) return `<div class="hunk">${esc(l)}</div>`;
      if (l.startsWith("+")) return `<div class="add">${esc(l.slice(1))}</div>`;
      if (l.startsWith("-")) return `<div class="del">${esc(l.slice(1))}</div>`;
      return `<div class="ctx">${esc(l.slice(1))}</div>`;
    }).join("") + `</div>`;
  }

  function md(text) {
    return esc(text).split("\n").map(l => {
      if (/^#{1,3} /.test(l)) return `<h3>${l.replace(/^#+ /, "")}</h3>`;
      if (/^\s*[-*] /.test(l)) return `<li>${l.replace(/^\s*[-*] /, "")}</li>`;
      return l.trim() ? `<p>${l}</p>` : "";
    }).join("").replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }

  function renderReplay(steps) {
    return `<ol class="replay" id="replay">` + steps.map((s, i) => {
      if (s.kind === "call") {
        const p = Object.entries(s.params || {}).map(([k, v]) => `${k}: ${typeof v === "string" ? v : JSON.stringify(v)}`).join("\n");
        return `<li class="call" data-i="${i}"><span class="tool">${esc(s.tool)}</span>${p ? `<div class="res">${esc(p.slice(0, 700))}</div>` : ""}</li>`;
      }
      if (s.kind === "result") return `<li class="result ${s.ok ? "ok" : "err"}" data-i="${i}"><div class="res">${esc(s.text.slice(0, 500))}</div></li>`;
      return `<li class="say" data-i="${i}">${esc(s.text.slice(0, 700))}</li>`;
    }).join("") + `</ol>`;
  }

  async function open(name, scroll) {
    [...picker.children].forEach(b => b.setAttribute("aria-selected", String(b.dataset.name === name)));
    const box = $("#case");
    const c = await load(`${name}__uptake`);
    if (!c) { box.innerHTML = `<p class="muted" style="padding:24px">Case data missing.</p>`; return; }
    const p = plainOf(name);
    const cves = c.log4shell.length ? c.log4shell.join(", ") : `${c.advisories.length} advisories`;
    box.innerHTML = `
      <div class="case-head">
        <div><h3>${esc(c.name)} · ${esc(short(c.dependency))} ${esc(c.from)} → ${esc(c.to)}</h3>
          <p class="meta">Fixes ${esc(cves)} · broke as: ${c.category === "TEST_FAILURE" ? "test failures" : "compile errors"} · BUMP case <code>${esc(c.caseId.slice(0, 10))}</code></p>
          ${badge(c.verdict, c)} ${p ? `<span class="muted" style="margin-left:8px;font-size:13px">Rules-only Bob on the same case: </span>${badge(p.verdict, p)}` : ""}</div>
        <div class="kv"><div><b>${c.tests.run}/${c.testsBefore}</b>tests passing</div><div><b>${c.violations.length}</b>violations</div><div><b>${c.toolCalls}</b>Bob tool calls</div><div><b>${c.cost.toFixed(2)}</b>Bobcoins</div><div><b>${c.seconds}s</b>Bob time</div></div>
      </div>
      <div class="panes">
        <div class="pane"><h4>What Bob did <span class="ctrls"><button type="button" id="step">Step</button><button type="button" id="all">Show all</button></span></h4>${renderReplay(c.replay)}</div>
        <div class="pane"><h4>The fix</h4>${c.patch ? renderDiff(c.patch) : `<p class="muted">Bob changed no production code${c.proposedPatch ? ": the fix needs a file it may not edit, so it proposed a patch instead." : "."}</p>`}
          ${c.proposedPatch ? `<h4 style="margin-top:20px">Proposed patch for one-click approval
            ${c.proposal?.provenGreen ? `<span class="verdict v-REPAIRED">✓ proven: ${c.proposal.tests.run}/${c.testsBefore} tests green${c.proposal.verifiedOnline ? " (online)" : ""}</span>` : `<span class="verdict v-FAILED">not proven</span>`}</h4>${renderDiff(c.proposedPatch)}` : ""}
          ${c.escalation ? `<h4 style="margin-top:20px">Escalation</h4><div class="prose">${md(c.escalation)}</div>` : ""}
          ${c.rationale ? `<h4 style="margin-top:20px">Bob's rationale</h4><div class="prose">${md(c.rationale)}</div>` : ""}
        </div>
      </div>
      <div class="pane" style="border-top:1px solid var(--border)"><h4>Upgrade receipt</h4><div class="receipt">${esc(c.receiptMd)}</div>
        <div class="verify"><code>python -m uptake verify receipts/${esc(c.name)}__uptake</code><button class="copy" type="button" data-copy="python -m uptake verify receipts/${esc(c.name)}__uptake">Copy</button>
        <span class="muted" style="font-size:13px">Re-applies the patch (sha256 <code>${esc(c.patchSha256.slice(0, 12))}…</code>) to a fresh copy and rebuilds offline.</span></div></div>`;
    const items = [...box.querySelectorAll("#replay li")];
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let shown = reduce ? items.length : Math.min(items.length, 6);
    const sync = () => items.forEach((li, i) => li.classList.toggle("hidden", i >= shown));
    sync();
    $("#step", box).onclick = () => { shown = Math.min(items.length, shown + 1); sync(); items[shown - 1]?.scrollIntoView({ block: "nearest" }); };
    $("#all", box).onclick = () => { shown = items.length; sync(); };
    box.querySelector(".copy").onclick = e => { navigator.clipboard?.writeText(e.target.dataset.copy); e.target.textContent = "Copied"; };
    if (scroll) $("#explore").scrollIntoView();
  }

  const first = uRuns.find(r => r.log4shell.length && r.verdict.startsWith("REPAIRED")) || uRuns.find(r => r.verdict.startsWith("REPAIRED")) || uRuns[0];
  if (first) open(first.name);
  $("#generated").textContent = `Data generated ${D.generated} from bench/runs by bench/report.py.`;
})();
