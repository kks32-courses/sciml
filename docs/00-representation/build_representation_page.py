"""Build the Representation lecture page with its interactive figures inline.

The page is Markdown for the course site. Each interactive figure is a
self-contained HTML document embedded as an <iframe srcdoc>, the pattern the
book's notebooks use (book/sciml_notebook/docs/sciml_labs.py), so it renders
inside the site's own layout and follows the OS light or dark mode.

Four labs are reused from the book's notebooks (three coordinates, samples at
stations, coordinates in a basis, the closest blend). Three are new here
(Bernstein's coin flips, hat functions as a basis, hat nodes that ride with a front).

Run:  python3 build_representation_page.py   (writes representation.md here)
"""

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
NB_DOCS = HERE.parents[2] / "sciml_notebook" / "docs"
sys.path.insert(0, str(NB_DOCS))
from sciml_labs import lab_html, embed_lab  # noqa: E402


def body_from(script, name):
    """Pull the raw-string lab body NAME = r'''...''' out of a notebook build script."""
    src = (NB_DOCS / "representations" / script).read_text()
    m = re.search(name + r" = r'''(.*?)'''", src, re.S)
    assert m, (script, name)
    return m.group(1)


hero_body = r"""
<div class="plot-wrap">
  <svg id="hero-plot" class="plot" viewBox="0 0 720 300"></svg>
</div>
<div class="slider-row" style="--slider-color: var(--blue)"><span>a&#8321; &nbsp;&middot;&nbsp; sin(&pi;x)</span><input id="a1" type="range" min="-1" max="1" step="0.05" value="0.5"><output id="a1v">0.50</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>a&#8322; &nbsp;&middot;&nbsp; sin(2&pi;x)</span><input id="a2" type="range" min="-1" max="1" step="0.05" value="0"><output id="a2v">0.00</output></div>
<div class="slider-row" style="--slider-color: var(--green)"><span>a&#8323; &nbsp;&middot;&nbsp; sin(3&pi;x)</span><input id="a3" type="range" min="-1" max="1" step="0.05" value="0"><output id="a3v">0.00</output></div>
<div class="btn-row"><button id="hero-solve">Solve by projection</button><button id="hero-reset">Reset to (0.5, 0, 0)</button></div>
<div class="readout-row">
  <div class="readout"><span class="label">weights (a&#8321;, a&#8322;, a&#8323;)</span><span class="num" id="coords">(0.50, 0.00, 0.00)</span></div>
  <div class="readout"><span class="label">L&#178; distance to the displacement</span><span class="num" id="dist">0.000</span></div>
  <div class="readout"><span class="label">projection a&#8342; = 2&int;&#8320;&sup1; u(x) sin(k&pi;x) dx</span><span class="num" id="proj">press Solve</span></div>
</div>
<div class="readout-row">
  <div class="readout"><span class="label">largest gap, relative (sup)</span><span class="num" id="h-esup">0</span></div>
  <div class="readout"><span class="label">root-mean-square gap, relative (L&#178;)</span><span class="num" id="h-el2">0</span></div>
  <div class="readout"><span class="label">slope error, relative (H&#185;)</span><span class="num" id="h-eh1">0</span></div>
</div>
<svg id="hero-hist" class="plot" viewBox="0 0 720 170"></svg>
<p class="lab-note">The solid black curve is the displacement to reproduce, and it does not move. The gray dashed curve is the weighted sum of the three modes, drawn faintly in color. The distance reads zero at the weights (0.8, 0.4, 0.2). Solve computes each weight as the inner product of the displacement with its mode, divided by the mode's squared norm 1/2, and moves the sliders there. The bottom plot traces the three relative errors, sup in red, L&#178; in blue, and H&#185; in orange, over the last two hundred slider moves.</p>
<script>
(function(){
  const svg = document.getElementById("hero-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.8, 1.8, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.8, xlabel: "x", ylabel: "u(x)"});
  const gT = L.el("g", {}, svg), gC = L.el("g", {}, svg), gS = L.el("g", {}, svg);
  const mode = k => x => Math.sin(k * Math.PI * x);
  const colors = ["var(--blue)", "var(--orange)", "var(--green)"];
  const t = [0.8, 0.4, 0.2];
  const a = [0.5, 0, 0];
  const dmode = k => x => k * Math.PI * Math.cos(k * Math.PI * x);
  const hs = document.getElementById("hero-hist");
  const Yh = L.scale(0, 1.2, 150, 12);
  L.axes(hs, L.scale(0, 1, 46, 706), Yh, {yMax: 1.2, ny: 2, xlabel: "", ylabel: "relative error"});
  const gH = L.el("g", {}, hs);
  const hist = [];
  const nq = 1000;
  function norms(f, df){
    let sup = 0, l2 = 0, h1 = 0;
    for (let i = 0; i <= nq; i++) {
      const x = i / nq, w = (i === 0 || i === nq) ? 0.5 : 1, e = f(x), de = df(x);
      sup = Math.max(sup, Math.abs(e)); l2 += w * e * e / nq; h1 += w * de * de / nq;
    }
    return [sup, Math.sqrt(l2), Math.sqrt(h1)];
  }
  const tu = x => t[0]*mode(1)(x) + t[1]*mode(2)(x) + t[2]*mode(3)(x);
  const tdu = x => t[0]*dmode(1)(x) + t[1]*dmode(2)(x) + t[2]*dmode(3)(x);
  const uN = norms(tu, tdu);
  L.curve(gT, x => t[0]*mode(1)(x) + t[1]*mode(2)(x) + t[2]*mode(3)(x), X, Y, {stroke: "var(--ink)", width: 4});
  function redraw(){
    gC.innerHTML = ""; gS.innerHTML = "";
    for (let k = 0; k < 3; k++)
      L.curve(gC, x => a[k] * mode(k + 1)(x), X, Y, {stroke: colors[k], width: 1.5, dash: "4 6", opacity: 0.35});
    L.curve(gS, x => a[0]*mode(1)(x) + a[1]*mode(2)(x) + a[2]*mode(3)(x), X, Y, {stroke: "var(--muted)", width: 3, dash: "9 7"});
    L.el("circle", {cx: X(0), cy: Y(0), r: 4, style: "fill: var(--ink)"}, gS);
    L.el("circle", {cx: X(1), cy: Y(0), r: 4, style: "fill: var(--ink)"}, gS);
    document.getElementById("coords").textContent =
      "(" + L.fmt(a[0]) + ", " + L.fmt(a[1]) + ", " + L.fmt(a[2]) + ")";
    // the modes are orthogonal with squared norm 1/2
    const d2 = 0.5 * ((a[0]-t[0])**2 + (a[1]-t[1])**2 + (a[2]-t[2])**2);
    document.getElementById("dist").textContent = Math.sqrt(d2).toFixed(3);
    const eN = norms(x => tu(x) - (a[0]*mode(1)(x) + a[1]*mode(2)(x) + a[2]*mode(3)(x)),
                     x => tdu(x) - (a[0]*dmode(1)(x) + a[1]*dmode(2)(x) + a[2]*dmode(3)(x)));
    const rel = eN.map((v, i) => v / uN[i]);
    document.getElementById("h-esup").textContent = (100 * rel[0]).toFixed(1) + "%";
    document.getElementById("h-el2").textContent = (100 * rel[1]).toFixed(1) + "%";
    document.getElementById("h-eh1").textContent = (100 * rel[2]).toFixed(1) + "%";
    hist.push(rel); if (hist.length > 200) hist.shift();
    gH.innerHTML = "";
    const Xh = L.scale(0, Math.max(19, hist.length - 1), 46, 706);
    ["var(--red)", "var(--blue)", "var(--orange)"].forEach((c, j) => {
      const pts = hist.map((r, i) => Xh(i) + "," + Yh(Math.min(r[j], 1.2))).join(" ");
      L.el("polyline", {points: pts, style: "fill: none; stroke: " + c + "; stroke-width: 2"}, gH);
    });
  }
  const ids = ["a1", "a2", "a3"];
  function setWeights(w){
    for (let k = 0; k < 3; k++) {
      a[k] = w[k];
      document.getElementById(ids[k]).value = w[k];
      document.getElementById(ids[k] + "v").textContent = L.fmt(w[k]);
    }
    redraw();
  }
  ids.forEach((id, k) => {
    document.getElementById(id).addEventListener("input", e => {
      a[k] = parseFloat(e.target.value);
      document.getElementById(id + "v").textContent = L.fmt(a[k]);
      redraw();
    });
  });
  // each weight is 2 times the integral of u(x) sin(k pi x), by the trapezoid rule on 2000 intervals
  const target = x => t[0]*mode(1)(x) + t[1]*mode(2)(x) + t[2]*mode(3)(x);
  function project(k){
    const n = 2000; let sum = 0;
    for (let i = 0; i <= n; i++) {
      const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1;
      sum += w * target(x) * mode(k)(x);
    }
    return 2 * sum / n;
  }
  document.getElementById("hero-solve").addEventListener("click", () => {
    const c = [project(1), project(2), project(3)];
    document.getElementById("proj").textContent =
      "(" + c.map(v => v.toFixed(3)).join(", ") + ")";
    setWeights(c.map(v => Math.round(v * 20) / 20));
  });
  document.getElementById("hero-reset").addEventListener("click", () => {
    document.getElementById("proj").textContent = "press Solve";
    hist.length = 0;
    setWeights([0.5, 0, 0]);
  });
  redraw();
})();
</script>"""
sampling_body = body_from("build_function_as_point_notebook.py", "sampling_body")
# the page starts from three stations, and odd counts keep the aliasing counts 17, 33, 65 reachable
sampling_body = (sampling_body
    .replace('<input id="sm-m" type="range" min="5" max="65" step="4" value="9"><output id="sm-mv">9</output>',
             '<input id="sm-m" type="range" min="3" max="65" step="2" value="3"><output id="sm-mv">3</output>')
    .replace("let m = 9, add = false;", "let m = 3, add = false;")
    .replace('<span class="num" id="sm-err">3.8%</span>', '<span class="num" id="sm-err">62.1%</span>'))
assert 'value="3"' in sampling_body and "let m = 3" in sampling_body
basis_body = body_from("build_basis_notebook.py", "basis_body")
proj_body = body_from("build_projection_notebook.py", "proj_body")

# --------------------------------------------------------------------------- error of the station guess in three norms
# Same displacement and stations as the sampling lab. At m = 5 the gap has sup 0.223, L2 0.093, and H1 seminorm 1.20
# (build_slide_data-report.md), relative 20.1, 14.4, and 42 percent.
norms_body = r'''
<svg id="nm-e" class="plot" viewBox="0 0 720 150"></svg>
<svg id="nm-e2" class="plot" viewBox="0 0 720 150"></svg>
<svg id="nm-de" class="plot" viewBox="0 0 720 150"></svg>
<div class="slider-row" style="--slider-color: var(--blue)"><span>stations m</span><input id="nm-m" type="range" min="3" max="33" step="2" value="5"><output id="nm-mv">5</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">sup norm, largest gap</span><span class="num" id="nm-sup">0</span></div>
  <div class="readout"><span class="label">L&#178; norm, root of the area</span><span class="num" id="nm-l2">0</span></div>
  <div class="readout"><span class="label">H&#185; seminorm, root-mean-square slope error</span><span class="num" id="nm-h1">0</span></div>
</div>
<p class="lab-note">Top, the gap e = u &minus; v between the displacement and the straight-segment guess, with the largest gap in red. Middle, the squared gap, whose area is the squared L&#178; norm. Bottom, the slope error e&prime;, which jumps at every station because the guess has a corner there. Each panel rescales to its own largest value as the station count changes, so read the sizes from the readouts. The percentages divide by the same norm of the displacement.</p>
<script>
(function(){
  const X = L.scale(0, 1, 46, 706);
  const u = x => 0.8*Math.sin(Math.PI*x) + 0.4*Math.sin(2*Math.PI*x) + 0.2*Math.sin(3*Math.PI*x);
  const du = x => 0.8*Math.PI*Math.cos(Math.PI*x) + 0.8*Math.PI*Math.cos(2*Math.PI*x) + 0.6*Math.PI*Math.cos(3*Math.PI*x);
  const s1 = document.getElementById("nm-e"), s2 = document.getElementById("nm-e2"), s3 = document.getElementById("nm-de");
  let Y1, Y2, Y3, g1, g2, g3;
  const n = 2000;
  let uSup = 0, uL2 = 0, uH1 = 0;
  for (let i = 0; i <= n; i++) {
    const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1;
    uSup = Math.max(uSup, Math.abs(u(x))); uL2 += w * u(x) ** 2 / n; uH1 += w * du(x) ** 2 / n;
  }
  uL2 = Math.sqrt(uL2); uH1 = Math.sqrt(uH1);
  let m = 5;
  function redraw(){
    const xi = Array.from({length: m}, (_, i) => i / (m - 1)), yi = xi.map(u), h = 1 / (m - 1);
    const seg = x => Math.min(m - 2, Math.floor(x / h));
    const v = x => { const k = seg(x), tt = x / h - k; return yi[k] * (1 - tt) + yi[k + 1] * tt; };
    const dv = x => { const k = seg(x); return (yi[k + 1] - yi[k]) / h; };
    const e = x => u(x) - v(x), de = x => du(x) - dv(x);
    let sup = 0, xs = 0, l2 = 0, h1 = 0, dmax = 0;
    for (let i = 0; i <= n; i++) {
      const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1, ee = e(x);
      if (Math.abs(ee) > sup) { sup = Math.abs(ee); xs = x; }
      l2 += w * ee * ee / n; h1 += w * de(x) ** 2 / n; dmax = Math.max(dmax, Math.abs(de(x)));
    }
    l2 = Math.sqrt(l2); h1 = Math.sqrt(h1);
    // each panel is rescaled to its current largest value, and its axis ticks show the size
    const r1 = 1.15 * sup, r2 = 1.15 * sup * sup, r3 = 1.15 * dmax;
    s1.innerHTML = ""; s2.innerHTML = ""; s3.innerHTML = "";
    Y1 = L.scale(-r1, r1, 136, 12); Y2 = L.scale(0, r2, 136, 12); Y3 = L.scale(-r3, r3, 136, 12);
    L.axes(s1, X, Y1, {yMax: r1, ny: 2, xlabel: "x", ylabel: "gap e"});
    L.axes(s2, X, Y2, {yMax: r2, ny: 2, xlabel: "x", ylabel: "e squared"});
    L.axes(s3, X, Y3, {yMax: r3, ny: 2, xlabel: "x", ylabel: "slope error"});
    g1 = L.el("g", {}, s1); g2 = L.el("g", {}, s2); g3 = L.el("g", {}, s3);
    for (let i = 0; i <= 180; i++) {
      const x = i / 180;
      L.el("line", {x1: X(x), x2: X(x), y1: Y2(0), y2: Y2(e(x) ** 2), style: "stroke: var(--yellow); stroke-width: 4; opacity: 0.45"}, g2);
    }
    L.curve(g1, e, X, Y1, {stroke: "var(--ink)", width: 2, n: 1201});
    L.el("circle", {cx: X(xs), cy: Y1(e(xs)), r: 4.5, style: "fill: var(--red)"}, g1);
    L.curve(g2, x => e(x) ** 2, X, Y2, {stroke: "var(--ink)", width: 1.5, n: 1201});
    L.curve(g3, de, X, Y3, {stroke: "var(--orange)", width: 2, n: 2401});
    document.getElementById("nm-sup").textContent = sup.toFixed(3) + ", or " + (100 * sup / uSup).toFixed(1) + "%";
    document.getElementById("nm-l2").textContent = l2.toFixed(3) + ", or " + (100 * l2 / uL2).toFixed(1) + "%";
    document.getElementById("nm-h1").textContent = h1.toFixed(2) + ", or " + (100 * h1 / uH1).toFixed(0) + "%";
  }
  document.getElementById("nm-m").addEventListener("input", ev => {
    m = parseInt(ev.target.value); document.getElementById("nm-mv").textContent = m; redraw();
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- corner against three sines
# Target: the point-load displacement u = min(x, 1 - x)/2.  L2 and H1 projections coincide for sines,
# c_k = 2 sin(k pi/2)/(k pi)^2 = (0.2026, 0, -0.0225).  The sup-closest weights (0.2045, 0, -0.0318) were
# found offline by Nelder-Mead on the largest gap over 20001 points.  Relative errors, L2/H1-closest:
# sup 9.9 %, L2 4.8 %, H1 31.5 %.  Sup-closest: sup 5.5 %, L2 6.7 %, H1 33.9 %.
corner_body = r'''
<svg id="cn-plot" class="plot" viewBox="0 0 720 250"></svg>
<svg id="cn-err" class="plot" viewBox="0 0 720 150"></svg>
<div class="slider-row" style="--slider-color: var(--blue)"><span>a&#8321; &nbsp;&middot;&nbsp; sin(&pi;x)</span><input id="cn-a1" type="range" min="0" max="0.3" step="0.0005" value="0.25"><output id="cn-a1v">0.2500</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>a&#8322; &nbsp;&middot;&nbsp; sin(2&pi;x)</span><input id="cn-a2" type="range" min="-0.1" max="0.1" step="0.0005" value="0"><output id="cn-a2v">0.0000</output></div>
<div class="slider-row" style="--slider-color: var(--green)"><span>a&#8323; &nbsp;&middot;&nbsp; sin(3&pi;x)</span><input id="cn-a3" type="range" min="-0.1" max="0.1" step="0.0005" value="0"><output id="cn-a3v">0.0000</output></div>
<div class="btn-row"><button id="cn-l2">Closest in L&#178; and H&#185;</button><button id="cn-sup">Closest in the sup norm</button><button id="cn-reset">Reset</button></div>
<div class="readout-row">
  <div class="readout"><span class="label">largest gap, relative (sup)</span><span class="num" id="cn-esup">0</span></div>
  <div class="readout"><span class="label">root-mean-square gap, relative (L&#178;)</span><span class="num" id="cn-el2">0</span></div>
  <div class="readout"><span class="label">slope error, relative (H&#185;)</span><span class="num" id="cn-eh1">0</span></div>
</div>
<p class="lab-note">Top, the point-load displacement (solid black, fixed) and the sum of three weighted sines (gray dashed). Bottom, the gap u &minus; v, with the largest gap marked in red. The L&#178;-closest sum is also the H&#185;-closest, because the sines are orthogonal in both inner products. The sup-closest weights were found by minimizing the largest gap numerically.</p>
<script>
(function(){
  const X = L.scale(0, 1, 46, 706);
  const svg = document.getElementById("cn-plot"), Y = L.scale(-0.03, 0.3, 236, 14);
  L.axes(svg, X, Y, {yMax: 0.3, ny: 3, xlabel: "x", ylabel: "u(x)"});
  const sve = document.getElementById("cn-err"), Ye = L.scale(-0.06, 0.06, 140, 10);
  L.axes(sve, X, Ye, {yMax: 0.06, ny: 2, xlabel: "x", ylabel: "u - v"});
  const gT = L.el("g", {}, svg), gS = L.el("g", {}, svg), gE = L.el("g", {}, sve);
  const u = x => 0.5 * Math.min(x, 1 - x), du = x => (x < 0.5 ? 0.5 : -0.5);
  const md = k => x => Math.sin(k * Math.PI * x), dmd = k => x => k * Math.PI * Math.cos(k * Math.PI * x);
  const a = [0.25, 0, 0], ids = ["cn-a1", "cn-a2", "cn-a3"];
  const v = x => a[0]*md(1)(x) + a[1]*md(2)(x) + a[2]*md(3)(x);
  const dv = x => a[0]*dmd(1)(x) + a[1]*dmd(2)(x) + a[2]*dmd(3)(x);
  L.curve(gT, u, X, Y, {stroke: "var(--ink)", width: 4, n: 801});
  const n = 2000, uSup = 0.25, uL2 = Math.sqrt(1 / 48), uH1 = 0.5;
  function redraw(){
    gS.innerHTML = ""; gE.innerHTML = "";
    L.curve(gS, v, X, Y, {stroke: "var(--muted)", width: 3, dash: "9 7", n: 801});
    L.curve(gE, x => u(x) - v(x), X, Ye, {stroke: "var(--ink)", width: 2, n: 801});
    let sup = 0, xs = 0, l2 = 0, h1 = 0;
    for (let i = 0; i <= n; i++) {
      const x = i / n, e = u(x) - v(x), de = du(x) - dv(x), w = (i === 0 || i === n) ? 0.5 : 1;
      if (Math.abs(e) > sup) { sup = Math.abs(e); xs = x; }
      l2 += w * e * e / n; h1 += w * de * de / n;
    }
    L.el("circle", {cx: X(xs), cy: Ye(u(xs) - v(xs)), r: 4.5, style: "fill: var(--red)"}, gE);
    document.getElementById("cn-esup").textContent = (100 * sup / uSup).toFixed(1) + "%";
    document.getElementById("cn-el2").textContent = (100 * Math.sqrt(l2) / uL2).toFixed(1) + "%";
    document.getElementById("cn-eh1").textContent = (100 * Math.sqrt(h1) / uH1).toFixed(1) + "%";
  }
  function setWeights(w){
    for (let k = 0; k < 3; k++) {
      a[k] = w[k];
      document.getElementById(ids[k]).value = w[k];
      document.getElementById(ids[k] + "v").textContent = w[k].toFixed(4);
    }
    redraw();
  }
  ids.forEach((id, k) => document.getElementById(id).addEventListener("input", e => {
    a[k] = parseFloat(e.target.value);
    document.getElementById(id + "v").textContent = a[k].toFixed(4);
    redraw();
  }));
  document.getElementById("cn-l2").addEventListener("click", () =>
    setWeights([2 / Math.PI ** 2, 0, -2 / (9 * Math.PI ** 2)]));
  document.getElementById("cn-sup").addEventListener("click", () => setWeights([0.2045, 0, -0.0318]));
  document.getElementById("cn-reset").addEventListener("click", () => setWeights([0.25, 0, 0]));
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- Bernstein derived on the string displacement
# Target: the displacement of the coefficients lab, 0.8 sin(pi x) + 0.4 sin(2 pi x) + 0.2 sin(3 pi x).
# Largest gap of B_n f, near x = 0.24: 0.299 (n = 8), 0.169 (16), 0.091 (32), 0.048 (64), 0.024 (128), 0.006 (512).
# Voronovskaya, max over x of x(1 - x) |f''(x)| / (2n) = 3.18 / n: 0.099 at n = 32, 0.025 at n = 128, 0.006 at n = 512.
bernbump_body = r'''
<svg id="bb-plot" class="plot" viewBox="0 0 720 270"></svg>
<svg id="bb-w" class="plot" viewBox="0 0 720 130"></svg>
<div class="slider-row" style="--slider-color: var(--blue)"><span>coins n</span><input id="bb-n" type="range" min="0" max="8" step="1" value="3"><output id="bb-nv">16</output></div>
<div class="slider-row" style="--slider-color: var(--red)"><span>probe x</span><input id="bb-x" type="range" min="0.02" max="0.98" step="0.01" value="0.25"><output id="bb-xv">0.25</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">u(x), the displacement at the probe</span><span class="num" id="bb-f">0</span></div>
  <div class="readout"><span class="label">B&#8345;f(x) = &Sigma; f(k/n) P(k heads)</span><span class="num" id="bb-b">0</span></div>
  <div class="readout"><span class="label">largest gap anywhere</span><span class="num" id="bb-max">0</span></div>
  <div class="readout"><span class="label">3.18 / n, large-n prediction of the largest gap</span><span class="num" id="bb-pred">0</span></div>
</div>
<p class="lab-note">Top, the string displacement (dashed), Bernstein's polynomial B&#8345;f (blue), the readings f(k/n) (dots, shown up to n = 64), and the weighted basis polynomials f(k/n) B&#8342;&#8345;(x) that add up to B&#8345;f (gray dashed, every one up to n = 32 and an evenly spaced selection above). Bottom, the probability of k heads in n coins that land heads with probability x, drawn at k/n. B&#8345;f(x) is the average of the readings with these weights, and the weights crowd around the probe as n grows.</p>
<script>
(function(){
  const X = L.scale(0, 1, 46, 706);
  const svg = document.getElementById("bb-plot"), Y = L.scale(-0.3, 1.4, 256, 14);
  L.axes(svg, X, Y, {yMax: 1.4, ny: 3, xlabel: "x", ylabel: "u(x)"});
  const sw = document.getElementById("bb-w");
  const gC = L.el("g", {}, svg), gD = L.el("g", {}, svg), gW = L.el("g", {}, sw);
  const f = x => 0.8 * Math.sin(Math.PI * x) + 0.4 * Math.sin(2 * Math.PI * x) + 0.2 * Math.sin(3 * Math.PI * x);
  const ns = [2, 4, 8, 16, 32, 64, 128, 256, 512];
  let n = 16, x0 = 0.25;
  function logC(n){
    const out = [0];
    for (let k = 1; k <= n; k++) out.push(out[k-1] + Math.log(n - k + 1) - Math.log(k));
    return out;
  }
  function redraw(){
    const lc = logC(n);
    const w = (k, x) => {
      if (x <= 0) return k === 0 ? 1 : 0;
      if (x >= 1) return k === n ? 1 : 0;
      return Math.exp(lc[k] + k * Math.log(x) + (n - k) * Math.log(1 - x));
    };
    const B = x => { let s = 0; for (let k = 0; k <= n; k++) s += f(k / n) * w(k, x); return s; };
    gC.innerHTML = ""; gD.innerHTML = ""; gW.innerHTML = "";
    // the weighted basis polynomials f(k/n) B_{k,n}(x) whose sum is B_n f, thinned to at most 33 curves
    const step = n > 32 ? Math.ceil(n / 32) : 1;
    for (let k = 0; k <= n; k += step)
      L.curve(gC, x => f(k / n) * w(k, x), X, Y, {stroke: "var(--muted)", width: 1.6, dash: "5 4", opacity: 0.9, n: 301});
    L.curve(gC, f, X, Y, {stroke: "var(--ink)", width: 2.5, dash: "7 6", n: 501});
    L.curve(gC, B, X, Y, {stroke: "var(--blue)", width: 3, n: 501});
    if (n <= 64) for (let k = 0; k <= n; k++)
      L.el("circle", {cx: X(k / n), cy: Y(f(k / n)), r: 2.6, style: "fill: var(--muted)"}, gD);
    L.el("line", {x1: X(x0), x2: X(x0), y1: Y(-0.3), y2: Y(1.4), style: "stroke: var(--red); stroke-width: 1.2; stroke-dasharray: 4 4"}, gD);
    L.el("circle", {cx: X(x0), cy: Y(B(x0)), r: 5, style: "fill: var(--red)"}, gD);
    let wmax = 0; for (let k = 0; k <= n; k++) wmax = Math.max(wmax, w(k, x0));
    const Yw = L.scale(0, 1.1 * wmax, 120, 10);
    sw.innerHTML = ""; L.axes(sw, X, Yw, {yMax: 1.1 * wmax, ny: 1, xlabel: "k / n", ylabel: "P(k heads)"});
    const gw = L.el("g", {}, sw);
    const bw = Math.max(1.5, Math.min(14, 560 / (n + 1)));
    for (let k = 0; k <= n; k++) {
      const p = w(k, x0);
      L.el("rect", {x: X(k / n) - bw / 2, y: Yw(p), width: bw, height: Yw(0) - Yw(p), style: "fill: var(--blue); opacity: 0.7"}, gw);
    }
    L.el("line", {x1: X(x0), x2: X(x0), y1: Yw(0), y2: Yw(1.1 * wmax), style: "stroke: var(--red); stroke-width: 1.2; stroke-dasharray: 4 4"}, gw);
    let worst = 0;
    for (let i = 0; i <= 400; i++) { const x = i / 400; worst = Math.max(worst, Math.abs(B(x) - f(x))); }
    document.getElementById("bb-f").textContent = f(x0).toFixed(3);
    document.getElementById("bb-b").textContent = B(x0).toFixed(3);
    document.getElementById("bb-max").textContent = worst.toFixed(3);
    document.getElementById("bb-pred").textContent = (3.18 / n).toFixed(3);
  }
  document.getElementById("bb-n").addEventListener("input", e => {
    n = ns[parseInt(e.target.value)]; document.getElementById("bb-nv").textContent = n; redraw();
  });
  document.getElementById("bb-x").addEventListener("input", e => {
    x0 = parseFloat(e.target.value); document.getElementById("bb-xv").textContent = x0.toFixed(2); redraw();
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- Bernstein
bern_body = r'''
<svg id="bn-plot" class="plot" viewBox="0 0 720 300"></svg>
<div class="slider-row" style="--slider-color: var(--blue)"><span>degree n</span><input id="bn-n" type="range" min="2" max="128" step="2" value="8"><output id="bn-nv">8</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">gap at the corner</span><span class="num" id="bn-corner">0.000</span></div>
  <div class="readout"><span class="label">0.4 / &radic;n</span><span class="num" id="bn-pred">0.000</span></div>
  <div class="readout"><span class="label">largest gap anywhere</span><span class="num" id="bn-max">0.000</span></div>
</div>
<p class="lab-note">Gray curves are the n + 1 hills, each scaled by the reading f(k/n) it weights. Their sum (blue) is Bernstein's polynomial for the corner function (dashed). The red dot marks the corner, where the gap is largest.</p>
<script>
(function(){
  const svg = document.getElementById("bn-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.1, 0.6, 286, 14);
  L.axes(svg, X, Y, {yMax: 0.6, ny: 3, xlabel: "x", ylabel: "f(x)"});
  const gB = L.el("g", {}, svg), gC = L.el("g", {}, svg), gD = L.el("g", {}, svg);
  const f = x => Math.abs(x - 0.5);
  let n = 8;
  function logC(n){
    const out = [0];
    for (let k = 1; k <= n; k++) out.push(out[k-1] + Math.log(n - k + 1) - Math.log(k));
    return out;
  }
  function redraw(){
    const lc = logC(n);
    const w = (k, x) => {
      if (x <= 0) return k === 0 ? 1 : 0;
      if (x >= 1) return k === n ? 1 : 0;
      return Math.exp(lc[k] + k * Math.log(x) + (n - k) * Math.log(1 - x));
    };
    const B = x => { let s = 0; for (let k = 0; k <= n; k++) s += f(k / n) * w(k, x); return s; };
    gB.innerHTML = ""; gC.innerHTML = ""; gD.innerHTML = "";
    const step = n > 32 ? Math.ceil(n / 32) : 1;
    for (let k = 0; k <= n; k += step)
      L.curve(gB, x => f(k / n) * w(k, x), X, Y, {stroke: "var(--muted)", width: 1, opacity: 0.45, n: 241});
    L.curve(gC, f, X, Y, {stroke: "var(--ink)", width: 2.5, dash: "7 6", n: 401});
    L.curve(gC, B, X, Y, {stroke: "var(--blue)", width: 3, n: 401});
    let worst = 0;
    for (let i = 0; i <= 400; i++) { const x = i / 400; worst = Math.max(worst, Math.abs(B(x) - f(x))); }
    const corner = B(0.5);
    L.el("circle", {cx: X(0.5), cy: Y(corner), r: 4.5, style: "fill: var(--red); stroke: var(--paper); stroke-width: 1"}, gD);
    document.getElementById("bn-corner").textContent = corner.toFixed(3);
    document.getElementById("bn-pred").textContent = (0.4 / Math.sqrt(n)).toFixed(3);
    document.getElementById("bn-max").textContent = worst.toFixed(3);
  }
  document.getElementById("bn-n").addEventListener("input", e => {
    n = parseInt(e.target.value);
    document.getElementById("bn-nv").textContent = n;
    redraw();
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- hat functions as a basis
# Nodal interpolation by hats at m evenly spaced stations (m coefficients, the readings).
# String displacement: largest gap 20.1 / 6.3 / 1.6 / 0.4 % at m = 5 / 9 / 17 / 33.
# Bump 1.15 exp(-90 (x - 0.38)^2) - 0.45 exp(-45 (x - 0.76)^2): 76.2 / 13.4 / 7.1 / 2.1 / 0.5 % at m = 5 / 9 / 17 / 33 / 65.
# Square pulse on [0.3, 0.7]: largest gap 60 to 80 % at every m, relative L2 46.5 / 23.3 / 11.6 % at m = 5 / 17 / 65.
hats_body = r'''
<svg id="hb-plot" class="plot" viewBox="0 0 720 300"></svg>
<div class="btn-row">
  <button id="hb-string" class="selected">string displacement</button>
  <button id="hb-point">point load</button>
  <button id="hb-bump">bump</button>
  <button id="hb-pulse">square pulse</button>
</div>
<div class="slider-row" style="--slider-color: var(--blue)"><span>stations m</span><input id="hb-m" type="range" min="3" max="65" step="2" value="5"><output id="hb-mv">5</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">coefficients, the readings</span><span class="num" id="hb-n">5</span></div>
  <div class="readout"><span class="label">largest gap, relative</span><span class="num" id="hb-sup">0</span></div>
  <div class="readout"><span class="label">root-mean-square gap, relative</span><span class="num" id="hb-l2">0</span></div>
</div>
<p class="lab-note">The target (solid black), one hat per station weighted by the reading there (gray dashed), and their sum (blue). Every hat equals one at its own station and zero at the others, so the sum passes through every reading and is straight between stations.</p>
<script>
(function(){
  const svg = document.getElementById("hb-plot");
  const X = L.scale(0, 1, 46, 706);
  let Y, gA;
  const targets = {
    string: {f: x => 0.8*Math.sin(Math.PI*x) + 0.4*Math.sin(2*Math.PI*x) + 0.2*Math.sin(3*Math.PI*x), lo: -0.3, hi: 1.3},
    point:  {f: x => 0.5 * Math.min(x, 1 - x), lo: -0.03, hi: 0.3},
    bump:   {f: x => 1.15*Math.exp(-90*(x-0.38)**2) - 0.45*Math.exp(-45*(x-0.76)**2), lo: -0.6, hi: 1.3},
    pulse:  {f: x => (x >= 0.3 && x <= 0.7) ? 1 : 0, lo: -0.15, hi: 1.25},
  };
  let kind = "string", m = 5;
  function redraw(){
    const T = targets[kind], f = T.f;
    svg.innerHTML = "";
    Y = L.scale(T.lo, T.hi, 286, 14);
    L.axes(svg, X, Y, {yMax: T.hi, ny: 3, xlabel: "x", ylabel: "u(x)"});
    gA = L.el("g", {}, svg);
    const h = 1 / (m - 1), xi = Array.from({length: m}, (_, i) => i * h), yi = xi.map(f);
    const hat = i => x => Math.max(0, 1 - Math.abs(x - xi[i]) / h);
    const v = x => { const k = Math.min(m - 2, Math.floor(x / h)), t = x / h - k; return yi[k] * (1 - t) + yi[k + 1] * t; };
    for (let i = 0; i < m; i++) if (yi[i] !== 0)
      L.curve(gA, x => yi[i] * hat(i)(x), X, Y, {stroke: "var(--muted)", width: 1.4, dash: "5 4", opacity: 0.85, n: 801});
    L.curve(gA, f, X, Y, {stroke: "var(--ink)", width: 3, n: 1601});
    L.curve(gA, v, X, Y, {stroke: "var(--blue)", width: 2.5, n: 1601});
    xi.forEach((x, i) => L.el("circle", {cx: X(x), cy: Y(yi[i]), r: 3.2, style: "fill: var(--red)"}, gA));
    const n = 4000; let sup = 0, fs = 0, num = 0, den = 0;
    for (let i = 0; i <= n; i++) {
      const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1, e = f(x) - v(x);
      sup = Math.max(sup, Math.abs(e)); fs = Math.max(fs, Math.abs(f(x))); num += w * e * e; den += w * f(x) * f(x);
    }
    document.getElementById("hb-n").textContent = m;
    document.getElementById("hb-sup").textContent = (100 * sup / fs).toFixed(1) + "%";
    document.getElementById("hb-l2").textContent = (100 * Math.sqrt(num / den)).toFixed(1) + "%";
  }
  for (const k of Object.keys(targets)) document.getElementById("hb-" + k).addEventListener("click", () => {
    kind = k;
    for (const j of Object.keys(targets)) document.getElementById("hb-" + j).className = (j === k) ? "selected" : "";
    redraw();
  });
  document.getElementById("hb-m").addEventListener("input", e => {
    m = parseInt(e.target.value); document.getElementById("hb-mv").textContent = m; redraw();
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- hat nodes that ride with the front
front_body = r'''
<svg id="fr-plot" class="plot" viewBox="0 0 720 300"></svg>
<div class="slider-row" style="--slider-color: var(--ink)"><span>shift of the front c</span><input id="fr-c" type="range" min="0" max="0.45" step="0.01" value="0"><output id="fr-cv">0.00</output></div>
<div class="slider-row" style="--slider-color: var(--blue)"><span>stations m</span><input id="fr-m" type="range" min="8" max="128" step="8" value="32"><output id="fr-mv">32</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>distance d from each node to its edge</span><input id="fr-d" type="range" min="0.005" max="0.08" step="0.005" value="0.02"><output id="fr-dv">0.020</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">m stations, relative L&#178; error</span><span class="num" id="fr-es">0.0%</span></div>
  <div class="readout"><span class="label">four nodes at the edges, relative L&#178; error</span><span class="num" id="fr-ek">0.0%</span></div>
</div>
<p class="lab-note">The front (dashed) has two edges of width w = 0.01. Blue joins m evenly spaced readings by straight lines. Orange is a straight-segment curve with only four nodes, at a &minus; d, a + d, b &minus; d, and b + d, where a and b are the edges (black ticks). It is the sum of the two hats that carry weight one (gray dashed), the hats at a + d and b &minus; d, and the hats at a &minus; d and b + d carry weight zero (gray dotted). The arrows below mark d. The nodes move when the front moves, so two edge positions, a height, and d describe the orange curve.</p>
<script>
(function(){
  const svg = document.getElementById("fr-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.3, 1.3, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.3, ny: 4, xlabel: "x", ylabel: "T(x)"});
  const gC = L.el("g", {}, svg), gD = L.el("g", {}, svg);
  const w = 0.01;
  let c = 0, m = 32, d = 0.02;
  function redraw(){
    const a = 0.15 + c, b = 0.45 + c;
    const T = x => 0.5 * (Math.tanh((x - a) / w) - Math.tanh((x - b) / w));
    const xi = Array.from({length: m}, (_, k) => k / (m - 1));
    const yi = xi.map(T);
    const seg = x => {
      const k = Math.min(m - 2, Math.floor(x * (m - 1)));
      const t = x * (m - 1) - k;
      return yi[k] * (1 - t) + yi[k + 1] * t;
    };
    // hat functions on the nonuniform nodes 0, a - d, a + d, b - d, b + d, 1
    const N = [0, a - d, a + d, b - d, b + d, 1];
    const hat = j => x => {
      if (x <= N[j - 1] || x >= N[j + 1]) return 0;
      return x <= N[j] ? (x - N[j - 1]) / (N[j] - N[j - 1]) : (N[j + 1] - x) / (N[j + 1] - N[j]);
    };
    const net = x => hat(2)(x) + hat(3)(x);
    gC.innerHTML = ""; gD.innerHTML = "";
    L.curve(gC, T, X, Y, {stroke: "var(--ink)", width: 2.5, dash: "7 6", n: 1201});
    L.curve(gC, seg, X, Y, {stroke: "var(--blue)", width: 2.5, n: 1201});
    [1, 4].forEach(j => L.curve(gC, hat(j), X, Y, {stroke: "var(--muted)", width: 1.3, dash: "2 4", opacity: 0.8, n: 2401}));
    [2, 3].forEach(j => L.curve(gC, hat(j), X, Y, {stroke: "var(--muted)", width: 1.8, dash: "6 4", opacity: 0.95, n: 2401}));
    L.curve(gC, net, X, Y, {stroke: "var(--orange)", width: 2.8, n: 2401});
    [a - d, a + d, b - d, b + d].forEach(x =>
      L.el("path", {d: "M" + (X(x)-5) + " " + (Y(-0.3)) + " l10 0 l-5 -9 z", style: "fill: var(--orange)"}, gD));
    // the edges a and b, and d marked on each side of each edge
    [[a, "a"], [b, "b"]].forEach(([e, lab]) => {
      L.el("line", {x1: X(e), x2: X(e), y1: Y(-0.2), y2: Y(-0.08), style: "stroke: var(--ink); stroke-width: 2"}, gD);
      const t = L.el("text", {x: X(e), y: Y(-0.02), "text-anchor": "middle", style: "fill: var(--ink); font-size: 12px"}, gD); t.textContent = lab;
      [[e - d, e], [e, e + d]].forEach(([u0, u1]) => {
        const yy = Y(-0.14);
        L.el("line", {x1: X(u0), x2: X(u1), y1: yy, y2: yy, style: "stroke: var(--orange); stroke-width: 1.5"}, gD);
        L.el("path", {d: "M" + X(u0) + " " + yy + " l5 -3 l0 6 z", style: "fill: var(--orange)"}, gD);
        L.el("path", {d: "M" + X(u1) + " " + yy + " l-5 -3 l0 6 z", style: "fill: var(--orange)"}, gD);
      });
      const td = L.el("text", {x: X(e + d / 2), y: Y(-0.24), "text-anchor": "middle", style: "fill: var(--orange); font-size: 12px"}, gD); td.textContent = "d";
    });
    let ns = 0, nk = 0, den = 0;
    for (let j = 0; j <= 4000; j++) {
      const x = j / 4000, t = T(x);
      ns += (seg(x) - t) ** 2; nk += (net(x) - t) ** 2; den += t * t;
    }
    document.getElementById("fr-es").textContent = (100 * Math.sqrt(ns / den)).toFixed(1) + "%";
    document.getElementById("fr-ek").textContent = (100 * Math.sqrt(nk / den)).toFixed(1) + "%";
  }
  document.getElementById("fr-c").addEventListener("input", e => { c = parseFloat(e.target.value); document.getElementById("fr-cv").textContent = c.toFixed(2); redraw(); });
  document.getElementById("fr-m").addEventListener("input", e => { m = parseInt(e.target.value); document.getElementById("fr-mv").textContent = m; redraw(); });
  document.getElementById("fr-d").addEventListener("input", e => { d = parseFloat(e.target.value); document.getElementById("fr-dv").textContent = d.toFixed(3); redraw(); });
  redraw();
})();
</script>'''

labs = {
    "BERNBUMP": embed_lab(lab_html("Bernstein polynomials for the string displacement",
                                   "Raise the number of coins, then move the probe and watch the weights crowd around it.", bernbump_body), 780),
    "NORMS": embed_lab(lab_html("Error of the station guess in the sup, L&#178;, and H&#185; norms",
                                "Change the station count and watch the three sizes of the same gap fall at different rates.", norms_body), 700),
    "CORNER": embed_lab(lab_html("Three sines against a corner, measured in three norms",
                                 "Move the weights, then press each button and compare the three error readouts.", corner_body), 700),
    "HERO": embed_lab(lab_html("Coefficients on three sine modes",
                               "Move the weights until the gray dashed sum lies on the fixed black displacement.", hero_body), 900),
    "SAMPLING": embed_lab(lab_html("Samples at fixed stations",
                                   "Sweep the station count, then add the sixteenth mode and check which station counts leave the readings unchanged.", sampling_body), 565),
    "BASIS": embed_lab(lab_html("Decay of the coefficients on sine modes",
                                "Pick a target and add modes. The bars are the coefficients, and the error readout measures what the dropped modes held.", basis_body), 600),
    "PROJ": embed_lab(lab_html("Minimizing the squared error over one coefficient",
                               "Slide the coefficient. The squared error is a bowl, and the projection formula finds its bottom without searching.", proj_body), 545),
    "BERN": embed_lab(lab_html("Bernstein polynomials for a corner",
                               "Raise the degree. The hills narrow, the sum closes in on the corner, and the gap at the corner follows 0.4 over the square root of n.", bern_body), 590),
    "HATS": embed_lab(lab_html("Hat functions as a basis",
                               "Pick a target and change the station count. The readings are the weights of the hats.", hats_body), 640),
    "FRONT": embed_lab(lab_html("Hat nodes on a moving front",
                                "Move the front. The stations stay where we put them, and the four nodes follow the edges.", front_body), 620),
}

PAGE = r"""# Representing a Function with Finitely Many Numbers

Here is a taut string, pinned at both ends and pulled sideways.
The whole curve is its displacement $u(x)$ on $0 \le x \le 1$, and we want to store it in a computer with a handful of numbers.
A computer cannot store a curve, so every method in this course, the multilayer perceptron included, stores a short list of numbers and a rule that turns the list back into a curve.
On this page we build such choices by hand, measure what each one loses, and arrive at hat functions whose nodes can move.

## Readings at fixed stations

The obvious move is to measure the string.
Put three sensors along it, at $x = 0$, $\tfrac12$, $1$.
For the displacement $u(x) = 0.8\sin(\pi x) + 0.4\sin(2\pi x) + 0.2\sin(3\pi x)$ they read $0$, $0.60$, $0$, and everything between the sensors is unknown.
So we guess.
The simplest guess connects neighboring readings with straight lines, and we have a curve again.
Now look where the guess is wrong.
The lines never rise above $0.60$, while the string peaks at $1.11$ near $x = 0.23$, so the worst miss is $0.82$, about three quarters of the largest displacement.

Would more sensors fix this?
Between two sensors a distance $h$ apart the curve bends away from a straight line by about $u''h^2/8$ at the middle, so halving $h$ should cut the miss to a quarter.
Five sensors read $0$, $1.11$, $0.60$, $0.31$, $0$ and miss by $20.1$ percent of the largest displacement, nine by $6.3$, and seventeen by $1.6$.
The first two halvings divide the miss by $3.7$ and $3.2$, short of four, because a segment still spans a large part of the shortest wavelength in the curve and the bend inside it is far from a parabola.
From nine sensors on each halving divides the miss by $4.0$.

These gaps are visible only because the curve is known.
Suppose only the seventeen readings were available.
Which curves could have produced them?
Add the wave $0.3\sin(16\pi x)$ to the displacement.
At every station $16\pi x_i$ is a multiple of $\pi$, so the wave is zero there and not one reading changes, while the curve moves by $0.3$ at each crest.
Two functions that agree at every station are aliases on that grid, and the readings cannot tell them apart.
The lab below starts from three stations.
Sweep the station count, then switch the added wave on and find the counts at which no reading moves.

@@SAMPLING@@

## Coefficients on shapes

Here is a different idea.
Instead of asking where the string is, ask what it is made of.
The string vibrates in sine modes, and the displacement above is the first three of them weighted by $0.8$, $0.4$, $0.2$.
Those three numbers give the whole curve, with no grid anywhere.
Check it at mid-span, where the second mode vanishes and the first and third read $1$ and $-1$, so $u(\tfrac12) = 0.8 - 0.2 = 0.6$.
Add two displacements and their coefficients add, scale one and its coefficients scale, so the three coefficients are coordinates and the displacement is a point in a three-dimensional space of functions.
In the lab below the displacement is the solid black curve, and it stays fixed.
The sliders set three weights, and the gray dashed curve is their weighted sum.
Start from the weights $(0.5, 0, 0)$ and move them until the gray curve lies on the black one.
One slider moves the whole gray curve, since each weight belongs to a shape that spans the string, and the distance to the displacement reads zero at $(0.8, 0.4, 0.2)$.
The lab also reports the error in the three norms defined further down the page, the largest gap, the root-mean-square gap, and the slope error, and traces them as the sliders move.
The Solve button finds those weights without searching.
The modes are orthogonal and each has squared norm $\tfrac12$, so each weight is one inner product, $a_k = 2\int_0^1 u(x)\sin(k\pi x)\,dx$, which is the projection developed further down the page.

@@HERO@@

So far every curve was smooth, because every sine is smooth.
Now press on the string at one point.
The point load bends it into two straight segments with a corner at mid-span, and no sum of three sines has a corner.
The closest sum is the best available, and which sum is closest depends on how the error is measured.
That depends on what matters.
If it is clearance under the string, only the worst gap matters, and that is the sup norm.
If it is the overall misfit, all the gaps count at once, so square them, integrate, and take the root, and that is the $L^2$ norm.
If it is the elastic energy, the values are the wrong thing to look at, since the energy is an integral of the squared slope, and the root of the integrated squared slope error is the $H^1$ seminorm.
For the five-sensor guess the three read $0.22$, $0.093$, and $1.20$.
In relative terms the values are off by $14$ percent and the slopes by $42$.
The lab below draws the gap, its square, and its slope error, and the station slider shows the three falling at different rates.

@@NORMS@@

A spike of height one on a base of width $0.04$ has sup norm one, $L^2$ norm $0.115$, and elastic energy $50$, and quartering the base leaves the first, halves the second, and quadruples the third, so the three can disagree without bound.

Now go back to the corner.
In the lab below the point-load displacement is the solid black curve, and three weighted sines make the gray dashed one.
The sum closest in $L^2$ has weights $c_k = 2\sin(k\pi/2)/(k\pi)^2$, that is $(0.2026, 0, -0.0225)$, and it is also the closest in $H^1$, because the sines are orthogonal in both inner products.
It misses by $9.9$ percent of the peak in the largest gap, $4.8$ percent in the root-mean-square gap, and $31.5$ percent in the slopes.
The sum closest in the sup norm has different weights, $(0.2045, 0, -0.0318)$, and it trades the other way, $5.5$ percent in the largest gap against $6.7$ in the root-mean-square gap and $33.9$ in the slopes.
Each sum is closer in the norm it minimizes, and no sum of three sines reaches the corner itself.

@@CORNER@@

Name $L^2$ and ask which sum of three sines is closest to the parabola $x(1-x)$, the shape of the string under a uniform load.
In ordinary geometry a perpendicular dropped from the point onto the plane finds the closest point, and a perpendicular needs a dot product.
For functions the dot product is the integral of the product, $\langle f, g\rangle = \int_0^1 f g\,dx$, and the sine modes are orthogonal in it.
Slide one coefficient and the squared error is a bowl whose bottom sits where the error is orthogonal to the mode, at $c_1 = 2\langle u, \sin(\pi x)\rangle = 8/\pi^3 = 0.258$, one division per coefficient and no search.
The closest sum misses the parabola by $0.87$ percent.
Push $c_1$ twenty percent higher and the eye cannot tell the new curve from the old, while its error norm is $23$ times larger.
The first lab below slides the coefficient.
The second lab adds modes to three targets and shows how fast the coefficients fall, one power of $k$ for each derivative the target keeps continuous, so a smooth target needs few modes and a step's coefficients fall like $1/k$.

@@PROJ@@

@@BASIS@@

## Can a smooth family reach a corner?

Three sines could not make a corner.
Can a family of smooth shapes come as close as we like to any continuous function, a corner included?
Here is Bernstein's idea, tried first on a function it can handle, the string displacement $u(x) = 0.8\sin(\pi x) + 0.4\sin(2\pi x) + 0.2\sin(3\pi x)$ from the coefficients lab.
Take readings of the displacement at the $n + 1$ points $k/n$.
To estimate the displacement at a point $x$, flip $n$ coins that land heads with probability $x$.
The fraction of heads $k/n$ lands near $x$, so average the readings $f(k/n)$ with the probability of exactly $k$ heads as the weight,

$$B_n f(x) = \sum_{k=0}^{n} f\!\left(\frac{k}{n}\right)\binom{n}{k} x^k (1-x)^{n-k}.$$

The weights are nonnegative and add to one, so $B_n f(x)$ is a weighted average of readings taken near $x$, and it is a polynomial of degree $n$ in $x$.
As $n$ grows the fraction of heads concentrates around $x$ with spread $\sqrt{x(1-x)/n}$, the average uses readings closer to $x$, and the gap shrinks.
For the displacement the largest gap sits near $x = 0.24$, below the hump, and it is $0.30$ with $8$ coins, $0.17$ with $16$, $0.091$ with $32$, and $0.024$ with $128$, so each doubling of $n$ halves it.
Voronovskaya's formula predicts the gap at a point where $f$ is twice differentiable, $x(1-x)\,|f''(x)|/(2n)$, and its largest value over the string is $3.18/n$, which gives $0.099$ at $n = 32$ and $0.025$ at $n = 128$.
The formula holds for large $n$, and at $8$ coins it overstates the gap, $0.40$ against the measured $0.30$.
So the gap falls like $1/n$, and at no finite $n$ does the polynomial reproduce the displacement, since a Bernstein polynomial reproduces only straight lines exactly.
The coefficients lab reproduced this displacement with three sine weights, and Bernstein needs $128$ coins to reach $2$ percent of its largest value, because his construction averages readings and never solves for the best weights.
Raise the number of coins in the lab below, then move the probe and watch the weights crowd around it.

@@BERNBUMP@@

Now the corner function $|x - \tfrac12|$.
With two coins the three weights are three hills, one at each wall and one at mid-span, and for the corner function $|x - \tfrac12|$ their sum reads $\tfrac14$ at mid-span where the function is $0$, because every neighbor of the corner sits higher than the corner and any average overshoots there.
As $n$ grows the fraction of heads concentrates near $x$, the hills narrow like $1/\sqrt{n}$, and so does the gap.
At $n = 8$ the gap at the corner is $0.137$ against a prediction of $0.4/\sqrt{n} = 0.141$, and at $n = 32$ it is $0.070$ against $0.071$.
The corner has no second derivative, so Voronovskaya's formula does not apply, and the gap falls like $1/\sqrt{n}$, slower than the bump's $1/n$.
Raise the degree below and watch the hills narrow while the gap at the corner follows the prediction.

@@BERN@@

Weierstrass's theorem states the general fact.
Every continuous function on an interval is within any tolerance of some polynomial.
Notice what the theorem does not say.
It names neither the polynomial nor the degree, and it says nothing about slopes, since every $B_n f$ has slope zero at the corner where the slope of $f$ jumps from $-1$ to $1$.
Universal approximation theorems for networks have the same form, existence without a procedure that finds the approximation.

## Hat functions as a basis

Look again at the straight segments.
They are a basis too.
Take one shape per station, equal to one at its own station, zero at every other station, and straight in between, a hat function $\phi_i$.
Weight each hat by the reading at its station and add,

$$u_h(x) = \sum_{i} u(x_i)\,\phi_i(x),$$

and the sum is the straight-segment guess, with the readings as its coefficients.
A hat is local, since it is zero outside the two segments beside its station, so each coefficient changes the curve only there.
The finite element method is built on this basis.
Courant proposed piecewise-linear hats in 1943, and Galerkin's method chooses their weights by making the error orthogonal to every hat in the energy inner product, which for the string gives the readings, as the energy projection showed above.

How many shapes can hats model?
Every continuous function on the interval, since the gap of the straight-segment guess goes to zero as the spacing $h$ shrinks.
For a function with $|u''| \le M$ the gap is at most $Mh^2/8$, so halving the spacing divides it by four.
Take the string displacement in the lab below.
Five stations miss by $20.1$ percent of the largest displacement, seventeen by $1.6$, and thirty-three by $0.4$.
The bump from the coefficient-decay lab is narrower and needs more hats, $13.4$ percent at nine stations, $2.1$ at thirty-three, and $0.5$ at sixty-five.

@@HATS@@

Back to the point load.
One hat whose node sits on the corner describes it with one number, $0.25$, and on the five-station grid the hats do it with $0.125$, $0.25$, $0.125$ and no error, while the closest three sines miss by $4.8$ percent and thirty-three still miss by $0.20$.
A shape that shares the function's corner needs one number where smooth shapes need infinitely many.

The square pulse, equal to one on $[0.3, 0.7]$ and zero elsewhere, is the case hats cannot finish.
Every sum of hats is continuous, and the pulse jumps.
The largest gap stays between $60$ and $80$ percent at every station count, because the straight segment across each jump misses both sides.
The root-mean-square gap still falls, from $46.5$ percent at five stations to $23.3$ at seventeen and $11.6$ at sixty-five, halving each time the stations are quadrupled, since the region of large error narrows with the spacing.
So which shapes to use depends on the function, and so far we have placed them by hand.

## Let the nodes move

The nodes of a hat basis need not sit on an even grid.
Where would we want them?
Hot fluid pushes a temperature front along a pipe, one shape $T(x - ct)$ whose whole history is its position.
Thirty-two evenly spaced stations reach an error of $8.7$ percent, because most of them record a flat line wherever the front sits.
A straight-segment curve with only four nodes, $0.02$ on either side of each edge, reaches $4.9$ percent, and when the front moves the nodes move with it while the stations stay where we put them.
Fixed nodes make the family a linear subspace, so fitting it is one solve, and the projection theorem guarantees that the solve finds the unique closest member.
Moving nodes give a non-convex problem, and no such guarantee.
The gain is on fields whose features sit in a few places, and the lab below moves the front.

@@FRONT@@

The book's notebooks on [functions as points](https://sciml-book.github.io/sciml_notebook/representations/function-as-a-point.html), [norms](https://sciml-book.github.io/sciml_notebook/representations/norms.html), [projection](https://sciml-book.github.io/sciml_notebook/representations/projection.html), and [Weierstrass by coin flips](https://sciml-book.github.io/sciml_notebook/foundations/weierstrass-bernstein.html) run the computations on this page.
The [second page](kernels-and-families.md) continues with noisy readings, kernels, families of functions, and shapes that move.
"""

page = PAGE
for tag, html in labs.items():
    page = page.replace("@@" + tag + "@@", html)
assert "@@" not in page
(HERE / "representation.md").write_text(page)
print("wrote", HERE / "representation.md", len(page), "chars,", len(labs), "labs")
