# Representing a Function with Finitely Many Numbers

Here is a taut string, pinned at both ends and pulled sideways.
The whole curve is its displacement $u(x)$ on $0 \le x \le 1$, and we want to store it in a computer with a handful of numbers.
A computer cannot store a curve, so every method in this course, the multilayer perceptron included, stores a short list of numbers and a rule that turns the list back into a curve.
On this page we build two such choices by hand, measure what each one loses, and arrive at a network whose kinks can move.

## Readings at fixed stations

The obvious move is to measure the string.
Put five sensors along it, at $x = 0$, $\tfrac14$, $\tfrac12$, $\tfrac34$, $1$.
For the displacement $u(x) = 0.8\sin(\pi x) + 0.4\sin(2\pi x) + 0.2\sin(3\pi x)$ they read $0$, $1.11$, $0.60$, $0.31$, $0$, and everything between the sensors is unknown.
So we guess.
The simplest guess connects neighboring readings with straight lines, and we have a curve again.
Now look where the guess is wrong.
The lines miss the bends between sensors, and the worst miss is $0.22$, about a fifth of the largest displacement.

Would more sensors fix this?
Between two sensors a distance $h$ apart the curve bends away from a straight line by about $u''h^2/8$ at the middle, so halving $h$ should cut the miss to a quarter.
Nine sensors give $6.3$ percent, a factor of $3.2$ and short of four, because at five sensors one segment spans more than a third of the shortest wavelength in the curve and the bend inside it is far from a parabola.
Seventeen give $1.6$ percent, a factor of $4.0$, and from there on every halving divides the miss by four.

These gaps are visible only because the curve is known.
Suppose only the seventeen readings were available.
Which curves could have produced them?
Add the wave $0.3\sin(16\pi x)$ to the displacement.
At every station $16\pi x_i$ is a multiple of $\pi$, so the wave is zero there and not one reading changes, while the curve moves by $0.3$ at each crest.
Two functions that agree at every station are aliases on that grid, and the readings cannot tell them apart.
Sweep the station count in the lab below, then switch the added wave on and find the counts at which no reading moves.

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
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;sm-m&quot; type=&quot;range&quot; min=&quot;5&quot; max=&quot;65&quot; step=&quot;4&quot; value=&quot;9&quot;&gt;&lt;output id=&quot;sm-mv&quot;&gt;9&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot;&gt;&lt;span&gt;added mode&lt;/span&gt;&lt;label style=&quot;flex:1;font-size:13px;&quot;&gt;&lt;input type=&quot;checkbox&quot; id=&quot;sm-alias&quot;&gt; add 0.3&amp;thinsp;sin(16&amp;pi;x) to the displacement&lt;/label&gt;&lt;output&gt;&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;readings changed by (max)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;sm-st&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;reconstruction error, relative RMS&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;sm-err&quot;&gt;3.8%&lt;/span&gt;&lt;/div&gt;
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
  let m = 9, add = false;
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
Move one coordinate in the lab below and the whole curve answers, since a coefficient belongs to a shape that spans the string.

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;Coefficients on three sine modes&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move a slider and the whole curve answers, because a coefficient belongs to a shape that spans the string.&lt;/p&gt;
&lt;div class=&quot;plot-wrap&quot;&gt;
  &lt;svg id=&quot;hero-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
  &lt;span class=&quot;float-label&quot;&gt;one point in function space&lt;/span&gt;
&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;a&amp;#8321; &amp;nbsp;&amp;middot;&amp;nbsp; sin(&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;a1&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0.8&quot;&gt;&lt;output id=&quot;a1v&quot;&gt;0.80&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;a&amp;#8322; &amp;nbsp;&amp;middot;&amp;nbsp; sin(2&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;a2&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0.4&quot;&gt;&lt;output id=&quot;a2v&quot;&gt;0.40&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--green)&quot;&gt;&lt;span&gt;a&amp;#8323; &amp;nbsp;&amp;middot;&amp;nbsp; sin(3&amp;pi;x)&lt;/span&gt;&lt;input id=&quot;a3&quot; type=&quot;range&quot; min=&quot;-1&quot; max=&quot;1&quot; step=&quot;0.05&quot; value=&quot;0.2&quot;&gt;&lt;output id=&quot;a3v&quot;&gt;0.20&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;coordinates (a&amp;#8321;, a&amp;#8322;, a&amp;#8323;)&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;coords&quot;&gt;(0.80, 0.40, 0.20)&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;pinned ends&lt;/span&gt;&lt;span class=&quot;num&quot;&gt;u(0) = u(1) = 0&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The dashed curves are the three weighted modes. The solid curve is their sum. One slider moves the whole sum, not one part of it.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;hero-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-1.8, 1.8, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.8, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
  const gC = L.el(&quot;g&quot;, {}, svg), gS = L.el(&quot;g&quot;, {}, svg);
  const mode = k =&gt; x =&gt; Math.sin(k * Math.PI * x);
  const colors = [&quot;var(--blue)&quot;, &quot;var(--orange)&quot;, &quot;var(--green)&quot;];
  const a = [0.8, 0.4, 0.2];
  function redraw(){
    gC.innerHTML = &quot;&quot;; gS.innerHTML = &quot;&quot;;
    for (let k = 0; k &lt; 3; k++)
      L.curve(gC, x =&gt; a[k] * mode(k + 1)(x), X, Y, {stroke: colors[k], width: 2, dash: &quot;7 7&quot;, opacity: 0.55});
    L.curve(gS, x =&gt; a[0]*mode(1)(x) + a[1]*mode(2)(x) + a[2]*mode(3)(x), X, Y, {stroke: &quot;var(--ink)&quot;, width: 4});
    L.el(&quot;circle&quot;, {cx: X(0), cy: Y(0), r: 4, style: &quot;fill: var(--ink)&quot;}, gS);
    L.el(&quot;circle&quot;, {cx: X(1), cy: Y(0), r: 4, style: &quot;fill: var(--ink)&quot;}, gS);
    document.getElementById(&quot;coords&quot;).textContent =
      &quot;(&quot; + L.fmt(a[0]) + &quot;, &quot; + L.fmt(a[1]) + &quot;, &quot; + L.fmt(a[2]) + &quot;)&quot;;
  }
  [&quot;a1&quot;, &quot;a2&quot;, &quot;a3&quot;].forEach((id, k) =&gt; {
    document.getElementById(id).addEventListener(&quot;input&quot;, e =&gt; {
      a[k] = parseFloat(e.target.value);
      document.getElementById(id + &quot;v&quot;).textContent = L.fmt(a[k]);
      redraw();
    });
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:575px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

So far every curve was smooth, because every sine is smooth.
Now press on the string at one point.
The point load bends it into two straight segments with a corner at mid-span, and no sum of three sines has a corner.
The closest sum is the best available, and which sum is closest depends on how the error is measured.
That depends on what matters.
If it is clearance under the string, only the worst gap matters, and that is the sup norm.
If it is the overall misfit, all the gaps count at once, so square them, integrate, and take the root, and that is the $L^2$ norm.
If it is the elastic energy, the values are the wrong thing to look at, since the energy is an integral of the squared slope, and the root of the integrated squared slope error is the $H^1$ seminorm.
For the five-sensor guess the three read $0.22$, $0.093$, and $1.20$.
A spike of height one on a base of width $0.04$ has sup norm one, $L^2$ norm $0.115$, and elastic energy $50$, and quartering the base leaves the first, halves the second, and quadruples the third, so the three can disagree without bound.

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
Can a family of smooth shapes get as close as we like to one?
Here is Bernstein's idea.
Flip $n$ coins that land heads with probability $x$, and weight the reading $f(k/n)$ by the probability of exactly $k$ heads,

$$B_n f(x) = \sum_{k=0}^{n} f\!\left(\frac{k}{n}\right)\binom{n}{k} x^k (1-x)^{n-k},$$

so $B_n f(x)$ is the expected reading when the fraction of heads stands in for $x$.
With two coins the three weights are three hills, one at each wall and one at mid-span, and for the corner function $|x - \tfrac12|$ their sum reads $\tfrac14$ at mid-span where the function is $0$, because every neighbor of the corner sits higher than the corner and any average overshoots there.
As $n$ grows the fraction of heads concentrates near $x$, the hills narrow like $1/\sqrt{n}$, and so does the gap.
At $n = 8$ the gap at the corner is $0.137$ against a prediction of $0.4/\sqrt{n} = 0.141$, and at $n = 32$ it is $0.070$ against $0.071$.
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
Universal approximation theorems for networks have the same form and the same silences.

## Hats are ReLUs

Look again at the straight segments.
They are a basis too.
Take one shape per interior station, equal to one at its own station, zero at the others, and straight in between, a hat function.
Weight each hat by the reading at its station and add, and the sum is the straight-segment guess with the readings as its coefficients.
Now look at one hat more closely.
It is three ramps,

$$\phi_i(x) = \frac{\mathrm{ReLU}(x - x_{i-1}) - 2\,\mathrm{ReLU}(x - x_i) + \mathrm{ReLU}(x - x_{i+1})}{h}, \qquad \mathrm{ReLU}(s) = \max(s, 0).$$

So the straight-segment guess is a network with one hidden layer of ReLU units whose kinks sit at the stations, and its error bound $Mh^2/8$ for $|u''| \le M$ is a universal approximation theorem with a rate, in one dimension.
The lab below draws the three ramps of one hat and reports the measured gap beside the bound, which the parabola $x(1-x)$ meets with equality because its second derivative is constant.

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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;A hat function from three ReLU ramps&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Change the station count. The straight-segment guess is a one-hidden-layer ReLU network, and its largest gap meets the bound.&lt;/p&gt;
&lt;svg id=&quot;ht-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;ht-m&quot; type=&quot;range&quot; min=&quot;3&quot; max=&quot;17&quot; step=&quot;2&quot; value=&quot;5&quot;&gt;&lt;output id=&quot;ht-mv&quot;&gt;5&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;show the hat at station&lt;/span&gt;&lt;input id=&quot;ht-i&quot; type=&quot;range&quot; min=&quot;1&quot; max=&quot;3&quot; step=&quot;1&quot; value=&quot;2&quot;&gt;&lt;output id=&quot;ht-iv&quot;&gt;2&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;hidden ReLU units&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;ht-units&quot;&gt;5&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;largest gap, measured&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;ht-err&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;bound M h&amp;#178; / 8 with M = 2&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;ht-bound&quot;&gt;0.000&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The parabola x(1&amp;minus;x) (dashed) and its straight-segment reconstruction (blue). The three orange ramps are ReLU(x&amp;minus;x&lt;sub&gt;i&amp;minus;1&lt;/sub&gt;), &amp;minus;2&amp;thinsp;ReLU(x&amp;minus;x&lt;sub&gt;i&lt;/sub&gt;), and ReLU(x&amp;minus;x&lt;sub&gt;i+1&lt;/sub&gt;), each divided by h. Their sum is the hat at station i (green), and the reconstruction is the hats weighted by the readings.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;ht-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.55, 1.15, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.15, ny: 3, xlabel: &quot;x&quot;, ylabel: &quot;u(x)&quot;});
  const defs = L.el(&quot;defs&quot;, {}, svg);
  const cp = L.el(&quot;clipPath&quot;, {id: &quot;ht-clip&quot;}, defs);
  L.el(&quot;rect&quot;, {x: 46, y: 14, width: 660, height: 272}, cp);
  const gR = L.el(&quot;g&quot;, {&quot;clip-path&quot;: &quot;url(#ht-clip)&quot;}, svg), gC = L.el(&quot;g&quot;, {}, svg), gD = L.el(&quot;g&quot;, {}, svg);
  const u = x =&gt; x * (1 - x);
  const relu = s =&gt; Math.max(s, 0);
  let m = 5, i = 2;
  function redraw(){
    const h = 1 / (m - 1);
    const xi = Array.from({length: m}, (_, k) =&gt; k * h);
    const yi = xi.map(u);
    const reb = x =&gt; {
      const k = Math.min(m - 2, Math.floor(x * (m - 1)));
      const t = x * (m - 1) - k;
      return yi[k] * (1 - t) + yi[k + 1] * t;
    };
    const ramps = [
      x =&gt; relu(x - xi[i-1]) / h,
      x =&gt; -2 * relu(x - xi[i]) / h,
      x =&gt; relu(x - xi[i+1]) / h,
    ];
    const hat = x =&gt; ramps[0](x) + ramps[1](x) + ramps[2](x);
    gR.innerHTML = &quot;&quot;; gC.innerHTML = &quot;&quot;; gD.innerHTML = &quot;&quot;;
    ramps.forEach(r =&gt; L.curve(gR, r, X, Y, {stroke: &quot;var(--orange)&quot;, width: 2, dash: &quot;6 6&quot;, opacity: 0.8, n: 401}));
    L.curve(gR, hat, X, Y, {stroke: &quot;var(--green)&quot;, width: 2.5, n: 401});
    L.curve(gC, u, X, Y, {stroke: &quot;var(--ink)&quot;, width: 2.5, dash: &quot;7 6&quot;, n: 401});
    L.curve(gC, reb, X, Y, {stroke: &quot;var(--blue)&quot;, width: 3, n: 801});
    xi.forEach((x, k) =&gt; {
      L.el(&quot;circle&quot;, {cx: X(x), cy: Y(yi[k]), r: 3.6, style: &quot;fill: var(--red); stroke: var(--paper); stroke-width: 1&quot;}, gD);
      L.el(&quot;path&quot;, {d: &quot;M&quot; + (X(x)-5) + &quot; &quot; + (Y(-0.55)) + &quot; l10 0 l-5 -9 z&quot;, style: &quot;fill: var(--muted)&quot;}, gD);
    });
    let worst = 0;
    for (let j = 0; j &lt;= 800; j++) { const x = j / 800; worst = Math.max(worst, Math.abs(reb(x) - u(x))); }
    document.getElementById(&quot;ht-units&quot;).textContent = m;
    document.getElementById(&quot;ht-err&quot;).textContent = worst.toFixed(4);
    document.getElementById(&quot;ht-bound&quot;).textContent = (2 * h * h / 8).toFixed(4);
  }
  const si = document.getElementById(&quot;ht-i&quot;);
  document.getElementById(&quot;ht-m&quot;).addEventListener(&quot;input&quot;, e =&gt; {
    m = parseInt(e.target.value);
    document.getElementById(&quot;ht-mv&quot;).textContent = m;
    si.max = m - 2; if (i &gt; m - 2) { i = m - 2; si.value = i; }
    document.getElementById(&quot;ht-iv&quot;).textContent = i;
    redraw();
  });
  si.addEventListener(&quot;input&quot;, e =&gt; {
    i = parseInt(e.target.value);
    document.getElementById(&quot;ht-iv&quot;).textContent = i;
    redraw();
  });
  redraw();
})();
&lt;/script&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;" style="width:100%;height:600px;border:none;overflow:hidden;" scrolling="no" loading="lazy"></iframe>

Back to the point load.
One hat whose node sits on the corner describes it with one number, $0.25$, and on the five-station grid three hats do it with $0.125$, $0.25$, $0.125$ and no error, while the closest three sines miss by $4.8$ percent and thirty-three still miss by $0.20$.
A shape that shares the function's corner needs one number where smooth shapes need infinitely many.
Which shapes to use depends on the function, and so far we have placed them by hand.

## Let the kinks move

A unit $\mathrm{ReLU}(wx + b)$ has its kink at $x = -b/w$, so the kink positions are parameters we can place.
Where would we want to?
Hot fluid pushes a temperature front along a pipe, one shape $T(x - ct)$ whose whole history is its position.
Thirty-two evenly spaced stations reach an error of $8.7$ percent, because most of them record a flat line wherever the front sits.
Four ReLU units with kinks $0.02$ on either side of each edge reach $4.9$ percent with four numbers, and when the front moves the kinks move with it while the stations stay where we put them.
A perceptron chooses between two problems.
Fixed kinks give a linear problem, one solve, and the projection theorem's guarantee that the solve finds the closest member of the family.
Moving kinks give a non-convex problem, gradient descent, and no such guarantee.
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
&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;div class=&quot;lab&quot;&gt;&lt;p class=&quot;lab-title&quot;&gt;ReLU kinks on a moving front&lt;/p&gt;&lt;p class=&quot;lab-sub&quot;&gt;Move the front. The stations stay where we put them, and the four kinks follow the edges.&lt;/p&gt;
&lt;svg id=&quot;fr-plot&quot; class=&quot;plot&quot; viewBox=&quot;0 0 720 300&quot;&gt;&lt;/svg&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--ink)&quot;&gt;&lt;span&gt;shift of the front c&lt;/span&gt;&lt;input id=&quot;fr-c&quot; type=&quot;range&quot; min=&quot;0&quot; max=&quot;0.45&quot; step=&quot;0.01&quot; value=&quot;0&quot;&gt;&lt;output id=&quot;fr-cv&quot;&gt;0.00&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--blue)&quot;&gt;&lt;span&gt;stations m&lt;/span&gt;&lt;input id=&quot;fr-m&quot; type=&quot;range&quot; min=&quot;8&quot; max=&quot;128&quot; step=&quot;8&quot; value=&quot;32&quot;&gt;&lt;output id=&quot;fr-mv&quot;&gt;32&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;slider-row&quot; style=&quot;--slider-color: var(--orange)&quot;&gt;&lt;span&gt;kink half-spacing d&lt;/span&gt;&lt;input id=&quot;fr-d&quot; type=&quot;range&quot; min=&quot;0.005&quot; max=&quot;0.08&quot; step=&quot;0.005&quot; value=&quot;0.02&quot;&gt;&lt;output id=&quot;fr-dv&quot;&gt;0.020&lt;/output&gt;&lt;/div&gt;
&lt;div class=&quot;readout-row&quot;&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;m stations, relative L&amp;#178; error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;fr-es&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
  &lt;div class=&quot;readout&quot;&gt;&lt;span class=&quot;label&quot;&gt;four kinks at the edges, relative L&amp;#178; error&lt;/span&gt;&lt;span class=&quot;num&quot; id=&quot;fr-ek&quot;&gt;0.0%&lt;/span&gt;&lt;/div&gt;
&lt;/div&gt;
&lt;p class=&quot;lab-note&quot;&gt;The front (dashed) has two edges of width w = 0.01. Blue joins m evenly spaced readings by straight lines. Orange is a network of four ReLU units whose kinks sit d on either side of each edge, and the kinks move when the front moves. Two edge positions, a height, and the kink spacing describe the orange curve.&lt;/p&gt;
&lt;script&gt;
(function(){
  const svg = document.getElementById(&quot;fr-plot&quot;);
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.3, 1.3, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.3, ny: 4, xlabel: &quot;x&quot;, ylabel: &quot;T(x)&quot;});
  const gC = L.el(&quot;g&quot;, {}, svg), gD = L.el(&quot;g&quot;, {}, svg);
  const w = 0.01;
  let c = 0, m = 32, d = 0.02;
  const relu = s =&gt; Math.max(s, 0);
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
    const net = x =&gt; (relu(x - (a - d)) - relu(x - (a + d)) - relu(x - (b - d)) + relu(x - (b + d))) / (2 * d);
    gC.innerHTML = &quot;&quot;; gD.innerHTML = &quot;&quot;;
    L.curve(gC, T, X, Y, {stroke: &quot;var(--ink)&quot;, width: 2.5, dash: &quot;7 6&quot;, n: 1201});
    L.curve(gC, seg, X, Y, {stroke: &quot;var(--blue)&quot;, width: 2.5, n: 1201});
    L.curve(gC, net, X, Y, {stroke: &quot;var(--orange)&quot;, width: 2.5, n: 1201});
    [a - d, a + d, b - d, b + d].forEach(x =&gt;
      L.el(&quot;path&quot;, {d: &quot;M&quot; + (X(x)-5) + &quot; &quot; + (Y(-0.3)) + &quot; l10 0 l-5 -9 z&quot;, style: &quot;fill: var(--orange)&quot;}, gD));
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

## Next lectures and notebooks

The [ReLU page](../00-mlp/relu.md) shows what depth adds to a single hidden layer.
The [universality proof](../00-mlp/uat-proof.md) and the [ReLU demo](../00-mlp/uat.md) extend the theorem to general activations and dimensions, with the same silences about width, data, and training.
The [gradient descent](../00-mlp/sgd.md), [automatic differentiation](../00-mlp/ad.md), and [regularization](../00-mlp/regularization.md) pages then say how the kinks are moved.
The book's notebooks on [functions as points](https://sciml-book.github.io/sciml_notebook/representations/function-as-a-point.html), [norms](https://sciml-book.github.io/sciml_notebook/representations/norms.html), [projection](https://sciml-book.github.io/sciml_notebook/representations/projection.html), and [Weierstrass by coin flips](https://sciml-book.github.io/sciml_notebook/foundations/weierstrass-bernstein.html) run every computation on this page.
The [second page](kernels-and-families.md) continues with noisy readings, kernels, families of functions, and shapes that move.
