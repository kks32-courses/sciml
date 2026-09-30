# Kernels, Families of Functions, and Shapes That Move

So far we knew the function and asked how well a list of numbers could stand in for it.
Now eight thermocouples on a cooling fin give eight noisy readings and nothing else, so the function is unknown and the readings may not identify it.
Then a temperature front moves along a pipe, so the target is a whole family of functions, and one fixed set of shapes must serve every member.

## Eight readings and a similarity rule

These are the eight readings from the fin.
Infinitely many curves pass near them.
What do we know that the readings do not say?
The fin conducts heat from its hot base along its length, so the temperature varies smoothly, nearby points should report similar values, and a reading should reach some distance along the fin before it stops telling us anything.
A kernel says how far.
$k(x, x') = \exp(-(x - x')^2/2\ell^2)$ assigns a similarity to every pair of locations, and its length scale $\ell$ states how far the temperature can change appreciably, an assumption about the fin that the readings will later test.

Put one copy of the kernel at each sensor and add the copies with weights, $\hat f(x) = \sum_i \alpha_i k(x, x_i)$.
Asking the sum to pass through every reading gives $\mathbf{K}\boldsymbol{\alpha} = \mathbf{y}$ with $K_{ij} = k(x_i, x_j)$, and for this kernel at distinct sites the matrix is symmetric positive definite, so the weights exist and are unique.
Look at what the solve does.
Two sensors a distance $\ell$ apart with equal readings have similarity $e^{-1/2} = 0.61$ and get weights $0.62$ each, because each neighbor already supplies part of what they share.
At $\ell = 0.15$ the eight copies overlap, the weights alternate in sign up to $4.30$ and $-3.75$, and their sum passes through every reading and stays smooth between them.
Shorten $\ell$ to $0.04$ and each weight is nearly its own reading, so the sum collapses between sensors, to $0.000$ at $x = 0.7$ where the true profile is $0.393$.
A similarity that reaches too short a distance leaves the curve unconstrained between sensors.

<iframe srcdoc="&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;meta charset=&quot;utf-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt;&lt;style&gt;:root { --paper: #fbfbf7; --ink: #1d252c; --muted: #687078; --grid: #e7e7e2; --blue: #2997c8; --orange: #ef8354; --green: #4f9d69; --red: #d95d5d; --yellow: #f0c84b; }
@media (prefers-color-scheme: dark) { :root { --paper: #1e1e1e; --ink: #e8e8e8; --muted: #a0a0a0; --grid: #3a3a3a; --blue: #6fbbdd; --orange: #f0997b; --green: #5dcaa5; --red: #e88a8a; --yellow: #fac775; } }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 14px 16px; background: var(--paper); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, Inter, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.lab { max-width: 760px; margin: 0 auto; }
.lab-title { font-size: 16px; font-weight: 650; margin: 0 0 2px; }
.lab-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 10px; }
svg.plot { width: 100%; display: block; background: var(--paper); }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--muted); stroke-width: 1.2; }
.axis-label { fill: var(--muted); font-size: 11px; }
.slider-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.slider-row &gt; span { font-size: 13px; white-space: nowrap; min-width: 110px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--slider-color, var(--blue)); }
.slider-row output {
  font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 600;
  min-width: 52px; text-align: right;
}
.readout-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 2px; }
.readout {
  background: color-mix(in srgb, var(--ink) 6%, var(--paper));
  border-radius: 8px; padding: 5px 12px;
}
.readout .label { display: block; font-size: 10.5px; color: var(--muted); }
.readout .num {
  font-size: 15px; font-weight: 650; font-variant-numeric: tabular-nums;
}
.btn-row { display: flex; gap: 8px; margin: 8px 0; flex-wrap: wrap; }
.btn-row button {
  font: inherit; font-size: 12.5px; padding: 4px 12px; cursor: pointer;
  color: var(--ink); background: transparent;
  border: 1px solid var(--grid); border-radius: 999px;
}
.btn-row button.selected { border-color: var(--blue); color: var(--blue); font-weight: 650; }
.lab-note { font-size: 12px; color: var(--muted); margin: 8px 0 0; }
.float-label {
  position: absolute; top: 10px; right: 12px; font-size: 11px;
  color: var(--muted); letter-spacing: .04em;
}
.plot-wrap { position: relative; }
&lt;/style&gt;&lt;script&gt;
const L = (function () {
  const NS = &quot;http://www.w3.org/2000/svg&quot;;
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function scale(a, b, pa, pb) { return v =&gt; pa + (v - a) * (pb - pa) / (b - a); }
  function pathd(fn, X, Y, n) {
    n = n || 241;
    let d = &quot;&quot;;
    for (let i = 0; i &lt; n; i++) {
      const x = i / (n - 1);
      d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(2) + &quot; &quot; + Y(fn(x)).toFixed(2);
    }
    return d;
  }
  function curve(svg, fn, X, Y, opts) {
    opts = opts || {};
    // Colors go through the style attribute: CSS var() is not valid in
    // SVG presentation attributes, but works in inline style.
    const style = &quot;stroke:&quot; + (opts.stroke || &quot;var(--blue)&quot;)
      + &quot;;stroke-width:&quot; + (opts.width || 3)
      + (opts.dash ? &quot;;stroke-dasharray:&quot; + opts.dash : &quot;&quot;)
      + &quot;;opacity:&quot; + (opts.opacity === undefined ? 1 : opts.opacity)
      + &quot;;stroke-linecap:round;stroke-linejoin:round&quot;;
    return el(&quot;path&quot;, { d: pathd(fn, X, Y, opts.n), fill: &quot;none&quot;, style: style }, svg);
  }
  function axes(svg, X, Y, opts) {
    opts = opts || {};
    const g = el(&quot;g&quot;, {}, svg);
    const nx = opts.nx || 8, ny = opts.ny || 4;
    for (let i = 0; i &lt;= nx; i++) {
      const px = X(i / nx);
      el(&quot;line&quot;, { x1: px, y1: Y(opts.yMax), x2: px, y2: Y(-opts.yMax), class: &quot;grid-line&quot; }, g);
    }
    for (let j = 0; j &lt;= ny; j++) {
      const u = -opts.yMax + 2 * opts.yMax * j / ny;
      el(&quot;line&quot;, { x1: X(0), y1: Y(u), x2: X(1), y2: Y(u), class: &quot;grid-line&quot; }, g);
    }
    el(&quot;line&quot;, { x1: X(0), y1: Y(0), x2: X(1), y2: Y(0), class: &quot;axis-line&quot; }, g);
    el(&quot;line&quot;, { x1: X(0), y1: Y(opts.yMax), x2: X(0), y2: Y(-opts.yMax), class: &quot;axis-line&quot; }, g);
    const lx = el(&quot;text&quot;, { x: X(1) - 4, y: Y(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot; }, g);
    lx.textContent = opts.xlabel || &quot;x&quot;;
    const ly = el(&quot;text&quot;, { x: X(0) + 6, y: Y(opts.yMax) + 12, class: &quot;axis-label&quot; }, g);
    ly.textContent = opts.ylabel || &quot;&quot;;
    return g;
  }
  function fmt(v, d) { const s = v.toFixed(d === undefined ? 2 : d); return s === &quot;-0.00&quot; ? &quot;0.00&quot; : s; }
  return { el, scale, pathd, curve, axes, fmt, NS };
})();
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Weighted kernel copies through eight readings&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move the two locations to read their similarity, then shorten the length scale and watch the interpolant collapse between the fin&#x27;s sensors.&lt;/p&gt;
&lt;div style=&quot;display:flex; gap:10px;&quot;&gt;
  &lt;div style=&quot;flex:1&quot;&gt;&lt;svg id=&quot;kb-sim&quot; class=&quot;plot&quot; viewBox=&quot;0 0 355 230&quot;&gt;&lt;/svg&gt;&lt;/div&gt;
  &lt;div style=&quot;flex:1&quot;&gt;&lt;svg id=&quot;kb-fit&quot; class=&quot;plot&quot; viewBox=&quot;0 0 355 230&quot;&gt;&lt;/svg&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;location x&lt;/span&gt;&lt;input id=&quot;kb-x1&quot; type=&quot;range&quot; min=&quot;0.02&quot; max=&quot;0.98&quot; step=&quot;0.01&quot; value=&quot;0.30&quot;&gt;&lt;output id=&quot;kb-x1v&quot;&gt;0.30&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;location x&amp;prime;&lt;/span&gt;&lt;input id=&quot;kb-x2&quot; type=&quot;range&quot; min=&quot;0.02&quot; max=&quot;0.98&quot; step=&quot;0.01&quot; value=&quot;0.45&quot;&gt;&lt;output id=&quot;kb-x2v&quot;&gt;0.45&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;length scale &amp;ell;&lt;/span&gt;&lt;input id=&quot;kb-l&quot; type=&quot;range&quot; min=&quot;0.04&quot; max=&quot;0.40&quot; step=&quot;0.01&quot; value=&quot;0.15&quot;&gt;&lt;output id=&quot;kb-lv&quot;&gt;0.15&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;similarity k(x, x&amp;prime;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;kb-k&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest weight |&amp;alpha;|&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;kb-a&quot;&gt;0.00&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;interpolant at x = 0.7 (true 0.393)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;kb-v&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Left, two kernel copies and their similarity. Right, one copy per fin reading (dashed) and the sum that passes through every reading (blue), against the true profile (dark dashed). Shorten &amp;ell; and watch the sum collapse between sensors.&lt;/p&gt;
&lt;script&gt;
(function(){
  function solve(A, b){
    const n = b.length, M = A.map((r, i) =&gt; [...r, b[i]]);
    for (let c = 0; c &lt; n; c++) {
      let p = c; for (let r = c + 1; r &lt; n; r++) if (Math.abs(M[r][c]) &gt; Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c] || 1e-12; for (let j = c; j &lt;= n; j++) M[c][j] /= d;
      for (let r = 0; r &lt; n; r++) if (r !== c) { const f = M[r][c]; for (let j = c; j &lt;= n; j++) M[r][j] -= f * M[c][j]; }
    }
    return M.map(r =&gt; r[n]);
  }
  const XS = [0.03, 0.12, 0.24, 0.33, 0.45, 0.53, 0.88, 0.97], YS = [1.1163, 1.1507, 0.9156, 0.5613, 0.3194, 0.2675, 0.3613, 0.2406];
  const Tfin = x =&gt; Math.exp(-1.5 * x) * (1 + 0.4 * Math.sin(3 * Math.PI * x));
  const sS = document.getElementById(&quot;kb-sim&quot;), sF = document.getElementById(&quot;kb-fit&quot;);
  const XA = L.scale(0, 1, 40, 345), YA = L.scale(-0.1, 1.2, 216, 14);
  L.axes(sS, XA, YA, {yMax: 1.2, ny: 2, xlabel: &quot;x&quot;});
  const XB = L.scale(0, 1, 40, 345), YB = L.scale(-1.2, 1.6, 216, 14);
  L.axes(sF, XB, YB, {yMax: 1.6, ny: 4, xlabel: &quot;x&quot;, ylabel: &quot;T&quot;});
  const gS = L.el(&quot;g&quot;, {}, sS), gF = L.el(&quot;g&quot;, {}, sF);
  let x1 = 0.30, x2 = 0.45, ell = 0.15;
  const k = (a, b) =&gt; Math.exp(-(a - b) * (a - b) / (2 * ell * ell));
  function redraw(){
    gS.innerHTML = &quot;&quot;; gF.innerHTML = &quot;&quot;;
    L.curve(gS, x =&gt; k(x, x1), XA, YA, {stroke: &quot;var(--blue)&quot;, width: 3});
    L.curve(gS, x =&gt; k(x, x2), XA, YA, {stroke: &quot;var(--orange)&quot;, width: 3});
    document.getElementById(&quot;kb-k&quot;).textContent = k(x1, x2).toFixed(3);
    const K = XS.map(a =&gt; XS.map(b =&gt; k(a, b)));
    const alpha = solve(K, YS);
    const fit = x =&gt; XS.reduce((s, xi, i) =&gt; s + alpha[i] * k(x, xi), 0);
    L.curve(gF, Tfin, XB, YB, {stroke: &quot;var(--ink)&quot;, width: 1.8, dash: &quot;6 6&quot;, n: 401});
    XS.forEach((xi, i) =&gt; L.curve(gF, x =&gt; alpha[i] * k(x, xi), XB, YB, {stroke: &quot;var(--muted)&quot;, width: 1, dash: &quot;4 4&quot;, opacity: 0.7}));
    L.curve(gF, fit, XB, YB, {stroke: &quot;var(--blue)&quot;, width: 3, n: 401});
    XS.forEach((xi, i) =&gt; L.el(&quot;circle&quot;, {cx: XB(xi), cy: YB(YS[i]), r: 4, style: &quot;fill: var(--red); stroke: var(--paper); stroke-width: 1&quot;}, gF));
    document.getElementById(&quot;kb-a&quot;).textContent = Math.max(...alpha.map(Math.abs)).toFixed(2);
    document.getElementById(&quot;kb-v&quot;).textContent = fit(0.7).toFixed(3);
  }
  [[&quot;kb-x1&quot;, v =&gt; x1 = v], [&quot;kb-x2&quot;, v =&gt; x2 = v], [&quot;kb-l&quot;, v =&gt; ell = v]].forEach(([id, set]) =&gt; {
    document.getElementById(id).addEventListener(&quot;input&quot;, e =&gt; {
      set(parseFloat(e.target.value)); document.getElementById(id + &quot;v&quot;).textContent = parseFloat(e.target.value).toFixed(2); redraw();
    });
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:610px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

Could we have picked any similarity rule?
Try one.
Put sensors at $0$, $0.6\ell$, $1.2\ell$, and call two of them similar, with value one, when closer than $\ell$ and unrelated otherwise.
The matrix has eigenvalues $1 - \sqrt2 = -0.414$, $1$, and $1 + \sqrt2$, and the weights $(1, -\sqrt2, 1)$ give $\mathbf{w}^\top\mathbf{K}\mathbf{w} = -1.66$.
A negative value cannot be a squared length, so no inner product produces this rule.
A kernel is positive definite when $\mathbf{w}^\top\mathbf{K}\mathbf{w} \ge 0$ for every choice of sites and weights.
Whenever $k(x, x') = \phi(x)^\top\phi(x')$ for some list of features, $\mathbf{w}^\top\mathbf{K}\mathbf{w} = \|\sum_i w_i \phi(x_i)\|^2 \ge 0$, and every positive definite kernel has this form with the list allowed to be infinite.
So a kernel method is linear regression on features we never write down.

## A space where evaluation is an inner product

Now make the kernel's geometry explicit.
Declare the inner product of two kernel copies to be their similarity, $\langle k(x_1, \cdot), k(x_2, \cdot)\rangle_k = k(x_1, x_2)$, extend it to finite sums by linearity, and complete the collection.
That is the reproducing kernel Hilbert space of the kernel.
Take $f = \alpha_1 k(x_1, \cdot) + \alpha_2 k(x_2, \cdot)$ and pair it with the copy centered at $x$.
The rule returns $\alpha_1 k(x_1, x) + \alpha_2 k(x_2, x)$, which is $f(x)$, and in general $f(x) = \langle f, k(x, \cdot)\rangle_k$ for every member of the space.
Evaluating at a point is an inner product, continuous by the Cauchy-Schwarz inequality, which is what $L^2$ could not give us.
Differentiate the identity and the slope is bounded too, $|f'(x)| \le \|f\|_k / \ell$, so a function that climbs by $1$ over $\ell/10$ has norm at least $10$.
The norm measures roughness, and we are about to penalize it.

<iframe srcdoc="&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;meta charset=&quot;utf-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt;&lt;style&gt;:root { --paper: #fbfbf7; --ink: #1d252c; --muted: #687078; --grid: #e7e7e2; --blue: #2997c8; --orange: #ef8354; --green: #4f9d69; --red: #d95d5d; --yellow: #f0c84b; }
@media (prefers-color-scheme: dark) { :root { --paper: #1e1e1e; --ink: #e8e8e8; --muted: #a0a0a0; --grid: #3a3a3a; --blue: #6fbbdd; --orange: #f0997b; --green: #5dcaa5; --red: #e88a8a; --yellow: #fac775; } }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 14px 16px; background: var(--paper); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, Inter, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.lab { max-width: 760px; margin: 0 auto; }
.lab-title { font-size: 16px; font-weight: 650; margin: 0 0 2px; }
.lab-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 10px; }
svg.plot { width: 100%; display: block; background: var(--paper); }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--muted); stroke-width: 1.2; }
.axis-label { fill: var(--muted); font-size: 11px; }
.slider-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.slider-row &gt; span { font-size: 13px; white-space: nowrap; min-width: 110px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--slider-color, var(--blue)); }
.slider-row output {
  font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 600;
  min-width: 52px; text-align: right;
}
.readout-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 2px; }
.readout {
  background: color-mix(in srgb, var(--ink) 6%, var(--paper));
  border-radius: 8px; padding: 5px 12px;
}
.readout .label { display: block; font-size: 10.5px; color: var(--muted); }
.readout .num {
  font-size: 15px; font-weight: 650; font-variant-numeric: tabular-nums;
}
.btn-row { display: flex; gap: 8px; margin: 8px 0; flex-wrap: wrap; }
.btn-row button {
  font: inherit; font-size: 12.5px; padding: 4px 12px; cursor: pointer;
  color: var(--ink); background: transparent;
  border: 1px solid var(--grid); border-radius: 999px;
}
.btn-row button.selected { border-color: var(--blue); color: var(--blue); font-weight: 650; }
.lab-note { font-size: 12px; color: var(--muted); margin: 8px 0 0; }
.float-label {
  position: absolute; top: 10px; right: 12px; font-size: 11px;
  color: var(--muted); letter-spacing: .04em;
}
.plot-wrap { position: relative; }
&lt;/style&gt;&lt;script&gt;
const L = (function () {
  const NS = &quot;http://www.w3.org/2000/svg&quot;;
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function scale(a, b, pa, pb) { return v =&gt; pa + (v - a) * (pb - pa) / (b - a); }
  function pathd(fn, X, Y, n) {
    n = n || 241;
    let d = &quot;&quot;;
    for (let i = 0; i &lt; n; i++) {
      const x = i / (n - 1);
      d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(2) + &quot; &quot; + Y(fn(x)).toFixed(2);
    }
    return d;
  }
  function curve(svg, fn, X, Y, opts) {
    opts = opts || {};
    // Colors go through the style attribute: CSS var() is not valid in
    // SVG presentation attributes, but works in inline style.
    const style = &quot;stroke:&quot; + (opts.stroke || &quot;var(--blue)&quot;)
      + &quot;;stroke-width:&quot; + (opts.width || 3)
      + (opts.dash ? &quot;;stroke-dasharray:&quot; + opts.dash : &quot;&quot;)
      + &quot;;opacity:&quot; + (opts.opacity === undefined ? 1 : opts.opacity)
      + &quot;;stroke-linecap:round;stroke-linejoin:round&quot;;
    return el(&quot;path&quot;, { d: pathd(fn, X, Y, opts.n), fill: &quot;none&quot;, style: style }, svg);
  }
  function axes(svg, X, Y, opts) {
    opts = opts || {};
    const g = el(&quot;g&quot;, {}, svg);
    const nx = opts.nx || 8, ny = opts.ny || 4;
    for (let i = 0; i &lt;= nx; i++) {
      const px = X(i / nx);
      el(&quot;line&quot;, { x1: px, y1: Y(opts.yMax), x2: px, y2: Y(-opts.yMax), class: &quot;grid-line&quot; }, g);
    }
    for (let j = 0; j &lt;= ny; j++) {
      const u = -opts.yMax + 2 * opts.yMax * j / ny;
      el(&quot;line&quot;, { x1: X(0), y1: Y(u), x2: X(1), y2: Y(u), class: &quot;grid-line&quot; }, g);
    }
    el(&quot;line&quot;, { x1: X(0), y1: Y(0), x2: X(1), y2: Y(0), class: &quot;axis-line&quot; }, g);
    el(&quot;line&quot;, { x1: X(0), y1: Y(opts.yMax), x2: X(0), y2: Y(-opts.yMax), class: &quot;axis-line&quot; }, g);
    const lx = el(&quot;text&quot;, { x: X(1) - 4, y: Y(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot; }, g);
    lx.textContent = opts.xlabel || &quot;x&quot;;
    const ly = el(&quot;text&quot;, { x: X(0) + 6, y: Y(opts.yMax) + 12, class: &quot;axis-label&quot; }, g);
    ly.textContent = opts.ylabel || &quot;&quot;;
    return g;
  }
  function fmt(v, d) { const s = v.toFixed(d === undefined ? 2 : d); return s === &quot;-0.00&quot; ? &quot;0.00&quot; : s; }
  return { el, scale, pathd, curve, axes, fmt, NS };
})();
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Point evaluation as an inner product&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Weight three kernel copies and move the probe. The value at the probe is an inner product, and the slope never exceeds the norm over the length scale.&lt;/p&gt;
&lt;svg id=&quot;rk-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 280&quot;&gt;&lt;/svg&gt;
&lt;div style=&quot;display:flex; gap:14px; flex-wrap:wrap;&quot;&gt;
  &lt;div class=&quot;slider-row&quot; style=&quot;flex:1; --slider-color: var(--blue)&quot;&gt;&lt;span&gt;&amp;alpha;&amp;#8321; at 0.2&lt;/span&gt;&lt;input id=&quot;rk-a1&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0.80&quot;&gt;&lt;output id=&quot;rk-a1v&quot;&gt;0.80&lt;/output&gt;&lt;/div&gt;
  &lt;div class=&quot;slider-row&quot; style=&quot;flex:1; --slider-color: var(--orange)&quot;&gt;&lt;span&gt;&amp;alpha;&amp;#8322; at 0.5&lt;/span&gt;&lt;input id=&quot;rk-a2&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;-0.45&quot;&gt;&lt;output id=&quot;rk-a2v&quot;&gt;-0.45&lt;/output&gt;&lt;/div&gt;
  &lt;div class=&quot;slider-row&quot; style=&quot;flex:1; --slider-color: var(--green)&quot;&gt;&lt;span&gt;&amp;alpha;&amp;#8323; at 0.8&lt;/span&gt;&lt;input id=&quot;rk-a3&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0.65&quot;&gt;&lt;output id=&quot;rk-a3v&quot;&gt;0.65&lt;/output&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--red)&quot;&gt;&lt;span&gt;probe x*&lt;/span&gt;&lt;input id=&quot;rk-p&quot; type=&quot;range&quot; min=&quot;0.02&quot; max=&quot;0.98&quot; step=&quot;0.01&quot; value=&quot;0.61&quot;&gt;&lt;output id=&quot;rk-pv&quot;&gt;0.61&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;length scale &amp;ell;&lt;/span&gt;&lt;input id=&quot;rk-l&quot; type=&quot;range&quot; min=&quot;0.06&quot; max=&quot;0.32&quot; step=&quot;0.01&quot; value=&quot;0.16&quot;&gt;&lt;output id=&quot;rk-lv&quot;&gt;0.16&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;f(x*) = &amp;lang;f, k(x*,&amp;middot;)&amp;rang;&lt;sub&gt;k&lt;/sub&gt;&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;rk-f&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;&amp;Vert;f&amp;Vert;&amp;#178;&lt;sub&gt;k&lt;/sub&gt; = &amp;alpha;&amp;#7488;K&amp;alpha;&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;rk-n&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;steepest slope, and the bound &amp;Vert;f&amp;Vert;&lt;sub&gt;k&lt;/sub&gt;/&amp;ell;&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;rk-s&quot;&gt;0.00 &amp;le; 0.00&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Three kernel copies (dashed) and their weighted sum (dark). The red probe reads f(x*), which the reproducing identity writes as an inner product with the copy centered at x*. The norm is a roughness measure, and the slope never exceeds the norm divided by the length scale.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;rk-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.4, 1.4, 266, 14);
  L.axes(svg, X, Y, {yMax: 1.4, xlabel: &quot;x&quot;, ylabel: &quot;f(x)&quot;});
  const g = L.el(&quot;g&quot;, {}, svg);
  const centers = [0.2, 0.5, 0.8], cols = [&quot;var(--blue)&quot;, &quot;var(--orange)&quot;, &quot;var(--green)&quot;];
  let alpha = [0.8, -0.45, 0.65], probe = 0.61, ell = 0.16;
  function redraw(){
    const k = (a, b) =&gt; Math.exp(-(a - b) * (a - b) / (2 * ell * ell));
    const f = x =&gt; alpha.reduce((s, q, i) =&gt; s + q * k(x, centers[i]), 0);
    g.innerHTML = &quot;&quot;;
    centers.forEach((c, i) =&gt; L.curve(g, x =&gt; alpha[i] * k(x, c), X, Y, {stroke: cols[i], width: 2, dash: &quot;7 7&quot;, opacity: 0.7}));
    L.curve(g, f, X, Y, {stroke: &quot;var(--ink)&quot;, width: 3.5, n: 401});
    L.el(&quot;line&quot;, {x1: X(probe), x2: X(probe), y1: Y(1.4), y2: Y(-1.4), style: &quot;stroke: var(--red); stroke-width: 1.5; stroke-dasharray: 5 5&quot;}, g);
    L.el(&quot;circle&quot;, {cx: X(probe), cy: Y(f(probe)), r: 5, style: &quot;fill: var(--red)&quot;}, g);
    let n2 = 0; for (let i = 0; i &lt; 3; i++) for (let j = 0; j &lt; 3; j++) n2 += alpha[i] * alpha[j] * k(centers[i], centers[j]);
    let slope = 0; for (let i = 1; i &lt; 800; i++) { const a = (i - 1) / 800, b = i / 800; slope = Math.max(slope, Math.abs(f(b) - f(a)) * 800); }
    document.getElementById(&quot;rk-f&quot;).textContent = f(probe).toFixed(3);
    document.getElementById(&quot;rk-n&quot;).textContent = n2.toFixed(3);
    document.getElementById(&quot;rk-s&quot;).textContent = slope.toFixed(2) + &quot; ≤ &quot; + (Math.sqrt(Math.max(n2, 0)) / ell).toFixed(2);
  }
  [[&quot;rk-a1&quot;, v =&gt; alpha[0] = v], [&quot;rk-a2&quot;, v =&gt; alpha[1] = v], [&quot;rk-a3&quot;, v =&gt; alpha[2] = v], [&quot;rk-p&quot;, v =&gt; probe = v], [&quot;rk-l&quot;, v =&gt; ell = v]].forEach(([id, set]) =&gt; {
    document.getElementById(id).addEventListener(&quot;input&quot;, e =&gt; {
      set(parseFloat(e.target.value)); document.getElementById(id + &quot;v&quot;).textContent = parseFloat(e.target.value).toFixed(2); redraw();
    });
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:650px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

## Noise, a penalty, and a band

The interpolant reproduces every reading, noise included.
How bad is that?
At overlap $0.99$ the two-sensor matrix has eigenvalues $1.99$ and $0.01$, along $(1, 1)$ and $(1, -1)$.
A reading pair $(1, 1)$ gives weights near one half each, and a noise pair $(\varepsilon, -\varepsilon)$, the difference between two nearly equal readings, gives weights $\pm\varepsilon/0.01$, a hundred times the noise.
The curve itself moves by fourteen times the noise, since the function $\phi_1 - \phi_2$ has norm $0.14$.
We have changed the question.
Approximating a known function asked which member is closest.
Recovering an unknown function from noisy readings asks whether the readings identify it, and interpolation answers by trusting every reading to the last digit.

So trade misfit against roughness and minimize $\sum_i (f(x_i) - y_i)^2 + \lambda\|f\|_k^2$ over the whole space.
Any component of $f$ orthogonal to the span of the data's kernel copies changes no reading and raises the norm, so the minimizer lies in that span, and substituting gives $(\mathbf{K} + \lambda\mathbf{I})\boldsymbol{\alpha} = \mathbf{y}$, the interpolation solve with $\lambda$ added to the diagonal.
At $\lambda = 0.1$ the small divisor rises from $0.01$ to $0.11$ and the amplification drops from a hundred to nine.

The same computation reads as probability.
Build two temperatures from independent standard normals, $f(x_1) = Z_1$ and $f(x_2) = \rho Z_1 + \sqrt{1 - \rho^2}\,Z_2$, so both have variance one and covariance $\rho$.
Observe $f(x_1) = y$.
That fixes $Z_1 = y$, and $f(x_2)$ is Gaussian with mean $\rho y$ and standard deviation $\sqrt{1 - \rho^2}$, which is $0.44$ at $\rho = 0.9$ and $0.95$ at $\rho = 0.3$.
A Gaussian process makes any finite list of values jointly Gaussian with covariances $k(x_i, x_j)$, and this was the case $n = 2$.
Condition it on the eight noisy readings and every location gets a Gaussian.
Its mean is the ridge curve with $\lambda = \sigma^2$, and its variance is the prior's variance minus what the sensors explained.
On the fin the two-standard-deviation band collapses at the sensors and swells in the unsensed stretch, to $0.90$ at $\ell = 0.15$ and to $1.99$ at $\ell = 0.075$.
Let the readings choose $\ell$ by the marginal likelihood, the probability the model assigns to the data seen, and they pick $\ell = 0.31$, where the mean is within $3.2$ percent and the band in the gap is $0.12$.
Remember what the band is.
It is the model's own uncertainty, conditional on the kernel, the noise level, and the length scale.

<iframe srcdoc="&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;meta charset=&quot;utf-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt;&lt;style&gt;:root { --paper: #fbfbf7; --ink: #1d252c; --muted: #687078; --grid: #e7e7e2; --blue: #2997c8; --orange: #ef8354; --green: #4f9d69; --red: #d95d5d; --yellow: #f0c84b; }
@media (prefers-color-scheme: dark) { :root { --paper: #1e1e1e; --ink: #e8e8e8; --muted: #a0a0a0; --grid: #3a3a3a; --blue: #6fbbdd; --orange: #f0997b; --green: #5dcaa5; --red: #e88a8a; --yellow: #fac775; } }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 14px 16px; background: var(--paper); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, Inter, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.lab { max-width: 760px; margin: 0 auto; }
.lab-title { font-size: 16px; font-weight: 650; margin: 0 0 2px; }
.lab-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 10px; }
svg.plot { width: 100%; display: block; background: var(--paper); }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--muted); stroke-width: 1.2; }
.axis-label { fill: var(--muted); font-size: 11px; }
.slider-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.slider-row &gt; span { font-size: 13px; white-space: nowrap; min-width: 110px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--slider-color, var(--blue)); }
.slider-row output {
  font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 600;
  min-width: 52px; text-align: right;
}
.readout-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 2px; }
.readout {
  background: color-mix(in srgb, var(--ink) 6%, var(--paper));
  border-radius: 8px; padding: 5px 12px;
}
.readout .label { display: block; font-size: 10.5px; color: var(--muted); }
.readout .num {
  font-size: 15px; font-weight: 650; font-variant-numeric: tabular-nums;
}
.btn-row { display: flex; gap: 8px; margin: 8px 0; flex-wrap: wrap; }
.btn-row button {
  font: inherit; font-size: 12.5px; padding: 4px 12px; cursor: pointer;
  color: var(--ink); background: transparent;
  border: 1px solid var(--grid); border-radius: 999px;
}
.btn-row button.selected { border-color: var(--blue); color: var(--blue); font-weight: 650; }
.lab-note { font-size: 12px; color: var(--muted); margin: 8px 0 0; }
.float-label {
  position: absolute; top: 10px; right: 12px; font-size: 11px;
  color: var(--muted); letter-spacing: .04em;
}
.plot-wrap { position: relative; }
&lt;/style&gt;&lt;script&gt;
const L = (function () {
  const NS = &quot;http://www.w3.org/2000/svg&quot;;
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function scale(a, b, pa, pb) { return v =&gt; pa + (v - a) * (pb - pa) / (b - a); }
  function pathd(fn, X, Y, n) {
    n = n || 241;
    let d = &quot;&quot;;
    for (let i = 0; i &lt; n; i++) {
      const x = i / (n - 1);
      d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(2) + &quot; &quot; + Y(fn(x)).toFixed(2);
    }
    return d;
  }
  function curve(svg, fn, X, Y, opts) {
    opts = opts || {};
    // Colors go through the style attribute: CSS var() is not valid in
    // SVG presentation attributes, but works in inline style.
    const style = &quot;stroke:&quot; + (opts.stroke || &quot;var(--blue)&quot;)
      + &quot;;stroke-width:&quot; + (opts.width || 3)
      + (opts.dash ? &quot;;stroke-dasharray:&quot; + opts.dash : &quot;&quot;)
      + &quot;;opacity:&quot; + (opts.opacity === undefined ? 1 : opts.opacity)
      + &quot;;stroke-linecap:round;stroke-linejoin:round&quot;;
    return el(&quot;path&quot;, { d: pathd(fn, X, Y, opts.n), fill: &quot;none&quot;, style: style }, svg);
  }
  function axes(svg, X, Y, opts) {
    opts = opts || {};
    const g = el(&quot;g&quot;, {}, svg);
    const nx = opts.nx || 8, ny = opts.ny || 4;
    for (let i = 0; i &lt;= nx; i++) {
      const px = X(i / nx);
      el(&quot;line&quot;, { x1: px, y1: Y(opts.yMax), x2: px, y2: Y(-opts.yMax), class: &quot;grid-line&quot; }, g);
    }
    for (let j = 0; j &lt;= ny; j++) {
      const u = -opts.yMax + 2 * opts.yMax * j / ny;
      el(&quot;line&quot;, { x1: X(0), y1: Y(u), x2: X(1), y2: Y(u), class: &quot;grid-line&quot; }, g);
    }
    el(&quot;line&quot;, { x1: X(0), y1: Y(0), x2: X(1), y2: Y(0), class: &quot;axis-line&quot; }, g);
    el(&quot;line&quot;, { x1: X(0), y1: Y(opts.yMax), x2: X(0), y2: Y(-opts.yMax), class: &quot;axis-line&quot; }, g);
    const lx = el(&quot;text&quot;, { x: X(1) - 4, y: Y(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot; }, g);
    lx.textContent = opts.xlabel || &quot;x&quot;;
    const ly = el(&quot;text&quot;, { x: X(0) + 6, y: Y(opts.yMax) + 12, class: &quot;axis-label&quot; }, g);
    ly.textContent = opts.ylabel || &quot;&quot;;
    return g;
  }
  function fmt(v, d) { const s = v.toFixed(d === undefined ? 2 : d); return s === &quot;-0.00&quot; ? &quot;0.00&quot; : s; }
  return { el, scale, pathd, curve, axes, fmt, NS };
})();
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Gaussian-process mean and band on the fin&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Change the length scale and the noise level. The band swells where no sensor reaches and collapses at the sensors.&lt;/p&gt;
&lt;svg id=&quot;gp-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 280&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;length scale &amp;ell;&lt;/span&gt;&lt;input id=&quot;gp-l&quot; type=&quot;range&quot; min=&quot;0.05&quot; max=&quot;0.40&quot; step=&quot;0.01&quot; value=&quot;0.15&quot;&gt;&lt;output id=&quot;gp-lv&quot;&gt;0.15&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;noise level &amp;sigma;&lt;/span&gt;&lt;input id=&quot;gp-s&quot; type=&quot;range&quot; min=&quot;0.01&quot; max=&quot;0.30&quot; step=&quot;0.01&quot; value=&quot;0.03&quot;&gt;&lt;output id=&quot;gp-sv&quot;&gt;0.03&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;mean at x = 0.7 (true 0.393)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;gp-m&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;two standard deviations in the gap, largest&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;gp-b&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;error of the mean, relative L&amp;#178;&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;gp-e&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The posterior mean (green) is the ridge curve with &amp;lambda; = &amp;sigma;&amp;#178;, and the shaded band is two standard deviations of the posterior. The band collapses at the sensors and swells in the unsensed stretch between 0.55 and 0.85. Try &amp;ell; = 0.15, 0.075, and 0.31.&lt;/p&gt;
&lt;script&gt;
(function(){
  function solve(A, b){
    const n = b.length, M = A.map((r, i) =&gt; [...r, b[i]]);
    for (let c = 0; c &lt; n; c++) {
      let p = c; for (let r = c + 1; r &lt; n; r++) if (Math.abs(M[r][c]) &gt; Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c] || 1e-12; for (let j = c; j &lt;= n; j++) M[c][j] /= d;
      for (let r = 0; r &lt; n; r++) if (r !== c) { const f = M[r][c]; for (let j = c; j &lt;= n; j++) M[r][j] -= f * M[c][j]; }
    }
    return M.map(r =&gt; r[n]);
  }
  const XS = [0.03, 0.12, 0.24, 0.33, 0.45, 0.53, 0.88, 0.97], YS = [1.1163, 1.1507, 0.9156, 0.5613, 0.3194, 0.2675, 0.3613, 0.2406];
  const Tfin = x =&gt; Math.exp(-1.5 * x) * (1 + 0.4 * Math.sin(3 * Math.PI * x));
  const svg = document.getElementById(&quot;gp-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.8, 1.8, 266, 14);
  L.axes(svg, X, Y, {yMax: 1.8, ny: 4, xlabel: &quot;x&quot;, ylabel: &quot;T(x)&quot;});
  const g = L.el(&quot;g&quot;, {}, svg);
  let ell = 0.15, sig = 0.03;
  function redraw(){
    const k = (a, b) =&gt; Math.exp(-(a - b) * (a - b) / (2 * ell * ell));
    const n = XS.length;
    const K = XS.map((a, i) =&gt; XS.map((b, j) =&gt; k(a, b) + (i === j ? sig * sig : 0)));
    const w = solve(K, YS);
    const mean = x =&gt; XS.reduce((s, xi, i) =&gt; s + w[i] * k(x, xi), 0);
    const sd = x =&gt; { const ks = XS.map(xi =&gt; k(x, xi)); const z = solve(K, ks); return Math.sqrt(Math.max(1e-9, 1 - ks.reduce((s, q, i) =&gt; s + q * z[i], 0))); };
    g.innerHTML = &quot;&quot;;
    let d = &quot;&quot;;
    for (let i = 0; i &lt;= 200; i++) { const x = i / 200; d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(1) + &quot; &quot; + Y(mean(x) + 2 * sd(x)).toFixed(1); }
    for (let i = 200; i &gt;= 0; i--) { const x = i / 200; d += &quot; L&quot; + X(x).toFixed(1) + &quot; &quot; + Y(mean(x) - 2 * sd(x)).toFixed(1); }
    L.el(&quot;path&quot;, {d: d + &quot; Z&quot;, style: &quot;fill: var(--green); opacity: 0.18&quot;}, g);
    L.curve(g, Tfin, X, Y, {stroke: &quot;var(--ink)&quot;, width: 1.8, dash: &quot;6 6&quot;, n: 401});
    L.curve(g, mean, X, Y, {stroke: &quot;var(--green)&quot;, width: 3, n: 401});
    XS.forEach((xi, i) =&gt; L.el(&quot;circle&quot;, {cx: X(xi), cy: Y(YS[i]), r: 4, style: &quot;fill: var(--red); stroke: var(--paper); stroke-width: 1&quot;}, g));
    let band = 0, num = 0, den = 0;
    for (let i = 0; i &lt;= 400; i++) { const x = i / 400; const t = Tfin(x), m = mean(x); num += (m - t) ** 2; den += t * t; if (x &gt;= 0.55 &amp;&amp; x &lt;= 0.85) band = Math.max(band, 2 * sd(x)); }
    document.getElementById(&quot;gp-m&quot;).textContent = mean(0.7).toFixed(3);
    document.getElementById(&quot;gp-b&quot;).textContent = band.toFixed(3);
    document.getElementById(&quot;gp-e&quot;).textContent = (100 * Math.sqrt(num / den)).toFixed(1) + &quot;%&quot;;
  }
  [[&quot;gp-l&quot;, v =&gt; ell = v], [&quot;gp-s&quot;, v =&gt; sig = v]].forEach(([id, set]) =&gt; {
    document.getElementById(id).addEventListener(&quot;input&quot;, e =&gt; {
      set(parseFloat(e.target.value)); document.getElementById(id + &quot;v&quot;).textContent = parseFloat(e.target.value).toFixed(2); redraw();
    });
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:560px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

## A family of functions and its width

Now the target itself moves.
Hot fluid pushes a temperature front along a pipe, one shape $T(x - ct)$ whose whole history is its position, and one description should cover every position at once.
Thirty-two evenly spaced stations reach an error of $8.7$ percent, since wherever the front sits most of them record a flat line, while two edge positions, a width, an amplitude, and a shift rebuild the front at every time.
The [kinks lab](representation.md#let-the-kinks-move) on the first page shows four ReLU kinks doing what the thirty-two stations cannot.

How well can any fixed basis do on a whole family?
Translate a unit spike across three grid points, so the snapshots are three perpendicular unit vectors.
For any plane through the origin the three squared distances to it add up to $3 - 2 = 1$, so the worst snapshot sits at distance at least $\sqrt{1/3} = 0.577$, whichever plane we choose.
A family that depends on one number needs all three dimensions.
The Kolmogorov $n$-width is the worst-case error of the best $n$-dimensional subspace, and a snapshot matrix's singular value decomposition gives a lower bound for it.
Diffuse a steep-edged pulse and its $k$-th coefficient shrinks by $e^{-(2\pi k)^2 t}$, so four modes reach one percent.
Translate the same pulse and the coefficient only changes phase, every frequency keeps its energy, and we need $103$ modes.
Every translate of a sine lies in a two-dimensional span, so the difficulty is a sharp edge at every position, and the width says nothing about how few parameters the family depends on.

## Shapes that move

Nothing below contradicts the width.
Each idea drops the hypothesis of one fixed subspace.
Let the physics move the shapes first.
Drop markers into the pipe and let each ride the flow with the temperature it started with.
For a constant-velocity flow a value that rides its carrier is never interpolated, so the front returns after five round trips unchanged, while a first-order upwind grid keeps eight, eleven, and sixteen percent of the edge steepness at $100$, $200$, and $400$ points, since each step averages neighbors.

<iframe srcdoc="&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;meta charset=&quot;utf-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt;&lt;style&gt;:root { --paper: #fbfbf7; --ink: #1d252c; --muted: #687078; --grid: #e7e7e2; --blue: #2997c8; --orange: #ef8354; --green: #4f9d69; --red: #d95d5d; --yellow: #f0c84b; }
@media (prefers-color-scheme: dark) { :root { --paper: #1e1e1e; --ink: #e8e8e8; --muted: #a0a0a0; --grid: #3a3a3a; --blue: #6fbbdd; --orange: #f0997b; --green: #5dcaa5; --red: #e88a8a; --yellow: #fac775; } }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 14px 16px; background: var(--paper); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, Inter, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.lab { max-width: 760px; margin: 0 auto; }
.lab-title { font-size: 16px; font-weight: 650; margin: 0 0 2px; }
.lab-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 10px; }
svg.plot { width: 100%; display: block; background: var(--paper); }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--muted); stroke-width: 1.2; }
.axis-label { fill: var(--muted); font-size: 11px; }
.slider-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.slider-row &gt; span { font-size: 13px; white-space: nowrap; min-width: 110px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--slider-color, var(--blue)); }
.slider-row output {
  font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 600;
  min-width: 52px; text-align: right;
}
.readout-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 2px; }
.readout {
  background: color-mix(in srgb, var(--ink) 6%, var(--paper));
  border-radius: 8px; padding: 5px 12px;
}
.readout .label { display: block; font-size: 10.5px; color: var(--muted); }
.readout .num {
  font-size: 15px; font-weight: 650; font-variant-numeric: tabular-nums;
}
.btn-row { display: flex; gap: 8px; margin: 8px 0; flex-wrap: wrap; }
.btn-row button {
  font: inherit; font-size: 12.5px; padding: 4px 12px; cursor: pointer;
  color: var(--ink); background: transparent;
  border: 1px solid var(--grid); border-radius: 999px;
}
.btn-row button.selected { border-color: var(--blue); color: var(--blue); font-weight: 650; }
.lab-note { font-size: 12px; color: var(--muted); margin: 8px 0 0; }
.float-label {
  position: absolute; top: 10px; right: 12px; font-size: 11px;
  color: var(--muted); letter-spacing: .04em;
}
.plot-wrap { position: relative; }
&lt;/style&gt;&lt;script&gt;
const L = (function () {
  const NS = &quot;http://www.w3.org/2000/svg&quot;;
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function scale(a, b, pa, pb) { return v =&gt; pa + (v - a) * (pb - pa) / (b - a); }
  function pathd(fn, X, Y, n) {
    n = n || 241;
    let d = &quot;&quot;;
    for (let i = 0; i &lt; n; i++) {
      const x = i / (n - 1);
      d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(2) + &quot; &quot; + Y(fn(x)).toFixed(2);
    }
    return d;
  }
  function curve(svg, fn, X, Y, opts) {
    opts = opts || {};
    // Colors go through the style attribute: CSS var() is not valid in
    // SVG presentation attributes, but works in inline style.
    const style = &quot;stroke:&quot; + (opts.stroke || &quot;var(--blue)&quot;)
      + &quot;;stroke-width:&quot; + (opts.width || 3)
      + (opts.dash ? &quot;;stroke-dasharray:&quot; + opts.dash : &quot;&quot;)
      + &quot;;opacity:&quot; + (opts.opacity === undefined ? 1 : opts.opacity)
      + &quot;;stroke-linecap:round;stroke-linejoin:round&quot;;
    return el(&quot;path&quot;, { d: pathd(fn, X, Y, opts.n), fill: &quot;none&quot;, style: style }, svg);
  }
  function axes(svg, X, Y, opts) {
    opts = opts || {};
    const g = el(&quot;g&quot;, {}, svg);
    const nx = opts.nx || 8, ny = opts.ny || 4;
    for (let i = 0; i &lt;= nx; i++) {
      const px = X(i / nx);
      el(&quot;line&quot;, { x1: px, y1: Y(opts.yMax), x2: px, y2: Y(-opts.yMax), class: &quot;grid-line&quot; }, g);
    }
    for (let j = 0; j &lt;= ny; j++) {
      const u = -opts.yMax + 2 * opts.yMax * j / ny;
      el(&quot;line&quot;, { x1: X(0), y1: Y(u), x2: X(1), y2: Y(u), class: &quot;grid-line&quot; }, g);
    }
    el(&quot;line&quot;, { x1: X(0), y1: Y(0), x2: X(1), y2: Y(0), class: &quot;axis-line&quot; }, g);
    el(&quot;line&quot;, { x1: X(0), y1: Y(opts.yMax), x2: X(0), y2: Y(-opts.yMax), class: &quot;axis-line&quot; }, g);
    const lx = el(&quot;text&quot;, { x: X(1) - 4, y: Y(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot; }, g);
    lx.textContent = opts.xlabel || &quot;x&quot;;
    const ly = el(&quot;text&quot;, { x: X(0) + 6, y: Y(opts.yMax) + 12, class: &quot;axis-label&quot; }, g);
    ly.textContent = opts.ylabel || &quot;&quot;;
    return g;
  }
  function fmt(v, d) { const s = v.toFixed(d === undefined ? 2 : d); return s === &quot;-0.00&quot; ? &quot;0.00&quot; : s; }
  return { el, scale, pathd, curve, axes, fmt, NS };
})();
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;A fixed grid and moving carriers&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move the material. The grid stays and re-interpolates, the carriers keep their values.&lt;/p&gt;
&lt;svg id=&quot;pt-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 760 320&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;material motion t&lt;/span&gt;&lt;input id=&quot;pt-t&quot; type=&quot;range&quot; min=&quot;0&quot; max=&quot;1&quot; step=&quot;0.01&quot; value=&quot;0.35&quot;&gt;&lt;output id=&quot;pt-tv&quot;&gt;0.35&lt;/output&gt;&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Left, a fixed grid whose cells stay where they are while a blob of material drifts through them, so its value must be re-interpolated onto the cells at every step. Right, carriers that move with the material and keep the value they started with, so nothing is interpolated until the field is read between them.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;pt-plot&quot;);
  const gL = L.el(&quot;g&quot;, {transform: &quot;translate(25 40)&quot;}, svg), gR = L.el(&quot;g&quot;, {transform: &quot;translate(405 40)&quot;}, svg);
  const t1 = L.el(&quot;text&quot;, {x: 190, y: 22, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;middle&quot;}, svg); t1.textContent = &quot;fixed grid, values re-interpolated&quot;;
  const t2 = L.el(&quot;text&quot;, {x: 570, y: 22, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;middle&quot;}, svg); t2.textContent = &quot;carriers that move with the material&quot;;
  let t = 0.35;
  function redraw(){
    gL.innerHTML = &quot;&quot;; gR.innerHTML = &quot;&quot;;
    L.el(&quot;rect&quot;, {width: 330, height: 240, style: &quot;fill: none; stroke: var(--grid)&quot;}, gL);
    for (let i = 0; i &lt;= 8; i++) L.el(&quot;line&quot;, {x1: i * 41.25, y1: 0, x2: i * 41.25, y2: 240, class: &quot;grid-line&quot;}, gL);
    for (let i = 0; i &lt;= 6; i++) L.el(&quot;line&quot;, {x1: 0, y1: i * 40, x2: 330, y2: i * 40, class: &quot;grid-line&quot;}, gL);
    L.el(&quot;circle&quot;, {cx: 145 + 34 * t, cy: 132 - 18 * t, r: 58, style: &quot;fill: var(--blue); opacity: 0.18&quot;}, gL);
    L.el(&quot;rect&quot;, {width: 330, height: 240, style: &quot;fill: none; stroke: var(--grid)&quot;}, gR);
    for (let i = 0; i &lt; 48; i++) {
      const x = 0.08 + (i % 8) * 0.12, y = 0.12 + Math.floor(i / 8) * 0.15;
      const nx = x + 0.12 * t * Math.sin(Math.PI * y), ny = y - 0.08 * t * Math.sin(Math.PI * x);
      const v = Math.exp(-18 * ((x - 0.42) ** 2 + (y - 0.55) ** 2));
      L.el(&quot;circle&quot;, {cx: nx * 330, cy: (1 - ny) * 240, r: 4 + 5 * v, style: &quot;fill: &quot; + (v &gt; 0.35 ? &quot;var(--orange)&quot; : &quot;var(--blue)&quot;) + &quot;; opacity: &quot; + (0.45 + 0.5 * v)}, gR);
    }
  }
  document.getElementById(&quot;pt-t&quot;).addEventListener(&quot;input&quot;, e =&gt; { t = parseFloat(e.target.value); document.getElementById(&quot;pt-tv&quot;).textContent = t.toFixed(2); redraw(); });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:520px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

Or let an optimizer move them.
Sixteen trained Gaussians, ninety-six parameters, reach a relative error of $0.0125$ on a field with two thin ridges, against $0.30$ for a fixed grid of one hundred coefficients, because two of them stretch into needles along the ridges.
With fixed shapes the fit is a linear solve with the projection theorem's guarantee, and with trained centers and covariances it is a non-convex optimization without one.

<iframe srcdoc="&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;meta charset=&quot;utf-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt;&lt;style&gt;:root { --paper: #fbfbf7; --ink: #1d252c; --muted: #687078; --grid: #e7e7e2; --blue: #2997c8; --orange: #ef8354; --green: #4f9d69; --red: #d95d5d; --yellow: #f0c84b; }
@media (prefers-color-scheme: dark) { :root { --paper: #1e1e1e; --ink: #e8e8e8; --muted: #a0a0a0; --grid: #3a3a3a; --blue: #6fbbdd; --orange: #f0997b; --green: #5dcaa5; --red: #e88a8a; --yellow: #fac775; } }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 14px 16px; background: var(--paper); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, Inter, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.lab { max-width: 760px; margin: 0 auto; }
.lab-title { font-size: 16px; font-weight: 650; margin: 0 0 2px; }
.lab-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 10px; }
svg.plot { width: 100%; display: block; background: var(--paper); }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--muted); stroke-width: 1.2; }
.axis-label { fill: var(--muted); font-size: 11px; }
.slider-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.slider-row &gt; span { font-size: 13px; white-space: nowrap; min-width: 110px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--slider-color, var(--blue)); }
.slider-row output {
  font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 600;
  min-width: 52px; text-align: right;
}
.readout-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 2px; }
.readout {
  background: color-mix(in srgb, var(--ink) 6%, var(--paper));
  border-radius: 8px; padding: 5px 12px;
}
.readout .label { display: block; font-size: 10.5px; color: var(--muted); }
.readout .num {
  font-size: 15px; font-weight: 650; font-variant-numeric: tabular-nums;
}
.btn-row { display: flex; gap: 8px; margin: 8px 0; flex-wrap: wrap; }
.btn-row button {
  font: inherit; font-size: 12.5px; padding: 4px 12px; cursor: pointer;
  color: var(--ink); background: transparent;
  border: 1px solid var(--grid); border-radius: 999px;
}
.btn-row button.selected { border-color: var(--blue); color: var(--blue); font-weight: 650; }
.lab-note { font-size: 12px; color: var(--muted); margin: 8px 0 0; }
.float-label {
  position: absolute; top: 10px; right: 12px; font-size: 11px;
  color: var(--muted); letter-spacing: .04em;
}
.plot-wrap { position: relative; }
&lt;/style&gt;&lt;script&gt;
const L = (function () {
  const NS = &quot;http://www.w3.org/2000/svg&quot;;
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function scale(a, b, pa, pb) { return v =&gt; pa + (v - a) * (pb - pa) / (b - a); }
  function pathd(fn, X, Y, n) {
    n = n || 241;
    let d = &quot;&quot;;
    for (let i = 0; i &lt; n; i++) {
      const x = i / (n - 1);
      d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(2) + &quot; &quot; + Y(fn(x)).toFixed(2);
    }
    return d;
  }
  function curve(svg, fn, X, Y, opts) {
    opts = opts || {};
    // Colors go through the style attribute: CSS var() is not valid in
    // SVG presentation attributes, but works in inline style.
    const style = &quot;stroke:&quot; + (opts.stroke || &quot;var(--blue)&quot;)
      + &quot;;stroke-width:&quot; + (opts.width || 3)
      + (opts.dash ? &quot;;stroke-dasharray:&quot; + opts.dash : &quot;&quot;)
      + &quot;;opacity:&quot; + (opts.opacity === undefined ? 1 : opts.opacity)
      + &quot;;stroke-linecap:round;stroke-linejoin:round&quot;;
    return el(&quot;path&quot;, { d: pathd(fn, X, Y, opts.n), fill: &quot;none&quot;, style: style }, svg);
  }
  function axes(svg, X, Y, opts) {
    opts = opts || {};
    const g = el(&quot;g&quot;, {}, svg);
    const nx = opts.nx || 8, ny = opts.ny || 4;
    for (let i = 0; i &lt;= nx; i++) {
      const px = X(i / nx);
      el(&quot;line&quot;, { x1: px, y1: Y(opts.yMax), x2: px, y2: Y(-opts.yMax), class: &quot;grid-line&quot; }, g);
    }
    for (let j = 0; j &lt;= ny; j++) {
      const u = -opts.yMax + 2 * opts.yMax * j / ny;
      el(&quot;line&quot;, { x1: X(0), y1: Y(u), x2: X(1), y2: Y(u), class: &quot;grid-line&quot; }, g);
    }
    el(&quot;line&quot;, { x1: X(0), y1: Y(0), x2: X(1), y2: Y(0), class: &quot;axis-line&quot; }, g);
    el(&quot;line&quot;, { x1: X(0), y1: Y(opts.yMax), x2: X(0), y2: Y(-opts.yMax), class: &quot;axis-line&quot; }, g);
    const lx = el(&quot;text&quot;, { x: X(1) - 4, y: Y(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot; }, g);
    lx.textContent = opts.xlabel || &quot;x&quot;;
    const ly = el(&quot;text&quot;, { x: X(0) + 6, y: Y(opts.yMax) + 12, class: &quot;axis-label&quot; }, g);
    ly.textContent = opts.ylabel || &quot;&quot;;
    return g;
  }
  function fmt(v, d) { const s = v.toFixed(d === undefined ? 2 : d); return s === &quot;-0.00&quot; ? &quot;0.00&quot; : s; }
  return { el, scale, pathd, curve, axes, fmt, NS };
})();
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;A field from Gaussian elements&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Add elements and change their width. Every number that describes an element can be trained.&lt;/p&gt;
&lt;svg id=&quot;sp-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;Gaussian elements&lt;/span&gt;&lt;input id=&quot;sp-n&quot; type=&quot;range&quot; min=&quot;1&quot; max=&quot;6&quot; step=&quot;1&quot; value=&quot;3&quot;&gt;&lt;output id=&quot;sp-nv&quot;&gt;3&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;width&lt;/span&gt;&lt;input id=&quot;sp-w&quot; type=&quot;range&quot; min=&quot;0.05&quot; max=&quot;0.25&quot; step=&quot;0.01&quot; value=&quot;0.13&quot;&gt;&lt;output id=&quot;sp-wv&quot;&gt;0.13&lt;/output&gt;&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;A two-dimensional field built from Gaussian elements, each with a center, a width, and an amplitude. In a fit every one of these numbers is trainable, so the elements move to where the field varies, and the fit becomes a non-convex optimization.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;sp-plot&quot;);
  const g = L.el(&quot;g&quot;, {}, svg);
  const splats = [[0.24, 0.68, 1], [0.47, 0.42, 0.8], [0.72, 0.66, 0.9], [0.66, 0.24, 0.58], [0.34, 0.2, 0.62], [0.84, 0.43, 0.48]];
  let n = 3, w = 0.13;
  function redraw(){
    g.innerHTML = &quot;&quot;;
    L.el(&quot;rect&quot;, {x: 40, y: 30, width: 640, height: 252, style: &quot;fill: none; stroke: var(--grid)&quot;}, g);
    for (let iy = 0; iy &lt; 18; iy++) for (let ix = 0; ix &lt; 35; ix++) {
      const x = (ix + 0.5) / 35, y = (iy + 0.5) / 18;
      const v = splats.slice(0, n).reduce((s, q) =&gt; s + q[2] * Math.exp(-((x - q[0]) ** 2 + (y - q[1]) ** 2) / (2 * w * w)), 0);
      L.el(&quot;rect&quot;, {x: 40 + ix * 18.3, y: 30 + (17 - iy) * 14, width: 18.8, height: 14.5, style: &quot;fill: &quot; + (v &gt; 0.85 ? &quot;var(--orange)&quot; : &quot;var(--blue)&quot;) + &quot;; opacity: &quot; + Math.min(0.92, v * 0.7)}, g);
    }
    splats.slice(0, n).forEach((q, i) =&gt; {
      L.el(&quot;circle&quot;, {cx: 40 + q[0] * 640, cy: 30 + (1 - q[1]) * 252, r: 5, style: &quot;fill: var(--ink); stroke: var(--paper); stroke-width: 2&quot;}, g);
      const tt = L.el(&quot;text&quot;, {x: 49 + q[0] * 640, y: 26 + (1 - q[1]) * 252, class: &quot;axis-label&quot;}, g); tt.textContent = &quot;g&quot; + (i + 1);
    });
  }
  document.getElementById(&quot;sp-n&quot;).addEventListener(&quot;input&quot;, e =&gt; { n = parseInt(e.target.value); document.getElementById(&quot;sp-nv&quot;).textContent = n; redraw(); });
  document.getElementById(&quot;sp-w&quot;).addEventListener(&quot;input&quot;, e =&gt; { w = parseFloat(e.target.value); document.getElementById(&quot;sp-wv&quot;).textContent = w.toFixed(2); redraw(); });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:520px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

Or keep every shape fixed and choose among them.
Keep the $n$ largest Haar coefficients of the front, and different functions keep different coefficients, so the family is no longer one fixed subspace.
Thirty-two selected coefficients represent the front with $1.3$ percent error against $5.1$ for the first thirty-two sines, at the storage of thirty-two values and thirty-two indices, and past about $128$ terms the sines resolve the edge width and win from there.

## Choosing for the fin

Suppose we did not know the fin's profile.
Which of five descriptions of the same eight readings should we trust?
Against the true profile they reach $6.5$ percent for straight segments, $23$ for a cubic by least squares, $31$ for the degree-seven polynomial through all eight readings, $11$ for the kernel interpolant at $\ell = 0.15$, and $3.2$ for the Gaussian-process mean at $\ell = 0.31$, the only one that also reports a band.
In practice the true profile is unavailable, and three kinds of evidence remain.
The known noise level rules out any description that reproduces the readings exactly, and three of the five do.
Withhold each reading in turn, fit the other seven, and predict it, and the held-out errors are $0.095$, $0.310$, $3.57$, $0.112$, and $0.034$ against a noise level of $0.03$, the same ranking with no knowledge of the truth.
The physics admits the smooth family, and the band's sensitivity to the length scale says what the gap assumes.

<iframe srcdoc="&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;meta charset=&quot;utf-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt;&lt;style&gt;:root { --paper: #fbfbf7; --ink: #1d252c; --muted: #687078; --grid: #e7e7e2; --blue: #2997c8; --orange: #ef8354; --green: #4f9d69; --red: #d95d5d; --yellow: #f0c84b; }
@media (prefers-color-scheme: dark) { :root { --paper: #1e1e1e; --ink: #e8e8e8; --muted: #a0a0a0; --grid: #3a3a3a; --blue: #6fbbdd; --orange: #f0997b; --green: #5dcaa5; --red: #e88a8a; --yellow: #fac775; } }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 14px 16px; background: var(--paper); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, Inter, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.lab { max-width: 760px; margin: 0 auto; }
.lab-title { font-size: 16px; font-weight: 650; margin: 0 0 2px; }
.lab-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 10px; }
svg.plot { width: 100%; display: block; background: var(--paper); }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--muted); stroke-width: 1.2; }
.axis-label { fill: var(--muted); font-size: 11px; }
.slider-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.slider-row &gt; span { font-size: 13px; white-space: nowrap; min-width: 110px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--slider-color, var(--blue)); }
.slider-row output {
  font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 600;
  min-width: 52px; text-align: right;
}
.readout-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 2px; }
.readout {
  background: color-mix(in srgb, var(--ink) 6%, var(--paper));
  border-radius: 8px; padding: 5px 12px;
}
.readout .label { display: block; font-size: 10.5px; color: var(--muted); }
.readout .num {
  font-size: 15px; font-weight: 650; font-variant-numeric: tabular-nums;
}
.btn-row { display: flex; gap: 8px; margin: 8px 0; flex-wrap: wrap; }
.btn-row button {
  font: inherit; font-size: 12.5px; padding: 4px 12px; cursor: pointer;
  color: var(--ink); background: transparent;
  border: 1px solid var(--grid); border-radius: 999px;
}
.btn-row button.selected { border-color: var(--blue); color: var(--blue); font-weight: 650; }
.lab-note { font-size: 12px; color: var(--muted); margin: 8px 0 0; }
.float-label {
  position: absolute; top: 10px; right: 12px; font-size: 11px;
  color: var(--muted); letter-spacing: .04em;
}
.plot-wrap { position: relative; }
&lt;/style&gt;&lt;script&gt;
const L = (function () {
  const NS = &quot;http://www.w3.org/2000/svg&quot;;
  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function scale(a, b, pa, pb) { return v =&gt; pa + (v - a) * (pb - pa) / (b - a); }
  function pathd(fn, X, Y, n) {
    n = n || 241;
    let d = &quot;&quot;;
    for (let i = 0; i &lt; n; i++) {
      const x = i / (n - 1);
      d += (i ? &quot; L&quot; : &quot;M&quot;) + X(x).toFixed(2) + &quot; &quot; + Y(fn(x)).toFixed(2);
    }
    return d;
  }
  function curve(svg, fn, X, Y, opts) {
    opts = opts || {};
    // Colors go through the style attribute: CSS var() is not valid in
    // SVG presentation attributes, but works in inline style.
    const style = &quot;stroke:&quot; + (opts.stroke || &quot;var(--blue)&quot;)
      + &quot;;stroke-width:&quot; + (opts.width || 3)
      + (opts.dash ? &quot;;stroke-dasharray:&quot; + opts.dash : &quot;&quot;)
      + &quot;;opacity:&quot; + (opts.opacity === undefined ? 1 : opts.opacity)
      + &quot;;stroke-linecap:round;stroke-linejoin:round&quot;;
    return el(&quot;path&quot;, { d: pathd(fn, X, Y, opts.n), fill: &quot;none&quot;, style: style }, svg);
  }
  function axes(svg, X, Y, opts) {
    opts = opts || {};
    const g = el(&quot;g&quot;, {}, svg);
    const nx = opts.nx || 8, ny = opts.ny || 4;
    for (let i = 0; i &lt;= nx; i++) {
      const px = X(i / nx);
      el(&quot;line&quot;, { x1: px, y1: Y(opts.yMax), x2: px, y2: Y(-opts.yMax), class: &quot;grid-line&quot; }, g);
    }
    for (let j = 0; j &lt;= ny; j++) {
      const u = -opts.yMax + 2 * opts.yMax * j / ny;
      el(&quot;line&quot;, { x1: X(0), y1: Y(u), x2: X(1), y2: Y(u), class: &quot;grid-line&quot; }, g);
    }
    el(&quot;line&quot;, { x1: X(0), y1: Y(0), x2: X(1), y2: Y(0), class: &quot;axis-line&quot; }, g);
    el(&quot;line&quot;, { x1: X(0), y1: Y(opts.yMax), x2: X(0), y2: Y(-opts.yMax), class: &quot;axis-line&quot; }, g);
    const lx = el(&quot;text&quot;, { x: X(1) - 4, y: Y(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot; }, g);
    lx.textContent = opts.xlabel || &quot;x&quot;;
    const ly = el(&quot;text&quot;, { x: X(0) + 6, y: Y(opts.yMax) + 12, class: &quot;axis-label&quot; }, g);
    ly.textContent = opts.ylabel || &quot;&quot;;
    return g;
  }
  function fmt(v, d) { const s = v.toFixed(d === undefined ? 2 : d); return s === &quot;-0.00&quot; ? &quot;0.00&quot; : s; }
  return { el, scale, pathd, curve, axes, fmt, NS };
})();
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Choosing a representation for the fin&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Pick a family and read what it stores, who places its shapes, what it assumes, and what to check first.&lt;/p&gt;
&lt;div class=&quot;btn-row&quot; id=&quot;cp-tabs&quot; role=&quot;tablist&quot;&gt;&lt;/div&gt;
&lt;div id=&quot;cp-panel&quot; style=&quot;border:1px solid var(--grid); border-radius:10px; padding:12px 14px; margin-top:6px;&quot;&gt;&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The assumption says where a family applies, and its failure is the first thing to check when a fit goes wrong.&lt;/p&gt;
&lt;script&gt;
(function(){
  const fams = [
    [&quot;stations&quot;, &quot;values at fixed points&quot;, &quot;the analyst&quot;, &quot;linear variation between stations&quot;, &quot;smooth fields on a fixed geometry&quot;, &quot;resolution, then aliasing&quot;],
    [&quot;hats&quot;, &quot;nodal values&quot;, &quot;the analyst and a mesher&quot;, &quot;piecewise-linear variation&quot;, &quot;complex geometry&quot;, &quot;resolution at corners and layers&quot;],
    [&quot;sine modes&quot;, &quot;global coefficients&quot;, &quot;the analyst&quot;, &quot;a smooth odd periodic continuation&quot;, &quot;smooth pinned or periodic fields&quot;, &quot;the overshoot beside a jump&quot;],
    [&quot;wavelets, selected&quot;, &quot;the largest coefficients and their indices&quot;, &quot;the analyst, the data selects&quot;, &quot;few active scales at each location&quot;, &quot;localized features&quot;, &quot;the count too small to resolve the finest scale&quot;],
    [&quot;kernels and GP&quot;, &quot;weights at the data sites&quot;, &quot;the data&quot;, &quot;smoothness at a length scale, a prior in the probabilistic reading&quot;, &quot;scattered noisy readings&quot;, &quot;a length scale wrong for the field&quot;],
    [&quot;particles&quot;, &quot;positions and payloads&quot;, &quot;the dynamics&quot;, &quot;payloads ride their carriers&quot;, &quot;advection and large deformation&quot;, &quot;derivatives from a disordered cloud&quot;],
    [&quot;Gaussian splats&quot;, &quot;centers, covariances, amplitudes&quot;, &quot;the optimizer&quot;, &quot;a smooth field with concentrated features&quot;, &quot;concentrated features&quot;, &quot;a descent that stalls&quot;],
    [&quot;neural fields&quot;, &quot;network weights&quot;, &quot;the optimizer&quot;, &quot;the network&#x27;s smoothness bias&quot;, &quot;the next lecture&quot;, &quot;optimization and hidden bias&quot;],
  ];
  const tabs = document.getElementById(&quot;cp-tabs&quot;), panel = document.getElementById(&quot;cp-panel&quot;);
  let sel = 0;
  function render(){
    tabs.innerHTML = &quot;&quot;;
    fams.forEach((f, i) =&gt; { const b = document.createElement(&quot;button&quot;); b.textContent = f[0]; if (i === sel) b.className = &quot;selected&quot;; b.onclick = () =&gt; { sel = i; render(); }; tabs.appendChild(b); });
    const f = fams[sel];
    panel.innerHTML = &quot;&lt;p class=&#x27;lab-title&#x27; style=&#x27;margin:0 0 6px&#x27;&gt;&quot; + f[0] + &quot;&lt;/p&gt;&quot; +
      &quot;&lt;div class=&#x27;readout-row&#x27;&gt;&quot; +
      &quot;&lt;div class=&#x27;readout&#x27;&gt;&lt;span class=&#x27;label&#x27;&gt;stores&lt;/span&gt;&lt;span class=&#x27;num&#x27; style=&#x27;font-size:13px&#x27;&gt;&quot; + f[1] + &quot;&lt;/span&gt;&lt;/div&gt;&quot; +
      &quot;&lt;div class=&#x27;readout&#x27;&gt;&lt;span class=&#x27;label&#x27;&gt;shapes placed by&lt;/span&gt;&lt;span class=&#x27;num&#x27; style=&#x27;font-size:13px&#x27;&gt;&quot; + f[2] + &quot;&lt;/span&gt;&lt;/div&gt;&quot; +
      &quot;&lt;div class=&#x27;readout&#x27;&gt;&lt;span class=&#x27;label&#x27;&gt;assumes&lt;/span&gt;&lt;span class=&#x27;num&#x27; style=&#x27;font-size:13px&#x27;&gt;&quot; + f[3] + &quot;&lt;/span&gt;&lt;/div&gt;&quot; +
      &quot;&lt;div class=&#x27;readout&#x27;&gt;&lt;span class=&#x27;label&#x27;&gt;native regime&lt;/span&gt;&lt;span class=&#x27;num&#x27; style=&#x27;font-size:13px&#x27;&gt;&quot; + f[4] + &quot;&lt;/span&gt;&lt;/div&gt;&quot; +
      &quot;&lt;div class=&#x27;readout&#x27;&gt;&lt;span class=&#x27;label&#x27;&gt;check first&lt;/span&gt;&lt;span class=&#x27;num&#x27; style=&#x27;font-size:13px&#x27;&gt;&quot; + f[5] + &quot;&lt;/span&gt;&lt;/div&gt;&quot; +
      &quot;&lt;/div&gt;&quot;;
  }
  render();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:380px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

The book's notebooks on [the cooling fin](https://sciml-book.github.io/sciml_notebook/kernels/the-fin.html) and [one front, every family](https://sciml-book.github.io/sciml_notebook/representations/one-front-every-family.html) run every computation on this page.
