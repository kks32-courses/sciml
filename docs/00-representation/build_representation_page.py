"""Build the Representation lecture page with its interactive figures inline.

The page is Markdown for the course site. Each interactive figure is a
self-contained HTML document embedded as an <iframe srcdoc>, the pattern the
book's notebooks use (book/sciml_notebook/docs/sciml_labs.py), so it renders
inside the site's own layout and follows the OS light or dark mode.

Four labs are reused from the book's notebooks (three coordinates, samples at
stations, coordinates in a basis, the closest blend). Three are new here
(Bernstein's coin flips, a hat from three ramps, kinks that ride with a front).

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


hero_body = body_from("build_function_as_point_notebook.py", "hero_body")
sampling_body = body_from("build_function_as_point_notebook.py", "sampling_body")
basis_body = body_from("build_basis_notebook.py", "basis_body")
proj_body = body_from("build_projection_notebook.py", "proj_body")

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

# --------------------------------------------------------------------------- hat = three ramps
hat_body = r'''
<svg id="ht-plot" class="plot" viewBox="0 0 720 300"></svg>
<div class="slider-row" style="--slider-color: var(--blue)"><span>stations m</span><input id="ht-m" type="range" min="3" max="17" step="2" value="5"><output id="ht-mv">5</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>show the hat at station</span><input id="ht-i" type="range" min="1" max="3" step="1" value="2"><output id="ht-iv">2</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">hidden ReLU units</span><span class="num" id="ht-units">5</span></div>
  <div class="readout"><span class="label">largest gap, measured</span><span class="num" id="ht-err">0.000</span></div>
  <div class="readout"><span class="label">bound M h&#178; / 8 with M = 2</span><span class="num" id="ht-bound">0.000</span></div>
</div>
<p class="lab-note">The parabola x(1&minus;x) (dashed) and its straight-segment reconstruction (blue). The three orange ramps are ReLU(x&minus;x<sub>i&minus;1</sub>), &minus;2&thinsp;ReLU(x&minus;x<sub>i</sub>), and ReLU(x&minus;x<sub>i+1</sub>), each divided by h. Their sum is the hat at station i (green), and the reconstruction is the hats weighted by the readings.</p>
<script>
(function(){
  const svg = document.getElementById("ht-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.55, 1.15, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.15, ny: 3, xlabel: "x", ylabel: "u(x)"});
  const defs = L.el("defs", {}, svg);
  const cp = L.el("clipPath", {id: "ht-clip"}, defs);
  L.el("rect", {x: 46, y: 14, width: 660, height: 272}, cp);
  const gR = L.el("g", {"clip-path": "url(#ht-clip)"}, svg), gC = L.el("g", {}, svg), gD = L.el("g", {}, svg);
  const u = x => x * (1 - x);
  const relu = s => Math.max(s, 0);
  let m = 5, i = 2;
  function redraw(){
    const h = 1 / (m - 1);
    const xi = Array.from({length: m}, (_, k) => k * h);
    const yi = xi.map(u);
    const reb = x => {
      const k = Math.min(m - 2, Math.floor(x * (m - 1)));
      const t = x * (m - 1) - k;
      return yi[k] * (1 - t) + yi[k + 1] * t;
    };
    const ramps = [
      x => relu(x - xi[i-1]) / h,
      x => -2 * relu(x - xi[i]) / h,
      x => relu(x - xi[i+1]) / h,
    ];
    const hat = x => ramps[0](x) + ramps[1](x) + ramps[2](x);
    gR.innerHTML = ""; gC.innerHTML = ""; gD.innerHTML = "";
    ramps.forEach(r => L.curve(gR, r, X, Y, {stroke: "var(--orange)", width: 2, dash: "6 6", opacity: 0.8, n: 401}));
    L.curve(gR, hat, X, Y, {stroke: "var(--green)", width: 2.5, n: 401});
    L.curve(gC, u, X, Y, {stroke: "var(--ink)", width: 2.5, dash: "7 6", n: 401});
    L.curve(gC, reb, X, Y, {stroke: "var(--blue)", width: 3, n: 801});
    xi.forEach((x, k) => {
      L.el("circle", {cx: X(x), cy: Y(yi[k]), r: 3.6, style: "fill: var(--red); stroke: var(--paper); stroke-width: 1"}, gD);
      L.el("path", {d: "M" + (X(x)-5) + " " + (Y(-0.55)) + " l10 0 l-5 -9 z", style: "fill: var(--muted)"}, gD);
    });
    let worst = 0;
    for (let j = 0; j <= 800; j++) { const x = j / 800; worst = Math.max(worst, Math.abs(reb(x) - u(x))); }
    document.getElementById("ht-units").textContent = m;
    document.getElementById("ht-err").textContent = worst.toFixed(4);
    document.getElementById("ht-bound").textContent = (2 * h * h / 8).toFixed(4);
  }
  const si = document.getElementById("ht-i");
  document.getElementById("ht-m").addEventListener("input", e => {
    m = parseInt(e.target.value);
    document.getElementById("ht-mv").textContent = m;
    si.max = m - 2; if (i > m - 2) { i = m - 2; si.value = i; }
    document.getElementById("ht-iv").textContent = i;
    redraw();
  });
  si.addEventListener("input", e => {
    i = parseInt(e.target.value);
    document.getElementById("ht-iv").textContent = i;
    redraw();
  });
  redraw();
})();
</script>'''

# --------------------------------------------------------------------------- kinks ride with the front
front_body = r'''
<svg id="fr-plot" class="plot" viewBox="0 0 720 300"></svg>
<div class="slider-row" style="--slider-color: var(--ink)"><span>shift of the front c</span><input id="fr-c" type="range" min="0" max="0.45" step="0.01" value="0"><output id="fr-cv">0.00</output></div>
<div class="slider-row" style="--slider-color: var(--blue)"><span>stations m</span><input id="fr-m" type="range" min="8" max="128" step="8" value="32"><output id="fr-mv">32</output></div>
<div class="slider-row" style="--slider-color: var(--orange)"><span>kink half-spacing d</span><input id="fr-d" type="range" min="0.005" max="0.08" step="0.005" value="0.02"><output id="fr-dv">0.020</output></div>
<div class="readout-row">
  <div class="readout"><span class="label">m stations, relative L&#178; error</span><span class="num" id="fr-es">0.0%</span></div>
  <div class="readout"><span class="label">four kinks at the edges, relative L&#178; error</span><span class="num" id="fr-ek">0.0%</span></div>
</div>
<p class="lab-note">The front (dashed) has two edges of width w = 0.01. Blue joins m evenly spaced readings by straight lines. Orange is a network of four ReLU units whose kinks sit d on either side of each edge, and the kinks move when the front moves. Two edge positions, a height, and the kink spacing describe the orange curve.</p>
<script>
(function(){
  const svg = document.getElementById("fr-plot");
  const X = L.scale(0, 1, 46, 706), Y = L.scale(-0.3, 1.3, 286, 14);
  L.axes(svg, X, Y, {yMax: 1.3, ny: 4, xlabel: "x", ylabel: "T(x)"});
  const gC = L.el("g", {}, svg), gD = L.el("g", {}, svg);
  const w = 0.01;
  let c = 0, m = 32, d = 0.02;
  const relu = s => Math.max(s, 0);
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
    const net = x => (relu(x - (a - d)) - relu(x - (a + d)) - relu(x - (b - d)) + relu(x - (b + d))) / (2 * d);
    gC.innerHTML = ""; gD.innerHTML = "";
    L.curve(gC, T, X, Y, {stroke: "var(--ink)", width: 2.5, dash: "7 6", n: 1201});
    L.curve(gC, seg, X, Y, {stroke: "var(--blue)", width: 2.5, n: 1201});
    L.curve(gC, net, X, Y, {stroke: "var(--orange)", width: 2.5, n: 1201});
    [a - d, a + d, b - d, b + d].forEach(x =>
      L.el("path", {d: "M" + (X(x)-5) + " " + (Y(-0.3)) + " l10 0 l-5 -9 z", style: "fill: var(--orange)"}, gD));
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
    "HERO": embed_lab(lab_html("Coefficients on three sine modes",
                               "Move a slider and the whole curve answers, because a coefficient belongs to a shape that spans the string.", hero_body), 575),
    "SAMPLING": embed_lab(lab_html("Samples at fixed stations",
                                   "Sweep the station count, then add the sixteenth mode and check which station counts leave the readings unchanged.", sampling_body), 565),
    "BASIS": embed_lab(lab_html("Decay of the coefficients on sine modes",
                                "Pick a target and add modes. The bars are the coefficients, and the error readout measures what the dropped modes held.", basis_body), 600),
    "PROJ": embed_lab(lab_html("Minimizing the squared error over one coefficient",
                               "Slide the coefficient. The squared error is a bowl, and the projection formula finds its bottom without searching.", proj_body), 545),
    "BERN": embed_lab(lab_html("Bernstein polynomials for a corner",
                               "Raise the degree. The hills narrow, the sum closes in on the corner, and the gap at the corner follows 0.4 over the square root of n.", bern_body), 590),
    "HAT": embed_lab(lab_html("A hat function from three ReLU ramps",
                              "Change the station count. The straight-segment guess is a one-hidden-layer ReLU network, and its largest gap meets the bound.", hat_body), 600),
    "FRONT": embed_lab(lab_html("ReLU kinks on a moving front",
                                "Move the front. The stations stay where we put them, and the four kinks follow the edges.", front_body), 620),
}

PAGE = r"""# Representing a Function with Finitely Many Numbers

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

@@SAMPLING@@

## Coefficients on shapes

Here is a different idea.
Instead of asking where the string is, ask what it is made of.
The string vibrates in sine modes, and the displacement above is the first three of them weighted by $0.8$, $0.4$, $0.2$.
Those three numbers give the whole curve, with no grid anywhere.
Check it at mid-span, where the second mode vanishes and the first and third read $1$ and $-1$, so $u(\tfrac12) = 0.8 - 0.2 = 0.6$.
Add two displacements and their coefficients add, scale one and its coefficients scale, so the three coefficients are coordinates and the displacement is a point in a three-dimensional space of functions.
Move one coordinate in the lab below and the whole curve answers, since a coefficient belongs to a shape that spans the string.

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
A spike of height one on a base of width $0.04$ has sup norm one, $L^2$ norm $0.115$, and elastic energy $50$, and quartering the base leaves the first, halves the second, and quadruples the third, so the three can disagree without bound.

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
Can a family of smooth shapes get as close as we like to one?
Here is Bernstein's idea.
Flip $n$ coins that land heads with probability $x$, and weight the reading $f(k/n)$ by the probability of exactly $k$ heads,

$$B_n f(x) = \sum_{k=0}^{n} f\!\left(\frac{k}{n}\right)\binom{n}{k} x^k (1-x)^{n-k},$$

so $B_n f(x)$ is the expected reading when the fraction of heads stands in for $x$.
With two coins the three weights are three hills, one at each wall and one at mid-span, and for the corner function $|x - \tfrac12|$ their sum reads $\tfrac14$ at mid-span where the function is $0$, because every neighbor of the corner sits higher than the corner and any average overshoots there.
As $n$ grows the fraction of heads concentrates near $x$, the hills narrow like $1/\sqrt{n}$, and so does the gap.
At $n = 8$ the gap at the corner is $0.137$ against a prediction of $0.4/\sqrt{n} = 0.141$, and at $n = 32$ it is $0.070$ against $0.071$.
Raise the degree below and watch the hills narrow while the gap at the corner follows the prediction.

@@BERN@@

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

@@HAT@@

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

@@FRONT@@

## Next lectures and notebooks

The [ReLU page](../00-mlp/relu.md) shows what depth adds to a single hidden layer.
The [universality proof](../00-mlp/uat-proof.md) and the [ReLU demo](../00-mlp/uat.md) extend the theorem to general activations and dimensions, with the same silences about width, data, and training.
The [gradient descent](../00-mlp/sgd.md), [automatic differentiation](../00-mlp/ad.md), and [regularization](../00-mlp/regularization.md) pages then say how the kinks are moved.
The book's notebooks on [functions as points](https://sciml-book.github.io/sciml_notebook/representations/function-as-a-point.html), [norms](https://sciml-book.github.io/sciml_notebook/representations/norms.html), [projection](https://sciml-book.github.io/sciml_notebook/representations/projection.html), and [Weierstrass by coin flips](https://sciml-book.github.io/sciml_notebook/foundations/weierstrass-bernstein.html) run every computation on this page.
The [second page](kernels-and-families.md) continues with noisy readings, kernels, families of functions, and shapes that move.
"""

page = PAGE
for tag, html in labs.items():
    page = page.replace("@@" + tag + "@@", html)
assert "@@" not in page
(HERE / "representation.md").write_text(page)
print("wrote", HERE / "representation.md", len(page), "chars,", len(labs), "labs")
