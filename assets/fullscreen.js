// Full screen per chart card as a CSS overlay (7.1): the button or ESC toggles it.
(function () {
  function toggle(card, on) {
    card.classList.toggle("is-fullscreen", on);
    const button = card.querySelector(".fullscreen-toggle");
    if (button) { button.textContent = on ? "Schließen" : "Vollbild"; }
    window.dispatchEvent(new Event("resize"));  // Plotly follows via responsive
  }
  document.addEventListener("click", function (event) {
    const button = event.target.closest(".fullscreen-toggle");
    if (!button) { return; }
    const card = button.closest(".chart-card");
    toggle(card, !card.classList.contains("is-fullscreen"));
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") { return; }
    document.querySelectorAll(".chart-card.is-fullscreen").forEach(function (card) { toggle(card, false); });
  });
})();
