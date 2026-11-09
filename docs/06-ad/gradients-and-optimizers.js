/* Gradients and optimizers. Widget 1 steps through the tape of a projectile loss in forward and reverse mode. Widget 2 runs gradient descent, Adam, Newton, and L-BFGS on the same loss and draws the quadratic model each one steps into, as contours or as a surface. */
/* Core math for the gradients-and-optimizers page: landscapes, the projectile tape, and four optimizers in two dimensions. */
const GOCore = (function () {
  'use strict';
  const G = 9.81, DEG = Math.PI / 180;
  const V_TRUE = 20, A_TRUE = 50;

  const V = {
    add: (a, b) => [a[0] + b[0], a[1] + b[1]],
    sub: (a, b) => [a[0] - b[0], a[1] - b[1]],
    mul: (a, s) => [a[0] * s, a[1] * s],
    dot: (a, b) => a[0] * b[0] + a[1] * b[1],
    norm: a => Math.hypot(a[0], a[1]),
  };
  const M = {
    vec: (A, x) => [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]],
    det: A => A[0][0] * A[1][1] - A[0][1] * A[1][0],
    inv: A => { const d = A[0][0] * A[1][1] - A[0][1] * A[1][0]; return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]; },
    add: (A, B) => [[A[0][0] + B[0][0], A[0][1] + B[0][1]], [A[1][0] + B[1][0], A[1][1] + B[1][1]]],
    scale: (A, s) => [[A[0][0] * s, A[0][1] * s], [A[1][0] * s, A[1][1] * s]],
    outer: (a, b) => [[a[0] * b[0], a[0] * b[1]], [a[1] * b[0], a[1] * b[1]]],
    eigSym: A => { const m = (A[0][0] + A[1][1]) / 2, r = Math.hypot((A[0][0] - A[1][1]) / 2, A[0][1]); return [m - r, m + r]; },
  };

  // ---------- projectile ----------
  function apex(v, adeg) { const t = adeg * DEG; return [v * v * Math.sin(2 * t) / (2 * G), v * v * Math.sin(t) ** 2 / (2 * G)]; }
  function landing(v, adeg) { const t = adeg * DEG; return v * v * Math.sin(2 * t) / G; }
  const APEX_TRUE = apex(V_TRUE, A_TRUE), R_TRUE = landing(V_TRUE, A_TRUE);

  // observations y(v, a_deg), their Jacobian rows, and their Hessians
  function obsApex(p) {
    const v = p[0], t = p[1] * DEG, k = DEG, s = Math.sin(t), s2 = Math.sin(2 * t), c2 = Math.cos(2 * t);
    return {
      y: [v * v * s2 / (2 * G), v * v * s * s / (2 * G)],
      J: [[v * s2 / G, k * v * v * c2 / G], [v * s * s / G, k * v * v * s2 / (2 * G)]],
      H: [[[s2 / G, k * 2 * v * c2 / G], [k * 2 * v * c2 / G, -k * k * 2 * v * v * s2 / G]],
          [[s * s / G, k * v * s2 / G], [k * v * s2 / G, k * k * v * v * c2 / G]]],
      target: APEX_TRUE,
    };
  }
  function obsLanding(p) {
    const v = p[0], t = p[1] * DEG, k = DEG, s2 = Math.sin(2 * t), c2 = Math.cos(2 * t);
    return {
      y: [v * v * s2 / G],
      J: [[2 * v * s2 / G, k * 2 * v * v * c2 / G]],
      H: [[[2 * s2 / G, k * 4 * v * c2 / G], [k * 4 * v * c2 / G, -k * k * 4 * v * v * s2 / G]]],
      target: [R_TRUE],
    };
  }
  function leastSquares(obs) {
    return {
      f: p => { const o = obs(p); let s = 0; o.y.forEach((y, i) => { s += (y - o.target[i]) ** 2; }); return 0.5 * s; },
      grad: p => { const o = obs(p); let g = [0, 0]; o.y.forEach((y, i) => { g = V.add(g, V.mul(o.J[i], y - o.target[i])); }); return g; },
      hess: p => {
        const o = obs(p); let H = [[0, 0], [0, 0]];
        o.y.forEach((y, i) => { H = M.add(H, M.add(M.outer(o.J[i], o.J[i]), M.scale(o.H[i], y - o.target[i]))); });
        return H;
      },
    };
  }

  // ---------- landscapes ----------
  function valley(alpha, phiDeg) {
    const p = phiDeg * DEG, c = Math.cos(p), s = Math.sin(p), l1 = 1, l2 = alpha * alpha;
    const H = [[l1 * c * c + l2 * s * s, (l1 - l2) * c * s], [(l1 - l2) * c * s, l1 * s * s + l2 * c * c]];
    return {
      key: 'valley', f: x => 0.5 * V.dot(x, M.vec(H, x)), grad: x => M.vec(H, x), hess: () => H,
      dom: [[-2, 2], [-2, 2]], start: [-1.6, 1.1], minima: [[0, 0]], labels: ['x₁', 'x₂'], eta: 0.025, lr: 0.1,
    };
  }
  const rosenbrock = () => ({
    key: 'rosenbrock',
    f: x => (1 - x[0]) ** 2 + 100 * (x[1] - x[0] * x[0]) ** 2,
    grad: x => [-2 * (1 - x[0]) - 400 * x[0] * (x[1] - x[0] * x[0]), 200 * (x[1] - x[0] * x[0])],
    hess: x => [[2 - 400 * x[1] + 1200 * x[0] * x[0], -400 * x[0]], [-400 * x[0], 200]],
    dom: [[-2, 2], [-1, 3]], start: [-1.2, 1], minima: [[1, 1]], labels: ['x₁', 'x₂'], eta: 0.001, lr: 0.1,
  });
  const doubleWell = () => ({
    key: 'doublewell',
    f: x => 0.25 * (x[0] * x[0] - 1) ** 2 + x[1] * x[1],
    grad: x => [x[0] * (x[0] * x[0] - 1), 2 * x[1]],
    hess: x => [[3 * x[0] * x[0] - 1, 0], [0, 2]],
    dom: [[-2, 2], [-2, 2]], start: [0.3, 1.2], minima: [[-1, 0], [1, 0]], saddles: [[0, 0]], labels: ['x₁', 'x₂'], eta: 0.3, lr: 0.1,
  });
  function projectile(mode) {
    const ls = leastSquares(mode === 'landing' ? obsLanding : obsApex);
    return Object.assign(ls, {
      key: 'projectile', mode, dom: [[5, 35], [5, 85]], start: [15, 35], labels: ['v (m/s)', 'a (deg)'],
      minima: mode === 'landing' ? [] : [[V_TRUE, A_TRUE]], eta: 0.1, lr: 0.5,
      // curve of minima for the landing-only loss, v^2 sin 2a = g R*
      minCurve: mode === 'landing' ? a => Math.sqrt(G * R_TRUE / Math.sin(2 * a * DEG)) : null,
    });
  }

  // ---------- seeded Gaussian noise, a pure function of (seed, call index, component) ----------
  function uniform(seed, n, j) {
    let t = (seed * 2654435761 + n * 40503 + j * 9973 + 0x6D2B79F5) >>> 0;
    t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return (((t ^ (t >>> 14)) >>> 0) + 0.5) / 4294967296;
  }
  function gauss(seed, n, j) {
    const u1 = uniform(seed, n, 2 * j), u2 = uniform(seed, n, 2 * j + 1);
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }

  // ---------- optimizers ----------
  // Each optimizer offers propose(), which computes its next step without changing state,
  // and commit(p), which takes that step. A proposal carries the quadratic model the optimizer uses:
  // q(x + d) = gm.d + d.B.d / 2, with stationary point c.
  function base(kind, land, x0, opt) {
    return {
      kind, land, opt, x: x0.slice(), k: 0, nf: 0, ng: 0, nh: 0, status: 'running',
      hist: [{ x: x0.slice(), f: land.f(x0) }],
      gradAt(x, n) {
        const g = land.grad(x);
        if (!opt.sigma) return g;
        const s = opt.sigma * opt.noiseScale;
        return [g[0] + s * gauss(opt.seed, n, 0), g[1] + s * gauss(opt.seed, n, 1)];
      },
      finish(xNew) {
        this.x = xNew; this.k += 1;
        const f = land.f(xNew);
        this.hist.push({ x: xNew.slice(), f });
        if (!isFinite(f) || !isFinite(xNew[0]) || !isFinite(xNew[1])) this.status = 'diverged';
        else if (outside(land.dom, xNew)) this.status = 'left the plot';
        else if (this.k >= opt.maxSteps) this.status = 'step limit';
      },
    };
  }
  function outside(dom, x) {
    const wx = dom[0][1] - dom[0][0], wy = dom[1][1] - dom[1][0];
    return x[0] < dom[0][0] - wx || x[0] > dom[0][1] + wx || x[1] < dom[1][0] - wy || x[1] > dom[1][1] + wy;
  }
  function stationary(g, H) { return M.det(H) !== 0 ? V.mul(M.vec(M.inv(H), g), -1) : null; }

  function GD(land, x0, opt) {
    const o = base('gd', land, x0, opt);
    o.propose = function () {
      const g = this.gradAt(this.x, this.ng + 1), eta = opt.eta, d = V.mul(g, -eta);
      return { g, d, xNew: V.add(this.x, d), model: { gm: g, B: [[1 / eta, 0], [0, 1 / eta]] } };
    };
    o.commit = function (p) { this.ng += 1; if (V.norm(p.g) < 1e-12 && !opt.sigma) this.status = 'stationary point'; this.finish(p.xNew); };
    return o;
  }

  function Adam(land, x0, opt) {
    const o = base('adam', land, x0, opt);
    const b1 = 0.9, b2 = 0.999, eps = 1e-8;
    o.m = [0, 0]; o.v = [0, 0];
    o.propose = function () {
      const g = this.gradAt(this.x, this.ng + 1), t = this.k + 1, lr = opt.lr;
      const m = [b1 * this.m[0] + (1 - b1) * g[0], b1 * this.m[1] + (1 - b1) * g[1]];
      const v = [b2 * this.v[0] + (1 - b2) * g[0] ** 2, b2 * this.v[1] + (1 - b2) * g[1] ** 2];
      const mh = V.mul(m, 1 / (1 - b1 ** t)), vh = V.mul(v, 1 / (1 - b2 ** t));
      const den = [Math.sqrt(vh[0]) + eps, Math.sqrt(vh[1]) + eps];
      const d = [-lr * mh[0] / den[0], -lr * mh[1] / den[1]];
      return { g, d, m, v, mh, vh, xNew: V.add(this.x, d), model: { gm: mh, B: [[den[0] / lr, 0], [0, den[1] / lr]] } };
    };
    o.commit = function (p) { this.ng += 1; this.m = p.m; this.v = p.v; this.finish(p.xNew); };
    return o;
  }

  function Newton(land, x0, opt) {
    const o = base('newton', land, x0, opt);
    o.propose = function () {
      const g = this.gradAt(this.x, this.ng + 1), H = land.hess(this.x);
      const scale = Math.abs(H[0][0]) + Math.abs(H[1][1]) + Math.abs(H[0][1]);
      if (Math.abs(M.det(H)) < 1e-12 * scale * scale) return { g, H, singular: true, d: [0, 0], xNew: this.x.slice(), model: null };
      const d = stationary(g, H);
      return { g, H, d, xNew: V.add(this.x, d), model: { gm: g, B: H } };
    };
    o.commit = function (p) {
      this.ng += 1; this.nh += 1;
      if (p.singular) { this.status = 'Hessian singular'; return; }
      if (V.norm(p.g) < 1e-12 && !opt.sigma) { this.status = 'stationary point'; return; }
      this.finish(p.xNew);
    };
    return o;
  }

  function LBFGS(land, x0, opt) {
    const o = base('lbfgs', land, x0, opt);
    o.pairs = [];
    o.g = o.gradAt(o.x, 1); o.ng = 1; o.nf = 1; o.fx = land.f(o.x);
    // H_k q by the two-loop recursion; with no pairs, H_0 = I / |g| so the first trial step has length 1
    o.applyH = function (q) {
      const P = this.pairs, al = [];
      let r = q.slice();
      for (let i = P.length - 1; i >= 0; i--) { al[i] = P[i].rho * V.dot(P[i].s, r); r = V.sub(r, V.mul(P[i].y, al[i])); }
      const last = P[P.length - 1];
      const gamma = last ? V.dot(last.s, last.y) / V.dot(last.y, last.y) : 1 / Math.max(V.norm(this.g), 1e-12);
      r = V.mul(r, gamma);
      for (let i = 0; i < P.length; i++) { const b = P[i].rho * V.dot(P[i].y, r); r = V.add(r, V.mul(P[i].s, al[i] - b)); }
      return r;
    };
    o.Hmat = function () { const c1 = this.applyH([1, 0]), c2 = this.applyH([0, 1]); return [[c1[0], c2[0]], [c1[1], c2[1]]]; };
    o.propose = function () {
      const g = this.g;
      if (V.norm(g) < 1e-12 && !opt.sigma) return { g, done: true };
      let reset = false, d = V.mul(this.applyH(g), -1);
      if (V.dot(g, d) >= 0) { reset = true; d = V.mul(g, -1 / Math.max(V.norm(g), 1e-12)); }
      const Hk = reset ? [[1 / V.norm(g), 0], [0, 1 / V.norm(g)]] : this.Hmat();
      const c1 = 1e-4, slope = V.dot(g, d), trials = [];
      let t = 1, xt, ft, ok = false;
      for (let i = 0; i < 40; i++) {
        xt = V.add(this.x, V.mul(d, t)); ft = land.f(xt); trials.push(xt);
        if (isFinite(ft) && ft <= this.fx + c1 * t * slope) { ok = true; break; }
        t *= 0.5;
      }
      return { g, d, t, ok, reset, trials, xNew: ok ? xt : this.x.slice(), fNew: ok ? ft : this.fx,
               model: { gm: g, B: M.inv(Hk) }, Hk };
    };
    o.commit = function (p) {
      if (p.done) { this.status = 'stationary point'; return; }
      this.nf += p.trials.length;
      if (p.reset) this.pairs = [];
      if (!p.ok) { this.status = 'line search failed'; this.k += 1; this.hist.push({ x: this.x.slice(), f: this.fx }); return; }
      const gNew = this.gradAt(p.xNew, this.ng + 1); this.ng += 1;
      const s = V.sub(p.xNew, this.x), y = V.sub(gNew, this.g), sy = V.dot(s, y);
      if (sy > 1e-10 * V.norm(s) * V.norm(y)) {
        this.pairs.push({ s, y, rho: 1 / sy });
        if (this.pairs.length > opt.memory) this.pairs.shift();
      }
      this.g = gNew; this.fx = p.fNew;
      this.finish(p.xNew);
    };
    return o;
  }

  const OPTIMIZERS = { gd: GD, adam: Adam, newton: Newton, lbfgs: LBFGS };

  // ---------- the tape for widget 1: L(v, a) = |apex(v, a) - apex*|^2 / 2, with a in degrees ----------
  function tape(v, adeg) {
    const th = adeg * DEG, s = Math.sin(th), c = Math.cos(th), q = v * v, p = q * s;
    const x = p * c / G, z = p * s / (2 * G), r1 = x - APEX_TRUE[0], r2 = z - APEX_TRUE[1];
    const L = 0.5 * (r1 * r1 + r2 * r2);
    const val = [v, adeg, th, s, c, q, p, x, z, r1, r2, L];
    function forward(dv, da) {
      const dth = da * DEG, ds = c * dth, dc = -s * dth, dq = 2 * v * dv, dp = dq * s + q * ds;
      const dx = (dp * c + p * dc) / G, dz = (dp * s + p * ds) / (2 * G);
      return [dv, da, dth, ds, dc, dq, dp, dx, dz, dx, dz, r1 * dx + r2 * dz];
    }
    function reverse() {
      const bL = 1, br2 = bL * r2, br1 = bL * r1, bz = br2, bx = br1;
      const bp = bx * c / G + bz * s / (2 * G), bq = bp * s, bc = bx * p / G, bs = bp * q + bz * p / (2 * G);
      const bth = bs * c - bc * s, ba = bth * DEG, bv = 2 * v * bq;
      return [bv, ba, bth, bs, bc, bq, bp, bx, bz, br1, br2, bL];
    }
    return { val, forward, reverse };
  }

  return { G, DEG, V_TRUE, A_TRUE, APEX_TRUE, R_TRUE, V, M, apex, landing, valley, rosenbrock, doubleWell, projectile, OPTIMIZERS, tape, gauss };
})();
if (typeof module !== 'undefined') module.exports = GOCore;

/* ---------------- user interface (browser only) ---------------- */
if (typeof document !== 'undefined') (function () {
  'use strict';
  const C = GOCore, V = C.V, M = C.M;
  const KINDS = ['gd', 'adam', 'newton', 'lbfgs'];
  const NAMES = { gd: 'Gradient descent', adam: 'Adam', newton: 'Newton', lbfgs: 'L-BFGS' };
  const STOPPED = {
    'stationary point': 'The gradient is zero, so the optimizer has stopped at a stationary point.',
    'Hessian singular': 'The Hessian is singular, so the Newton step is undefined.',
    'line search failed': 'No trial step lowered the loss enough, so the line search failed.',
    'left the plot': 'The iterate left the plotted region.',
    'diverged': 'The loss overflowed.',
    'step limit': 'The optimizer reached the limit of 500 steps.',
  };
  const SHAPES = { gd: d3.symbolCircle, adam: d3.symbolSquare, newton: d3.symbolTriangle, lbfgs: d3.symbolDiamond };

  function fmt(x, p) {
    p = p || 4;
    if (x === undefined || x === null) return '';
    if (!isFinite(x)) return String(x);
    if (x === 0) return '0';
    const a = Math.abs(x);
    if (a >= 1e5 || a < 1e-3) return x.toExponential(2);
    return String(Number(x.toPrecision(p)));
  }
  const fv = (a, p) => '(' + fmt(a[0], p) + ', ' + fmt(a[1], p) + ')';
  function h(tag, attrs, parent, text) {
    const e = document.createElement(tag);
    if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }

  // a plot with linear scales over a 2D domain, drawn into an SVG with a fixed viewBox
  function makePlot(parent, W, H, mg, dom, labels) {
    const svg = d3.select(parent).append('svg').attr('class', 'go-svg').attr('viewBox', `0 0 ${W} ${H}`);
    const pw = W - mg.l - mg.r, ph = H - mg.t - mg.b;
    const sx = d3.scaleLinear().domain(dom[0]).range([0, pw]);
    const sy = d3.scaleLinear().domain(dom[1]).range([ph, 0]);
    const root = svg.append('g').attr('transform', `translate(${mg.l},${mg.t})`);
    const id = 'goclip' + Math.random().toString(36).slice(2);
    svg.append('defs').append('clipPath').attr('id', id).append('rect').attr('width', pw).attr('height', ph);
    root.append('rect').attr('class', 'go-frame').attr('width', pw).attr('height', ph);
    const ax = root.append('g').attr('class', 'go-axis');
    ax.append('g').attr('transform', `translate(0,${ph})`).call(d3.axisBottom(sx).ticks(5).tickSizeOuter(0));
    ax.append('g').call(d3.axisLeft(sy).ticks(5).tickSizeOuter(0));
    ax.append('text').attr('x', pw / 2).attr('y', ph + mg.b - 4).attr('text-anchor', 'middle').text(labels[0]);
    ax.append('text').attr('transform', `translate(${-mg.l + 12},${ph / 2}) rotate(-90)`).attr('text-anchor', 'middle').text(labels[1]);
    const g = root.append('g').attr('clip-path', `url(#${id})`);
    return { svg, root, g, sx, sy, pw, ph, mg, toPx: p => [sx(p[0]), sy(p[1])] };
  }

  // contour lines of f over the plot's domain, as SVG path strings
  function contourPaths(P, f, n, levels) {
    const d0 = P.sx.domain(), d1 = P.sy.domain(), vals = new Array(n * n);
    for (let j = 0; j < n; j++) {
      const y = d1[1] - (j + 0.5) * (d1[1] - d1[0]) / n;
      for (let i = 0; i < n; i++) vals[i + j * n] = f([d0[0] + (i + 0.5) * (d0[1] - d0[0]) / n, y]);
    }
    if (typeof levels === 'number') {
      const pos = vals.filter(v => v > 0 && isFinite(v)).sort((a, b) => a - b);
      const lo = Math.log(pos[Math.floor(0.005 * pos.length)]), hi = Math.log(pos[Math.floor(0.97 * pos.length)]);
      levels = d3.range(levels).map(i => Math.exp(lo + (hi - lo) * i / (levels - 1)));
    }
    // d3.contours closes each region along the grid border, so segments that lie on the border are skipped
    const onEdge = (p, q, k) => Math.abs(p[k] - q[k]) < 1e-9 && (p[k] < 1e-9 || p[k] > n - 1e-9);
    return d3.contours().size([n, n]).thresholds(levels)(vals).map(mp => {
      let d = '';
      mp.coordinates.forEach(poly => poly.forEach(ring => ring.forEach((p, i) => {
        const q = ring[i - 1], X = (p[0] * P.pw / n).toFixed(1), Y = (p[1] * P.ph / n).toFixed(1);
        d += (!q || onEdge(p, q, 0) || onEdge(p, q, 1) ? 'M' : 'L') + X + ',' + Y;
      })));
      return d;
    }).filter(Boolean);
  }

  function arrow(g, p0, p1, cls, head) {
    head = head || 8;
    const dx = p1[0] - p0[0], dy = p1[1] - p0[1], L = Math.hypot(dx, dy);
    if (!(L > 2)) return;
    const ux = dx / L, uy = dy / L, hh = Math.min(head, 0.6 * L), b = [p1[0] - ux * hh, p1[1] - uy * hh];
    g.append('line').attr('class', 'go-arrow ' + cls).attr('x1', p0[0]).attr('y1', p0[1]).attr('x2', b[0]).attr('y2', b[1]);
    g.append('path').attr('class', 'go-head ' + cls)
      .attr('d', `M${p1[0]},${p1[1]}L${b[0] - uy * hh * 0.5},${b[1] + ux * hh * 0.5}L${b[0] + uy * hh * 0.5},${b[1] - ux * hh * 0.5}Z`);
  }
  function star(g, p, cls, r) {
    g.append('path').attr('class', cls).attr('transform', `translate(${p[0]},${p[1]})`).attr('d', d3.symbol(d3.symbolStar, (r || 7) ** 2 * 1.6)());
  }
  function arcPoints(v, adeg) {
    const t = adeg * C.DEG, T = 2 * v * Math.sin(t) / C.G;
    return d3.range(61).map(i => { const s = T * i / 60; return [v * Math.cos(t) * s, v * Math.sin(t) * s - 0.5 * C.G * s * s]; });
  }

  /* ================= widget 1: the tape ================= */
  function initTape(root) {
    const st = { v: 15, a: 35, mode: 'fwd-v', step: 0 };
    const DOM = [[5, 35], [5, 85]];
    const ROWS = [
      ['v', 'input', "v̇ = seed", "v̄ = 2v·q̄"],
      ['a', 'input, degrees', "ȧ = seed", "ā = θ̄·π/180"],
      ['θ = a·π/180', '', "θ̇ = ȧ·π/180", "θ̄ = s̄·cos θ − c̄·sin θ"],
      ['s = sin θ', '', "ṡ = cos θ · θ̇", "s̄ = p̄·q + z̄·p/(2g)"],
      ['c = cos θ', '', "ċ = −sin θ · θ̇", "c̄ = x̄·p/g"],
      ['q = v²', '', "q̇ = 2v·v̇", "q̄ = p̄·s"],
      ['p = q·s', '', "ṗ = q̇·s + q·ṡ", "p̄ = x̄·c/g + z̄·s/(2g)"],
      ['x = p·c/g', 'top of arc', "ẋ = (ṗ·c + p·ċ)/g", "x̄ = r̄₁"],
      ['z = p·s/(2g)', 'top of arc', "ż = (ṗ·s + p·ṡ)/(2g)", "z̄ = r̄₂"],
      ['r₁ = x − x*', 'residual', "ṙ₁ = ẋ", "r̄₁ = L̄·r₁"],
      ['r₂ = z − z*', 'residual', "ṙ₂ = ż", "r̄₂ = L̄·r₂"],
      ['L = (r₁² + r₂²)/2', 'loss', "L̇ = r₁·ṙ₁ + r₂·ṙ₂", "L̄ = 1"],
    ];
    const ctl = h('div', { class: 'go-controls' }, root);
    const modeBtns = {};
    [['fwd-v', 'Forward, seed v'], ['fwd-a', 'Forward, seed a'], ['rev', 'Reverse']].forEach(([k, t]) => {
      modeBtns[k] = h('button', { class: 'go-btn' }, ctl, t);
      modeBtns[k].onclick = () => { st.mode = k; st.step = 0; draw(); };
    });
    h('span', { class: 'go-sep' }, ctl);
    const bNext = h('button', { class: 'go-btn go-primary' }, ctl, 'Next row');
    const bAll = h('button', { class: 'go-btn' }, ctl, 'All rows');
    const bReset = h('button', { class: 'go-btn' }, ctl, 'Reset');
    const maxStep = () => (st.mode === 'rev' ? 13 : 12);
    bNext.onclick = () => { st.step = Math.min(st.step + 1, maxStep()); draw(); };
    bAll.onclick = () => { st.step = maxStep(); draw(); };
    bReset.onclick = () => { st.step = 0; draw(); };
    const status = h('div', { class: 'go-status' }, root);
    const grid = h('div', { class: 'go-grid3' }, root);
    const pPar = h('div', { class: 'go-panel' }, grid), pPhy = h('div', { class: 'go-panel' }, grid), pTab = h('div', { class: 'go-panel go-scroll' }, grid);
    h('div', { class: 'go-cap' }, pPar, 'Parameters. Contours of L, target ★, drag the dot.');
    h('div', { class: 'go-cap' }, pPhy, 'Physics. Solid arc from (v, a), dashed arc from the true values.');
    h('div', { class: 'go-cap' }, pTab, 'Tape');

    const P = makePlot(pPar, 330, 300, { l: 46, r: 10, t: 8, b: 34 }, DOM, ['v (m/s)', 'a (degrees)']);
    const land = C.projectile('apex');
    P.g.append('g').selectAll('path').data(contourPaths(P, land.f, 140, 14)).join('path').attr('class', 'go-contour').attr('d', d => d);
    star(P.g, P.toPx([C.V_TRUE, C.A_TRUE]), 'go-fill-ink');
    const pDyn = P.g.append('g');
    const dot = P.root.append('circle').attr('r', 7).attr('class', 'go-handle');
    dot.call(d3.drag().on('drag', ev => {
      st.v = Math.max(DOM[0][0], Math.min(DOM[0][1], P.sx.invert(ev.x)));
      st.a = Math.max(DOM[1][0], Math.min(DOM[1][1], P.sy.invert(ev.y)));
      draw();
    }));

    const Q = makePlot(pPhy, 400, 236, { l: 34, r: 8, t: 8, b: 34 }, [[0, 45], [0, 24.4]], ['x (m)', 'z (m)']);
    Q.g.append('path').attr('class', 'go-arc go-dashed').attr('d', d3.line().x(p => Q.sx(p[0])).y(p => Q.sy(p[1]))(arcPoints(C.V_TRUE, C.A_TRUE)));
    star(Q.g, Q.toPx(C.APEX_TRUE), 'go-fill-ink');
    const qDyn = Q.g.append('g');

    const tbl = h('table', { class: 'go-tape' }, pTab);
    const thead = h('tr', null, h('thead', null, tbl));
    ['#', 'operation', 'value', ''].forEach(t => h('th', null, thead, t));
    const tb = h('tbody', null, tbl);
    const trs = ROWS.map((r, i) => {
      const tr = h('tr', null, tb);
      h('td', null, tr, String(i + 1));
      const op = h('td', { class: 'op' }, tr, r[0]);
      if (r[1]) h('span', { class: 'go-note' }, op, '  ' + r[1]);
      return { tr, val: h('td', null, tr), der: h('td', null, tr) };
    });
    const check = h('div', { class: 'go-check' }, pTab);

    function draw() {
      Object.keys(modeBtns).forEach(k => modeBtns[k].classList.toggle('on', k === st.mode));
      const T = C.tape(st.v, st.a), rev = st.mode === 'rev';
      const seed = st.mode === 'fwd-v' ? [1, 0] : [0, 1];
      const tan = rev ? null : T.forward(seed[0], seed[1]), adj = rev ? T.reverse() : null;
      thead.lastChild.textContent = rev ? 'adjoint' : 'tangent';
      bNext.disabled = st.step >= maxStep();
      // which rows are filled
      let cur = -1;
      trs.forEach((r, i) => {
        let showVal, showDer;
        if (rev) { showVal = st.step >= 1; showDer = st.step >= 1 && i >= 12 - (st.step - 1); if (st.step >= 2 && i === 13 - st.step) cur = i; }
        else { showVal = showDer = i < st.step; if (i === st.step - 1) cur = i; }
        r.val.textContent = showVal ? fmt(T.val[i]) : '';
        r.der.textContent = showDer ? fmt(rev ? adj[i] : tan[i]) : '';
        r.tr.classList.toggle('cur', i === cur);
      });
      // status line
      const L = T.val[11], gL = rev ? [adj[0], adj[1]] : null;
      if (st.step === 0) status.textContent = rev
        ? 'Reverse mode. The first sweep records every value on the tape, and the second sweep runs up the tape from L̄ = 1.'
        : `Forward mode. The seed (v̇, ȧ) = (${seed[0]}, ${seed[1]}) asks how L changes when ${seed[0] ? 'v' : 'a'} grows. Each row computes its value and its tangent together.`;
      else if (rev && st.step === 1) status.textContent = `Forward sweep done. The tape holds all 12 values, and L = ${fmt(L)} m².`;
      else if (cur >= 0) {
        const f = rev ? ROWS[cur][3] : ROWS[cur][2], d = rev ? adj[cur] : tan[cur];
        status.textContent = `Row ${cur + 1}. ${f} = ${fmt(d)}`;
      }
      if (st.step === maxStep()) {
        status.textContent += rev
          ? `. The gradient is ∇L = (v̄, ā) = ${fv(gL)}, both components from one sweep.`
          : `. One sweep gives one directional derivative, ∂L/∂${seed[0] ? 'v' : 'a'} = ${fmt(tan[11])}.`;
      }
      // finite-difference check after a full sweep
      const hstep = 1e-3, fd = [(land.f([st.v + hstep, st.a]) - land.f([st.v - hstep, st.a])) / (2 * hstep),
        (land.f([st.v, st.a + hstep]) - land.f([st.v, st.a - hstep])) / (2 * hstep)];
      check.textContent = st.step === maxStep()
        ? (rev ? `Central differences with h = 0.001 give ${fv(fd, 7)}, and AD gives ${fv(gL, 7)}.`
               : `A central difference with h = 0.001 gives ${fmt(fd[seed[0] ? 0 : 1], 7)}, and AD gives ${fmt(tan[11], 7)}.`)
        : '';

      // parameter panel
      const x0 = P.toPx([st.v, st.a]);
      dot.attr('cx', x0[0]).attr('cy', x0[1]);
      pDyn.selectAll('*').remove();
      if (!rev && st.step >= 1) arrow(pDyn, x0, [x0[0] + seed[0] * 42, x0[1] - seed[1] * 42], 'go-ink', 8);
      if (rev && st.step === maxStep()) {
        const gp = [P.sx(st.v - gL[0]) - P.sx(st.v), P.sy(st.a - gL[1]) - P.sy(st.a)], n = Math.hypot(gp[0], gp[1]);
        if (n > 0) arrow(pDyn, x0, [x0[0] + 52 * gp[0] / n, x0[1] + 52 * gp[1] / n], 'go-ink', 9);
        pDyn.append('text').attr('class', 'go-lbl').attr('x', x0[0] + 52 * gp[0] / n + 6).attr('y', x0[1] + 52 * gp[1] / n).text('−∇L');
      }
      // physics panel
      qDyn.selectAll('*').remove();
      const line = d3.line().x(p => Q.sx(p[0])).y(p => Q.sy(p[1]));
      qDyn.append('path').attr('class', 'go-arc').attr('d', line(arcPoints(st.v, st.a)));
      const top = C.apex(st.v, st.a), tp = Q.toPx(top);
      if (!rev && st.step >= 9) {
        const dv = seed[0] * 2, da = seed[1] * 5, top2 = C.apex(st.v + dv, st.a + da);
        qDyn.append('path').attr('class', 'go-arc go-dotted').attr('d', line(arcPoints(st.v + dv, st.a + da)));
        const pred = [top[0] + tan[7] * (dv + da), top[1] + tan[8] * (dv + da)];
        arrow(qDyn, tp, Q.toPx(pred), 'go-accent', 8);
        qDyn.append('circle').attr('class', 'go-hollow').attr('r', 4).attr('cx', Q.sx(top2[0])).attr('cy', Q.sy(top2[1]));
        qDyn.append('text').attr('class', 'go-lbl').attr('x', Q.sx(pred[0]) + 6).attr('y', Q.sy(pred[1]) - 4)
          .text(seed[0] ? 'J·δθ for δv = 2 m/s' : 'J·δθ for δa = 5°');
      }
      if (rev && st.step >= 6) {
        arrow(qDyn, tp, Q.toPx(C.APEX_TRUE), 'go-accent', 8);
        qDyn.append('text').attr('class', 'go-lbl').attr('x', (tp[0] + Q.sx(C.APEX_TRUE[0])) / 2 + 6).attr('y', (tp[1] + Q.sy(C.APEX_TRUE[1])) / 2).text('−r = −(x̄, z̄)');
      }
      qDyn.append('circle').attr('class', 'go-fill-ink').attr('r', 4).attr('cx', tp[0]).attr('cy', tp[1]);
    }
    draw();
  }

  /* ================= widget 2: four optimizers ================= */
  function initLab(root) {
    const st = { land: 'valley', alpha: 8, phi: 0, mode: 'apex', memory: 5, sigma: 0, focus: 'adam', timer: null, base: null,
                 view: typeof Plotly !== 'undefined' ? 'surface' : 'contours' };
    const rot = (x, p) => { const c = Math.cos(p * C.DEG), s = Math.sin(p * C.DEG); return [c * x[0] - s * x[1], s * x[0] + c * x[1]]; };
    function landscape() {
      if (st.land === 'valley') return C.valley(st.alpha, st.phi);
      if (st.land === 'rosenbrock') return C.rosenbrock();
      if (st.land === 'doublewell') return C.doubleWell();
      return C.projectile(st.mode);
    }

    // controls
    const c1 = h('div', { class: 'go-controls' }, root);
    const lab = (parent, text) => { const l = h('label', null, parent); h('span', null, l, text); return l; };
    const selLand = h('select', null, lab(c1, 'Loss'));
    [['valley', 'Narrow valley'], ['rosenbrock', 'Rosenbrock'], ['doublewell', 'Double well'], ['projectile', 'Projectile']].forEach(([k, t]) => h('option', { value: k }, selLand, t));
    const wAlpha = lab(c1, 'α'), inAlpha = h('input', { type: 'range', min: 1, max: 10, step: 0.5, value: st.alpha }, wAlpha), oAlpha = h('output', null, wAlpha);
    const wPhi = lab(c1, 'rotation'), inPhi = h('input', { type: 'range', min: 0, max: 90, step: 5, value: 0 }, wPhi), oPhi = h('output', null, wPhi);
    const wObs = lab(c1, 'observe'), selObs = h('select', null, wObs);
    [['apex', 'top of the arc'], ['landing', 'landing distance']].forEach(([k, t]) => h('option', { value: k }, selObs, t));
    const c2 = h('div', { class: 'go-controls' }, root);
    const wEta = lab(c2, 'GD η'), inEta = h('input', { type: 'range', min: -4, max: 0, step: 'any' }, wEta), oEta = h('output', null, wEta);
    const wLr = lab(c2, 'Adam lr'), inLr = h('input', { type: 'range', min: -3, max: 0.5, step: 'any' }, wLr), oLr = h('output', null, wLr);
    const wMem = lab(c2, 'L-BFGS memory m'), inMem = h('input', { type: 'range', min: 1, max: 5, step: 1, value: 5 }, wMem), oMem = h('output', null, wMem);
    const wSig = lab(c2, 'gradient noise'), inSig = h('input', { type: 'range', min: 0, max: 0.2, step: 0.01, value: 0 }, wSig), oSig = h('output', null, wSig);
    const c3 = h('div', { class: 'go-controls' }, root);
    h('span', { class: 'go-lab' }, c3, 'View');
    const viewBtns = {};
    [['surface', 'Surface'], ['contours', 'Contours']].forEach(([k, t]) => {
      const b = h('button', { class: 'go-btn' }, c3, t);
      b.onclick = () => { st.view = k; applyView(); draw(); };
      if (k === 'surface' && typeof Plotly === 'undefined') b.disabled = true;
      viewBtns[k] = b;
    });
    h('span', { class: 'go-sep' }, c3);
    h('span', { class: 'go-lab' }, c3, 'Bowl of');
    const focusBtns = {};
    KINDS.forEach(k => {
      const b = h('button', { class: 'go-btn go-chip' }, c3);
      const sw = d3.select(b).append('svg').attr('width', 14).attr('height', 14).attr('class', 'go-swatch');
      sw.append('path').attr('transform', 'translate(7,7)').attr('d', d3.symbol(SHAPES[k], 64)()).attr('class', 'go-mark-' + k);
      h('span', null, b, NAMES[k]);
      b.onclick = () => { st.focus = k; draw(); };
      focusBtns[k] = b;
    });
    h('span', { class: 'go-sep' }, c3);
    const bStep = h('button', { class: 'go-btn go-primary' }, c3, 'Step');
    const bRun = h('button', { class: 'go-btn' }, c3, 'Run');
    const bReset = h('button', { class: 'go-btn' }, c3, 'Reset');

    const grid = h('div', { class: 'go-grid2' }, root);
    const pPar = h('div', { class: 'go-panel' }, grid), right = h('div', { class: 'go-col' }, grid);
    const capPar = h('div', { class: 'go-cap' }, pPar);
    const surf = h('div', { class: 'go-surf' }, pPar);
    let S = null;
    const pLoss = h('div', { class: 'go-panel' }, right), pInfo = h('div', { class: 'go-panel go-info' }, right);
    h('div', { class: 'go-cap' }, pLoss, 'Loss against step, log scale');
    const pPhy = h('div', { class: 'go-panel' }, root);
    h('div', { class: 'go-cap' }, pPhy, 'Physics. Each optimizer\'s current arc, and the true arc dashed.');
    const tbl = h('table', { class: 'go-table' }, h('div', { class: 'go-panel go-scroll' }, root));
    const tip = h('div', { class: 'go-tip' }, root);

    let land, P, pStatic, pDyn, handle, LP, Q;
    const lossPlot = { W: 420, H: 230, mg: { l: 52, r: 10, t: 8, b: 32 } };

    function buildPlots() {
      pPar.querySelectorAll(':scope > svg').forEach(e => e.remove());
      P = makePlot(pPar, 430, 410, { l: 48, r: 10, t: 8, b: 36 }, land.dom, land.labels);
      pStatic = P.g.append('g'); pDyn = P.g.append('g');
      handle = P.root.append('circle').attr('r', 8).attr('class', 'go-handle go-start');
      handle.call(d3.drag().on('drag', ev => {
        const x = [P.sx.invert(ev.x), P.sy.invert(ev.y)];
        const d = land.dom;
        x[0] = Math.max(d[0][0], Math.min(d[0][1], x[0])); x[1] = Math.max(d[1][0], Math.min(d[1][1], x[1]));
        st.base = st.land === 'valley' ? rot(x, -st.phi) : x;
        resetRuns();
      }));
      P.svg.on('mousemove', ev => hoverPar(ev)).on('mouseleave', () => { tip.style.display = 'none'; });
      pPhy.style.display = st.land === 'projectile' ? '' : 'none';
      pPhy.querySelectorAll('svg').forEach(e => e.remove());
      if (st.land === 'projectile') Q = makePlot(pPhy, 760, 250, { l: 40, r: 10, t: 8, b: 34 }, [[0, 60], [0, 17.6]], ['x (m)', 'z (m)']);
    }
    function drawStatic() {
      pStatic.selectAll('*').remove();
      pStatic.selectAll('path').data(contourPaths(P, land.f, 150, 15)).join('path').attr('class', 'go-contour').attr('d', d => d);
      (land.minima || []).forEach(m => star(pStatic, P.toPx(m), 'go-fill-ink'));
      (land.saddles || []).forEach(s => pStatic.append('path').attr('class', 'go-ink go-x').attr('transform', `translate(${P.sx(s[0])},${P.sy(s[1])}) rotate(45)`).attr('d', d3.symbol(d3.symbolCross, 60)()));
      if (land.minCurve) {
        const pts = d3.range(9.5, 81, 0.5).map(a => [land.minCurve(a), a]).filter(p => p[0] <= 35);
        pStatic.append('path').attr('class', 'go-mincurve').attr('d', d3.line().x(p => P.sx(p[0])).y(p => P.sy(p[1]))(pts));
      }
      st.caption = {
        valley: `Parameters. L = (u₁² + α²u₂²)/2 in coordinates rotated by ${st.phi}°, minimum ★.`,
        rosenbrock: 'Parameters. L = (1 − x₁)² + 100(x₂ − x₁²)², minimum ★ at (1, 1).',
        doublewell: 'Parameters. L = (x₁² − 1)²/4 + x₂², minima ★, saddle point ×.',
        projectile: st.mode === 'apex' ? 'Parameters. L = |top of arc − observed top|²/2, true values ★ at (20 m/s, 50°).'
          : 'Parameters. L = (landing distance − observed distance)²/2. The dashed curve is v² sin 2a = gR*, where L = 0.',
      }[st.land];
      S = surfaceGrid();
      if (typeof Plotly !== 'undefined') Plotly.purge(surf);
      applyView();
      // loss plot frame
      pLoss.querySelectorAll('svg').forEach(e => e.remove());
      LP = { svg: d3.select(pLoss).append('svg').attr('class', 'go-svg').attr('viewBox', `0 0 ${lossPlot.W} ${lossPlot.H}`) };
      LP.root = LP.svg.append('g').attr('transform', `translate(${lossPlot.mg.l},${lossPlot.mg.t})`);
      LP.pw = lossPlot.W - lossPlot.mg.l - lossPlot.mg.r; LP.ph = lossPlot.H - lossPlot.mg.t - lossPlot.mg.b;
      LP.ax = LP.root.append('g').attr('class', 'go-axis'); LP.lines = LP.root.append('g'); LP.hover = LP.root.append('g');
      LP.svg.on('mousemove', ev => hoverLoss(ev)).on('mouseleave', () => { tip.style.display = 'none'; LP.hover.selectAll('*').remove(); });
    }

    function setDefaults() {
      land = landscape();
      inEta.value = Math.log10(land.eta); inLr.value = Math.log10(land.lr);
      st.base = land.start.slice();
    }
    function options() {
      const base = landscape();
      const start0 = st.land === 'valley' ? rot(base.start, st.phi) : base.start;
      return { eta: 10 ** +inEta.value, lr: 10 ** +inLr.value, memory: +inMem.value, sigma: +inSig.value,
               noiseScale: V.norm(base.grad(start0)), seed: 7, maxSteps: 500 };
    }
    function startPoint() { return st.land === 'valley' ? rot(st.base, st.phi) : st.base.slice(); }
    function resetRuns() {
      stopTimer();
      land = landscape();
      const opt = options(), x0 = startPoint();
      st.opt = {};
      KINDS.forEach(k => { st.opt[k] = C.OPTIMIZERS[k](land, x0, Object.assign({}, opt)); });
      draw();
    }
    function stepAll() {
      let any = false;
      KINDS.forEach(k => { const o = st.opt[k]; if (o.status === 'running') { o.commit(o.propose()); any = true; } });
      return any;
    }
    function stopTimer() { if (st.timer) { clearInterval(st.timer); st.timer = null; } bRun.textContent = 'Run'; }
    bStep.onclick = () => { stopTimer(); stepAll(); draw(); };
    bRun.onclick = () => {
      if (st.timer) { stopTimer(); return; }
      bRun.textContent = 'Pause';
      st.timer = setInterval(() => { if (!stepAll()) stopTimer(); draw(); }, 60);
    };
    bReset.onclick = () => resetRuns();
    function labels() {
      oAlpha.textContent = `${(+inAlpha.value).toFixed(1)}, ratio α² = ${fmt((+inAlpha.value) ** 2)}`;
      oPhi.textContent = `${inPhi.value}°`;
      oEta.textContent = fmt(10 ** +inEta.value, 2); oLr.textContent = fmt(10 ** +inLr.value, 2);
      oMem.textContent = inMem.value; oSig.textContent = (+inSig.value).toFixed(2);
      wAlpha.style.display = wPhi.style.display = st.land === 'valley' ? '' : 'none';
      wObs.style.display = st.land === 'projectile' ? '' : 'none';
    }
    selLand.onchange = () => { st.land = selLand.value; setDefaults(); labels(); buildPlots(); drawStatic(); resetRuns(); };
    selObs.onchange = () => { st.mode = selObs.value; land = landscape(); buildPlots(); drawStatic(); resetRuns(); };
    inAlpha.oninput = () => { st.alpha = +inAlpha.value; labels(); land = landscape(); drawStatic(); resetRuns(); };
    inPhi.oninput = () => { st.phi = +inPhi.value; labels(); land = landscape(); drawStatic(); resetRuns(); };
    [inEta, inLr, inMem, inSig].forEach(e => { e.oninput = () => { labels(); resetRuns(); }; });

    function applyView() {
      const s3 = st.view === 'surface';
      Object.keys(viewBtns).forEach(k => viewBtns[k].classList.toggle('on', k === st.view));
      if (P) P.svg.style('display', s3 ? 'none' : null);
      surf.style.display = s3 ? '' : 'none';
      capPar.textContent = (st.caption || '') + (s3
        ? ' Drag to rotate the surface, and use the Contours view to move the start.'
        : ' Drag the ring to move the start.');
    }

    // heights for the surface view: L itself, or log10(L + 0.01) where L spans many decades
    function surfaceGrid() {
      const log = st.land === 'rosenbrock' || st.land === 'projectile', c0 = st.land === 'projectile' ? 1 : 0.1;
      const hf = log ? (L => (L > -c0 ? Math.log10(L + c0) : NaN)) : (L => L);
      const n = 100, d = land.dom;
      const xs = d3.range(n).map(i => d[0][0] + (d[0][1] - d[0][0]) * i / (n - 1));
      const ys = d3.range(n).map(j => d[1][0] + (d[1][1] - d[1][0]) * j / (n - 1));
      // on a linear height scale the surface is capped a little above the loss at the default start, so the walls do not hide the paths
      const raw = ys.map(y => xs.map(x => hf(land.f([x, y]))));
      const flat = raw.flat().filter(isFinite), L0 = land.f(land.start);
      const zlo = d3.min(flat), zhi = log ? d3.max(flat) : Math.min(d3.max(flat), 1.6 * L0);
      // a smooth minimum with the cap, so steep walls meet the flat top without a sawtooth
      const sc = 0.04 * (zhi - zlo), Z = raw.map(r => r.map(z => zhi - sc * Math.log1p(Math.exp((zhi - z) / sc))));
      return { xs, ys, Z, hf, log, zlo, zhi, zlabel: log ? `log₁₀(L + ${c0})` : 'L' };
    }

    function draw3d(prop) {
      if (typeof Plotly === 'undefined' || !S) return;
      const cs = getComputedStyle(root), col = k => cs.getPropertyValue('--go-' + k).trim();
      const R = S.zhi - S.zlo, lift = 0.012 * R, d = land.dom;
      const inDom = p => p[0] >= d[0][0] && p[0] <= d[0][1] && p[1] >= d[1][0] && p[1] <= d[1][1];
      const traces = [{
        type: 'surface', x: S.xs, y: S.ys, z: S.Z, showscale: false, opacity: 0.85, hoverinfo: 'skip',
        colorscale: [[0, col('surf-lo')], [1, col('surf-hi')]],
        contours: { z: { show: true, start: S.zlo + R / 22, end: S.log ? S.zlo + 0.65 * R : S.zhi - 0.12 * R, size: R / 11, color: col('contour'), width: 1, project: { z: true } } },
        lighting: { ambient: 0.75, diffuse: 0.5, specular: 0.05, roughness: 0.9 },
      }];
      // the focused optimizer's quadratic model, drawn as a translucent surface through the current point
      const fo = st.opt[st.focus];
      if (prop && prop.model && fo.status === 'running') {
        const x = fo.x, Lx = land.f(x), m = prop.model.gm, B = prop.model.B;
        const Mf = p => { const dd = V.sub(p, x); return Lx + V.dot(m, dd) + 0.5 * V.dot(dd, M.vec(B, dd)); };
        // sample the bowl on a fine grid around the current point, its bottom, and the step
        const pts = [x, prop.xNew];
        if (M.det(B) !== 0) pts.push(V.sub(x, M.vec(M.inv(B), m)));
        const box = [0, 1].map(i => {
          const v = pts.map(p => p[i]).filter(isFinite), w = d[i][1] - d[i][0];
          const lo = Math.min(...v), hi = Math.max(...v), pad = Math.max(0.5 * (hi - lo), 0.15 * w);
          return [Math.max(d[i][0], lo - pad), Math.min(d[i][1], hi + pad)];
        });
        const nb = 90;
        const bx = d3.range(nb).map(i => box[0][0] + (box[0][1] - box[0][0]) * i / (nb - 1));
        const by = d3.range(nb).map(j => box[1][0] + (box[1][1] - box[1][0]) * j / (nb - 1));
        // the part of the bowl below the current height, with a small rim above it
        const ztop = Math.min(S.zhi, S.hf(Lx) + 0.12 * R);
        const bz = by.map(y => bx.map(xx => { const z = S.hf(Mf([xx, y])); return isFinite(z) && z >= S.zlo - 0.05 * R && z <= ztop ? z : null; }));
        const c = col(st.focus);
        // a wire cage in the optimizer's color, so the parts of the bowl below the loss stay readable
        const wire = (a, k) => ({ show: true, start: a[0], end: a[a.length - 1], size: (a[a.length - 1] - a[0]) / 14, color: c, width: 2 });
        traces.push({ type: 'surface', x: bx, y: by, z: bz, showscale: false, hidesurface: true, hoverinfo: 'skip',
                      colorscale: [[0, c], [1, c]], contours: { x: wire(bx), y: wire(by), z: { show: false } } });
        if (M.det(B) !== 0) {
          const cen = V.sub(x, M.vec(M.inv(B), m)), zc = S.hf(Mf(cen));
          if (inDom(cen) && isFinite(zc)) traces.push({ type: 'scatter3d', mode: 'markers', x: [cen[0]], y: [cen[1]], z: [zc], hoverinfo: 'skip',
                                                        marker: { symbol: 'x', size: 6, color: c } });
        }
        const zn = S.hf(Mf(prop.xNew)), z0 = S.hf(Lx);
        if (inDom(prop.xNew) && isFinite(zn)) traces.push({ type: 'scatter3d', mode: 'lines', x: [x[0], prop.xNew[0]], y: [x[1], prop.xNew[1]],
                                                            z: [z0 + lift, zn + lift], hoverinfo: 'skip', line: { color: c, width: 7 } });
      }
      // the four paths on the surface, broken where they leave the plotted region
      const sym3 = { gd: 'circle', adam: 'square', newton: 'cross', lbfgs: 'diamond' };
      KINDS.forEach(k => {
        const hs = st.opt[k].hist, c = col(k);
        const ok = e => inDom(e.x) && isFinite(S.hf(e.f)) && S.hf(e.f) <= S.zhi;
        traces.push({ type: 'scatter3d', mode: 'lines+markers', name: NAMES[k], connectgaps: false,
          x: hs.map(e => (ok(e) ? e.x[0] : null)), y: hs.map(e => (ok(e) ? e.x[1] : null)), z: hs.map(e => (ok(e) ? S.hf(e.f) + lift : null)),
          customdata: hs.map((e, i) => [i, fmt(e.f, 3)]), hovertemplate: NAMES[k] + ', step %{customdata[0]}<br>L = %{customdata[1]}<extra></extra>',
          line: { color: c, width: 5 }, marker: { size: 2.5, color: c } });
        const last = hs[hs.length - 1];
        if (ok(last)) traces.push({ type: 'scatter3d', mode: 'markers', x: [last.x[0]], y: [last.x[1]], z: [S.hf(last.f) + lift], hoverinfo: 'skip',
                                    marker: { symbol: sym3[k], size: 7, color: c, line: { color: col('surface'), width: 2 } } });
      });
      (land.minima || []).forEach(p => { const z = S.hf(land.f(p)); if (isFinite(z)) traces.push({ type: 'scatter3d', mode: 'markers', x: [p[0]], y: [p[1]], z: [z],
        hoverinfo: 'skip', marker: { symbol: 'diamond-open', size: 7, color: col('ink') } }); });
      if (land.minCurve) {
        const pts = d3.range(9.5, 81, 0.5).map(a => [land.minCurve(a), a]).filter(p => p[0] <= 35);
        traces.push({ type: 'scatter3d', mode: 'lines', x: pts.map(p => p[0]), y: pts.map(p => p[1]), z: pts.map(() => S.hf(0) + lift),
                      hoverinfo: 'skip', line: { color: col('ink'), width: 4, dash: 'dash' } });
      }
      const ax = (title, range) => ({ title: { text: title }, range, color: col('ink2'), gridcolor: col('line'), zerolinecolor: col('line'),
                                      showbackground: false, showspikes: false });
      const layout = {
        margin: { l: 8, r: 8, t: 0, b: 0 }, paper_bgcolor: 'rgba(0,0,0,0)', showlegend: false,
        font: { color: col('ink2'), size: 11 }, hoverlabel: { bgcolor: col('panel'), font: { color: col('ink') } },
        uirevision: [st.land, st.mode, st.alpha, st.phi].join('|'),
        scene: { xaxis: ax(land.labels[0], d[0]), yaxis: ax(land.labels[1], d[1]), zaxis: ax(S.zlabel, [S.zlo - 0.05 * R, S.zhi]),
                 aspectmode: 'manual', aspectratio: { x: 1, y: 1, z: 0.6 }, camera: { eye: { x: 1.3, y: -1.6, z: 1.45 } } },
      };
      Plotly.react(surf, traces, layout, { displayModeBar: false, responsive: true });
    }

    // the quadratic model of the focused optimizer: q(x + d) = m.d + d.B.d/2
    function bowlPaths(x, model) {
      const B = model.B, m = model.gm;
      if (!B || M.det(B) === 0) return { paths: [], c: null };
      const c = V.sub(x, M.vec(M.inv(B), m));
      const q = p => { const d = V.sub(p, x); return V.dot(m, d) + 0.5 * V.dot(d, M.vec(B, d)); };
      const qc = q(c);
      if (!(Math.abs(qc) > 0)) return { paths: [], c };
      // two ellipses for a positive-definite B; for an indefinite B, the hyperbola through x and its conjugate
      const D = -qc, definite = M.eigSym(B)[0] > 0, levels = (definite ? [qc + D / 4, qc + D] : [qc - D, qc + D]).sort((a, b) => a - b);
      return { paths: contourPaths(P, q, 90, levels), c };
    }

    function draw() {
      KINDS.forEach(k => focusBtns[k].classList.toggle('on', k === st.focus));
      const x0 = startPoint(), sp = P.toPx(x0);
      handle.attr('cx', sp[0]).attr('cy', sp[1]);
      pDyn.selectAll('*').remove();
      const line = d3.line().x(p => P.sx(p[0])).y(p => P.sy(p[1]));
      // the focused optimizer's bowl, under the trajectories
      const fo = st.opt[st.focus];
      let prop = null;
      if (fo.status === 'running') {
        prop = fo.propose();
        if (prop.model) {
          const bw = bowlPaths(fo.x, prop.model);
          pDyn.append('g').selectAll('path').data(bw.paths).join('path').attr('class', 'go-bowl go-stroke-' + st.focus).attr('d', d => d);
          if (bw.c) pDyn.append('path').attr('class', 'go-x go-stroke-' + st.focus).attr('transform', `translate(${P.sx(bw.c[0])},${P.sy(bw.c[1])}) rotate(45)`).attr('d', d3.symbol(d3.symbolCross, 70)());
        }
      }
      KINDS.forEach(k => {
        const o = st.opt[k], pts = o.hist.map(e => e.x);
        pDyn.append('path').attr('class', 'go-traj go-stroke-' + k).attr('d', line(pts));
        pDyn.append('g').selectAll('circle').data(pts.slice(0, -1)).join('circle').attr('r', 2.2).attr('class', 'go-mark-' + k)
          .attr('cx', p => P.sx(p[0])).attr('cy', p => P.sy(p[1]));
      });
      if (prop && prop.d) {
        const xp = P.toPx(fo.x), np = P.toPx(prop.xNew), L = Math.max(Math.hypot(np[0] - xp[0], np[1] - xp[1]), 36);
        if (prop.trials) prop.trials.slice(0, -1).forEach(t => pDyn.append('circle').attr('class', 'go-hollow go-stroke-' + st.focus).attr('r', 3.5).attr('cx', P.sx(t[0])).attr('cy', P.sy(t[1])));
        const gp = [P.sx(fo.x[0] - prop.g[0]) - xp[0], P.sy(fo.x[1] - prop.g[1]) - xp[1]], gn = Math.hypot(gp[0], gp[1]);
        if (gn > 0) arrow(pDyn, xp, [xp[0] + L * gp[0] / gn, xp[1] + L * gp[1] / gn], 'go-ink', 8);
        arrow(pDyn, xp, np, 'go-stroke-' + st.focus + ' go-fill-' + st.focus, 9);
      }
      KINDS.forEach(k => {
        const o = st.opt[k], p = P.toPx(o.x);
        pDyn.append('path').attr('class', 'go-cur go-mark-' + k).attr('transform', `translate(${p[0]},${p[1]})`).attr('d', d3.symbol(SHAPES[k], 90)());
      });
      drawLoss(); drawInfo(prop); drawTable(); drawPhysics();
      if (st.view === 'surface') draw3d(prop);
    }

    function drawLoss() {
      const all = [];
      KINDS.forEach(k => st.opt[k].hist.forEach(e => { if (e.f > 0 && isFinite(e.f)) all.push(e.f); }));
      const lo = Math.max(1e-16, d3.min(all) || 1e-16), hi = Math.max(d3.max(all) || 1, lo * 10);
      const nmax = Math.max(10, d3.max(KINDS, k => st.opt[k].hist.length - 1));
      LP.sx = d3.scaleLinear().domain([0, nmax]).range([0, LP.pw]);
      LP.sy = d3.scaleLog().domain([lo, hi]).range([LP.ph, 0]).clamp(true);
      LP.ax.selectAll('*').remove();
      LP.ax.append('g').attr('transform', `translate(0,${LP.ph})`).call(d3.axisBottom(LP.sx).ticks(6).tickSizeOuter(0));
      LP.ax.append('g').call(d3.axisLeft(LP.sy).ticks(5, '.0e').tickSizeOuter(0));
      LP.ax.append('text').attr('x', LP.pw / 2).attr('y', LP.ph + 28).attr('text-anchor', 'middle').text('step');
      LP.lines.selectAll('*').remove();
      KINDS.forEach(k => {
        const hs = st.opt[k].hist;
        LP.lines.append('path').attr('class', 'go-traj go-stroke-' + k)
          .attr('d', d3.line().x((e, i) => LP.sx(i)).y(e => LP.sy(Math.max(e.f, lo)))(hs));
        const last = hs[hs.length - 1];
        LP.lines.append('path').attr('class', 'go-cur go-mark-' + k).attr('transform', `translate(${LP.sx(hs.length - 1)},${LP.sy(Math.max(last.f, lo))})`).attr('d', d3.symbol(SHAPES[k], 50)());
      });
    }

    function drawInfo(prop) {
      const k = st.focus, o = st.opt[k];
      pInfo.innerHTML = '';
      h('div', { class: 'go-infohead' }, pInfo, `${NAMES[k]}, step ${o.k}`);
      if (o.status !== 'running') { h('div', null, pInfo, STOPPED[o.status] || o.status); return; }
      if (!prop) return;
      const lines = [];
      lines.push(`Gradient g = ${fv(prop.g)}.`);
      if (k === 'gd') {
        lines.push(`Step −ηg = ${fv(prop.d)}.`);
        lines.push(`The bowl is round, with curvature 1/η = ${fmt(1 / o.opt.eta)} in every direction.`);
      } else if (k === 'adam') {
        lines.push(`Averaged gradient m̂ = ${fv(prop.mh)}, and √v̂ = (${fmt(Math.sqrt(prop.vh[0]))}, ${fmt(Math.sqrt(prop.vh[1]))}).`);
        lines.push(`Step −lr·m̂/(√v̂ + ε) = ${fv(prop.d)}.`);
        lines.push(`The bowl is aligned with the axes, with curvatures (√v̂ + ε)/lr = (${fmt(prop.model.B[0][0])}, ${fmt(prop.model.B[1][1])}).`);
      } else if (k === 'newton') {
        if (prop.singular) { lines.push('The Hessian is singular, so the bowl has no bottom.'); }
        else {
          const ev = M.eigSym(prop.H);
          lines.push(`Hessian eigenvalues (${fmt(ev[0])}, ${fmt(ev[1])}).`);
          lines.push(`Step −H⁻¹g = ${fv(prop.d)}.`);
          if (ev[0] < 0) lines.push('One eigenvalue is negative, so the bowl is a saddle and the step goes to its stationary point.');
        }
      } else {
        const ev = M.eigSym(prop.model.B), evH = M.eigSym(land.hess(o.x));
        lines.push(`Stored pairs ${o.pairs.length} of ${o.opt.memory}.` + (o.pairs.length ? ' Curvature along each stored step, yᵢᵀsᵢ/sᵢᵀsᵢ = ' + o.pairs.map(p => fmt(V.dot(p.y, p.s) / V.dot(p.s, p.s), 3)).join(', ') + '.' : ''));
        lines.push(`Bowl curvatures, eigenvalues of H_k⁻¹, (${fmt(ev[0])}, ${fmt(ev[1])}). The Hessian has (${fmt(evH[0])}, ${fmt(evH[1])}).`);
        lines.push(`Line search: t = ${fmt(prop.t)} after ${prop.trials.length} trial${prop.trials.length > 1 ? 's' : ''}` + (prop.ok ? '.' : ', and no trial lowered the loss enough.'));
      }
      if (prop.model) {
        const d = V.sub(prop.xNew, o.x), B = prop.model.B, pred = V.dot(prop.model.gm, d) + 0.5 * V.dot(d, M.vec(B, d));
        lines.push(`The bowl predicts a change of ${fmt(pred)} in L, and L changes by ${fmt(land.f(prop.xNew) - land.f(o.x))}.`);
      }
      lines.forEach(t => h('div', null, pInfo, t));
    }

    function drawTable() {
      tbl.innerHTML = '';
      const proj = st.land === 'projectile';
      const hr = h('tr', null, h('thead', null, tbl));
      ['', 'steps', 'loss', 'gradients', 'loss values', 'Hessians'].concat(proj ? ['v (m/s)', 'a (deg)'] : ['x₁', 'x₂']).concat(['status']).forEach(t => h('th', null, hr, t));
      const tb = h('tbody', null, tbl);
      KINDS.forEach(k => {
        const o = st.opt[k], tr = h('tr', null, tb), td = h('td', { class: 'go-name' }, tr);
        const sw = d3.select(td).append('svg').attr('width', 14).attr('height', 14).attr('class', 'go-swatch');
        sw.append('path').attr('transform', 'translate(7,7)').attr('d', d3.symbol(SHAPES[k], 64)()).attr('class', 'go-mark-' + k);
        h('span', null, td, ' ' + NAMES[k]);
        const fx = land.f(o.x);
        [o.k, fmt(fx, 3), o.ng, o.nf, o.nh, fmt(o.x[0], 4), fmt(o.x[1], 4), o.status].forEach(v => h('td', null, tr, String(v)));
      });
    }

    function drawPhysics() {
      if (st.land !== 'projectile' || !Q) return;
      Q.g.selectAll('*').remove();
      const line = d3.line().x(p => Q.sx(p[0])).y(p => Q.sy(p[1]));
      Q.g.append('path').attr('class', 'go-arc go-dashed').attr('d', line(arcPoints(C.V_TRUE, C.A_TRUE)));
      if (st.mode === 'apex') star(Q.g, Q.toPx(C.APEX_TRUE), 'go-fill-ink');
      else Q.g.append('path').attr('class', 'go-fill-ink').attr('transform', `translate(${Q.sx(C.R_TRUE)},${Q.sy(0)})`).attr('d', d3.symbol(d3.symbolTriangle, 110)());
      KINDS.forEach(k => {
        const o = st.opt[k];
        if (!(o.x[0] > 0 && o.x[1] > 0 && o.x[1] < 90)) return;
        Q.g.append('path').attr('class', 'go-arc go-stroke-' + k).attr('d', line(arcPoints(o.x[0], o.x[1])));
        const top = C.apex(o.x[0], o.x[1]);
        Q.g.append('path').attr('class', 'go-cur go-mark-' + k).attr('transform', `translate(${Q.sx(top[0])},${Q.sy(top[1])})`).attr('d', d3.symbol(SHAPES[k], 60)());
      });
    }

    function showTip(ev, html) {
      const r = root.getBoundingClientRect();
      tip.innerHTML = html; tip.style.display = 'block';
      let x = ev.clientX - r.left + 14, y = ev.clientY - r.top + 14;
      if (x + tip.offsetWidth > r.width) x = ev.clientX - r.left - tip.offsetWidth - 14;
      tip.style.left = x + 'px'; tip.style.top = y + 'px';
    }
    function hoverPar(ev) {
      const m = d3.pointer(ev, P.root.node());
      let best = null, bd = 12;
      KINDS.forEach(k => st.opt[k].hist.forEach((e, i) => {
        const p = P.toPx(e.x), d = Math.hypot(p[0] - m[0], p[1] - m[1]);
        if (d < bd) { bd = d; best = { k, i, e }; }
      }));
      if (!best) { tip.style.display = 'none'; return; }
      showTip(ev, `<b>${NAMES[best.k]}</b>, step ${best.i}<br>L = ${fmt(best.e.f, 3)}<br>x = ${fv(best.e.x)}`);
    }
    function hoverLoss(ev) {
      const m = d3.pointer(ev, LP.root.node()), i = Math.round(LP.sx.invert(m[0]));
      LP.hover.selectAll('*').remove();
      if (i < 0 || m[0] > LP.pw) { tip.style.display = 'none'; return; }
      LP.hover.append('line').attr('class', 'go-crosshair').attr('x1', LP.sx(i)).attr('x2', LP.sx(i)).attr('y1', 0).attr('y2', LP.ph);
      const rows = KINDS.map(k => { const hs = st.opt[k].hist, e = hs[Math.min(i, hs.length - 1)]; return `${NAMES[k]} ${fmt(e.f, 3)}${i >= hs.length ? ' (stopped)' : ''}`; });
      showTip(ev, `<b>step ${i}</b><br>` + rows.join('<br>'));
    }

    setDefaults(); labels(); buildPlots(); drawStatic(); resetRuns();
    const redraw = () => { if (st.view === 'surface') draw(); };
    new MutationObserver(redraw).observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });
    new MutationObserver(redraw).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    if (window.matchMedia) window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', redraw);
  }

  function boot() {
    const a = document.getElementById('go-tape'), b = document.getElementById('go-lab');
    if (a && !a.dataset.ready) { a.dataset.ready = '1'; initTape(a); }
    if (b && !b.dataset.ready) { b.dataset.ready = '1'; initLab(b); }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
