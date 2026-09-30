# Kernels, Families of Functions, and Shapes That Move

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Gaussian-process mean and band on the fin&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Change the length scale and the noise level. The band swells where no sensor reaches and narrows at the sensors.&lt;/p&gt;
&lt;svg id=&quot;gp-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 280&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;length scale &amp;ell;&lt;/span&gt;&lt;input id=&quot;gp-l&quot; type=&quot;range&quot; min=&quot;0.05&quot; max=&quot;0.40&quot; step=&quot;0.01&quot; value=&quot;0.15&quot;&gt;&lt;output id=&quot;gp-lv&quot;&gt;0.15&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;noise level &amp;sigma;&lt;/span&gt;&lt;input id=&quot;gp-s&quot; type=&quot;range&quot; min=&quot;0.01&quot; max=&quot;0.30&quot; step=&quot;0.01&quot; value=&quot;0.03&quot;&gt;&lt;output id=&quot;gp-sv&quot;&gt;0.03&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;mean at x = 0.7 (true 0.393)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;gp-m&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;two standard deviations in the gap, largest&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;gp-b&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;error of the mean, relative L&amp;#178;&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;gp-e&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The posterior mean (green) is the ridge curve with &amp;lambda; = &amp;sigma;&amp;#178;, and the shaded band is two standard deviations of the posterior. The band narrows at the sensors, where the noise keeps it open, and swells in the unsensed stretch between 0.55 and 0.85. Try &amp;ell; = 0.15, 0.075, and 0.31.&lt;/p&gt;
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

### Fit the locations and shapes

A Gaussian element describes a localized field through its center, covariance, and amplitude.
An anisotropic covariance permits a long, narrow shape aligned with a ridge.
Fitting these parameters lets the elements concentrate where the field varies.
The Gaussian-field figure illustrates the reconstruction as elements are added and their widths change.

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

For a moving front, a reconstruction must also be checked across its possible positions.
A low-dimensional parameterization can describe a family that is difficult for one small fixed linear space.
Choosing a representation therefore requires both a reconstruction rule and a clear statement of which functions it must approximate.

The companion notebooks on [the cooling fin](https://sciml-book.github.io/sciml_notebook/kernels/the-fin.html) and [one front, every family](https://sciml-book.github.io/sciml_notebook/representations/one-front-every-family.html) contain the underlying experiments.
The fin notebook compares interpolation, regularization, and uncertainty from the same measurements.
The front notebook compares fixed and adaptive representations of the transported profile.
