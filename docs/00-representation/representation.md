# Representing a Function with Finitely Many Numbers

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Samples at fixed stations&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Sweep the station count, then add the sixteenth mode and check which station counts leave the readings unchanged.&lt;/p&gt;
&lt;svg id=&quot;sm-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;sm-m&quot; type=&quot;range&quot; min=&quot;3&quot; max=&quot;65&quot; step=&quot;2&quot; value=&quot;3&quot;&gt;&lt;output id=&quot;sm-mv&quot;&gt;3&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot;&gt;&lt;span&gt;added mode&lt;/span&gt;&lt;label style=&quot;flex:1;font-size:13px;&quot;&gt;&lt;input type=&quot;checkbox&quot; id=&quot;sm-alias&quot;&gt; add 0.3&amp;thinsp;sin(16&amp;pi;x) to the displacement&lt;/label&gt;&lt;output&gt;&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;readings changed by (max)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;sm-st&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;reconstruction error, relative RMS&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;sm-err&quot;&gt;62.1%&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Yellow bars mark the gaps between the reconstruction and the true curve. The red dots are the stored readings. When the added mode vanishes at every station, the readings do not change while the true error grows.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;sm-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.8, 1.8, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.8, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
  const gGap = L.el(&quot;g&quot;, {}, svg), gCur = L.el(&quot;g&quot;, {}, svg), gDot = L.el(&quot;g&quot;, {}, svg);
  const u0 = x =&gt; 0.8*Math.sin(Math.PI*x) + 0.4*Math.sin(2*Math.PI*x) + 0.2*Math.sin(3*Math.PI*x);
  const al = x =&gt; 0.3*Math.sin(16*Math.PI*x);
  let m = 3, add = false;
  function redraw(){
    const f = x =&gt; u0(x) + (add ? al(x) : 0);
    const xi = Array.from({length: m}, (_, i) =&gt; i / (m - 1));
    const yi = xi.map(f);
    const reb = x =&gt; {
      const k = Math.min(m - 2, Math.floor(x * (m - 1)));
      const t = x * (m - 1) - k;
      return yi[k] * (1 - t) + yi[k + 1] * t;
    };
    gGap.innerHTML = &quot;&quot;; gCur.innerHTML = &quot;&quot;; gDot.innerHTML = &quot;&quot;;
    for (let i = 0; i &lt;= 72; i++) {
      const x = i / 72;
      L.el(&quot;line&quot;, {x1: X(x), x2: X(x), y1: Y(f(x)), y2: Y(reb(x)),
        style: &quot;stroke: var(--yellow); stroke-width: 5; opacity: 0.30&quot;}, gGap);
    }
    L.curve(gCur, f, X, Y, {stroke: &quot;var(--ink)&quot;, width: 3, n: 801});
    L.curve(gCur, reb, X, Y, {stroke: &quot;var(--blue)&quot;, width: 2.5, n: 801});
    xi.forEach((x, i) =&gt; L.el(&quot;circle&quot;, {cx: X(x), cy: Y(yi[i]), r: 3.6,
      style: &quot;fill: var(--red); stroke: var(--paper); stroke-width: 1&quot;}, gDot));
    let change = 0;
    if (add) xi.forEach(x =&gt; { change = Math.max(change, Math.abs(al(x))); });
    let num = 0, den = 0;
    for (let i = 0; i &lt;= 800; i++) {
      const x = i / 800, d = reb(x) - f(x), v = f(x);
      num += d * d; den += v * v;
    }
    document.getElementById(&quot;sm-st&quot;).textContent = change.toFixed(3);
    document.getElementById(&quot;sm-err&quot;).textContent = (100 * Math.sqrt(num / den)).toFixed(1) + &quot;%&quot;;
  }
  document.getElementById(&quot;sm-m&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    m = parseInt(e.target.value);
    document.getElementById(&quot;sm-mv&quot;).textContent = m;
    redraw();
  });
  document.getElementById(&quot;sm-alias&quot;).addEventListener(&quot;change&quot;, e =&gt; {
    add = e.target.checked;
    redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:565px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Coefficients on three sine modes&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move the weights until the gray dashed sum lies on the fixed black displacement.&lt;/p&gt;
&lt;div class=&quot;plot-wrap&quot;&gt;
  &lt;svg id=&quot;hero-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;a&amp;#8321; &amp;nbsp;&amp;middot;&amp;nbsp; sin(&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;a1&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0.5&quot;&gt;&lt;output id=&quot;a1v&quot;&gt;0.50&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;a&amp;#8322; &amp;nbsp;&amp;middot;&amp;nbsp; sin(2&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;a2&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0&quot;&gt;&lt;output id=&quot;a2v&quot;&gt;0.00&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;a&amp;#8323; &amp;nbsp;&amp;middot;&amp;nbsp; sin(3&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;a3&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0&quot;&gt;&lt;output id=&quot;a3v&quot;&gt;0.00&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;btn-row&quot;&gt;&lt;button id=&quot;hero-solve&quot;&gt;Solve by projection&lt;/button&gt;&lt;button id=&quot;hero-reset&quot;&gt;Reset to (0.5, 0, 0)&lt;/button&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;weights (a&amp;#8321;, a&amp;#8322;, a&amp;#8323;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;coords&quot;&gt;(0.50, 0.00, 0.00)&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;L&amp;#178; distance to the displacement&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;dist&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;projection a&amp;#8342; = 2&amp;int;&amp;#8320;&amp;sup1; u(x) sin(k&amp;pi;x) dx&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;proj&quot;&gt;press Solve&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest gap, relative (sup)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;h-esup&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;root-mean-square gap, relative (L&amp;#178;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;h-el2&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;slope error, relative (H&amp;#185;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;h-eh1&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;svg id=&quot;hero-hist&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 170&quot;&gt;&lt;/svg&gt;
&lt;p class=&quot;lab-note&quot;&gt;The solid black curve is the displacement to reproduce, and it does not move. The gray dashed curve is the weighted sum of the three modes, drawn faintly in color. The distance reads zero at the weights (0.8, 0.4, 0.2). Solve computes each weight as the inner product of the displacement with its mode, divided by the mode&#x27;s squared norm 1/2, and moves the sliders there. The bottom plot traces the three relative errors, sup in red, L&amp;#178; in blue, and H&amp;#185; in orange, over the last two hundred slider moves.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;hero-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.8, 1.8, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.8, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
  const gT = L.el(&quot;g&quot;, {}, svg), gC = L.el(&quot;g&quot;, {}, svg), gS = L.el(&quot;g&quot;, {}, svg);
  const mode = k =&gt; x =&gt; Math.sin(k * Math.PI * x);
  const colors = [&quot;var(--blue)&quot;, &quot;var(--orange)&quot;, &quot;var(--green)&quot;];
  const t = [0.8, 0.4, 0.2];
  const a = [0.5, 0, 0];
  const dmode = k =&gt; x =&gt; k * Math.PI * Math.cos(k * Math.PI * x);
  const hs = document.getElementById(&quot;hero-hist&quot;);
  const Yh = L.scale(0, 1.2, 150, 12);
  L.axes(hs, L.scale(0, 1, 46, 706), Yh, {yMax: 1.2, ny: 2, xlabel: &quot;&quot;, ylabel: &quot;relative error&quot;});
  const gH = L.el(&quot;g&quot;, {}, hs);
  const hist = [];
  const nq = 1000;
  function norms(f, df){
    let sup = 0, l2 = 0, h1 = 0;
    for (let i = 0; i &lt;= nq; i++) {
      const x = i / nq, w = (i === 0 || i === nq) ? 0.5 : 1, e = f(x), de = df(x);
      sup = Math.max(sup, Math.abs(e)); l2 += w * e * e / nq; h1 += w * de * de / nq;
    }
    return [sup, Math.sqrt(l2), Math.sqrt(h1)];
  }
  const tu = x =&gt; t[0]*mode(1)(x) + t[1]*mode(2)(x) + t[2]*mode(3)(x);
  const tdu = x =&gt; t[0]*dmode(1)(x) + t[1]*dmode(2)(x) + t[2]*dmode(3)(x);
  const uN = norms(tu, tdu);
  L.curve(gT, x =&gt; t[0]*mode(1)(x) + t[1]*mode(2)(x) + t[2]*mode(3)(x), X, Y, {stroke: &quot;var(--ink)&quot;, width: 4});
  function redraw(){
    gC.innerHTML = &quot;&quot;; gS.innerHTML = &quot;&quot;;
    for (let k = 0; k &lt; 3; k++)
      L.curve(gC, x =&gt; a[k] * mode(k + 1)(x), X, Y, {stroke: colors[k], width: 1.5, dash: &quot;4 6&quot;, opacity: 0.35});
    L.curve(gS, x =&gt; a[0]*mode(1)(x) + a[1]*mode(2)(x) + a[2]*mode(3)(x), X, Y, {stroke: &quot;var(--muted)&quot;, width: 3, dash: &quot;9 7&quot;});
    L.el(&quot;circle&quot;, {cx: X(0), cy: Y(0), r: 4, style: &quot;fill: var(--ink)&quot;}, gS);
    L.el(&quot;circle&quot;, {cx: X(1), cy: Y(0), r: 4, style: &quot;fill: var(--ink)&quot;}, gS);
    document.getElementById(&quot;coords&quot;).textContent =
      &quot;(&quot; + L.fmt(a[0]) + &quot;, &quot; + L.fmt(a[1]) + &quot;, &quot; + L.fmt(a[2]) + &quot;)&quot;;
    // the modes are orthogonal with squared norm 1/2
    const d2 = 0.5 * ((a[0]-t[0])**2 + (a[1]-t[1])**2 + (a[2]-t[2])**2);
    document.getElementById(&quot;dist&quot;).textContent = Math.sqrt(d2).toFixed(3);
    const eN = norms(x =&gt; tu(x) - (a[0]*mode(1)(x) + a[1]*mode(2)(x) + a[2]*mode(3)(x)),
                     x =&gt; tdu(x) - (a[0]*dmode(1)(x) + a[1]*dmode(2)(x) + a[2]*dmode(3)(x)));
    const rel = eN.map((v, i) =&gt; v / uN[i]);
    document.getElementById(&quot;h-esup&quot;).textContent = (100 * rel[0]).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;h-el2&quot;).textContent = (100 * rel[1]).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;h-eh1&quot;).textContent = (100 * rel[2]).toFixed(1) + &quot;%&quot;;
    hist.push(rel); if (hist.length &gt; 200) hist.shift();
    gH.innerHTML = &quot;&quot;;
    const Xh = L.scale(0, Math.max(19, hist.length - 1), 46, 706);
    [&quot;var(--red)&quot;, &quot;var(--blue)&quot;, &quot;var(--orange)&quot;].forEach((c, j) =&gt; {
      const pts = hist.map((r, i) =&gt; Xh(i) + &quot;,&quot; + Yh(Math.min(r[j], 1.2))).join(&quot; &quot;);
      L.el(&quot;polyline&quot;, {points: pts, style: &quot;fill: none; stroke: &quot; + c + &quot;; stroke-width: 2&quot;}, gH);
    });
  }
  const ids = [&quot;a1&quot;, &quot;a2&quot;, &quot;a3&quot;];
  function setWeights(w){
    for (let k = 0; k &lt; 3; k++) {
      a[k] = w[k];
      document.getElementById(ids[k]).value = w[k];
      document.getElementById(ids[k] + &quot;v&quot;).textContent = L.fmt(w[k]);
    }
    redraw();
  }
  ids.forEach((id, k) =&gt; {
    document.getElementById(id).addEventListener(&quot;input&quot;, e =&gt; {
      a[k] = parseFloat(e.target.value);
      document.getElementById(id + &quot;v&quot;).textContent = L.fmt(a[k]);
      redraw();
    });
  });
  // each weight is 2 times the integral of u(x) sin(k pi x), by the trapezoid rule on 2000 intervals
  const target = x =&gt; t[0]*mode(1)(x) + t[1]*mode(2)(x) + t[2]*mode(3)(x);
  function project(k){
    const n = 2000; let sum = 0;
    for (let i = 0; i &lt;= n; i++) {
      const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1;
      sum += w * target(x) * mode(k)(x);
    }
    return 2 * sum / n;
  }
  document.getElementById(&quot;hero-solve&quot;).addEventListener(&quot;click&quot;, () =&gt; {
    const c = [project(1), project(2), project(3)];
    document.getElementById(&quot;proj&quot;).textContent =
      &quot;(&quot; + c.map(v =&gt; v.toFixed(3)).join(&quot;, &quot;) + &quot;)&quot;;
    setWeights(c.map(v =&gt; Math.round(v * 20) / 20));
  });
  document.getElementById(&quot;hero-reset&quot;).addEventListener(&quot;click&quot;, () =&gt; {
    document.getElementById(&quot;proj&quot;).textContent = &quot;press Solve&quot;;
    hist.length = 0;
    setWeights([0.5, 0, 0]);
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:900px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Error of the station guess in the sup, L&amp;#178;, and H&amp;#185; norms&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Change the station count and watch the three sizes of the same gap fall at different rates.&lt;/p&gt;
&lt;svg id=&quot;nm-e&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 150&quot;&gt;&lt;/svg&gt;
&lt;svg id=&quot;nm-e2&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 150&quot;&gt;&lt;/svg&gt;
&lt;svg id=&quot;nm-de&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 150&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;nm-m&quot; type=&quot;range&quot; min=&quot;3&quot; max=&quot;33&quot; step=&quot;2&quot; value=&quot;5&quot;&gt;&lt;output id=&quot;nm-mv&quot;&gt;5&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;sup norm, largest gap&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;nm-sup&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;L&amp;#178; norm, root of the area&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;nm-l2&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;H&amp;#185; seminorm, root-mean-square slope error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;nm-h1&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Top, the gap e = u &amp;minus; v between the displacement and the straight-segment guess, with the largest gap in red. Middle, the squared gap, whose area is the squared L&amp;#178; norm. Bottom, the slope error e&amp;prime;, which jumps at every station because the guess has a corner there. Each panel rescales to its own largest value as the station count changes, so read the sizes from the readouts. The percentages divide by the same norm of the displacement.&lt;/p&gt;
&lt;script&gt;
(function(){
  const X = L.scale(0, 1, 46, 706);
  const u = x =&gt; 0.8*Math.sin(Math.PI*x) + 0.4*Math.sin(2*Math.PI*x) + 0.2*Math.sin(3*Math.PI*x);
  const du = x =&gt; 0.8*Math.PI*Math.cos(Math.PI*x) + 0.8*Math.PI*Math.cos(2*Math.PI*x) + 0.6*Math.PI*Math.cos(3*Math.PI*x);
  const s1 = document.getElementById(&quot;nm-e&quot;), s2 = document.getElementById(&quot;nm-e2&quot;), s3 = document.getElementById(&quot;nm-de&quot;);
  let Y1, Y2, Y3, g1, g2, g3;
  const n = 2000;
  let uSup = 0, uL2 = 0, uH1 = 0;
  for (let i = 0; i &lt;= n; i++) {
    const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1;
    uSup = Math.max(uSup, Math.abs(u(x))); uL2 += w * u(x) ** 2 / n; uH1 += w * du(x) ** 2 / n;
  }
  uL2 = Math.sqrt(uL2); uH1 = Math.sqrt(uH1);
  let m = 5;
  function redraw(){
    const xi = Array.from({length: m}, (_, i) =&gt; i / (m - 1)), yi = xi.map(u), h = 1 / (m - 1);
    const seg = x =&gt; Math.min(m - 2, Math.floor(x / h));
    const v = x =&gt; { const k = seg(x), tt = x / h - k; return yi[k] * (1 - tt) + yi[k + 1] * tt; };
    const dv = x =&gt; { const k = seg(x); return (yi[k + 1] - yi[k]) / h; };
    const e = x =&gt; u(x) - v(x), de = x =&gt; du(x) - dv(x);
    let sup = 0, xs = 0, l2 = 0, h1 = 0, dmax = 0;
    for (let i = 0; i &lt;= n; i++) {
      const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1, ee = e(x);
      if (Math.abs(ee) &gt; sup) { sup = Math.abs(ee); xs = x; }
      l2 += w * ee * ee / n; h1 += w * de(x) ** 2 / n; dmax = Math.max(dmax, Math.abs(de(x)));
    }
    l2 = Math.sqrt(l2); h1 = Math.sqrt(h1);
    // each panel is rescaled to its current largest value, and its axis ticks show the size
    const r1 = 1.15 * sup, r2 = 1.15 * sup * sup, r3 = 1.15 * dmax;
    s1.innerHTML = &quot;&quot;; s2.innerHTML = &quot;&quot;; s3.innerHTML = &quot;&quot;;
    Y1 = L.scale(-r1, r1, 136, 12); Y2 = L.scale(0, r2, 136, 12); Y3 = L.scale(-r3, r3, 136, 12);
    L.axes(s1, X, Y1, {yMax: r1, ny: 2, xlabel: &quot;x&quot;, ylabel: &quot;gap e&quot;});
    L.axes(s2, X, Y2, {yMax: r2, ny: 2, xlabel: &quot;x&quot;, ylabel: &quot;e squared&quot;});
    L.axes(s3, X, Y3, {yMax: r3, ny: 2, xlabel: &quot;x&quot;, ylabel: &quot;slope error&quot;});
    g1 = L.el(&quot;g&quot;, {}, s1); g2 = L.el(&quot;g&quot;, {}, s2); g3 = L.el(&quot;g&quot;, {}, s3);
    for (let i = 0; i &lt;= 180; i++) {
      const x = i / 180;
      L.el(&quot;line&quot;, {x1: X(x), x2: X(x), y1: Y2(0), y2: Y2(e(x) ** 2), style: &quot;stroke: var(--yellow); stroke-width: 4; opacity: 0.45&quot;}, g2);
    }
    L.curve(g1, e, X, Y1, {stroke: &quot;var(--ink)&quot;, width: 2, n: 1201});
    L.el(&quot;circle&quot;, {cx: X(xs), cy: Y1(e(xs)), r: 4.5, style: &quot;fill: var(--red)&quot;}, g1);
    L.curve(g2, x =&gt; e(x) ** 2, X, Y2, {stroke: &quot;var(--ink)&quot;, width: 1.5, n: 1201});
    L.curve(g3, de, X, Y3, {stroke: &quot;var(--orange)&quot;, width: 2, n: 2401});
    document.getElementById(&quot;nm-sup&quot;).textContent = sup.toFixed(3) + &quot;, or &quot; + (100 * sup / uSup).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;nm-l2&quot;).textContent = l2.toFixed(3) + &quot;, or &quot; + (100 * l2 / uL2).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;nm-h1&quot;).textContent = h1.toFixed(2) + &quot;, or &quot; + (100 * h1 / uH1).toFixed(0) + &quot;%&quot;;
  }
  document.getElementById(&quot;nm-m&quot;).addEventListener(&quot;input&quot;, ev =&gt; {
    m = parseInt(ev.target.value); document.getElementById(&quot;nm-mv&quot;).textContent = m; redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:700px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

A spike of height one on a base of width $0.04$ has sup norm one, $L^2$ norm $0.115$, and elastic energy $50$, and quartering the base leaves the first, halves the second, and quadruples the third, so the three can disagree without bound.

Now go back to the corner.
In the lab below the point-load displacement is the solid black curve, and three weighted sines make the gray dashed one.
The sum closest in $L^2$ has weights $c_k = 2\sin(k\pi/2)/(k\pi)^2$, that is $(0.2026, 0, -0.0225)$, and it is also the closest in $H^1$, because the sines are orthogonal in both inner products.
It misses by $9.9$ percent of the peak in the largest gap, $4.8$ percent in the root-mean-square gap, and $31.5$ percent in the slopes.
The sum closest in the sup norm has different weights, $(0.2045, 0, -0.0318)$, and it trades the other way, $5.5$ percent in the largest gap against $6.7$ in the root-mean-square gap and $33.9$ in the slopes.
Each sum is closer in the norm it minimizes, and no sum of three sines reaches the corner itself.

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Three sines against a corner, measured in three norms&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move the weights, then press each button and compare the three error readouts.&lt;/p&gt;
&lt;svg id=&quot;cn-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 250&quot;&gt;&lt;/svg&gt;
&lt;svg id=&quot;cn-err&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 150&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;a&amp;#8321; &amp;nbsp;&amp;middot;&amp;nbsp; sin(&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;cn-a1&quot; type=&quot;range&quot; min=&quot;0&quot; max=&quot;0.3&quot; step=&quot;0.0005&quot; value=&quot;0.25&quot;&gt;&lt;output id=&quot;cn-a1v&quot;&gt;0.2500&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;a&amp;#8322; &amp;nbsp;&amp;middot;&amp;nbsp; sin(2&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;cn-a2&quot; type=&quot;range&quot; min=&quot;-0.1&quot; max=&quot;0.1&quot; step=&quot;0.0005&quot; value=&quot;0&quot;&gt;&lt;output id=&quot;cn-a2v&quot;&gt;0.0000&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;a&amp;#8323; &amp;nbsp;&amp;middot;&amp;nbsp; sin(3&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;cn-a3&quot; type=&quot;range&quot; min=&quot;-0.1&quot; max=&quot;0.1&quot; step=&quot;0.0005&quot; value=&quot;0&quot;&gt;&lt;output id=&quot;cn-a3v&quot;&gt;0.0000&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;btn-row&quot;&gt;&lt;button id=&quot;cn-l2&quot;&gt;Closest in L&amp;#178; and H&amp;#185;&lt;/button&gt;&lt;button id=&quot;cn-sup&quot;&gt;Closest in the sup norm&lt;/button&gt;&lt;button id=&quot;cn-reset&quot;&gt;Reset&lt;/button&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest gap, relative (sup)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;cn-esup&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;root-mean-square gap, relative (L&amp;#178;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;cn-el2&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;slope error, relative (H&amp;#185;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;cn-eh1&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Top, the point-load displacement (solid black, fixed) and the sum of three weighted sines (gray dashed). Bottom, the gap u &amp;minus; v, with the largest gap marked in red. The L&amp;#178;-closest sum is also the H&amp;#185;-closest, because the sines are orthogonal in both inner products. The sup-closest weights were found by minimizing the largest gap numerically.&lt;/p&gt;
&lt;script&gt;
(function(){
  const X = L.scale(0, 1, 46, 706);
  const svg = document.getElementById(&quot;cn-plot&quot;), Y = L.scale(-0.03, 0.3, 236, 14);
  L.axes(svg, X, Y, {yMax: 0.3, ny: 3, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
  const sve = document.getElementById(&quot;cn-err&quot;), Ye = L.scale(-0.06, 0.06, 140, 10);
  L.axes(sve, X, Ye, {yMax: 0.06, ny: 2, xlabel: &quot;x&quot;, ylabel: &quot;u - v&quot;});
  const gT = L.el(&quot;g&quot;, {}, svg), gS = L.el(&quot;g&quot;, {}, svg), gE = L.el(&quot;g&quot;, {}, sve);
  const u = x =&gt; 0.5 * Math.min(x, 1 - x), du = x =&gt; (x &lt; 0.5 ? 0.5 : -0.5);
  const md = k =&gt; x =&gt; Math.sin(k * Math.PI * x), dmd = k =&gt; x =&gt; k * Math.PI * Math.cos(k * Math.PI * x);
  const a = [0.25, 0, 0], ids = [&quot;cn-a1&quot;, &quot;cn-a2&quot;, &quot;cn-a3&quot;];
  const v = x =&gt; a[0]*md(1)(x) + a[1]*md(2)(x) + a[2]*md(3)(x);
  const dv = x =&gt; a[0]*dmd(1)(x) + a[1]*dmd(2)(x) + a[2]*dmd(3)(x);
  L.curve(gT, u, X, Y, {stroke: &quot;var(--ink)&quot;, width: 4, n: 801});
  const n = 2000, uSup = 0.25, uL2 = Math.sqrt(1 / 48), uH1 = 0.5;
  function redraw(){
    gS.innerHTML = &quot;&quot;; gE.innerHTML = &quot;&quot;;
    L.curve(gS, v, X, Y, {stroke: &quot;var(--muted)&quot;, width: 3, dash: &quot;9 7&quot;, n: 801});
    L.curve(gE, x =&gt; u(x) - v(x), X, Ye, {stroke: &quot;var(--ink)&quot;, width: 2, n: 801});
    let sup = 0, xs = 0, l2 = 0, h1 = 0;
    for (let i = 0; i &lt;= n; i++) {
      const x = i / n, e = u(x) - v(x), de = du(x) - dv(x), w = (i === 0 || i === n) ? 0.5 : 1;
      if (Math.abs(e) &gt; sup) { sup = Math.abs(e); xs = x; }
      l2 += w * e * e / n; h1 += w * de * de / n;
    }
    L.el(&quot;circle&quot;, {cx: X(xs), cy: Ye(u(xs) - v(xs)), r: 4.5, style: &quot;fill: var(--red)&quot;}, gE);
    document.getElementById(&quot;cn-esup&quot;).textContent = (100 * sup / uSup).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;cn-el2&quot;).textContent = (100 * Math.sqrt(l2) / uL2).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;cn-eh1&quot;).textContent = (100 * Math.sqrt(h1) / uH1).toFixed(1) + &quot;%&quot;;
  }
  function setWeights(w){
    for (let k = 0; k &lt; 3; k++) {
      a[k] = w[k];
      document.getElementById(ids[k]).value = w[k];
      document.getElementById(ids[k] + &quot;v&quot;).textContent = w[k].toFixed(4);
    }
    redraw();
  }
  ids.forEach((id, k) =&gt; document.getElementById(id).addEventListener(&quot;input&quot;, e =&gt; {
    a[k] = parseFloat(e.target.value);
    document.getElementById(id + &quot;v&quot;).textContent = a[k].toFixed(4);
    redraw();
  }));
  document.getElementById(&quot;cn-l2&quot;).addEventListener(&quot;click&quot;, () =&gt;
    setWeights([2 / Math.PI ** 2, 0, -2 / (9 * Math.PI ** 2)]));
  document.getElementById(&quot;cn-sup&quot;).addEventListener(&quot;click&quot;, () =&gt; setWeights([0.2045, 0, -0.0318]));
  document.getElementById(&quot;cn-reset&quot;).addEventListener(&quot;click&quot;, () =&gt; setWeights([0.25, 0, 0]));
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:700px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

Name $L^2$ and ask which sum of three sines is closest to the parabola $x(1-x)$, the shape of the string under a uniform load.
In ordinary geometry a perpendicular dropped from the point onto the plane finds the closest point, and a perpendicular needs a dot product.
For functions the dot product is the integral of the product, $\langle f, g\rangle = \int_0^1 f g\,dx$, and the sine modes are orthogonal in it.
Slide one coefficient and the squared error is a bowl whose bottom sits where the error is orthogonal to the mode, at $c_1 = 2\langle u, \sin(\pi x)\rangle = 8/\pi^3 = 0.258$, one division per coefficient and no search.
The closest sum misses the parabola by $0.87$ percent.
Push $c_1$ twenty percent higher and the eye cannot tell the new curve from the old, while its error norm is $23$ times larger.
The first lab below slides the coefficient.
The second lab adds modes to three targets and shows how fast the coefficients fall, one power of $k$ for each derivative the target keeps continuous, so a smooth target needs few modes and a step's coefficients fall like $1/k$.

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Minimizing the squared error over one coefficient&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Slide the coefficient. The squared error is a bowl, and the projection formula finds its bottom without searching.&lt;/p&gt;
&lt;div style=&quot;display:flex; gap:10px;&quot;&gt;
  &lt;div style=&quot;flex:1&quot;&gt;&lt;svg id=&quot;pj-f&quot; class=&quot;plot&quot; viewBox=&quot;0 0 355 250&quot;&gt;&lt;/svg&gt;&lt;/div&gt;
  &lt;div style=&quot;flex:1&quot;&gt;&lt;svg id=&quot;pj-e&quot; class=&quot;plot&quot; viewBox=&quot;0 0 355 250&quot;&gt;&lt;/svg&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;coefficient c&amp;#8321;&lt;/span&gt;&lt;input id=&quot;pj-c&quot; type=&quot;range&quot; min=&quot;0.15&quot; max=&quot;0.37&quot; step=&quot;0.002&quot; value=&quot;0.31&quot;&gt;&lt;output id=&quot;pj-cv&quot;&gt;0.310&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;relative L&amp;#178; error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;pj-err&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;best value 8/&amp;pi;&amp;#179;&lt;/span&gt;&lt;span class=&quot;num&quot;&gt;0.258&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Left, the parabola (dark) and the blend (blue). Right, the squared error against c&amp;#8321; with the current position as a dot. The minimum is the perpendicular drop.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svgF = document.getElementById(&quot;pj-f&quot;), svgE = document.getElementById(&quot;pj-e&quot;);
  const XF = L.scale(0, 1, 40, 345), YF = L.scale(-0.05, 0.32, 226, 14);
  L.axes(svgF, XF, YF, {yMax: 0.32, xlabel: &quot;x&quot;, ylabel: &quot;u&quot;});
  const C1MIN = 0.15, C1MAX = 0.37;
  const XE = L.scale(C1MIN, C1MAX, 40, 345);
  const c3 = 8 / (27 * Math.PI ** 3);
  const parab = x =&gt; x * (1 - x);
  function err2(c1){
    let s = 0;
    for (let i = 0; i &lt; 800; i++) {
      const x = (i + 0.5) / 800;
      const d = parab(x) - c1 * Math.sin(Math.PI * x) - c3 * Math.sin(3 * Math.PI * x);
      s += d * d / 800;
    }
    return s;
  }
  const E2MAX = Math.max(err2(C1MIN), err2(C1MAX)) * 1.05;
  const YE = L.scale(0, E2MAX, 226, 14);
  const gAx = L.el(&quot;g&quot;, {}, svgE);
  L.el(&quot;line&quot;, {x1: 40, y1: YE(0), x2: 345, y2: YE(0), class: &quot;axis-line&quot;}, gAx);
  L.el(&quot;line&quot;, {x1: 40, y1: YE(0), x2: 40, y2: 14, class: &quot;axis-line&quot;}, gAx);
  const le = L.el(&quot;text&quot;, {x: 320, y: YE(0) - 6, class: &quot;axis-label&quot;, &quot;text-anchor&quot;: &quot;end&quot;}, gAx);
  le.textContent = &quot;c1&quot;;
  let d = &quot;&quot;;
  for (let i = 0; i &lt;= 120; i++) {
    const c = C1MIN + (C1MAX - C1MIN) * i / 120;
    d += (i ? &quot; L&quot; : &quot;M&quot;) + XE(c).toFixed(2) + &quot; &quot; + YE(err2(c)).toFixed(2);
  }
  L.el(&quot;path&quot;, {d: d, fill: &quot;none&quot;, style: &quot;stroke: var(--ink); stroke-width: 2&quot;}, svgE);
  const gF = L.el(&quot;g&quot;, {}, svgF), gDot = L.el(&quot;g&quot;, {}, svgE);
  const uNorm2 = err2(0) ? null : null;
  let relDen = 0;
  for (let i = 0; i &lt; 800; i++) { const x = (i + 0.5) / 800; relDen += parab(x) ** 2 / 800; }
  let c1 = 0.31;
  function redraw(){
    gF.innerHTML = &quot;&quot;; gDot.innerHTML = &quot;&quot;;
    L.curve(gF, parab, XF, YF, {stroke: &quot;var(--ink)&quot;, width: 3, n: 401});
    L.curve(gF, x =&gt; c1 * Math.sin(Math.PI * x) + c3 * Math.sin(3 * Math.PI * x),
            XF, YF, {stroke: &quot;var(--blue)&quot;, width: 2.5, n: 401});
    const e2 = err2(c1);
    L.el(&quot;circle&quot;, {cx: XE(c1), cy: YE(e2), r: 5, style: &quot;fill: var(--blue)&quot;}, gDot);
    document.getElementById(&quot;pj-err&quot;).textContent =
      (100 * Math.sqrt(e2 / relDen)).toFixed(1) + &quot;%&quot;;
  }
  document.getElementById(&quot;pj-c&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    c1 = parseFloat(e.target.value);
    document.getElementById(&quot;pj-cv&quot;).textContent = c1.toFixed(3);
    redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:545px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Decay of the coefficients on sine modes&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Pick a target and add modes. The bars are the coefficients, and the error readout measures what the dropped modes held.&lt;/p&gt;
&lt;div class=&quot;btn-row&quot; role=&quot;group&quot;&gt;
  &lt;button id=&quot;bt-parab&quot; class=&quot;selected&quot;&gt;displacement x(1&amp;minus;x)&lt;/button&gt;
  &lt;button id=&quot;bt-bump&quot;&gt;bump&lt;/button&gt;
  &lt;button id=&quot;bt-step&quot;&gt;step&lt;/button&gt;
&lt;/div&gt;
&lt;svg id=&quot;bs-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 280&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;modes kept p&lt;/span&gt;&lt;input id=&quot;bs-p&quot; type=&quot;range&quot; min=&quot;1&quot; max=&quot;16&quot; step=&quot;1&quot; value=&quot;3&quot;&gt;&lt;output id=&quot;bs-pv&quot;&gt;3&lt;/output&gt;&lt;/div&gt;
&lt;div id=&quot;bs-bars&quot; style=&quot;display:flex; gap:4px; align-items:flex-end; height:56px; margin:6px 0;&quot;&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;relative L&amp;#178; error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bs-err&quot;&gt;0.9%&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The bars are the coefficients c&amp;#8321;, &amp;hellip;, c&amp;#8346;, blue positive and orange negative. The coordinate list of a smooth target decays fast; the step&#x27;s does not.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;bs-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.3, 1.3, 266, 14);
  L.axes(svg, X, Y, {yMax: 1.3, xlabel: &quot;x&quot;});
  const gC = L.el(&quot;g&quot;, {}, svg);
  const targets = {
    parab: x =&gt; 4 * x * (1 - x),
    bump: x =&gt; 1.15 * Math.exp(-90 * (x - 0.38) ** 2) - 0.45 * Math.exp(-45 * (x - 0.76) ** 2),
    step: x =&gt; x &lt; 0.48 ? -0.65 : 0.65,
  };
  let kind = &quot;parab&quot;, p = 3;
  function coeffs(f, P){
    const c = [];
    for (let k = 1; k &lt;= P; k++) {
      let s = 0;
      for (let i = 0; i &lt; 1200; i++) {
        const x = (i + 0.5) / 1200;
        s += f(x) * Math.sin(k * Math.PI * x) / 1200;
      }
      c.push(2 * s);
    }
    return c;
  }
  function redraw(){
    const f = targets[kind];
    const c = coeffs(f, p);
    const v = x =&gt; c.reduce((s, ck, i) =&gt; s + ck * Math.sin((i + 1) * Math.PI * x), 0);
    gC.innerHTML = &quot;&quot;;
    L.curve(gC, f, X, Y, {stroke: &quot;var(--ink)&quot;, width: 2.5, dash: &quot;8 7&quot;, n: 1201});
    L.curve(gC, v, X, Y, {stroke: &quot;var(--blue)&quot;, width: 2.5, n: 801});
    const bars = document.getElementById(&quot;bs-bars&quot;);
    bars.innerHTML = &quot;&quot;;
    for (let i = 0; i &lt; Math.min(p, 16); i++) {
      const d = document.createElement(&quot;div&quot;);
      const h = Math.min(52, Math.abs(c[i]) * 48 + 2);
      d.style.cssText = &quot;width:22px;height:&quot; + h + &quot;px;border-radius:3px 3px 0 0;background:&quot;
        + (c[i] &gt;= 0 ? &quot;var(--blue)&quot; : &quot;var(--orange)&quot;);
      d.title = &quot;c&quot; + (i + 1) + &quot; = &quot; + c[i].toFixed(3);
      bars.appendChild(d);
    }
    let num = 0, den = 0;
    for (let i = 0; i &lt; 1200; i++) {
      const x = (i + 0.5) / 1200, d = f(x) - v(x);
      num += d * d; den += f(x) * f(x);
    }
    document.getElementById(&quot;bs-err&quot;).textContent = (100 * Math.sqrt(num / den)).toFixed(1) + &quot;%&quot;;
  }
  for (const id of [&quot;parab&quot;, &quot;bump&quot;, &quot;step&quot;]) {
    document.getElementById(&quot;bt-&quot; + id).addEventListener(&quot;click&quot;, () =&gt; {
      kind = id;
      for (const j of [&quot;parab&quot;, &quot;bump&quot;, &quot;step&quot;])
        document.getElementById(&quot;bt-&quot; + j).classList.toggle(&quot;selected&quot;, j === id);
      redraw();
    });
  }
  document.getElementById(&quot;bs-p&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    p = parseInt(e.target.value);
    document.getElementById(&quot;bs-pv&quot;).textContent = p;
    redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:600px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Bernstein polynomials for the string displacement&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Raise the number of coins, then move the probe and watch the weights crowd around it.&lt;/p&gt;
&lt;svg id=&quot;bb-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 270&quot;&gt;&lt;/svg&gt;
&lt;svg id=&quot;bb-w&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 130&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;coins n&lt;/span&gt;&lt;input id=&quot;bb-n&quot; type=&quot;range&quot; min=&quot;0&quot; max=&quot;8&quot; step=&quot;1&quot; value=&quot;3&quot;&gt;&lt;output id=&quot;bb-nv&quot;&gt;16&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--red)&quot;&gt;&lt;span&gt;probe x&lt;/span&gt;&lt;input id=&quot;bb-x&quot; type=&quot;range&quot; min=&quot;0.02&quot; max=&quot;0.98&quot; step=&quot;0.01&quot; value=&quot;0.25&quot;&gt;&lt;output id=&quot;bb-xv&quot;&gt;0.25&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;u(x), the displacement at the probe&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bb-f&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;B&amp;#8345;f(x) = &amp;Sigma; f(k/n) P(k heads)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bb-b&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest gap anywhere&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bb-max&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;3.18 / n, large-n prediction of the largest gap&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bb-pred&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Top, the string displacement (dashed), Bernstein&#x27;s polynomial B&amp;#8345;f (blue), the readings f(k/n) (dots, shown up to n = 64), and the weighted basis polynomials f(k/n) B&amp;#8342;&amp;#8345;(x) that add up to B&amp;#8345;f (gray dashed, every one up to n = 32 and an evenly spaced selection above). Bottom, the probability of k heads in n coins that land heads with probability x, drawn at k/n. B&amp;#8345;f(x) is the average of the readings with these weights, and the weights crowd around the probe as n grows.&lt;/p&gt;
&lt;script&gt;
(function(){
  const X = L.scale(0, 1, 46, 706);
  const svg = document.getElementById(&quot;bb-plot&quot;), Y = L.scale(-0.3, 1.4, 256, 14);
  L.axes(svg, X, Y, {yMax: 1.4, ny: 3, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
  const sw = document.getElementById(&quot;bb-w&quot;);
  const gC = L.el(&quot;g&quot;, {}, svg), gD = L.el(&quot;g&quot;, {}, svg), gW = L.el(&quot;g&quot;, {}, sw);
  const f = x =&gt; 0.8 * Math.sin(Math.PI * x) + 0.4 * Math.sin(2 * Math.PI * x) + 0.2 * Math.sin(3 * Math.PI * x);
  const ns = [2, 4, 8, 16, 32, 64, 128, 256, 512];
  let n = 16, x0 = 0.25;
  function logC(n){
    const out = [0];
    for (let k = 1; k &lt;= n; k++) out.push(out[k-1] + Math.log(n - k + 1) - Math.log(k));
    return out;
  }
  function redraw(){
    const lc = logC(n);
    const w = (k, x) =&gt; {
      if (x &lt;= 0) return k === 0 ? 1 : 0;
      if (x &gt;= 1) return k === n ? 1 : 0;
      return Math.exp(lc[k] + k * Math.log(x) + (n - k) * Math.log(1 - x));
    };
    const B = x =&gt; { let s = 0; for (let k = 0; k &lt;= n; k++) s += f(k / n) * w(k, x); return s; };
    gC.innerHTML = &quot;&quot;; gD.innerHTML = &quot;&quot;; gW.innerHTML = &quot;&quot;;
    // the weighted basis polynomials f(k/n) B_{k,n}(x) whose sum is B_n f, thinned to at most 33 curves
    const step = n &gt; 32 ? Math.ceil(n / 32) : 1;
    for (let k = 0; k &lt;= n; k += step)
      L.curve(gC, x =&gt; f(k / n) * w(k, x), X, Y, {stroke: &quot;var(--muted)&quot;, width: 1.6, dash: &quot;5 4&quot;, opacity: 0.9, n: 301});
    L.curve(gC, f, X, Y, {stroke: &quot;var(--ink)&quot;, width: 2.5, dash: &quot;7 6&quot;, n: 501});
    L.curve(gC, B, X, Y, {stroke: &quot;var(--blue)&quot;, width: 3, n: 501});
    if (n &lt;= 64) for (let k = 0; k &lt;= n; k++)
      L.el(&quot;circle&quot;, {cx: X(k / n), cy: Y(f(k / n)), r: 2.6, style: &quot;fill: var(--muted)&quot;}, gD);
    L.el(&quot;line&quot;, {x1: X(x0), x2: X(x0), y1: Y(-0.3), y2: Y(1.4), style: &quot;stroke: var(--red); stroke-width: 1.2; stroke-dasharray: 4 4&quot;}, gD);
    L.el(&quot;circle&quot;, {cx: X(x0), cy: Y(B(x0)), r: 5, style: &quot;fill: var(--red)&quot;}, gD);
    let wmax = 0; for (let k = 0; k &lt;= n; k++) wmax = Math.max(wmax, w(k, x0));
    const Yw = L.scale(0, 1.1 * wmax, 120, 10);
    sw.innerHTML = &quot;&quot;; L.axes(sw, X, Yw, {yMax: 1.1 * wmax, ny: 1, xlabel: &quot;k / n&quot;, ylabel: &quot;P(k heads)&quot;});
    const gw = L.el(&quot;g&quot;, {}, sw);
    const bw = Math.max(1.5, Math.min(14, 560 / (n + 1)));
    for (let k = 0; k &lt;= n; k++) {
      const p = w(k, x0);
      L.el(&quot;rect&quot;, {x: X(k / n) - bw / 2, y: Yw(p), width: bw, height: Yw(0) - Yw(p), style: &quot;fill: var(--blue); opacity: 0.7&quot;}, gw);
    }
    L.el(&quot;line&quot;, {x1: X(x0), x2: X(x0), y1: Yw(0), y2: Yw(1.1 * wmax), style: &quot;stroke: var(--red); stroke-width: 1.2; stroke-dasharray: 4 4&quot;}, gw);
    let worst = 0;
    for (let i = 0; i &lt;= 400; i++) { const x = i / 400; worst = Math.max(worst, Math.abs(B(x) - f(x))); }
    document.getElementById(&quot;bb-f&quot;).textContent = f(x0).toFixed(3);
    document.getElementById(&quot;bb-b&quot;).textContent = B(x0).toFixed(3);
    document.getElementById(&quot;bb-max&quot;).textContent = worst.toFixed(3);
    document.getElementById(&quot;bb-pred&quot;).textContent = (3.18 / n).toFixed(3);
  }
  document.getElementById(&quot;bb-n&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    n = ns[parseInt(e.target.value)]; document.getElementById(&quot;bb-nv&quot;).textContent = n; redraw();
  });
  document.getElementById(&quot;bb-x&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    x0 = parseFloat(e.target.value); document.getElementById(&quot;bb-xv&quot;).textContent = x0.toFixed(2); redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:780px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

Now the corner function $|x - \tfrac12|$.
With two coins the three weights are three hills, one at each wall and one at mid-span, and for the corner function $|x - \tfrac12|$ their sum reads $\tfrac14$ at mid-span where the function is $0$, because every neighbor of the corner sits higher than the corner and any average overshoots there.
As $n$ grows the fraction of heads concentrates near $x$, the hills narrow like $1/\sqrt{n}$, and so does the gap.
At $n = 8$ the gap at the corner is $0.137$ against a prediction of $0.4/\sqrt{n} = 0.141$, and at $n = 32$ it is $0.070$ against $0.071$.
The corner has no second derivative, so Voronovskaya's formula does not apply, and the gap falls like $1/\sqrt{n}$, slower than the bump's $1/n$.
Raise the degree below and watch the hills narrow while the gap at the corner follows the prediction.

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Bernstein polynomials for a corner&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Raise the degree. The hills narrow, the sum closes in on the corner, and the gap at the corner follows 0.4 over the square root of n.&lt;/p&gt;
&lt;svg id=&quot;bn-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;degree n&lt;/span&gt;&lt;input id=&quot;bn-n&quot; type=&quot;range&quot; min=&quot;2&quot; max=&quot;128&quot; step=&quot;2&quot; value=&quot;8&quot;&gt;&lt;output id=&quot;bn-nv&quot;&gt;8&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;gap at the corner&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bn-corner&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;0.4 / &amp;radic;n&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bn-pred&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest gap anywhere&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;bn-max&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;Gray curves are the n + 1 hills, each scaled by the reading f(k/n) it weights. Their sum (blue) is Bernstein&#x27;s polynomial for the corner function (dashed). The red dot marks the corner, where the gap is largest.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;bn-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.1, 0.6, 286, 14);
  L.axes(svg, X, Y, {yMax: 0.6, ny: 3, xlabel: &quot;x&quot;, ylabel: &quot;f(x)&quot;});
  const gB = L.el(&quot;g&quot;, {}, svg), gC = L.el(&quot;g&quot;, {}, svg), gD = L.el(&quot;g&quot;, {}, svg);
  const f = x =&gt; Math.abs(x - 0.5);
  let n = 8;
  function logC(n){
    const out = [0];
    for (let k = 1; k &lt;= n; k++) out.push(out[k-1] + Math.log(n - k + 1) - Math.log(k));
    return out;
  }
  function redraw(){
    const lc = logC(n);
    const w = (k, x) =&gt; {
      if (x &lt;= 0) return k === 0 ? 1 : 0;
      if (x &gt;= 1) return k === n ? 1 : 0;
      return Math.exp(lc[k] + k * Math.log(x) + (n - k) * Math.log(1 - x));
    };
    const B = x =&gt; { let s = 0; for (let k = 0; k &lt;= n; k++) s += f(k / n) * w(k, x); return s; };
    gB.innerHTML = &quot;&quot;; gC.innerHTML = &quot;&quot;; gD.innerHTML = &quot;&quot;;
    const step = n &gt; 32 ? Math.ceil(n / 32) : 1;
    for (let k = 0; k &lt;= n; k += step)
      L.curve(gB, x =&gt; f(k / n) * w(k, x), X, Y, {stroke: &quot;var(--muted)&quot;, width: 1, opacity: 0.45, n: 241});
    L.curve(gC, f, X, Y, {stroke: &quot;var(--ink)&quot;, width: 2.5, dash: &quot;7 6&quot;, n: 401});
    L.curve(gC, B, X, Y, {stroke: &quot;var(--blue)&quot;, width: 3, n: 401});
    let worst = 0;
    for (let i = 0; i &lt;= 400; i++) { const x = i / 400; worst = Math.max(worst, Math.abs(B(x) - f(x))); }
    const corner = B(0.5);
    L.el(&quot;circle&quot;, {cx: X(0.5), cy: Y(corner), r: 4.5, style: &quot;fill: var(--red); stroke: var(--paper); stroke-width: 1&quot;}, gD);
    document.getElementById(&quot;bn-corner&quot;).textContent = corner.toFixed(3);
    document.getElementById(&quot;bn-pred&quot;).textContent = (0.4 / Math.sqrt(n)).toFixed(3);
    document.getElementById(&quot;bn-max&quot;).textContent = worst.toFixed(3);
  }
  document.getElementById(&quot;bn-n&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    n = parseInt(e.target.value);
    document.getElementById(&quot;bn-nv&quot;).textContent = n;
    redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:590px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Hat functions as a basis&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Pick a target and change the station count. The readings are the weights of the hats.&lt;/p&gt;
&lt;svg id=&quot;hb-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;btn-row&quot;&gt;
  &lt;button id=&quot;hb-string&quot; class=&quot;selected&quot;&gt;string displacement&lt;/button&gt;
  &lt;button id=&quot;hb-point&quot;&gt;point load&lt;/button&gt;
  &lt;button id=&quot;hb-bump&quot;&gt;bump&lt;/button&gt;
  &lt;button id=&quot;hb-pulse&quot;&gt;square pulse&lt;/button&gt;
&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;hb-m&quot; type=&quot;range&quot; min=&quot;3&quot; max=&quot;65&quot; step=&quot;2&quot; value=&quot;5&quot;&gt;&lt;output id=&quot;hb-mv&quot;&gt;5&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;coefficients, the readings&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;hb-n&quot;&gt;5&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest gap, relative&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;hb-sup&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;root-mean-square gap, relative&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;hb-l2&quot;&gt;0&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The target (solid black), one hat per station weighted by the reading there (gray dashed), and their sum (blue). Every hat equals one at its own station and zero at the others, so the sum passes through every reading and is straight between stations.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;hb-plot&quot;);
  const X = L.scale(0, 1, 46, 706);
  let Y, gA;
  const targets = {
    string: {f: x =&gt; 0.8*Math.sin(Math.PI*x) + 0.4*Math.sin(2*Math.PI*x) + 0.2*Math.sin(3*Math.PI*x), lo: -0.3, hi: 1.3},
    point:  {f: x =&gt; 0.5 * Math.min(x, 1 - x), lo: -0.03, hi: 0.3},
    bump:   {f: x =&gt; 1.15*Math.exp(-90*(x-0.38)**2) - 0.45*Math.exp(-45*(x-0.76)**2), lo: -0.6, hi: 1.3},
    pulse:  {f: x =&gt; (x &gt;= 0.3 &amp;&amp; x &lt;= 0.7) ? 1 : 0, lo: -0.15, hi: 1.25},
  };
  let kind = &quot;string&quot;, m = 5;
  function redraw(){
    const T = targets[kind], f = T.f;
    svg.innerHTML = &quot;&quot;;
    Y = L.scale(T.lo, T.hi, 286, 14);
    L.axes(svg, X, Y, {yMax: T.hi, ny: 3, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
    gA = L.el(&quot;g&quot;, {}, svg);
    const h = 1 / (m - 1), xi = Array.from({length: m}, (_, i) =&gt; i * h), yi = xi.map(f);
    const hat = i =&gt; x =&gt; Math.max(0, 1 - Math.abs(x - xi[i]) / h);
    const v = x =&gt; { const k = Math.min(m - 2, Math.floor(x / h)), t = x / h - k; return yi[k] * (1 - t) + yi[k + 1] * t; };
    for (let i = 0; i &lt; m; i++) if (yi[i] !== 0)
      L.curve(gA, x =&gt; yi[i] * hat(i)(x), X, Y, {stroke: &quot;var(--muted)&quot;, width: 1.4, dash: &quot;5 4&quot;, opacity: 0.85, n: 801});
    L.curve(gA, f, X, Y, {stroke: &quot;var(--ink)&quot;, width: 3, n: 1601});
    L.curve(gA, v, X, Y, {stroke: &quot;var(--blue)&quot;, width: 2.5, n: 1601});
    xi.forEach((x, i) =&gt; L.el(&quot;circle&quot;, {cx: X(x), cy: Y(yi[i]), r: 3.2, style: &quot;fill: var(--red)&quot;}, gA));
    const n = 4000; let sup = 0, fs = 0, num = 0, den = 0;
    for (let i = 0; i &lt;= n; i++) {
      const x = i / n, w = (i === 0 || i === n) ? 0.5 : 1, e = f(x) - v(x);
      sup = Math.max(sup, Math.abs(e)); fs = Math.max(fs, Math.abs(f(x))); num += w * e * e; den += w * f(x) * f(x);
    }
    document.getElementById(&quot;hb-n&quot;).textContent = m;
    document.getElementById(&quot;hb-sup&quot;).textContent = (100 * sup / fs).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;hb-l2&quot;).textContent = (100 * Math.sqrt(num / den)).toFixed(1) + &quot;%&quot;;
  }
  for (const k of Object.keys(targets)) document.getElementById(&quot;hb-&quot; + k).addEventListener(&quot;click&quot;, () =&gt; {
    kind = k;
    for (const j of Object.keys(targets)) document.getElementById(&quot;hb-&quot; + j).className = (j === k) ? &quot;selected&quot; : &quot;&quot;;
    redraw();
  });
  document.getElementById(&quot;hb-m&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    m = parseInt(e.target.value); document.getElementById(&quot;hb-mv&quot;).textContent = m; redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:640px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Hat nodes on a moving front&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move the front. The stations stay where we put them, and the four nodes follow the edges.&lt;/p&gt;
&lt;svg id=&quot;fr-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--ink)&quot;&gt;&lt;span&gt;shift of the front c&lt;/span&gt;&lt;input id=&quot;fr-c&quot; type=&quot;range&quot; min=&quot;0&quot; max=&quot;0.45&quot; step=&quot;0.01&quot; value=&quot;0&quot;&gt;&lt;output id=&quot;fr-cv&quot;&gt;0.00&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;fr-m&quot; type=&quot;range&quot; min=&quot;8&quot; max=&quot;128&quot; step=&quot;8&quot; value=&quot;32&quot;&gt;&lt;output id=&quot;fr-mv&quot;&gt;32&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;distance d from each node to its edge&lt;/span&gt;&lt;input id=&quot;fr-d&quot; type=&quot;range&quot; min=&quot;0.005&quot; max=&quot;0.08&quot; step=&quot;0.005&quot; value=&quot;0.02&quot;&gt;&lt;output id=&quot;fr-dv&quot;&gt;0.020&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;m stations, relative L&amp;#178; error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;fr-es&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;four nodes at the edges, relative L&amp;#178; error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;fr-ek&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The front (dashed) has two edges of width w = 0.01. Blue joins m evenly spaced readings by straight lines. Orange is a straight-segment curve with only four nodes, at a &amp;minus; d, a + d, b &amp;minus; d, and b + d, where a and b are the edges (black ticks). It is the sum of the two hats that carry weight one (gray dashed), the hats at a + d and b &amp;minus; d, and the hats at a &amp;minus; d and b + d carry weight zero (gray dotted). The arrows below mark d. The nodes move when the front moves, so two edge positions, a height, and d describe the orange curve.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;fr-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.3, 1.3, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.3, ny: 4, xlabel: &quot;x&quot;, ylabel: &quot;T(x)&quot;});
  const gC = L.el(&quot;g&quot;, {}, svg), gD = L.el(&quot;g&quot;, {}, svg);
  const w = 0.01;
  let c = 0, m = 32, d = 0.02;
  function redraw(){
    const a = 0.15 + c, b = 0.45 + c;
    const T = x =&gt; 0.5 * (Math.tanh((x - a) / w) - Math.tanh((x - b) / w));
    const xi = Array.from({length: m}, (_, k) =&gt; k / (m - 1));
    const yi = xi.map(T);
    const seg = x =&gt; {
      const k = Math.min(m - 2, Math.floor(x * (m - 1)));
      const t = x * (m - 1) - k;
      return yi[k] * (1 - t) + yi[k + 1] * t;
    };
    // hat functions on the nonuniform nodes 0, a - d, a + d, b - d, b + d, 1
    const N = [0, a - d, a + d, b - d, b + d, 1];
    const hat = j =&gt; x =&gt; {
      if (x &lt;= N[j - 1] || x &gt;= N[j + 1]) return 0;
      return x &lt;= N[j] ? (x - N[j - 1]) / (N[j] - N[j - 1]) : (N[j + 1] - x) / (N[j + 1] - N[j]);
    };
    const net = x =&gt; hat(2)(x) + hat(3)(x);
    gC.innerHTML = &quot;&quot;; gD.innerHTML = &quot;&quot;;
    L.curve(gC, T, X, Y, {stroke: &quot;var(--ink)&quot;, width: 2.5, dash: &quot;7 6&quot;, n: 1201});
    L.curve(gC, seg, X, Y, {stroke: &quot;var(--blue)&quot;, width: 2.5, n: 1201});
    [1, 4].forEach(j =&gt; L.curve(gC, hat(j), X, Y, {stroke: &quot;var(--muted)&quot;, width: 1.3, dash: &quot;2 4&quot;, opacity: 0.8, n: 2401}));
    [2, 3].forEach(j =&gt; L.curve(gC, hat(j), X, Y, {stroke: &quot;var(--muted)&quot;, width: 1.8, dash: &quot;6 4&quot;, opacity: 0.95, n: 2401}));
    L.curve(gC, net, X, Y, {stroke: &quot;var(--orange)&quot;, width: 2.8, n: 2401});
    [a - d, a + d, b - d, b + d].forEach(x =&gt;
      L.el(&quot;path&quot;, {d: &quot;M&quot; + (X(x)-5) + &quot; &quot; + (Y(-0.3)) + &quot; l10 0 l-5 -9 z&quot;, style: &quot;fill: var(--orange)&quot;}, gD));
    // the edges a and b, and d marked on each side of each edge
    [[a, &quot;a&quot;], [b, &quot;b&quot;]].forEach(([e, lab]) =&gt; {
      L.el(&quot;line&quot;, {x1: X(e), x2: X(e), y1: Y(-0.2), y2: Y(-0.08), style: &quot;stroke: var(--ink); stroke-width: 2&quot;}, gD);
      const t = L.el(&quot;text&quot;, {x: X(e), y: Y(-0.02), &quot;text-anchor&quot;: &quot;middle&quot;, style: &quot;fill: var(--ink); font-size: 12px&quot;}, gD); t.textContent = lab;
      [[e - d, e], [e, e + d]].forEach(([u0, u1]) =&gt; {
        const yy = Y(-0.14);
        L.el(&quot;line&quot;, {x1: X(u0), x2: X(u1), y1: yy, y2: yy, style: &quot;stroke: var(--orange); stroke-width: 1.5&quot;}, gD);
        L.el(&quot;path&quot;, {d: &quot;M&quot; + X(u0) + &quot; &quot; + yy + &quot; l5 -3 l0 6 z&quot;, style: &quot;fill: var(--orange)&quot;}, gD);
        L.el(&quot;path&quot;, {d: &quot;M&quot; + X(u1) + &quot; &quot; + yy + &quot; l-5 -3 l0 6 z&quot;, style: &quot;fill: var(--orange)&quot;}, gD);
      });
      const td = L.el(&quot;text&quot;, {x: X(e + d / 2), y: Y(-0.24), &quot;text-anchor&quot;: &quot;middle&quot;, style: &quot;fill: var(--orange); font-size: 12px&quot;}, gD); td.textContent = &quot;d&quot;;
    });
    let ns = 0, nk = 0, den = 0;
    for (let j = 0; j &lt;= 4000; j++) {
      const x = j / 4000, t = T(x);
      ns += (seg(x) - t) ** 2; nk += (net(x) - t) ** 2; den += t * t;
    }
    document.getElementById(&quot;fr-es&quot;).textContent = (100 * Math.sqrt(ns / den)).toFixed(1) + &quot;%&quot;;
    document.getElementById(&quot;fr-ek&quot;).textContent = (100 * Math.sqrt(nk / den)).toFixed(1) + &quot;%&quot;;
  }
  document.getElementById(&quot;fr-c&quot;).addEventListener(&quot;input&quot;, e =&gt; { c = parseFloat(e.target.value); document.getElementById(&quot;fr-cv&quot;).textContent = c.toFixed(2); redraw(); });
  document.getElementById(&quot;fr-m&quot;).addEventListener(&quot;input&quot;, e =&gt; { m = parseInt(e.target.value); document.getElementById(&quot;fr-mv&quot;).textContent = m; redraw(); });
  document.getElementById(&quot;fr-d&quot;).addEventListener(&quot;input&quot;, e =&gt; { d = parseFloat(e.target.value); document.getElementById(&quot;fr-dv&quot;).textContent = d.toFixed(3); redraw(); });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:620px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

The book's notebooks on [functions as points](https://sciml-book.github.io/sciml_notebook/representations/function-as-a-point.html), [norms](https://sciml-book.github.io/sciml_notebook/representations/norms.html), [projection](https://sciml-book.github.io/sciml_notebook/representations/projection.html), and [Weierstrass by coin flips](https://sciml-book.github.io/sciml_notebook/foundations/weierstrass-bernstein.html) run the computations on this page.
The [second page](kernels-and-families.md) continues with noisy readings, kernels, families of functions, and shapes that move.
