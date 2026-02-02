(function () {
  const money = (pence) => "£" + (pence / 100).toFixed(2);

  const toastEl = document.getElementById("cartToast");
  const subtotalEl = document.getElementById("cartSubtotal");
  const totalEl = document.getElementById("cartTotal");

  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => toastEl.classList.remove("show"), 1400);
  }

  function recalcTotals() {
    let subtotal = 0;
    document.querySelectorAll(".cart-item").forEach((row) => {
      const price = parseInt(row.dataset.price || "0", 10);
      const qty = parseInt(row.querySelector("[data-qty]")?.textContent || "0", 10);
      subtotal += price * qty;
    });

    if (subtotalEl) subtotalEl.textContent = money(subtotal);
    if (totalEl) totalEl.textContent = money(subtotal);
  }

  async function setQty(itemId, qty) {
    const res = await fetch("/api/cart/setqty", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId, qty }),
    });
    if (!res.ok) throw new Error("Failed to update cart");
    return res.json();
  }

  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const row = btn.closest(".cart-item");
    if (!row) return;

    const itemId = row.dataset.id;
    const price = parseInt(row.dataset.price || "0", 10);

    const qtyEl = row.querySelector("[data-qty]");
    const lineTotalEl = row.querySelector("[data-line-total]");
    let qty = parseInt(qtyEl?.textContent || "0", 10);

    const action = btn.dataset.action;
    const nextQty = action === "inc" ? qty + 1 : qty - 1;

    // optimistic UI (feels fast)
    if (nextQty <= 0) {
      row.classList.add("removing");
    } else {
      qtyEl.textContent = String(nextQty);
      if (lineTotalEl) lineTotalEl.textContent = money(price * nextQty);
      row.classList.add("pulse");
      setTimeout(() => row.classList.remove("pulse"), 220);
    }
    recalcTotals();

    try {
      const data = await setQty(itemId, nextQty);

      // server is source of truth
      if (nextQty <= 0) {
        row.remove();
        toast("Removed from cart");
      } else {
        toast("Cart updated");
      }

      // if cart empty after removal → reload to show empty state
      if ((data.cart || []).length === 0) {
        window.location.reload();
        return;
      }

      // update subtotal from server (more accurate)
      if (typeof data.subtotalPence === "number") {
        if (subtotalEl) subtotalEl.textContent = money(data.subtotalPence);
        if (totalEl) totalEl.textContent = money(data.subtotalPence);
      }
    } catch (err) {
      // rollback simplest: refresh to restore correct UI
      toast("Couldn’t update. Refreshing…");
      setTimeout(() => window.location.reload(), 500);
    }
  });

  // initial calc safety
  recalcTotals();
})();
