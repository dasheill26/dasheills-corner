/* =========================
   Dasheill's Corner — Homepage Hero Slider
   Auto-shuffle every 3s, arrows + dots
   ========================= */

(function () {
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(() => {
    const root = document.getElementById("dcHero");
    if (!root) return;

    const bg = document.getElementById("dcHeroBg");
    const img = document.getElementById("dcHeroImg");
    const dotsWrap = document.getElementById("dcHeroDots");
    const prevBtn = root.querySelector(".dc-hero-prev");
    const nextBtn = root.querySelector(".dc-hero-next");

    const intervalMs = Number(root.getAttribute("data-interval")) || 3000;

    // Read slide sources from hidden <img data-hero-src="...">
    const sources = Array.from(root.querySelectorAll(".dc-hero-sources img"))
      .map(el => ({
        src: el.getAttribute("data-hero-src"),
        alt: el.getAttribute("alt") || "Dasheill's Corner promo"
      }))
      .filter(x => !!x.src);

    if (sources.length < 1) return;

    let index = 0;
    let timer = null;
    let paused = false;

    // Build dots
    dotsWrap.innerHTML = "";
    const dots = sources.map((_, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "dc-dot" + (i === 0 ? " is-active" : "");
      b.setAttribute("aria-label", `Go to slide ${i + 1}`);
      b.addEventListener("click", () => {
        goTo(i);
        restart();
      });
      dotsWrap.appendChild(b);
      return b;
    });

    function render(i) {
      const s = sources[i];

      // Foreground image (contain = show whole image)
      img.src = s.src;
      img.alt = s.alt;

      // Blurred fill background (cover) to remove side bars
      bg.style.backgroundImage = `url("${s.src}")`;

      dots.forEach((d, di) => {
        d.classList.toggle("is-active", di === i);
      });
    }

    function goTo(i) {
      index = (i + sources.length) % sources.length;
      render(index);
    }

    function next() {
      goTo(index + 1);
    }

    function prev() {
      goTo(index - 1);
    }

    function start() {
      stop();
      timer = window.setInterval(() => {
        if (!paused) next();
      }, intervalMs);
    }

    function stop() {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    }

    function restart() {
      start();
    }

    // Hook arrows
    if (nextBtn) nextBtn.addEventListener("click", () => { next(); restart(); });
    if (prevBtn) prevBtn.addEventListener("click", () => { prev(); restart(); });

    // Pause on hover/focus
    root.addEventListener("mouseenter", () => { paused = true; });
    root.addEventListener("mouseleave", () => { paused = false; });

    root.addEventListener("focusin", () => { paused = true; });
    root.addEventListener("focusout", () => { paused = false; });

    // Init
    render(index);
    start();
  });
})();
