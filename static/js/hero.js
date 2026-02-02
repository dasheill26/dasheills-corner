(function () {
  const slides = Array.from(document.querySelectorAll(".hero-slide"));
  const dots = Array.from(document.querySelectorAll(".hero-dot"));
  const prev = document.querySelector(".hero-prev");
  const next = document.querySelector(".hero-next");

  if (!slides.length) return;

  let i = 0;
  let timer = null;

  function setActive(idx) {
    i = (idx + slides.length) % slides.length;

    slides.forEach((s, k) => s.classList.toggle("is-active", k === i));
    dots.forEach((d, k) => d.classList.toggle("is-active", k === i));
  }

  function start() {
    stop();
    timer = setInterval(() => setActive(i + 1), 4500);
  }

  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  // Buttons
  if (prev) prev.addEventListener("click", () => { setActive(i - 1); start(); });
  if (next) next.addEventListener("click", () => { setActive(i + 1); start(); });

  // Dots
  dots.forEach((d) => {
    d.addEventListener("click", () => {
      const idx = parseInt(d.dataset.slide || "0", 10);
      setActive(idx);
      start();
    });
  });

  // Pause on hover (nice UX)
  const slider = document.querySelector(".hero-slider");
  if (slider) {
    slider.addEventListener("mouseenter", stop);
    slider.addEventListener("mouseleave", start);
  }

  setActive(0);
  start();
})();
