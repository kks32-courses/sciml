"""Build the second Representation page, kernels, families, and shapes that move.

The page follows Chapter 2 from the cooling fin onward. Its interactive figures
are the Function Studio's kernel, RKHS, Gaussian-process, particle, Gaussian-field,
and comparison labs, rewritten in the plain JavaScript lab pattern of the book's
notebooks (book/sciml_notebook/docs/sciml_labs.py) so they render inside the site's
own layout. The fin readings are the chapter's (seed 3), read from data/fin_readings.dat,
so every readout agrees with the chapter's script reports.

Run:  python3 build_kernels_page.py   (writes kernels-and-families.md here)
"""

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
NB_DOCS = HERE.parents[2] / "sciml_notebook" / "docs"
sys.path.insert(0, str(NB_DOCS))
from sciml_labs import lab_html, embed_lab  # noqa: E402

rows = [l.split() for l in (HERE / "data" / "fin_readings.dat").read_text().strip().split("\n")[1:]]
XS = "[" + ", ".join(r[0] for r in rows) + "]"
YS = "[" + ", ".join(f"{float(r[1]):.4f}" for r in rows) + "]"

SOLVE = r'''
  function solve(A, b){
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c] || 1e-12; for (let j = c; j <= n; j++) M[c][j] /= d;
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let j = c; j <= n; j++) M[r][j] -= f * M[c][j]; }
    }
    return M.map(r => r[n]);
  }
  const XS = ''' + XS + r''', YS = ''' + YS + r''';
  const Tfin = x => Math.exp(-1.5 * x) * (1 + 0.4 * Math.sin(3 * Math.PI * x));
'''

# --------------------------------------------------------------------------- A. kernel bumps
kernel_body = r'''
<div style="display:flex; gap:10px;">
  <div style="flex:1"><svg id="kb-sim" class="plot" viewBox="0 0 355 230"></svg></div>
  <div style="flex:1"><svg id="kb-fit" class="plot" viewBox="0 0 355 230"></svg></div>
</div>
<div class="slider-row" style="--slider-color: var(--blue)"><span>location x</span><input id="kb-x1" type="range" min="0.02" max="0.98" step="0.01" value="0.30"><output id="kb-x1v">0.30</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>location x&prime;</span><input id="kb-x2" type="range" min="0.02" max="0.98" step="0.01" value="0.45"><output id="kb-x2v">0.45</output></div>
<div class="slider-row" style="--slider-color: var(--green)"><span>length scale &ell;</span><input id="kb-l" type="range" min="0.04" max="0.40" step="0.01" value="0.15"><output id="kb-lv">0.15</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">similarity k(x, x&prime;)</span><span class="num" id="kb-k">0.000</span></div>
  <div class="readout"><span class="label">largest weight |&alpha;|</span><span class="num" id="kb-a">0.00</span></div>
  <div class="readout"><span class="label">interpolant at x = 0.7 (true 0.393)</span><span class="num" id="kb-v">0.000</span></div>
</div>
<p class="lab-note">Left, two kernel copies and their similarity. Right, one copy per fin reading (dashed) and the sum that passes through every reading (blue), against the true profile (dark dashed). Shorten &ell; and watch the sum collapse between sensors.</p>
<script>
(function(){''' + SOLVE + r'''
  const sS = document.getElementById("kb-sim"), sF = document.getElementById("kb-fit");
  const XA = L.scale(0, 1, 40, 345), YA = L.scale(-0.1, 1.2, 216, 14);
  L.axes(sS, XA, YA, {yMax: 1.2, ny: 2, xlabel: "x"});
  const XB = L.scale(0, 1, 40, 345), YB = L.scale(-1.2, 1.6, 216, 14);
  L.axes(sF, XB, YB, {yMax: 1.6, ny: 4, xlabel: "x", ylabel: "T"});
  const gS = L.el("g", {}, sS), gF = L.el("g", {}, sF);
  let x1 = 0.30, x2 = 0.45, ell = 0.15;
  const k = (a, b) => Math.exp(-(a - b) * (a - b) / (2 * ell * ell));
  function redraw(){
    gS.innerHTML = ""; gF.innerHTML = "";
    L.curve(gS, x => k(x, x1), XA, YA, {stroke: "var(--blue)", width: 3});
    L.curve(gS, x => k(x, x2), XA, YA, {stroke: "var(--orange)", width: 3});
    document.getElementById("kb-k").textContent = k(x1, x2).toFixed(3);
    const K = XS.map(a => XS.map(b => k(a, b)));
    const alpha = solve(K, YS);
    const fit = x => XS.reduce((s, xi, i) => s + alpha[i] * k(x, xi), 0);
    L.curve(gF, Tfin, XB, YB, {stroke: "var(--ink)", width: 1.8, dash: "6 6", n: 401});
    XS.forEach((xi, i) => L.curve(gF, x => alpha[i] * k(x, xi), XB, YB, {stroke: "var(--muted)", width: 1, dash: "4 4", opacity: 0.7}));
    L.curve(gF, fit, XB, YB, {stroke: "var(--blue)", width: 3, n: 401});
    XS.forEach((xi, i) => L.el("circle", {cx: XB(xi), cy: YB(YS[i]), r: 4, style: "fill: var(--red); stroke: var(--paper); stroke-width: 1"}, gF));
    document.getElementById("kb-a").textContent = Math.max(...alpha.map(Math.abs)).toFixed(2);
    document.getElementById("kb-v").textContent = fit(0.7).toFixed(3);
  }
  [["kb-x1", v => x1 = v], ["kb-x2", v => x2 = v], ["kb-l", v => ell = v]].forEach(([id, set]) => {
    document.getElementById(id).addEventListener("input", e => {
      set(parseFloat(e.target.value)); document.getElementById(id + "v").textContent = parseFloat(e.target.value).toFixed(2); redraw();
    });
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- B. RKHS builder
rkhs_body = r'''
<svg id="rk-plot" class="plot" viewBox="0 0 720 280"></svg>
<div style="display:flex; gap:14px; flex-wrap:wrap;">
  <div class="slider-row" style="flex:1; --slider-color: var(--blue)"><span>&alpha;&#8321; at 0.2</span><input id="rk-a1" type="range" min="-1" max="1" step="0.05" value="0.80"><output id="rk-a1v">0.80</output></div>
  <div class="slider-row" style="flex:1; --slider-color: var(--orange)"><span>&alpha;&#8322; at 0.5</span><input id="rk-a2" type="range" min="-1" max="1" step="0.05" value="-0.45"><output id="rk-a2v">-0.45</output></div>
  <div class="slider-row" style="flex:1; --slider-color: var(--green)"><span>&alpha;&#8323; at 0.8</span><input id="rk-a3" type="range" min="-1" max="1" step="0.05" value="0.65"><output id="rk-a3v">0.65</output></div>
</div>
<div class="slider-row" style="--slider-color: var(--red)"><span>probe x*</span><input id="rk-p" type="range" min="0.02" max="0.98" step="0.01" value="0.61"><output id="rk-pv">0.61</output></div>
<div class="slider-row" style="--slider-color: var(--green)"><span>length scale &ell;</span><input id="rk-l" type="range" min="0.06" max="0.32" step="0.01" value="0.16"><output id="rk-lv">0.16</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">f(x*) = &lang;f, k(x*,&middot;)&rang;<sub>k</sub></span><span class="num" id="rk-f">0.000</span></div>
  <div class="readout"><span class="label">&Vert;f&Vert;&#178;<sub>k</sub> = &alpha;&#7488;K&alpha;</span><span class="num" id="rk-n">0.000</span></div>
  <div class="readout"><span class="label">steepest slope, and the bound &Vert;f&Vert;<sub>k</sub>/&ell;</span><span class="num" id="rk-s">0.00 &le; 0.00</span></div>
</div>
<p class="lab-note">Three kernel copies (dashed) and their weighted sum (dark). The red probe reads f(x*), which the reproducing identity writes as an inner product with the copy centered at x*. The norm is a roughness measure, and the slope never exceeds the norm divided by the length scale.</p>
<script>
(function(){
  const svg = document.getElementById("rk-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.4, 1.4, 266, 14);
  L.axes(svg, X, Y, {yMax: 1.4, xlabel: "x", ylabel: "f(x)"});
  const g = L.el("g", {}, svg);
  const centers = [0.2, 0.5, 0.8], cols = ["var(--blue)", "var(--orange)", "var(--green)"];
  let alpha = [0.8, -0.45, 0.65], probe = 0.61, ell = 0.16;
  function redraw(){
    const k = (a, b) => Math.exp(-(a - b) * (a - b) / (2 * ell * ell));
    const f = x => alpha.reduce((s, q, i) => s + q * k(x, centers[i]), 0);
    g.innerHTML = "";
    centers.forEach((c, i) => L.curve(g, x => alpha[i] * k(x, c), X, Y, {stroke: cols[i], width: 2, dash: "7 7", opacity: 0.7}));
    L.curve(g, f, X, Y, {stroke: "var(--ink)", width: 3.5, n: 401});
    L.el("line", {x1: X(probe), x2: X(probe), y1: Y(1.4), y2: Y(-1.4), style: "stroke: var(--red); stroke-width: 1.5; stroke-dasharray: 5 5"}, g);
    L.el("circle", {cx: X(probe), cy: Y(f(probe)), r: 5, style: "fill: var(--red)"}, g);
    let n2 = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) n2 += alpha[i] * alpha[j] * k(centers[i], centers[j]);
    let slope = 0; for (let i = 1; i < 800; i++) { const a = (i - 1) / 800, b = i / 800; slope = Math.max(slope, Math.abs(f(b) - f(a)) * 800); }
    document.getElementById("rk-f").textContent = f(probe).toFixed(3);
    document.getElementById("rk-n").textContent = n2.toFixed(3);
    document.getElementById("rk-s").textContent = slope.toFixed(2) + " ≤ " + (Math.sqrt(Math.max(n2, 0)) / ell).toFixed(2);
  }
  [["rk-a1", v => alpha[0] = v], ["rk-a2", v => alpha[1] = v], ["rk-a3", v => alpha[2] = v], ["rk-p", v => probe = v], ["rk-l", v => ell = v]].forEach(([id, set]) => {
    document.getElementById(id).addEventListener("input", e => {
      set(parseFloat(e.target.value)); document.getElementById(id + "v").textContent = parseFloat(e.target.value).toFixed(2); redraw();
    });
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- C. Gaussian process on the fin
gp_body = r'''
<svg id="gp-plot" class="plot" viewBox="0 0 720 280"></svg>
<div class="slider-row" style="--slider-color: var(--green)"><span>length scale &ell;</span><input id="gp-l" type="range" min="0.05" max="0.40" step="0.01" value="0.15"><output id="gp-lv">0.15</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>noise level &sigma;</span><input id="gp-s" type="range" min="0.01" max="0.30" step="0.01" value="0.03"><output id="gp-sv">0.03</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">mean at x = 0.7 (true 0.393)</span><span class="num" id="gp-m">0.000</span></div>
  <div class="readout"><span class="label">two standard deviations in the gap, largest</span><span class="num" id="gp-b">0.000</span></div>
  <div class="readout"><span class="label">error of the mean, relative L&#178;</span><span class="num" id="gp-e">0.0%</span></div>
</div>
<p class="lab-note">The posterior mean (green) is the ridge curve with &lambda; = &sigma;&#178;, and the shaded band is two standard deviations of the posterior. The band narrows at the sensors, where the noise keeps it open, and swells in the unsensed stretch between 0.55 and 0.85. Try &ell; = 0.15, 0.075, and 0.31.</p>
<script>
(function(){''' + SOLVE + r'''
  const svg = document.getElementById("gp-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.8, 1.8, 266, 14);
  L.axes(svg, X, Y, {yMax: 1.8, ny: 4, xlabel: "x", ylabel: "T(x)"});
  const g = L.el("g", {}, svg);
  let ell = 0.15, sig = 0.03;
  function redraw(){
    const k = (a, b) => Math.exp(-(a - b) * (a - b) / (2 * ell * ell));
    const n = XS.length;
    const K = XS.map((a, i) => XS.map((b, j) => k(a, b) + (i === j ? sig * sig : 0)));
    const w = solve(K, YS);
    const mean = x => XS.reduce((s, xi, i) => s + w[i] * k(x, xi), 0);
    const sd = x => { const ks = XS.map(xi => k(x, xi)); const z = solve(K, ks); return Math.sqrt(Math.max(1e-9, 1 - ks.reduce((s, q, i) => s + q * z[i], 0))); };
    g.innerHTML = "";
    let d = "";
    for (let i = 0; i <= 200; i++) { const x = i / 200; d += (i ? " L" : "M") + X(x).toFixed(1) + " " + Y(mean(x) + 2 * sd(x)).toFixed(1); }
    for (let i = 200; i >= 0; i--) { const x = i / 200; d += " L" + X(x).toFixed(1) + " " + Y(mean(x) - 2 * sd(x)).toFixed(1); }
    L.el("path", {d: d + " Z", style: "fill: var(--green); opacity: 0.18"}, g);
    L.curve(g, Tfin, X, Y, {stroke: "var(--ink)", width: 1.8, dash: "6 6", n: 401});
    L.curve(g, mean, X, Y, {stroke: "var(--green)", width: 3, n: 401});
    XS.forEach((xi, i) => L.el("circle", {cx: X(xi), cy: Y(YS[i]), r: 4, style: "fill: var(--red); stroke: var(--paper); stroke-width: 1"}, g));
    let band = 0, num = 0, den = 0;
    for (let i = 0; i <= 400; i++) { const x = i / 400; const t = Tfin(x), m = mean(x); num += (m - t) ** 2; den += t * t; if (x >= 0.55 && x <= 0.85) band = Math.max(band, 2 * sd(x)); }
    document.getElementById("gp-m").textContent = mean(0.7).toFixed(3);
    document.getElementById("gp-b").textContent = band.toFixed(3);
    document.getElementById("gp-e").textContent = (100 * Math.sqrt(num / den)).toFixed(1) + "%";
  }
  [["gp-l", v => ell = v], ["gp-s", v => sig = v]].forEach(([id, set]) => {
    document.getElementById(id).addEventListener("input", e => {
      set(parseFloat(e.target.value)); document.getElementById(id + "v").textContent = parseFloat(e.target.value).toFixed(2); redraw();
    });
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- D. particles against a grid
particle_body = r'''
<svg id="pt-plot" class="plot" viewBox="0 0 760 320"></svg>
<div class="slider-row" style="--slider-color: var(--orange)"><span>material motion t</span><input id="pt-t" type="range" min="0" max="1" step="0.01" value="0.35"><output id="pt-tv">0.35</output></div>
<p class="lab-note">Left, a fixed grid whose cells stay where they are while a blob of material drifts through them, so its value must be re-interpolated onto the cells at every step. Right, carriers that move with the material and keep the value they started with, so nothing is interpolated until the field is read between them.</p>
<script>
(function(){
  const svg = document.getElementById("pt-plot");
  const gL = L.el("g", {transform: "translate(25 40)"}, svg), gR = L.el("g", {transform: "translate(405 40)"}, svg);
  const t1 = L.el("text", {x: 190, y: 22, class: "axis-label", "text-anchor": "middle"}, svg); t1.textContent = "fixed grid, values re-interpolated";
  const t2 = L.el("text", {x: 570, y: 22, class: "axis-label", "text-anchor": "middle"}, svg); t2.textContent = "carriers that move with the material";
  let t = 0.35;
  function redraw(){
    gL.innerHTML = ""; gR.innerHTML = "";
    L.el("rect", {width: 330, height: 240, style: "fill: none; stroke: var(--grid)"}, gL);
    for (let i = 0; i <= 8; i++) L.el("line", {x1: i * 41.25, y1: 0, x2: i * 41.25, y2: 240, class: "grid-line"}, gL);
    for (let i = 0; i <= 6; i++) L.el("line", {x1: 0, y1: i * 40, x2: 330, y2: i * 40, class: "grid-line"}, gL);
    L.el("circle", {cx: 145 + 34 * t, cy: 132 - 18 * t, r: 58, style: "fill: var(--blue); opacity: 0.18"}, gL);
    L.el("rect", {width: 330, height: 240, style: "fill: none; stroke: var(--grid)"}, gR);
    for (let i = 0; i < 48; i++) {
      const x = 0.08 + (i % 8) * 0.12, y = 0.12 + Math.floor(i / 8) * 0.15;
      const nx = x + 0.12 * t * Math.sin(Math.PI * y), ny = y - 0.08 * t * Math.sin(Math.PI * x);
      const v = Math.exp(-18 * ((x - 0.42) ** 2 + (y - 0.55) ** 2));
      L.el("circle", {cx: nx * 330, cy: (1 - ny) * 240, r: 4 + 5 * v, style: "fill: " + (v > 0.35 ? "var(--orange)" : "var(--blue)") + "; opacity: " + (0.45 + 0.5 * v)}, gR);
    }
  }
  document.getElementById("pt-t").addEventListener("input", e => { t = parseFloat(e.target.value); document.getElementById("pt-tv").textContent = t.toFixed(2); redraw(); });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- E. Gaussian field
splat_body = r'''
<svg id="sp-plot" class="plot" viewBox="0 0 720 300"></svg>
<div class="slider-row" style="--slider-color: var(--orange)"><span>Gaussian elements</span><input id="sp-n" type="range" min="1" max="6" step="1" value="3"><output id="sp-nv">3</output></div>
<div class="slider-row" style="--slider-color: var(--blue)"><span>width</span><input id="sp-w" type="range" min="0.05" max="0.25" step="0.01" value="0.13"><output id="sp-wv">0.13</output></div>
<p class="lab-note">A two-dimensional field built from Gaussian elements, each with a center, a width, and an amplitude. In a fit every one of these numbers is trainable, so the elements move to where the field varies, and the fit becomes a non-convex optimization.</p>
<script>
(function(){
  const svg = document.getElementById("sp-plot");
  const g = L.el("g", {}, svg);
  const splats = [[0.24, 0.68, 1], [0.47, 0.42, 0.8], [0.72, 0.66, 0.9], [0.66, 0.24, 0.58], [0.34, 0.2, 0.62], [0.84, 0.43, 0.48]];
  let n = 3, w = 0.13;
  function redraw(){
    g.innerHTML = "";
    L.el("rect", {x: 40, y: 30, width: 640, height: 252, style: "fill: none; stroke: var(--grid)"}, g);
    for (let iy = 0; iy < 18; iy++) for (let ix = 0; ix < 35; ix++) {
      const x = (ix + 0.5) / 35, y = (iy + 0.5) / 18;
      const v = splats.slice(0, n).reduce((s, q) => s + q[2] * Math.exp(-((x - q[0]) ** 2 + (y - q[1]) ** 2) / (2 * w * w)), 0);
      L.el("rect", {x: 40 + ix * 18.3, y: 30 + (17 - iy) * 14, width: 18.8, height: 14.5, style: "fill: " + (v > 0.85 ? "var(--orange)" : "var(--blue)") + "; opacity: " + Math.min(0.92, v * 0.7)}, g);
    }
    splats.slice(0, n).forEach((q, i) => {
      L.el("circle", {cx: 40 + q[0] * 640, cy: 30 + (1 - q[1]) * 252, r: 5, style: "fill: var(--ink); stroke: var(--paper); stroke-width: 2"}, g);
      const tt = L.el("text", {x: 49 + q[0] * 640, y: 26 + (1 - q[1]) * 252, class: "axis-label"}, g); tt.textContent = "g" + (i + 1);
    });
  }
  document.getElementById("sp-n").addEventListener("input", e => { n = parseInt(e.target.value); document.getElementById("sp-nv").textContent = n; redraw(); });
  document.getElementById("sp-w").addEventListener("input", e => { w = parseFloat(e.target.value); document.getElementById("sp-wv").textContent = w.toFixed(2); redraw(); });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- F. comparison tabs
compare_body = r'''
<div class="btn-row" id="cp-tabs" role="tablist"></div>
<div id="cp-panel" style="border:1px solid var(--grid); border-radius:10px; padding:12px 14px; margin-top:6px;"></div>
<p class="lab-note">The assumption says where a family applies, and its failure is the first thing to check when a fit goes wrong.</p>
<script>
(function(){
  const fams = [
    ["stations", "values at fixed points", "the analyst", "linear variation between stations", "smooth fields on a fixed geometry", "resolution, then aliasing"],
    ["hats", "nodal values", "the analyst and a mesher", "piecewise-linear variation", "complex geometry", "resolution at corners and layers"],
    ["sine modes", "global coefficients", "the analyst", "a smooth odd periodic continuation", "smooth pinned or periodic fields", "the overshoot beside a jump"],
    ["wavelets, selected", "the largest coefficients and their indices", "the analyst, the data selects", "few active scales at each location", "localized features", "the count too small to resolve the finest scale"],
    ["kernels and GP", "weights at the data sites", "the data", "smoothness at a length scale, a prior in the probabilistic reading", "scattered noisy readings", "a length scale wrong for the field"],
    ["particles", "positions and payloads", "the dynamics", "payloads ride their carriers", "advection and large deformation", "derivatives from a disordered cloud"],
    ["Gaussian splats", "centers, covariances, amplitudes", "the optimizer", "a smooth field with concentrated features", "concentrated features", "a descent that stalls"],
    ["neural fields", "network weights", "the optimizer", "the network's smoothness bias", "the next lecture", "optimization and hidden bias"],
  ];
  const tabs = document.getElementById("cp-tabs"), panel = document.getElementById("cp-panel");
  let sel = 0;
  function render(){
    tabs.innerHTML = "";
    fams.forEach((f, i) => { const b = document.createElement("button"); b.textContent = f[0]; if (i === sel) b.className = "selected"; b.onclick = () => { sel = i; render(); }; tabs.appendChild(b); });
    const f = fams[sel];
    panel.innerHTML = "<p class='lab-title' style='margin:0 0 6px'>" + f[0] + "</p>" +
      "<div class='readout-row'>" +
      "<div class='readout'><span class='label'>stores</span><span class='num' style='font-size:13px'>" + f[1] + "</span></div>" +
      "<div class='readout'><span class='label'>shapes placed by</span><span class='num' style='font-size:13px'>" + f[2] + "</span></div>" +
      "<div class='readout'><span class='label'>assumes</span><span class='num' style='font-size:13px'>" + f[3] + "</span></div>" +
      "<div class='readout'><span class='label'>native regime</span><span class='num' style='font-size:13px'>" + f[4] + "</span></div>" +
      "<div class='readout'><span class='label'>check first</span><span class='num' style='font-size:13px'>" + f[5] + "</span></div>" +
      "</div>";
  }
  render();
})();
</script>'''

labs = {
    "KERNEL": embed_lab(lab_html("Weighted kernel copies through eight readings",
                                 "Move the two locations to read their similarity, then shorten the length scale and watch the interpolant collapse between the fin's sensors.", kernel_body), 610),
    "RKHS": embed_lab(lab_html("Point evaluation as an inner product",
                               "Weight three kernel copies and move the probe. The value at the probe is an inner product, and the slope never exceeds the norm over the length scale.", rkhs_body), 650),
    "GP": embed_lab(lab_html("Gaussian-process mean and band on the fin",
                             "Change the length scale and the noise level. The band swells where no sensor reaches and narrows at the sensors.", gp_body), 560),
    "PARTICLES": embed_lab(lab_html("A fixed grid and moving carriers",
                                    "Move the material. The grid stays and re-interpolates, the carriers keep their values.", particle_body), 520),
    "SPLATS": embed_lab(lab_html("A field from Gaussian elements",
                                 "Add elements and change their width. Every number that describes an element can be trained.", splat_body), 520),
    "COMPARE": embed_lab(lab_html("Choosing a representation for the fin",
                                  "Pick a family and read what it stores, who places its shapes, what it assumes, and what to check first.", compare_body), 380),
}

PAGE = r"""# Kernels, Families of Functions, and Shapes That Move

So far, the function is known and the question is how well a finite representation approximates it.
For a cooling fin, only noisy temperature measurements are available.
The unknown curve must now be inferred from those measurements and assumptions about its variation.

## Reconstructing temperature from scattered measurements

Consider thermocouples measuring temperature at fixed locations along a cooling fin.
Let $x \in [0,1]$ denote normalized distance along the fin, and let $y_i$ be the reading at $x_i$.
The readings constrain the temperature at the sensors, but leave infinitely many possible curves between them.
How should a reading influence the estimate at a neighboring location?

Heat conduction motivates a smooth temperature profile.
Nearby locations should have similar temperatures, with less agreement expected as their separation grows.
The squared-exponential kernel expresses this assumption through

$$
k(x,x') = \exp\!\left(-\frac{(x-x')^2}{2\ell^2}\right), \qquad \ell>0.
$$

Here $\ell$ sets the distance over which the similarity decreases.
It is a parameter of the representation, whose suitability must be checked against the measurements.
A short length scale permits rapid variation, while a long one favors gradual variation.

A copy of this kernel centered at a sensor is a smooth function of position.
A weighted sum of the copies gives the temperature estimate,

$$
\hat f(x) = \sum_i \alpha_i k(x,x_i).
$$

Each weight determines how much its copy contributes to the reconstructed curve.
Because neighboring copies overlap, their weights generally differ from the readings.
The weights must be chosen together.

To interpolate the readings, evaluate the sum at each sensor and require $\hat f(x_i)=y_i$.
With $K_{ij}=k(x_i,x_j)$, these equations form the linear system

$$
\mathbf{K}\boldsymbol{\alpha}=\mathbf{y}.
$$

For distinct sensor locations, the squared-exponential kernel gives a symmetric positive-definite matrix.
The interpolation weights are therefore unique.
This guarantee concerns agreement at the sensors, not accuracy between them.

For a hand calculation, take two sensors separated by $\ell$, each with reading one.
Their similarity is $\rho=e^{-1/2}$, and symmetry gives equal weights $\alpha$.
At either sensor, the sum is $\alpha+\rho\alpha=1$, so each weight is $1/(1+\rho)$.
The contribution from the neighboring copy reduces the weight needed at that sensor.

@@KERNEL@@

The interactive figure uses synthetic fin measurements, so a reference profile is available for comparison.
At $\ell=0.15$, the interpolant at $x=0.7$ is $0.216$, against the reference value $0.393$.
At $\ell=0.04$, the estimate there is below $0.001$, although every sensor reading is still reproduced.
Agreement at the sensors alone does not validate the length scale.

## When a similarity defines an inner product

The similarity between two locations should also describe the inner product of their kernel copies.
An arbitrary similarity rule need not support such an interpretation.
Consider a rule that assigns one to locations less than $\ell$ apart and zero otherwise.
At the sites $0$, $0.6\ell$, and $1.2\ell$, it gives

$$
\mathbf{K}=
\begin{pmatrix}
1&1&0\\
1&1&1\\
0&1&1
\end{pmatrix}.
$$

For the weights $\mathbf{w}=(1,-\sqrt{2},1)^\top$, the quadratic form is $\mathbf{w}^\top\mathbf{K}\mathbf{w}=4-4\sqrt{2}<0$.
If the entries were inner products, this value would be the squared norm of a weighted sum.
A squared norm cannot be negative, so this rule fails.

A symmetric kernel is positive definite when every finite choice of sites and weights gives a nonnegative quadratic form.
Here the convention permits zero, so the associated matrices are positive semidefinite.
Strict positive definiteness requires a positive value for nonzero weights at distinct sites.
The squared-exponential kernel satisfies this stronger condition.

A kernel constructed from feature vectors $\Phi(x)$ has the required nonnegativity.
If $k(x,x')=\langle\Phi(x),\Phi(x')\rangle$, then

$$
\mathbf{w}^\top\mathbf{K}\mathbf{w}
=\left\|\sum_i w_i\Phi(x_i)\right\|^2\geq 0.
$$

The feature vectors may belong to an infinite-dimensional inner-product space.
A positive-definite kernel admits such a feature representation, even when the features are not written explicitly.
What function space does this inner product define?

## Point evaluation in a kernel space

For the squared-exponential kernel, a single copy has squared norm $k(x_i,x_i)=1$.
Copies centered at $x_1$ and $x_2$ have inner product $\rho=k(x_1,x_2)$.
Their sum has squared norm $2+2\rho$, while their difference has squared norm $2-2\rho$.
Thus nearby copies are close in this norm.

These calculations extend to every finite weighted sum by linearity.
Their Cauchy sequences have terms that become arbitrarily close in this norm.
Completing the sums includes the limits of those sequences.
The resulting function space is the reproducing kernel Hilbert space $\mathcal{H}_k$.
Its inner product satisfies

$$
\langle k(x_1,\cdot),k(x_2,\cdot)\rangle_k=k(x_1,x_2).
$$

This inner product differs from the integral of the product of two kernel copies.
Its geometry is specified by the kernel values themselves.
The norm in this geometry is denoted by $\|f\|_k$.

To evaluate a weighted sum $f$, take its inner product with the copy centered at the evaluation point.
For $f=\alpha_1k(x_1,\cdot)+\alpha_2k(x_2,\cdot)$, linearity gives $\alpha_1k(x_1,x)+\alpha_2k(x_2,x)$.
This expression is the value $f(x)$.
The same identity extends to every member of $\mathcal{H}_k$,

$$
f(x)=\langle f,k(x,\cdot)\rangle_k.
$$

The Cauchy-Schwarz inequality therefore bounds each point value by $|f(x)|\leq\|f\|_k\sqrt{k(x,x)}$.
For the squared-exponential kernel, $k(x,x)=1$, so closeness in the RKHS norm implies closeness at every point.
This makes point readings well-defined and continuous, which the $L^2$ norm alone does not provide.

For this differentiable kernel, the reproducing identity also gives the slope bound $|f'(x)|\leq\|f\|_k/\ell$.
A function that increases by one over a distance $\ell/10$ must have a slope of at least $10/\ell$ somewhere, so its RKHS norm is at least ten.
The norm constrains both amplitude and variation.
How can this constraint help when the readings contain noise?

@@RKHS@@

## Fitting noisy measurements

Interpolation reproduces the noise along with the measured temperature.
The effect can be large when nearby kernel copies are nearly dependent.
For two sensors with similarity $\rho=0.99$, the matrix eigenvalues are $1+\rho=1.99$ and $1-\rho=0.01$.
They correspond to equal and opposite changes in the readings.

Opposite measurement errors $(\varepsilon,-\varepsilon)$ change the interpolation weights by $(100\varepsilon,-100\varepsilon)$.
The difference of the two kernel copies has RKHS norm $\sqrt{2-2\rho}$.
Thus the reconstructed function changes by approximately $14.1|\varepsilon|$ in RKHS norm.
Large coefficient changes and large function changes are related, but their magnitudes differ.

A regularized fit permits disagreement with noisy readings and penalizes the RKHS norm.
For $\lambda>0$, kernel ridge regression minimizes

$$
\sum_i \bigl(f(x_i)-y_i\bigr)^2+\lambda\|f\|_k^2,
\qquad f\in\mathcal{H}_k.
$$

The first term measures squared disagreement at the sensors.
The second discourages the amplitude and variation needed to fit every fluctuation.
The parameter $\lambda$ determines their relative importance.

Any component orthogonal to the span of the sensors' kernel copies has zero value at every sensor.
It changes none of the fitting errors and increases the norm, so the minimizer has no such component.
The fit therefore remains a weighted kernel sum, with weights satisfying

$$
(\mathbf{K}+\lambda\mathbf{I})\boldsymbol{\alpha}=\mathbf{y}.
$$

Adding $\lambda$ to each eigenvalue reduces the amplification caused by small eigenvalues.
In the two-sensor example, $\lambda=0.1$ changes the small divisor from $0.01$ to $0.11$.
The coefficient amplification falls from $100$ to approximately $9.1$.
Can the same kernel also describe uncertainty between the sensors?

## Uncertainty from a Gaussian process

A temperature at an unmeasured location can be described by a probability distribution.
To see how a measurement changes that distribution, take independent standard Gaussian variables $Z_1$ and $Z_2$.
Define temperatures at two locations by

$$
f(x_1)=Z_1,\qquad
f(x_2)=\rho Z_1+\sqrt{1-\rho^2}\,Z_2.
$$

Both temperatures have mean zero and variance one, with covariance $\rho$.
Observing $f(x_1)=y$ fixes $Z_1=y$.
The remaining temperature has conditional mean $\rho y$ and standard deviation $\sqrt{1-\rho^2}$.
Stronger correlation gives less remaining uncertainty.

A Gaussian process extends this construction to any finite collection of locations.
Assume a zero prior mean and covariance $k(x,x')$.
The measured values are $y_i=f(x_i)+\varepsilon_i$, with independent Gaussian noise of variance $\sigma^2$.
For $\mathbf{k}_x=(k(x,x_1),\ldots,k(x,x_m))^\top$, conditioning gives

$$
\begin{aligned}
m(x)&=\mathbf{k}_x^\top(\mathbf{K}+\sigma^2\mathbf{I})^{-1}\mathbf{y},\\
v(x)&=k(x,x)-\mathbf{k}_x^\top(\mathbf{K}+\sigma^2\mathbf{I})^{-1}\mathbf{k}_x.
\end{aligned}
$$

The posterior mean $m$ equals the kernel ridge fit with $\lambda=\sigma^2$ for the unnormalized squared-error objective above.
The posterior variance $v$ measures remaining uncertainty about the latent temperature, rather than a future noisy measurement.
The subtracted term is the reduction in variance supplied by the sensors.

@@GP@@

The shaded band is $m(x)\pm2\sqrt{v(x)}$, conditional on the selected kernel and noise model.
With noise standard deviation $0.03$, its largest half-width in the unsensed stretch is $0.90$ at $\ell=0.15$ and $1.99$ at $\ell=0.075$.
Shorter-range correlations leave greater uncertainty between the sensors.
These are pointwise posterior bands, without a guarantee of simultaneous coverage of the whole curve.

The marginal likelihood scores how well a kernel and noise model explain the observed readings.
Maximizing it over the tested length scales gives $\ell=0.31$ in this synthetic experiment.
The resulting mean has relative $L^2$ error $3.2$ percent, and the maximum band half-width in the gap is $0.12$.
These results depend on the model assumptions, which must be reconsidered if the temperature has a sharp transition.

## A moving front gives a family of functions

Now consider a hot region transported along a pipe.
For constant flow speed $c$ and negligible diffusion, its temperature profile translates without changing shape.
At each time, the profile is a function of position on the same interval.
The reconstruction must describe the hot region wherever it moves.

The figure below shows the hot region in the pipe, its temperature profiles, and their reconstructions on one fixed grid.
The edges move to new locations, while the grid nodes remain in place.
The reconstruction joins the temperature values at those nodes with straight segments.

![A hot region moves to the right along a pipe. Its temperature profiles share the same spatial interval. Straight-line reconstructions use the same fixed nodes at every time and differ from the steep edges between nodes.](figs/rep-flow-family.svg)

The plotted profile has transition width $w=0.01$ and moves at normalized speed $c=1$.
The fixed grid has $32$ nodes, with spacing $1/31$.
At times $0$, $0.15$, and $0.30$, its relative $L^2$ reconstruction errors are $8.7$, $6.3$, and $9.6$ percent.
The same grid represents some edge locations more accurately than others.

Let $T_0$ denote the initial profile.
Translation gives the profile at time $t$,

$$
T(x,t)=T_0(x-ct).
$$

Each time selects a different function of $x$, while $T_0$ and $c$ remain fixed.
The collection $\mathcal{S}=\{T_0(\cdot-ct)\mid 0\leq t\leq0.30\}$ is a family parameterized by time.
Knowing the initial shape and the translation rule specifies every member from that parameter.

A fixed-grid representation uses hat functions $\phi_i$ centered at nodes $x_i$.
Only their coefficients change with time,

$$
\hat T(x,t)=\sum_i T(x_i,t)\phi_i(x).
$$

Every reconstructed profile therefore belongs to the same linear span of the hats.
Many nodes are needed when the edge width is small compared with their spacing.
The [moving-nodes lab](representation.md#let-the-nodes-move) instead places its breakpoints near the edges.
Does choosing a different fixed basis remove this difficulty for the whole family?

## The limits of a fixed linear space

A narrow pulse centered at separated locations gives profiles with little overlap.
The finite-dimensional version is a unit spike translated across three grid points.
Its snapshots are the perpendicular vectors $\mathbf{e}_1$, $\mathbf{e}_2$, and $\mathbf{e}_3$ in $\mathbb{R}^3$.
These snapshots provide a calculation that applies to every plane through the origin.

Let $P$ be the orthogonal projection onto such a plane.
The squared projection lengths add to the plane's dimension, so the squared errors satisfy

$$
\sum_{j=1}^3\|\mathbf{e}_j-P\mathbf{e}_j\|_2^2=3-2=1.
$$

At least one error is therefore no smaller than $1/\sqrt{3}$.
No choice of the plane can approximate all the snapshots more closely than this bound in Euclidean norm.
Exact linear representation of the snapshots requires dimension three, although one position parameter selects the spike.

For a family of functions, the Kolmogorov $n$-width asks how well the best fixed $n$-dimensional linear space approximates its worst member.
Using the $L^2$ norm, it is

$$
d_n(\mathcal{S})=
\inf_{\dim V=n}\ \sup_{f\in\mathcal{S}}\ \inf_{v\in V}\|f-v\|_{L^2}.
$$

The inner infimum chooses the closest member of $V$ for each target.
The supremum chooses the hardest target in the family, and the outer infimum chooses the space.
The space must be chosen once for the entire family.

Motion alone does not imply a large width.
Every translate of $\sin(kx)$ lies in the span of $\sin(kx)$ and $\cos(kx)$ by the angle-subtraction identity.
A localized pulse with steep edges instead requires many frequencies, and translation does not reduce their magnitudes.
For a periodic heat equation with unit diffusivity, those magnitudes decay by $e^{-(2\pi k)^2t}$, explaining why diffusion can reduce the required number of modes.

A snapshot matrix's singular value decomposition minimizes average squared projection error over the sampled profiles.
The width concerns the worst profile over the entire family.
A small average error on snapshots therefore needs a separate check of poorly represented positions.
Can the representation adapt to the target instead of using one fixed linear space?

## Representations that adapt to the front

The translated-template formula already gives an alternative to fixed-grid coefficients.
It stores the initial shape and evaluates that shape at shifted coordinates.
This representation assumes a known translation law, but its functions need not belong to one low-dimensional linear space.
Other adaptive representations change their locations, shapes, or selected terms.

### Move the locations with the flow

A particle representation stores positions together with temperature values.
For pure advection, each particle keeps its temperature while its position follows the flow.
The field between particles is reconstructed from their values and an interpolation rule.
Exact transport of stored values does not remove this reconstruction error.

A first-order upwind grid scheme provides a useful comparison.
For positive speed and $0<\nu=c\Delta t/h<1$, its update is

$$
T_i^{n+1}=(1-\nu)T_i^n+\nu T_{i-1}^n.
$$

Each step averages neighboring temperatures, which spreads a steep transition.
This numerical diffusion comes from the update rule, separately from the fixed basis's approximation error.
At $\nu=1$, the update shifts grid values without averaging.

@@PARTICLES@@

### Fit the locations and shapes

A Gaussian element describes a localized field through its center, covariance, and amplitude.
An anisotropic covariance permits a long, narrow shape aligned with a ridge.
Fitting these parameters lets the elements concentrate where the field varies.
The Gaussian-field figure illustrates the reconstruction as elements are added and their widths change.

@@SPLATS@@

With centers and covariances fixed, a quadratic fitting objective gives a linear system for the amplitudes.
Fitting the centers and covariances as well generally makes the objective non-convex.
The representation can adapt to localized features, but the fitting algorithm may stop at a poor local minimum.

### Select localized terms

A wavelet representation keeps its dictionary fixed and selects terms for each profile.
For an orthonormal Haar expansion, retaining the $n$ largest coefficients minimizes the $L^2$ truncation error among selections of $n$ terms.
For a front, the selected terms tend to be concentrated near the edges.
As the edges move, different terms are selected.

The selected functions belong to different dictionary subspaces, so the width's fixed-space restriction no longer describes this approximation.
Storage must include the selected indices as well as the coefficient values.
Resolution and truncation still limit accuracy, so adapting the selection does not guarantee a good reconstruction.

## Choosing a representation for the fin

For the fin, the unknown profile must be reconstructed from the same noisy measurements.
The synthetic reference permits a direct comparison, but such a reference is unavailable in practice.
The table compares relative $L^2$ error against that reference with prediction error obtained by withholding readings.

| Representation and fitting principle | Relative $L^2$ error against reference | Held-out RMSE |
| --- | --- | --- |
| Straight segments | $6.5\%$ | $0.095$ |
| Cubic polynomial, least squares | $23\%$ | $0.310$ |
| Polynomial interpolation | $31\%$ | $3.57$ |
| Kernel interpolation, $\ell=0.15$ | $11\%$ | $0.112$ |
| Gaussian-process mean, $\ell=0.31$ | $3.2\%$ | $0.034$ |

The held-out calculation removes each reading, fits the remaining readings, and predicts the omitted value.
Its RMSE is measured in the normalized temperature units, against noise standard deviation $0.03$.
The length scales remain fixed at values selected using all the readings, so this is a fixed-hyperparameter diagnostic.
Testing the complete selection procedure requires choosing the length scale again within each fold.

The table favors the Gaussian-process fit in this experiment, without establishing that it is best for every fin.
The kernel specifies the possible functions and their geometry, while regularized fitting selects a function using the measurements.
The posterior band adds uncertainty conditional on the same assumptions.
The comparison below records the assumptions that should be checked for each representation.

@@COMPARE@@

For a moving front, a reconstruction must also be checked across its possible positions.
A low-dimensional parameterization can describe a family that is difficult for one small fixed linear space.
Choosing a representation therefore requires both a reconstruction rule and a clear statement of which functions it must approximate.

The companion notebooks on [the cooling fin](https://sciml-book.github.io/sciml_notebook/kernels/the-fin.html) and [one front, every family](https://sciml-book.github.io/sciml_notebook/representations/one-front-every-family.html) contain the underlying experiments.
The fin notebook compares interpolation, regularization, and uncertainty from the same measurements.
The front notebook compares fixed and adaptive representations of the transported profile.
"""

page = PAGE
for tag, html in labs.items():
    page = page.replace("@@" + tag + "@@", html)
assert "@@" not in page
(HERE / "kernels-and-families.md").write_text(page)
print("wrote", HERE / "kernels-and-families.md", len(page), "chars,", len(labs), "labs")
