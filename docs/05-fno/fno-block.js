/* One FNO block, step by step. The core computes the block on a 64-point ring and runs under Node for tests.
   The widget below it draws the data flow and runs only in a browser. */
const FBCore = (function () {
  const N = 64, C = 4, KMAX = 16, HALF = N / 2;
  const X = Array.from({ length: N }, (_, j) => 2 * Math.PI * j / N);

  function rng(seed) {
    // mulberry32, a small deterministic generator, so a seed always gives the same weights
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function gaussian(r) { return Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r()); }

  const INPUTS = {
    three: { label: 'Three waves', f: x => Math.sin(x) + 0.5 * Math.sin(3 * x) + 0.25 * Math.sin(7 * x) },
    square: { label: 'Square wave', f: x => (x < Math.PI - 1e-12 ? 1 : -1) },
    bump: { label: 'Narrow bump', f: x => Math.exp(-((x - Math.PI) ** 2) / (2 * 0.25 * 0.25)) },
  };

  function weights(seed) {
    const r = rng(seed), g = () => gaussian(r);
    const P = [], p = [], W = [], b = [], Q = [], R = [];
    for (let c = 0; c < C; c++) { P.push(g()); p.push(0.3 * g()); }
    for (let k = 0; k < KMAX; k++) {
      const M = [];
      for (let o = 0; o < C; o++) {
        const row = [];
        // Mode 0 is real, so the spectral path returns a real field.
        for (let i = 0; i < C; i++) row.push(k === 0 ? [g() / Math.sqrt(C), 0] : [g() / Math.sqrt(2 * C), g() / Math.sqrt(2 * C)]);
        M.push(row);
      }
      R.push(M);
    }
    for (let o = 0; o < C; o++) { W.push(Array.from({ length: C }, () => g() / Math.sqrt(C))); b.push(0.1 * g()); }
    for (let c = 0; c < C; c++) Q.push(g() / Math.sqrt(C));
    return { P, p, R, W, b, Q, q: 0 };
  }

  function dft(v) {
    // Forward-normalized coefficients for k = 0..N/2, as [re, im].
    const out = [];
    for (let k = 0; k <= HALF; k++) {
      let re = 0, im = 0;
      for (let j = 0; j < N; j++) { re += v[j] * Math.cos(k * X[j]); im -= v[j] * Math.sin(k * X[j]); }
      out.push([re / N, im / N]);
    }
    return out;
  }
  function idft(V) {
    // The real field whose coefficients for k = 0..N/2 are V.
    return X.map((x, j) => {
      let s = V[0][0];
      for (let k = 1; k < HALF; k++) s += 2 * (V[k][0] * Math.cos(k * x) - V[k][1] * Math.sin(k * x));
      return s + V[HALF][0] * Math.cos(Math.PI * j);
    });
  }
  function amplitude(V) {
    // Amplitude of each real wave: |V_0|, 2|V_k| for 0 < k < N/2, |V_{N/2}|.
    return V.map((c, k) => (k === 0 || k === HALF ? 1 : 2) * Math.hypot(c[0], c[1]));
  }
  function gelu(s) { return 0.5 * s * (1 + Math.tanh(Math.sqrt(2 / Math.PI) * (s + 0.044715 * s * s * s))); }

  function forward(inputName, K, w) {
    const a = X.map(INPUTS[inputName].f);
    const v = w.P.map((P, c) => a.map(value => P * value + w.p[c]));
    const V = v.map(dft);
    const Z = [];
    for (let o = 0; o < C; o++) {
      const row = [];
      for (let k = 0; k <= HALF; k++) {
        let re = 0, im = 0;
        if (k < K) for (let i = 0; i < C; i++) {
          const [rr, ri] = w.R[k][o][i], [vr, vi] = V[i][k];
          re += rr * vr - ri * vi; im += rr * vi + ri * vr;
        }
        row.push([re, im]);
      }
      Z.push(row);
    }
    const z = Z.map(idft);
    const y = w.W.map((Wrow, o) => X.map((_, j) => Wrow.reduce((sum, wi, i) => sum + wi * v[i][j], w.b[o])));
    const s = z.map((zo, o) => zo.map((value, j) => value + y[o][j]));
    const v1 = s.map(row => row.map(gelu));
    const V1 = v1.map(dft);
    const u = X.map((_, j) => w.Q.reduce((sum, qc, c) => sum + qc * v1[c][j], w.q));
    return { a, v, V, Z, z, y, s, v1, V1, u };
  }

  return { N, C, KMAX, HALF, X, INPUTS, weights, dft, idft, amplitude, gelu, forward };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = FBCore;

if (typeof document !== 'undefined') (function () {
  const root = document.getElementById('fb-root');
  if (!root) return;
  const { N, C, KMAX, HALF, X, INPUTS } = FBCore;
  const NS = 'http://www.w3.org/2000/svg';
  const TAU = 2 * Math.PI;

  const PHASES = [
    { key: 'lift', label: '1. Lift', title: 'Lift the input', domain: 'Spatial domain',
      nodes: ['a', 'P', 'v'],
      text: () => 'Here is the input $a(x)$ at 64 points around a ring. The lifting $P$ acts at each point by itself. ' +
        'It turns the one number $a(x_j)$ into $C=4$ numbers, so each channel of $v(x)$ is a scaled and shifted copy of the input.',
      eq: 'v_c(x)=P_c\\,a(x)+p_c,\\qquad c=1,\\dots,4' },
    { key: 'fft', label: '2. FFT', title: 'Change to waves', domain: 'Spatial to frequency',
      nodes: ['v', 'F', 'vh'],
      text: st => 'The FFT writes each channel as a sum of waves. The bars show the amplitude of each mode $k$ in channel ' + (st.channel + 1) +
        '. This step changes coordinates and learns nothing. The dashed line separates the kept modes $k\\le k_{\\max}=' + (st.K - 1) + '$ from the dropped ones.',
      eq: '\\hat v_c(k)=\\frac1N\\sum_{j=0}^{N-1}v_c(x_j)\\,e^{-ikx_j}' },
    { key: 'mult', label: '3. Multiply', title: 'Keep low modes and multiply by R(k)', domain: 'Frequency domain',
      nodes: ['vh', 'R', 'zh'],
      text: st => 'The layer keeps the modes $k\\le ' + (st.K - 1) + '$ and sets the rest to zero. At each kept mode, a learned $4\\times4$ complex matrix $R(k)$ mixes the channels. ' +
        'Output mode $k$ uses input mode $k$ alone, so different modes never mix in this step. The left panel shows $|R(k)|$ for $k=' + Math.min(st.mode, st.K - 1) + '$.',
      eq: '\\hat z_o(k)=\\sum_{i=1}^{4}R_{oi}(k)\\,\\hat v_i(k),\\qquad k\\le k_{\\max}' },
    { key: 'ifft', label: '4. Inverse FFT', title: 'Back to the grid', domain: 'Frequency to spatial',
      nodes: ['zh', 'Fi', 'z'],
      text: () => 'The inverse FFT adds the kept waves back together. Each channel of $z(x)$ contains only the modes $k\\le k_{\\max}$. ' +
        'Choose the square wave and a small $k_{\\max}$, and $z(x)$ comes out smooth while the input has corners.',
      eq: 'z_o(x)=\\sum_{|k|\\le k_{\\max}}\\hat z_o(k)\\,e^{ikx}' },
    { key: 'local', label: '5. Local path', title: 'The local path W', domain: 'Spatial domain',
      nodes: ['v', 'W', 'y'],
      text: () => 'The second path acts at each point. The matrix $W$ mixes the four channels of $v(x_j)$ and adds a bias. ' +
        'It keeps every mode of $v$, including the modes that the first path dropped.',
      eq: 'y(x)=W\\,v(x)+b' },
    { key: 'act', label: '6. Activate', title: 'Add the paths and activate', domain: 'Spatial domain',
      nodes: ['z', 'y', 'S', 'v1'],
      text: st => {
        const created = st.created;
        const lead = 'Adding the two paths and applying $\\sigma$ at each point gives the next feature field $v_1(x)$, with $\\sigma$ the GELU function. ';
        return lead + (created > 0
          ? 'The orange bars mark ' + created + ' modes of channel ' + (st.channel + 1) + ' that were zero in $v(x)$, so only the activation created them.'
          : 'Every mode is already present in this input, so the activation changes amplitudes. Choose the three-wave input to see new modes appear.');
      },
      eq: 'v_1(x)=\\sigma\\big(z(x)+y(x)\\big)' },
    { key: 'proj', label: '7. Project', title: 'Project to the output', domain: 'Spatial domain',
      nodes: ['v1', 'Q', 'u'],
      text: () => 'The projection $Q$ turns the four channels at each point back into one number. A full FNO stacks four blocks between $P$ and $Q$. ' +
        'These weights are random, so $u(x)$ shows the data flow only. Training chooses $P$, $R(k)$, $W$, and $Q$ so that $u(x)$ matches the solution of a PDE.',
      eq: 'u(x)=Q\\,v_1(x)+q' },
  ];

  const st = { phase: 0, input: 'three', K: 8, channel: 0, mode: 1, seed: 7, created: 0 };
  let w = FBCore.weights(st.seed), res = null;

  // ---------- DOM helpers ----------
  function h(tag, attrs, parent, text) {
    const el = document.createElement(tag);
    for (const k in attrs || {}) el.setAttribute(k, attrs[k]);
    if (text !== undefined) el.textContent = text;
    if (parent) parent.appendChild(el);
    return el;
  }
  function s(tag, attrs, parent, text) {
    const el = document.createElementNS(NS, tag);
    for (const k in attrs || {}) el.setAttribute(k, attrs[k]);
    if (text !== undefined) el.textContent = text;
    if (parent) parent.appendChild(el);
    return el;
  }
  function typeset(el) {
    if (typeof renderMathInElement === 'function') {
      renderMathInElement(el, { delimiters: [{ left: '$', right: '$', display: false }], throwOnError: false });
    }
  }
  function tex(el, source) {
    if (typeof katex !== 'undefined') katex.render(source, el, { displayMode: true, throwOnError: false });
    else el.textContent = source;
  }

  // ---------- controls ----------
  const controls = h('div', { class: 'fb-controls' }, root);
  const inLab = h('label', {}, controls, 'Input ');
  const inSel = h('select', {}, inLab);
  for (const key in INPUTS) h('option', { value: key }, inSel, INPUTS[key].label);
  const kLab = h('label', {}, controls, 'Largest kept mode $k_{\\max}$ ');
  const kIn = h('input', { type: 'range', min: 0, max: KMAX - 1, step: 1, value: st.K - 1 }, kLab);
  const kOut = h('output', {}, kLab, String(st.K - 1));
  const cLab = h('label', {}, controls, 'Channel ');
  const cSel = h('select', {}, cLab);
  for (let c = 0; c < C; c++) h('option', { value: c }, cSel, String(c + 1));
  const mLab = h('label', { class: 'fb-mode' }, controls, 'Mode $k$ for $R(k)$ ');
  const mIn = h('input', { type: 'range', min: 0, max: KMAX - 1, step: 1, value: st.mode }, mLab);
  const mOut = h('output', {}, mLab, String(st.mode));
  const bSeed = h('button', { class: 'fb-btn', type: 'button' }, controls, 'New random weights');

  // ---------- diagram ----------
  const diagramWrap = h('div', { class: 'fb-panel fb-diagram' }, root);
  const D = s('svg', { viewBox: '0 0 1190 330', class: 'fb-svg', role: 'img',
    'aria-label': 'Data flow through one FNO block' }, diagramWrap);
  s('rect', { x: 298, y: 18, width: 434, height: 136, rx: 10, class: 'fb-freq' }, D);
  s('text', { x: 310, y: 36, class: 'fb-region' }, D, 'Frequency domain, mode k');
  s('text', { x: 20, y: 36, class: 'fb-region' }, D, 'Spatial domain, position x');
  s('text', { x: 1170, y: 318, class: 'fb-region', 'text-anchor': 'end' }, D, 'Spatial domain');

  const BOX = {
    a: [20, 65, 90, 60, 'plot', 'a(x)'], P: [126, 75, 52, 40, 'op', 'P'], v: [194, 65, 90, 60, 'plot', 'v(x)'],
    F: [312, 75, 46, 40, 'op', 'FFT'], vh: [372, 65, 90, 60, 'bars', 'v̂(k)'], R: [476, 75, 66, 40, 'op', 'R(k)'],
    zh: [556, 65, 90, 60, 'bars', 'ẑ(k)'], Fi: [660, 75, 56, 40, 'op', 'iFFT'], z: [748, 65, 90, 60, 'plot', 'z(x)'],
    W: [476, 225, 66, 40, 'op', 'W'], y: [556, 215, 90, 60, 'plot', 'y(x)'],
    S: [862, 225, 56, 40, 'op', '+, σ'], v1: [934, 215, 90, 60, 'plot', 'v₁(x)'],
    Q: [1036, 225, 40, 40, 'op', 'Q'], u: [1088, 215, 90, 60, 'plot', 'u(x)'],
  };
  const EDGES = [
    ['a', 'P', 'M110,95 H126'], ['P', 'v', 'M178,95 H194'], ['v', 'F', 'M284,95 H312'],
    ['F', 'vh', 'M358,95 H372'], ['vh', 'R', 'M462,95 H476'], ['R', 'zh', 'M542,95 H556'],
    ['zh', 'Fi', 'M646,95 H660'], ['Fi', 'z', 'M716,95 H748'], ['z', 'S', 'M838,95 H890 V225'],
    ['v', 'W', 'M239,125 V245 H476'], ['W', 'y', 'M542,245 H556'], ['y', 'S', 'M646,245 H862'],
    ['S', 'v1', 'M918,245 H934'], ['v1', 'Q', 'M1024,245 H1036'], ['Q', 'u', 'M1076,245 H1088'],
  ];
  s('defs', {}, D).innerHTML = '<marker id="fb-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="fb-headfill"/></marker>';
  const edgeEls = EDGES.map(([from, to, d]) => ({ from, to, el: s('path', { d, class: 'fb-edge', 'marker-end': 'url(#fb-head)' }, D) }));
  const nodeEls = {};
  for (const key in BOX) {
    const [x, y, wd, ht, kind, label] = BOX[key];
    const g = s('g', { class: 'fb-node fb-' + kind, tabindex: 0, role: 'button', 'aria-label': label }, D);
    s('rect', { x, y, width: wd, height: ht, rx: kind === 'op' ? 8 : 6, class: 'fb-box' }, g);
    if (kind === 'op') s('text', { x: x + wd / 2, y: y + ht / 2 + 5, class: 'fb-oplabel', 'text-anchor': 'middle' }, g, label);
    else s('text', { x: x + 4, y: y - 4, class: 'fb-plotlabel' }, g, label);
    const inner = s('g', {}, g);
    nodeEls[key] = { g, inner, x, y, wd, ht, kind };
    g.addEventListener('click', () => { const i = PHASES.findIndex(ph => ph.nodes.includes(key)); if (i >= 0) go(i); });
  }

  // ---------- phase card, detail plot, navigation ----------
  const card = h('div', { class: 'fb-panel fb-card' }, root);
  const head = h('div', { class: 'fb-cardhead' }, card);
  const badge = h('span', { class: 'fb-badge' }, head);
  const title = h('span', { class: 'fb-title' }, head);
  const domain = h('span', { class: 'fb-domain' }, head);
  const body = h('div', { class: 'fb-grid' }, card);
  const textCol = h('div', {}, body);
  const text = h('p', { class: 'fb-text' }, textCol);
  const eq = h('div', { class: 'fb-eq' }, textCol);
  const detail = s('svg', { viewBox: '0 0 560 250', class: 'fb-svg fb-detail', role: 'img' }, body);
  const nav = h('div', { class: 'fb-nav' }, root);
  const bPrev = h('button', { class: 'fb-btn', type: 'button' }, nav, 'Prev');
  const bNext = h('button', { class: 'fb-btn fb-primary', type: 'button' }, nav, 'Next');
  const stepBtns = PHASES.map((ph, i) => {
    const b = h('button', { class: 'fb-btn fb-step', type: 'button' }, nav, ph.label);
    b.addEventListener('click', () => go(i));
    return b;
  });

  // ---------- plotting ----------
  function chColor(c) { return 'fb-c' + (c + 1); }
  function lineChart(g, box, series, opt) {
    const [x0, y0, wd, ht] = box;
    let lo = Infinity, hi = -Infinity;
    for (const sr of series) for (const v of sr.y) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    if (opt && opt.range) [lo, hi] = opt.range;
    if (hi - lo < 1e-9) { lo -= 1; hi += 1; }
    const pad = 0.08 * (hi - lo); lo -= pad; hi += pad;
    const px = x => x0 + wd * x / TAU, py = v => y0 + ht - ht * (v - lo) / (hi - lo);
    if (lo < 0 && hi > 0) s('line', { x1: x0, x2: x0 + wd, y1: py(0), y2: py(0), class: 'fb-zero' }, g);
    for (const sr of series) {
      const xs = X.concat([TAU]), ys = sr.y.concat([sr.y[0]]);
      const d = xs.map((x, j) => (j ? 'L' : 'M') + px(x).toFixed(1) + ',' + py(ys[j]).toFixed(1)).join(' ');
      s('path', { d, class: 'fb-line ' + (sr.cls || '') }, g);
    }
    return { px, py, lo, hi };
  }
  function barChart(g, box, amps, opt) {
    const [x0, y0, wd, ht] = box;
    const n = opt.n || amps.length;
    const top = Math.max(1e-9, opt.top || Math.max(...amps.slice(0, n)));
    const bw = wd / n;
    for (let k = 0; k < n; k++) {
      const hgt = ht * Math.min(1, amps[k] / top);
      const cls = 'fb-bar ' + (opt.cls ? opt.cls(k) : '');
      s('rect', { x: x0 + k * bw + bw * 0.12, y: y0 + ht - hgt, width: bw * 0.76, height: Math.max(0, hgt), class: cls }, g);
    }
    if (opt.cut !== undefined) {
      const xc = x0 + opt.cut * bw;
      s('line', { x1: xc, x2: xc, y1: y0 - 2, y2: y0 + ht, class: 'fb-cut' }, g);
    }
    s('line', { x1: x0, x2: x0 + wd, y1: y0 + ht, y2: y0 + ht, class: 'fb-axisline' }, g);
    return { bw, top };
  }
  function axisLabel(g, x, y, label, anchor) { s('text', { x, y, class: 'fb-axis', 'text-anchor': anchor || 'middle' }, g, label); }

  // ---------- drawing ----------
  function present(V) { return FBCore.amplitude(V).map(a => a > 1e-9); }
  // A mode counts as created when it was zero in v and is visible as a bar, above 0.1 percent of the largest.
  function createdModes(Vbefore, Vafter) {
    const had = present(Vbefore), amps = FBCore.amplitude(Vafter), top = Math.max(...amps);
    return amps.map((a, k) => !had[k] && a > 1e-3 * top);
  }

  function drawDiagram() {
    const ph = PHASES[st.phase];
    for (const key in nodeEls) {
      const n = nodeEls[key];
      n.g.classList.toggle('on', ph.nodes.includes(key));
      while (n.inner.firstChild) n.inner.removeChild(n.inner.firstChild);
      const box = [n.x + 5, n.y + 6, n.wd - 10, n.ht - 12];
      if (key === 'a') lineChart(n.inner, box, [{ y: res.a, cls: 'fb-ink' }]);
      if (key === 'u') lineChart(n.inner, box, [{ y: res.u, cls: 'fb-ink' }]);
      if (['v', 'z', 'y', 'v1'].includes(key)) {
        const data = res[key];
        lineChart(n.inner, box, data.map((row, c) => ({ y: row, cls: chColor(c) + (c === st.channel ? ' fb-thick' : ' fb-faint') })));
      }
      if (key === 'vh') barChart(n.inner, box, FBCore.amplitude(res.V[st.channel]), { cut: st.K, cls: k => (k < st.K ? chColor(st.channel) : 'fb-dropped') });
      if (key === 'zh') barChart(n.inner, box, FBCore.amplitude(res.Z[st.channel]), { top: Math.max(...FBCore.amplitude(res.V[st.channel])), cut: st.K, cls: () => chColor(st.channel) });
    }
    for (const e of edgeEls) e.el.classList.toggle('on', ph.nodes.includes(e.from) && ph.nodes.includes(e.to));
  }

  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  function drawDetail() {
    clear(detail);
    const key = PHASES[st.phase].key;
    const g = s('g', {}, detail);
    const xTicks = (box) => {
      axisLabel(g, box[0], box[1] + box[3] + 14, '0'); axisLabel(g, box[0] + box[2] / 2, box[1] + box[3] + 14, 'π');
      axisLabel(g, box[0] + box[2], box[1] + box[3] + 14, '2π'); axisLabel(g, box[0] + box[2] / 2, box[1] + box[3] + 28, 'position x');
    };
    const kTicks = (box, n) => {
      for (const k of [0, 8, 16, 24, 32]) if (k <= n - 1) axisLabel(g, box[0] + (k + 0.5) * box[2] / n, box[1] + box[3] + 14, String(k));
      axisLabel(g, box[0] + box[2] / 2, box[1] + box[3] + 28, 'mode k');
    };
    const legend = (x, y, entries) => entries.forEach(([cls, label], i) => {
      s('line', { x1: x, x2: x + 18, y1: y + 14 * i, y2: y + 14 * i, class: 'fb-line ' + cls }, g);
      s('text', { x: x + 22, y: y + 14 * i + 4, class: 'fb-axis' }, g, label);
    });
    const channelLegend = (x, y) => legend(x, y, res.v.map((_, c) => [chColor(c) + ' fb-thick', 'channel ' + (c + 1)]));
    const full = [40, 18, 400, 190];

    if (key === 'lift') {
      lineChart(g, full, [{ y: res.a, cls: 'fb-ink fb-dash' }].concat(res.v.map((row, c) => ({ y: row, cls: chColor(c) + ' fb-thick' }))));
      xTicks(full); legend(455, 30, [['fb-ink fb-dash', 'input a(x)']]); channelLegend(455, 50);
    }
    if (key === 'fft') {
      const amps = FBCore.amplitude(res.V[st.channel]);
      barChart(g, full, amps, { cut: st.K, cls: k => (k < st.K ? chColor(st.channel) : 'fb-dropped') });
      kTicks(full, HALF + 1);
      axisLabel(g, full[0] + st.K * full[2] / (HALF + 1) + 4, full[1] + 10, 'kept k ≤ ' + (st.K - 1), 'start');
      legend(455, 30, [[chColor(st.channel) + ' fb-thick', 'kept, k ≤ ' + (st.K - 1)], ['fb-dropped fb-thick', 'dropped']]);
    }
    if (key === 'mult') {
      const k = Math.min(st.mode, st.K - 1);
      const M = w.R[k], cell = 34, x0 = 40, y0 = 40;
      let top = 0;
      for (const row of M) for (const [re, im] of row) top = Math.max(top, Math.hypot(re, im));
      M.forEach((row, o) => row.forEach(([re, im], i) => {
        const mag = Math.hypot(re, im);
        s('rect', { x: x0 + i * cell, y: y0 + o * cell, width: cell - 2, height: cell - 2, class: 'fb-cell', 'fill-opacity': (0.15 + 0.85 * mag / top).toFixed(2) }, g);
        s('text', { x: x0 + i * cell + cell / 2 - 1, y: y0 + o * cell + cell / 2 + 3, class: 'fb-celltext', 'text-anchor': 'middle' }, g, mag.toFixed(2));
      }));
      axisLabel(g, x0 + 2 * cell, y0 - 10, '|R(k)| at k = ' + k);
      axisLabel(g, x0 + 2 * cell, y0 + 4 * cell + 16, 'input channel i');
      s('text', { x: x0 - 12, y: y0 + 2 * cell, class: 'fb-axis', 'text-anchor': 'middle', transform: 'rotate(-90 ' + (x0 - 12) + ' ' + (y0 + 2 * cell) + ')' }, g, 'output channel o');
      const box = [230, 18, 310, 190];
      const before = FBCore.amplitude(res.V[st.channel]), after = FBCore.amplitude(res.Z[st.channel]);
      const n = Math.min(HALF + 1, 24), top2 = Math.max(...before.slice(0, n), ...after.slice(0, n));
      barChart(g, box, after, { n, top: top2, cut: st.K, cls: () => chColor(st.channel) });
      const bw = box[2] / n;
      for (let kk = 0; kk < n; kk++) {
        const hgt = box[3] * Math.min(1, before[kk] / top2);
        s('rect', { x: box[0] + kk * bw + bw * 0.12, y: box[1] + box[3] - hgt, width: bw * 0.76, height: hgt, class: 'fb-outline' }, g);
      }
      kTicks(box, n);
      axisLabel(g, box[0] + box[2], box[1] + 8, 'outline v̂, filled ẑ, channel ' + (st.channel + 1), 'end');
    }
    if (key === 'ifft' || key === 'local') {
      const data = key === 'ifft' ? res.z : res.y;
      lineChart(g, full, [{ y: res.a, cls: 'fb-ink fb-dash' }].concat(data.map((row, c) => ({ y: row, cls: chColor(c) + (c === st.channel ? ' fb-thick' : ' fb-mid') }))));
      xTicks(full); legend(455, 30, [['fb-ink fb-dash', 'input a(x)']]); channelLegend(455, 50);
    }
    if (key === 'act') {
      const left = [40, 18, 230, 190], right = [310, 18, 230, 190];
      lineChart(g, left, res.v1.map((row, c) => ({ y: row, cls: chColor(c) + (c === st.channel ? ' fb-thick' : ' fb-mid') })));
      xTicks(left);
      const created = createdModes(res.V[st.channel], res.V1[st.channel]), amps = FBCore.amplitude(res.V1[st.channel]);
      barChart(g, right, amps, { cut: st.K, cls: k => (created[k] ? 'fb-new' : chColor(st.channel)) });
      kTicks(right, HALF + 1);
      axisLabel(g, right[0] + right[2], right[1] + 8, 'v₁, channel ' + (st.channel + 1), 'end');
    }
    if (key === 'proj') {
      lineChart(g, full, [{ y: res.a, cls: 'fb-ink fb-dash' }, { y: res.u, cls: 'fb-out fb-thick' }]);
      xTicks(full); legend(455, 30, [['fb-ink fb-dash', 'input a(x)'], ['fb-out fb-thick', 'output u(x)']]);
    }
  }

  function drawCard() {
    const ph = PHASES[st.phase];
    badge.textContent = 'Step ' + (st.phase + 1) + ' / ' + PHASES.length;
    title.textContent = ph.title;
    domain.textContent = ph.domain;
    text.textContent = ph.text(st);
    typeset(text);
    tex(eq, ph.eq);
    detail.setAttribute('aria-label', ph.title);
    bPrev.disabled = st.phase === 0;
    bNext.disabled = st.phase === PHASES.length - 1;
    stepBtns.forEach((b, i) => b.classList.toggle('on', i === st.phase));
    mLab.style.display = ph.key === 'mult' ? '' : 'none';
  }

  function compute() {
    res = FBCore.forward(st.input, st.K, w);
    st.created = createdModes(res.V[st.channel], res.V1[st.channel]).filter(Boolean).length;
  }
  function render() { compute(); drawDiagram(); drawDetail(); drawCard(); }
  function go(i) { st.phase = Math.max(0, Math.min(PHASES.length - 1, i)); render(); }

  inSel.addEventListener('change', () => { st.input = inSel.value; render(); });
  kIn.addEventListener('input', () => {
    st.K = +kIn.value + 1; kOut.textContent = String(st.K - 1);
    mIn.max = String(st.K - 1); if (st.mode > st.K - 1) { st.mode = st.K - 1; mIn.value = String(st.mode); mOut.textContent = String(st.mode); }
    render();
  });
  cSel.addEventListener('change', () => { st.channel = +cSel.value; render(); });
  mIn.addEventListener('input', () => { st.mode = +mIn.value; mOut.textContent = String(st.mode); render(); });
  bSeed.addEventListener('click', () => { st.seed += 1; w = FBCore.weights(st.seed); render(); });
  bPrev.addEventListener('click', () => go(st.phase - 1));
  bNext.addEventListener('click', () => go(st.phase + 1));
  root.addEventListener('keydown', ev => {
    if (ev.target.tagName === 'INPUT' || ev.target.tagName === 'SELECT') return;
    if (ev.key === 'ArrowRight') go(st.phase + 1);
    if (ev.key === 'ArrowLeft') go(st.phase - 1);
  });
  mIn.max = String(st.K - 1);
  // KaTeX loads after this script, so the first render waits for the document.
  const first = () => { typeset(controls); render(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', first);
  else first();
})();
