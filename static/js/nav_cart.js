(function () {
  function sumQty(cart) {
    return (cart || []).reduce((a, it) => a + (parseInt(it.qty || 0, 10) || 0), 0);
  }

  window.DC = window.DC || {};

  window.DC.toast = function (msg) {
    const el = document.getElementById("globalToast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(window.__dc_toast);
    window.__dc_toast = setTimeout(() => el.classList.remove("show"), 1400);
  };

  window.DC.setCartBadgeFromCart = function (cart) {
    const count = sumQty(cart);
    const badge = document.getElementById("navCartCount");
    if (!badge) return;
    if (count <= 0) {
      badge.style.display = "none";
      badge.textContent = "0";
    } else {
      badge.style.display = "inline-flex";
      badge.textContent = String(count);
      badge.classList.add("pop");
      setTimeout(() => badge.classList.remove("pop"), 180);
    }
  };

  window.DC.syncCartBadge = async function () {
    try {
      const res = await fetch("/api/cart/summary", { cache: "no-store" });
      if (!res.ok) return;
      const data = await res.json();
      const badge = document.getElementById("navCartCount");
      if (!badge) return;
      if ((data.count || 0) <= 0) {
        badge.style.display = "none";
        badge.textContent = "0";
      } else {
        badge.style.display = "inline-flex";
        badge.textContent = String(data.count);
      }
    } catch (_) {}
  };

  // on every page load, sync badge
  document.addEventListener("DOMContentLoaded", () => {
    window.DC.syncCartBadge();
  });
})();
