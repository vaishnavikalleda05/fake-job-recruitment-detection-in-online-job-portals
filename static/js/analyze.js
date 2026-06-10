let lastResult = null;

async function analyzeJob() {
  const raw     = document.getElementById("jobText").value.trim();
  const btn     = document.getElementById("analyzeBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("spinner");
  const results = document.getElementById("results");
  const defSt   = document.getElementById("defaultState");
  const errEl   = document.getElementById("errorMsg");

  if (!raw || raw.length < 30) { showError("Please paste a job posting with enough content."); return; }

  // Loading
  btn.disabled = true;
  btnText.textContent = "Analyzing...";
  spinner.classList.remove("hidden");
  results.classList.add("hidden");
  defSt.classList.remove("hidden");
  errEl.classList.add("hidden");

  try {
    const res  = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: raw }),
    });
    const data = await res.json();
    if (!res.ok) { showError(data.error || "Analysis failed."); return; }

    lastResult = data;
    renderResults(data);
    defSt.classList.add("hidden");
    results.classList.remove("hidden");
    results.scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (e) {
    showError("Network error. Is the Flask server running?");
  } finally {
    btn.disabled = false;
    btnText.textContent = "Run Detection";
    spinner.classList.add("hidden");
  }
}


function renderResults(data) {
  renderChips(data.extracted);
  renderVerdict(data.analysis, data.ml);
  renderGauge(data.analysis.risk_score);
  renderProgressBar(data.analysis.risk_score);
  document.getElementById("riskMeta").textContent =
    `ML confidence: ${data.ml.probability}% fake probability  ·  ${data.analysis.rule_flags_count} rule flags triggered`;
  renderFlags(data.analysis.red_flags);
  renderValidation(data.validation, data.extracted);
}


function renderChips(ex) {
  const fields = [
    ["💼 Title",    ex.title],
    ["🏢 Company",  ex.company_name],
    ["📍 Location", ex.location],
    ["💰 Salary",   ex.salary_range],
    ["📧 Email",    ex.contact_email],
    ["📞 Phone",    ex.contact_phone],
    ["🌐 Website",  ex.company_website],
    ["🕐 Type",     ex.employment_type],
    ["📅 Exp",      ex.experience],
  ];
  document.getElementById("chips").innerHTML = fields.map(([l, v]) =>
    `<span class="chip${!v ? ' dim' : ''}"><span class="chip-label">${l}</span>${v || "Not detected"}</span>`
  ).join("");
}


function renderVerdict(an, ml) {
  const box  = document.getElementById("verdictBox");
  const text = document.getElementById("verdictText");
  const pill = document.getElementById("riskPill");

  box.className = "verdict-box";
  if (an.verdict_color === "red")         box.classList.add("verdict-fake");
  else if (an.verdict_color === "orange") box.classList.add("verdict-warn");
  else                                     box.classList.add("verdict-safe");

  text.textContent = an.verdict;

  pill.className = "risk-pill";
  if (an.risk_score >= 65)      pill.classList.add("risk-high");
  else if (an.risk_score >= 35) pill.classList.add("risk-medium");
  else                           pill.classList.add("risk-low");
  pill.textContent = `Risk Score: ${an.risk_score}%`;
}


function renderGauge(score) {
  const path  = document.getElementById("gaugePath");
  const num   = document.getElementById("gaugeNum");
  const total = 173;
  const off   = total - (score / 100) * total;
  const color = score >= 65 ? "#ff2d55" : score >= 35 ? "#f39c12" : "#2ecc71";

  path.style.stroke           = color;
  path.style.strokeDashoffset = off;
  path.style.transition       = "stroke-dashoffset 1s ease, stroke 0.3s";
  num.textContent = score + "%";
  num.style.color = color;
}


function renderProgressBar(score) {
  const bar   = document.getElementById("pbar");
  const color = score >= 65 ? "#ff2d55" : score >= 35 ? "#f39c12" : "#2ecc71";
  setTimeout(() => {
    bar.style.width      = score + "%";
    bar.style.background = `linear-gradient(90deg, #0055cc, ${color})`;
  }, 100);
}


function renderFlags(flags) {
  document.getElementById("flagCount").textContent = flags.length;
  if (!flags.length) {
    document.getElementById("flagsList").innerHTML = `<div class="v-ok" style="padding:12px">No red flags detected by rule engine.</div>`;
    return;
  }
  const icons = { HIGH:"⛔", MEDIUM:"⚠️", LOW:"ℹ️" };
  document.getElementById("flagsList").innerHTML = flags.map(f => `
    <div class="flag-card ${f.severity}">
      <div class="flag-card-title">${icons[f.severity]||"•"} [${f.severity}] ${f.name}</div>
      <div class="flag-card-msg">${f.message}</div>
      <div class="flag-card-det">${f.detail}</div>
    </div>
  `).join("");
}


function renderValidation(val, ex) {
  // Email
  const ev = val.email;
  let emailHtml;
  if (!ex.contact_email)    emailHtml = `<div class="v-info">No email detected in posting</div>`;
  else if (!ev.is_valid)    emailHtml = `<div class="v-err">❌ Invalid email format</div>`;
  else if (ev.is_free_domain) emailHtml = `<div class="v-warn">⚠️ Free domain: <code>${ev.domain}</code><br><small style="color:var(--text-mute)">Legitimate companies use official domains.</small></div>`;
  else                       emailHtml = `<div class="v-ok">✅ Official domain: <code>${ev.domain}</code></div>`;
  document.getElementById("emailVal").innerHTML = emailHtml;

  // Salary
  const sf = val.salary.flags;
  document.getElementById("salaryVal").innerHTML = !sf.length
    ? `<div class="v-info">No salary info detected</div>`
    : sf.map(f => `<div class="${f.includes("✅")?"v-ok":f.includes("🚨")?"v-err":"v-warn"}">${f}</div>`).join("");
}


function toggleReport() {
  document.getElementById("reportPanel").classList.toggle("hidden");
}

async function submitReport() {
  if (!lastResult) return;
  const reason = document.getElementById("reportReason").value;
  const ex = lastResult.extracted;
  const an = lastResult.analysis;

  const res = await fetch("/api/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_title: ex.title, company_name: ex.company_name,
      contact_email: ex.contact_email,
      job_description: document.getElementById("jobText").value.substring(0, 500),
      risk_score: an.risk_score, verdict: an.verdict,
      red_flags_count: an.rule_flags_count,
      reason: reason || "User reported",
    }),
  });
  const data = await res.json();
  document.getElementById("reportMsg").innerHTML = data.success
    ? `<span class="success-text">✅ Report submitted. Thank you for protecting others.</span>`
    : `<span class="error-text">❌ Could not save report.</span>`;
}

function clearAll() {
  document.getElementById("jobText").value = "";
  document.getElementById("results").classList.add("hidden");
  document.getElementById("defaultState").classList.remove("hidden");
  document.getElementById("errorMsg").classList.add("hidden");
  document.getElementById("pbar").style.width = "0%";
  lastResult = null;
}

function showError(msg) {
  const el = document.getElementById("errorMsg");
  el.textContent = msg;
  el.classList.remove("hidden");
  el.style.display = "block";
}
