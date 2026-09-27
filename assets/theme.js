// Colour scheme (E-5): report system changes to the Dash store "theme"; the initial value comes
// from a clientside callback. Before printing the charts switch to the light template.
(function () {
  const query = window.matchMedia("(prefers-color-scheme: dark)");
  function report(mode) {
    if (window.dash_clientside && window.dash_clientside.set_props) {
      window.dash_clientside.set_props("theme", { data: mode });
    }
  }
  query.addEventListener("change", function (event) { report(event.matches ? "dark" : "light"); });
  window.addEventListener("beforeprint", function () { report("light"); });
  window.addEventListener("afterprint", function () { report(query.matches ? "dark" : "light"); });
})();
