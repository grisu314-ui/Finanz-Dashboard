// y axis fitted to the visible part of a time series (E-88): after zoom, range buttons, double
// click and the 5-minute refresh the lowest visible value sits at the bottom, the highest at the
// top. Only charts with layout.meta.autoY; fixed scales (percentiles, scores, levels) keep theirs.
// A y range the user dragged is kept until the x range changes. Same computation as fitted_range
// in fever/web/figures.py, which sets the range of the first view.
(function () {
  "use strict";
  const PADDING = 0.05;

  function day(value) {
    return typeof value === "number" ? new Date(value).toISOString().slice(0, 10) : String(value).slice(0, 10);
  }

  // Per trace the values inside the window, plus the last one before and the first one after it.
  function fitted(gd) {
    const xaxis = gd._fullLayout && gd._fullLayout.xaxis;
    if (!xaxis || !xaxis.range) { return null; }
    const x0 = day(xaxis.range[0]), x1 = day(xaxis.range[1]);
    let low = Infinity, high = -Infinity;
    (gd.data || []).forEach(function (trace) {
      if ((trace.yaxis && trace.yaxis !== "y") || trace.visible === false || trace.visible === "legendonly") { return; }
      const xs = trace.x || [], ys = trace.y || [];
      let before = null;
      for (let i = 0; i < xs.length; i++) {
        const y = ys[i];
        if (y === null || y === undefined || Number.isNaN(y)) { continue; }
        const d = String(xs[i]).slice(0, 10);
        if (d < x0) { before = y; continue; }
        low = Math.min(low, y);
        high = Math.max(high, y);
        if (d > x1) { break; }
      }
      if (before !== null) { low = Math.min(low, before); high = Math.max(high, before); }
    });
    if (low === Infinity) { return null; }
    const span = high - low;
    const pad = span > 0 ? span * PADDING : (Math.abs(high) * PADDING || 1);
    return [low - pad, high + pad];
  }

  function same(a, b) {
    return Boolean(a && b) && [0, 1].every(function (i) {
      return Math.abs(a[i] - b[i]) <= 1e-9 * Math.max(1, Math.abs(b[i]));
    });
  }

  function fit(gd) {
    const meta = gd.layout && gd.layout.meta;
    if (!meta || !meta.autoY || gd.feverUserY || gd.feverFitting || !window.Plotly) { return; }
    const range = fitted(gd);
    const yaxis = gd._fullLayout && gd._fullLayout.yaxis;
    if (!range || !yaxis || same(yaxis.range, range)) { return; }
    gd.feverFitting = true;
    const done = function () { gd.feverFitting = false; fit(gd); };  // an x change meanwhile is caught here
    window.Plotly.relayout(gd, {"yaxis.range": range}).then(done, done);
  }

  function watch(gd) {
    gd.dataset.autoY = "1";
    gd.on("plotly_relayout", function (event) {
      if (gd.feverFitting || !event) { return; }
      const keys = Object.keys(event);
      if (keys.some(function (key) { return key.indexOf("yaxis.range") === 0; })) {
        gd.feverUserY = true;  // dragged by the user (box zoom, pan): keep it
      } else if (keys.some(function (key) { return key.indexOf("xaxis.range") === 0 || key === "xaxis.autorange"; })) {
        gd.feverUserY = false;
        fit(gd);
      }
    });
    gd.on("plotly_doubleclick", function () { gd.feverUserY = false; fit(gd); });
    gd.on("plotly_afterplot", function () { fit(gd); });  // also after the refresh (Plotly.react)
  }

  function scan() {
    document.querySelectorAll(".js-plotly-plot").forEach(function (gd) {
      if (gd.dataset.autoY !== "1" && typeof gd.on === "function") { watch(gd); fit(gd); }
    });
  }

  let queued = false;
  new MutationObserver(function () {
    if (queued) { return; }
    queued = true;
    window.requestAnimationFrame(function () { queued = false; scan(); });
  }).observe(document.documentElement, {childList: true, subtree: true});
})();
