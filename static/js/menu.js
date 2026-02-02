
(function () {
  const badge = document.getElementById("cartBadge");
  const toastEl = document.getElementById("uiToast");

  function showToast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(window.__uiToastTimer);
    window.__uiToastTimer = setTimeout(() => toastEl.classList.remove("show"), 1400);
  }

  function setBadgeCount(n) {
    if (!badge) return;
    const val = parseInt(n || 0, 10);
    badge.textContent = String(val);
    if (val > 0) badge.classList.add("show");
    else badge.classList.remove("show");
  }

  async function apiAdd(itemId, name, pricePence) {
    const res = await fetch("/api/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId, name, pricePence }),
    });
    if (!res.ok) throw new Error("Add failed");
    return res.json();
  }

  async function apiSetQty(itemId, qty) {
    const res = await fetch("/api/cart/setqty", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId, qty }),
    });
    if (!res.ok) throw new Error("Set qty failed");
    return res.json();
  }

  // Tabs
  const tabs = document.querySelectorAll(".tab[data-tab]");
  const sections = document.querySelectorAll(".menu-section[data-section]");
  function showSection(name) {
    sections.forEach((s) => {
      s.style.display = (s.dataset.section === name) ? "" : "none";
    });
    tabs.forEach((t) => t.classList.toggle("is-active", t.dataset.tab === name));
  }
  tabs.forEach((t) => t.addEventListener("click", () => showSection(t.dataset.tab)));
  showSection("Mains");

  // Search + availability filter
  const searchEl = document.getElementById("menuSearch");
  const onlyAvailEl = document.getElementById("onlyAvailable");

  function applyFilters() {
    const q = (searchEl?.value || "").trim().toLowerCase();
    const onlyAvail = !!onlyAvailEl?.checked;

    document.querySelectorAll(".menu-item").forEach((card) => {
      const name = (card.dataset.nameSearch || "");
      const desc = (card.dataset.descSearch || "");
      const avail = (card.dataset.available || "true") === "true";

      const matches = !q || name.includes(q) || desc.includes(q);
      const passesAvail = !onlyAvail || avail;

      card.style.display = (matches && passesAvail) ? "" : "none";
    });
  }

  if (searchEl) searchEl.addEventListener("input", applyFilters);
  if (onlyAvailEl) onlyAvailEl.addEventListener("change", applyFilters);

  // Add / Stepper
  document.addEventListener("click", async (e) => {
    const addBtn = e.target.closest(".add-btn");
    const stepBtn = e.target.closest("button[data-action]");

    // ADD
    if (addBtn) {
      const card = addBtn.closest(".menu-item");
      if (!card) return;

      const itemId = card.dataset.id;
      const name = card.dataset.name;
      const price = parseInt(card.dataset.price || "0", 10);

      try {
        const data = await apiAdd(itemId, name, price);
        setBadgeCount(data.cartCount || 0);

        const stepper = card.querySelector(".menu-stepper");
        const qtyEl = card.querySelector("[data-qty]");
        if (qtyEl) qtyEl.textContent = "1";

        addBtn.classList.add("hide");
        if (stepper) stepper.classList.remove("hide");

        card.classList.add("in-cart");
        showToast("Added to cart");
      } catch (err) {
        showToast("Couldn’t add. Try again.");
      }
      return;
    }

    // STEPPER +/- (menu)
    if (stepBtn && stepBtn.closest(".menu-item")) {
      const card = stepBtn.closest(".menu-item");
      if (!card) return;

      const action = stepBtn.dataset.action;
      const itemId = card.dataset.id;

      const qtyEl = card.querySelector("[data-qty]");
      const addBtn2 = card.querySelector(".add-btn");
      const stepper2 = card.querySelector(".menu-stepper");

      let qty = parseInt(qtyEl?.textContent || "0", 10);
      const nextQty = action === "inc" ? qty + 1 : qty - 1;

      // optimistic UI
      if (qtyEl) qtyEl.textContent = String(Math.max(0, nextQty));

      try {
        const data = await apiSetQty(itemId, nextQty);
        setBadgeCount(data.cartCount || 0);

        if (nextQty <= 0) {
          if (stepper2) stepper2.classList.add("hide");
          if (addBtn2) addBtn2.classList.remove("hide");
          card.classList.remove("in-cart");
          showToast("Removed from cart");
        } else {
          card.classList.add("in-cart");
          showToast("Cart updated");
        }
      } catch (err) {
        showToast("Couldn’t update. Refreshing…");
        setTimeout(() => window.location.reload(), 600);
      }
    }
  });
})();
