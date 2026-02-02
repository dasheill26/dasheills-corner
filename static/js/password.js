(() => {
  const pw = document.getElementById("password");
  const bar = document.getElementById("pwBar");
  const label = document.getElementById("pwLabel");
  const hint = document.getElementById("pwHint");
  const meter = document.querySelector(".pw-meter");

  // Eye toggle (optional)
  document.querySelectorAll('[data-toggle="password"]').forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!pw) return;
      pw.type = pw.type === "password" ? "text" : "password";
    });
  });

  if (!pw || !bar || !label || !hint || !meter) return;

  const hasLower = (s) => /[a-z]/.test(s);
  const hasUpper = (s) => /[A-Z]/.test(s);
  const hasNum = (s) => /[0-9]/.test(s);
  const hasSym = (s) => /[^A-Za-z0-9]/.test(s);

  function scorePassword(s) {
    if (!s) return { score: 0, text: "—", colorClass: "is-none", hint: "Use 8+ chars, upper/lower, number, symbol." };

    let score = 0;

    // Length
    if (s.length >= 8) score++;
    if (s.length >= 12) score++;
    if (s.length >= 16) score++;

    // Variety
    let variety = 0;
    if (hasLower(s)) variety++;
    if (hasUpper(s)) variety++;
    if (hasNum(s)) variety++;
    if (hasSym(s)) variety++;
    if (variety >= 2) score++;
    if (variety >= 3) score++;
    if (variety >= 4) score++;

    // Penalties (very common patterns)
    const lower = s.toLowerCase();
    if (/^(password|qwerty|123456|letmein|admin)/.test(lower)) score -= 2;
    if (/^(.)\1+$/.test(s)) score -= 2; // all same char
    if (/1234|abcd|qwer/.test(lower)) score -= 1;

    // Clamp 0..4
    score = Math.max(0, Math.min(4, score));

    let text = "Weak";
    let colorClass = "is-weak";
    let h = "Add more length + mix letters/numbers.";

    if (score === 0) { text = "—"; colorClass = "is-none"; }
    if (score === 1) { text = "Weak"; colorClass = "is-weak"; }
    if (score === 2) { text = "Okay"; colorClass = "is-ok"; h = "Good start — add a symbol or more length."; }
    if (score === 3) { text = "Strong"; colorClass = "is-strong"; h = "Nice — strong password."; }
    if (score === 4) { text = "Very strong"; colorClass = "is-very-strong"; h = "Excellent — very strong password."; }

    // Extra hint: show missing rules for your coursework checklist
    const missing = [];
    if (s.length < 8) missing.push("8+ chars");
    if (!hasLower(s)) missing.push("lowercase");
    if (!hasUpper(s)) missing.push("uppercase");
    if (!hasNum(s)) missing.push("number");
    if (missing.length) h = `Add: ${missing.join(", ")}.`;

    return { score, text, colorClass, hint: h };
  }

  function render() {
    const { score, text, colorClass, hint: h } = scorePassword(pw.value);

    // meter width: 0..4
    const pct = (score / 4) * 100;
    bar.style.width = `${pct}%`;

    // classes
    meter.classList.remove("is-none", "is-weak", "is-ok", "is-strong", "is-very-strong");
    meter.classList.add(colorClass);

    meter.setAttribute("aria-valuenow", String(score));
    label.textContent = `Strength: ${text}`;
    hint.textContent = h;
  }

  pw.addEventListener("input", render);
  pw.addEventListener("blur", render);
  render();
})();
