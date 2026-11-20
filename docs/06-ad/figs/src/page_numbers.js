// Numbers from the page's own code. Run: node page_numbers.js > page_numbers-report.txt
const C = require(process.argv[2] || require('path').join(__dirname, '..', '..', 'gradients-and-optimizers.js'));
const names = ['v', 'a', 'theta', 's', 'c', 'q', 'p', 'x', 'z', 'r1', 'r2', 'L'];
const T = C.tape(15, 35);
const fv = T.forward(1, 0), fa = T.forward(0, 1), rev = T.reverse();
console.log('apex true', C.APEX_TRUE.map(x => x.toFixed(4)), 'R true', C.R_TRUE.toFixed(4));
names.forEach((n, i) => console.log(n.padEnd(6), T.val[i].toFixed(5).padStart(12), fv[i].toFixed(5).padStart(12), fa[i].toFixed(5).padStart(12), rev[i].toFixed(5).padStart(12)));

function run(land, kind, opt, stop) {
  const o = C.OPTIMIZERS[kind](land, land.start, Object.assign({ eta: land.eta, lr: land.lr, memory: 5, maxSteps: 500, sigma: 0 }, opt || {}));
  let hit = null;
  while (o.status === 'running') {
    const p = o.propose(); o.commit(p);
    const f = o.hist[o.hist.length - 1].f;
    if (hit === null && stop(o, f)) hit = o.k;
  }
  const last = o.hist[o.hist.length - 1];
  return { hit, k: o.k, status: o.status, x: last.x.map(v => +v.toFixed(4)), f: last.f, maxf: Math.max(...o.hist.map(h => h.f)), hist: o.hist };
}
const below = tol => (o, f) => f < tol;
for (const [label, land] of [['valley 0', C.valley(8, 0)], ['valley 45', C.valley(8, 45)], ['rosenbrock', C.rosenbrock()], ['doublewell', C.doubleWell()], ['projectile apex', C.projectile('apex')], ['projectile landing', C.projectile('landing')]]) {
  console.log('\n' + label, 'start', land.start, 'f0', land.f(land.start).toFixed(4), 'eta', land.eta, 'lr', land.lr);
  for (const kind of ['gd', 'adam', 'newton', 'lbfgs']) {
    const r = run(land, kind, {}, below(1e-6));
    console.log(' ', kind.padEnd(7), 'f<1e-6 at', String(r.hit).padStart(5), '| steps', String(r.k).padStart(4), r.status.padEnd(18), 'x', r.x, 'f', r.f.toExponential(2), 'max f', r.maxf.toFixed(1));
    if (label === 'rosenbrock' && kind === 'newton') console.log('    newton f history', r.hist.slice(0, 9).map(h => h.f.toFixed(3)).join(' '));
  }
}

// rotated start, as the page does for the valley
{
  const DEG = Math.PI / 180, phi = 45, c = Math.cos(phi * DEG), s = Math.sin(phi * DEG);
  const land = C.valley(8, 45), st = land.start, start = [c * st[0] - s * st[1], s * st[0] + c * st[1]];
  const rotated = Object.assign({}, land, { start });
  console.log('\nvalley 45, rotated start', start.map(v => v.toFixed(4)), 'f0', land.f(start).toFixed(4));
  for (const kind of ['gd', 'adam', 'newton', 'lbfgs']) {
    const r = run(rotated, kind, {}, below(1e-6));
    console.log(' ', kind.padEnd(7), 'f<1e-6 at', String(r.hit).padStart(5), '| steps', String(r.k).padStart(4), r.status.padEnd(18), 'f', r.f.toExponential(2));
  }
}
// first steps on the valley, for the bowl figure
{
  const land = C.valley(8, 0);
  for (const kind of ['gd', 'adam', 'newton', 'lbfgs']) {
    const o = C.OPTIMIZERS[kind](land, land.start, { eta: land.eta, lr: land.lr, memory: 5, maxSteps: 500, sigma: 0 });
    const rows = [];
    for (let i = 0; i < 4 && o.status === 'running'; i++) { const p = o.propose(); rows.push('x=' + o.x.map(v => v.toFixed(4)) + ' d=' + (p.d || [0, 0]).map(v => v.toFixed(4)) + (p.t !== undefined ? ' t=' + p.t : '')); o.commit(p); }
    console.log(kind, rows.join(' | '));
  }
}
// noise runs with the page's seed
for (const sigma of [0.05, 0.1, 0.2]) {
  const land = C.valley(8, 0), ns = C.V.norm(land.grad(land.start));
  const out = ['gd', 'adam', 'newton', 'lbfgs'].map(kind => {
    const r = run(land, kind, { sigma, noiseScale: ns, seed: 7 }, below(1e-6));
    const tail = r.hist.slice(-100).map(h => Math.hypot(h.x[0], h.x[1]));
    return kind + ': ' + r.status + ' k=' + r.k + ' mean|x| last100=' + (tail.reduce((a, b) => a + b, 0) / tail.length).toFixed(4);
  });
  console.log('noise', sigma, '|', out.join(' | '));
}
