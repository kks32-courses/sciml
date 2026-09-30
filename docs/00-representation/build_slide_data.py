"""Data tables for the native pgfplots figures of 00-rep.tex.

Every table reproduces a computation of the book's Chapter 2 scripts with the
same parameters (test displacement, stations, fin readings with seed 3), so the
numbers the slides show agree with the chapter's script reports.

Run:  ../../env/bin/python build_slide_data.py    (writes data/*.dat here)
"""

import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")
os.makedirs(OUT, exist_ok=True)


def save(name, cols, **arrays):
    keys = list(arrays)
    data = np.column_stack([arrays[k] for k in keys])
    header = " ".join(keys)
    np.savetxt(os.path.join(OUT, name), data, header=header, comments="", fmt="%.6g")


x = np.linspace(0.0, 1.0, 401)
lines = ["# build_slide_data report", ""]

# --- the test displacement, readings, segments, gaps ---------------------------------
u = lambda t: 0.8 * np.sin(np.pi * t) + 0.4 * np.sin(2 * np.pi * t) + 0.2 * np.sin(3 * np.pi * t)
umax = np.max(np.abs(u(x)))
save("string.dat", None, x=x, u=u(x))
for m in (3, 5, 9, 17):
    xi = np.linspace(0, 1, m)
    save(f"readings{m}.dat", None, x=xi, u=u(xi))
    v = np.interp(x, xi, u(xi))
    save(f"segments{m}.dat", None, x=x, v=v, gap=u(x) - v)
    lines.append(f"m = {m}: largest gap / largest displacement = {100*np.max(np.abs(u(x)-v))/umax:.1f} %")
# gap bars at m = 5 on a coarse grid
xb = np.linspace(0, 1, 41)
xi5 = np.linspace(0, 1, 5)
save("gaps5.dat", None, x=xb, u=u(xb), v=np.interp(xb, xi5, u(xi5)))
xi3 = np.linspace(0, 1, 3)
save("gaps3.dat", None, x=xb, u=u(xb), v=np.interp(xb, xi3, u(xi3)))
# aliasing at m = 17
alias = lambda t: u(t) + 0.3 * np.sin(16 * np.pi * t)
save("alias.dat", None, x=np.linspace(0, 1, 801), a=alias(np.linspace(0, 1, 801)))
xi17 = np.linspace(0, 1, 17)
lines.append(f"aliasing: max change in the 17 readings = {np.max(np.abs(alias(xi17)-u(xi17))):.1e}, crest move 0.3 = {100*0.3/umax:.0f} % of largest displacement")

# --- error curve at m = 5, its square, its slope -------------------------------------
xf = np.linspace(0, 1, 2001)
v5 = np.interp(xf, xi5, u(xi5))
e = u(xf) - v5
du = 0.8 * np.pi * np.cos(np.pi * xf) + 0.8 * np.pi * np.cos(2 * np.pi * xf) + 0.6 * np.pi * np.cos(3 * np.pi * xf)
dv = np.gradient(v5, xf)
save("error5.dat", None, x=xf, e=e, e2=e**2, de=du - dv)
sup = np.max(np.abs(e)); l2 = np.sqrt(np.trapezoid(e**2, xf)); h1 = np.sqrt(np.trapezoid((du - dv)**2, xf))
lines.append(f"m = 5 error: sup {sup:.3f}, L2 {l2:.3f}, H1 {h1:.2f}, energy {0.5*h1**2:.2f}")

# --- projection of the parabola: squared error against c1 ----------------------------
parab = xf * (1 - xf)
c3 = 8 / (27 * np.pi**3)
c1s = np.linspace(0.15, 0.37, 111)
err2 = np.array([np.trapezoid((parab - c * np.sin(np.pi * xf) - c3 * np.sin(3 * np.pi * xf))**2, xf) for c in c1s])
save("proj_err2.dat", None, c1=c1s, err2=err2)
lines.append(f"projection: c1* = 8/pi^3 = {8/np.pi**3:.4f}, min squared error {err2.min():.2e}")

# --- two inner products on the segment family -------------------------------------------
nodes = np.array([0.25, 0.5, 0.75])
save("seg_energy.dat", None, x=np.r_[0, nodes, 1], v=np.r_[0, nodes * (1 - nodes), 0])
save("seg_l2.dat", None, x=np.r_[0, nodes, 1], v=np.r_[0, 0.2009, 0.2589, 0.2009, 0])

# --- Gibbs partial sums of a step near the jump -----------------------------------------
xg = np.linspace(0.3, 0.7, 801)
step = np.where(xg < 0.5, 0.0, 1.0)
for N in (9, 33, 129):
    s = 0.5 + sum((2 / (k * np.pi)) * np.sin(k * np.pi * (xg - 0.5)) for k in range(1, N + 1, 2))
    save(f"gibbs{N}.dat", None, x=xg, s=s)
    lines.append(f"Gibbs N = {N}: overshoot {s.max()-1:.3f}")

# --- Bernstein hills and polynomials for the corner function -----------------------------
from math import lgamma, log
f = lambda t: np.abs(t - 0.5)


def bern(n, t):
    out = np.zeros_like(t)
    for k in range(n + 1):
        lc = lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
        with np.errstate(divide="ignore", invalid="ignore"):
            w = np.exp(lc + k * np.log(np.clip(t, 1e-300, 1)) + (n - k) * np.log(np.clip(1 - t, 1e-300, 1)))
        w = np.where(t <= 0, 1.0 if k == 0 else 0.0, w)
        w = np.where(t >= 1, 1.0 if k == n else 0.0, w)
        out += f(k / n) * w
    return out


def hills(n, t):
    cols = {}
    for k in range(n + 1):
        lc = lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
        with np.errstate(divide="ignore", invalid="ignore"):
            w = np.exp(lc + k * np.log(np.clip(t, 1e-300, 1)) + (n - k) * np.log(np.clip(1 - t, 1e-300, 1)))
        w = np.where(t <= 0, 1.0 if k == 0 else 0.0, w)
        w = np.where(t >= 1, 1.0 if k == n else 0.0, w)
        cols[f"h{k}"] = w
    return cols


for n in (2, 8, 32):
    save(f"bern{n}.dat", None, x=x, B=bern(n, x), f=f(x))
    lines.append(f"Bernstein n = {n}: gap at corner {bern(n, np.array([0.5]))[0]:.3f}, 0.4/sqrt(n) = {0.4/np.sqrt(n):.3f}")
save("hills2.dat", None, x=x, **hills(2, x))
save("hills8.dat", None, x=x, **hills(8, x))

# --- ramps toward the step (Cauchy) ------------------------------------------------------
for n in (2, 8, 32):
    w = 1 / n
    r = np.clip((x - 0.5) / w + 0.5, 0, 1)
    save(f"ramp{n}.dat", None, x=x, r=r)

# --- hat from three ramps and the interpolant of x(1-x) at five stations -----------------
h = 0.25
relu = lambda s: np.maximum(s, 0)
save("hat_ramps.dat", None, x=x, r1=relu(x - 0.25) / h, r2=-2 * relu(x - 0.5) / h, r3=relu(x - 0.75) / h,
     hat=(relu(x - 0.25) - 2 * relu(x - 0.5) + relu(x - 0.75)) / h)
save("parab.dat", None, x=x, u=x * (1 - x))

# --- the front, stations, and kinks ----------------------------------------------------
w = 0.01
d = 0.02


def front(t, c):
    a, b = 0.15 + c, 0.45 + c
    return 0.5 * (np.tanh((t - a) / w) - np.tanh((t - b) / w))


xff = np.linspace(0, 1, 1201)
for tag, c in (("0", 0.0), ("15", 0.15), ("30", 0.30)):
    T = front(xff, c)
    xs = np.linspace(0, 1, 32)
    seg = np.interp(xff, xs, front(xs, c))
    a, b = 0.15 + c, 0.45 + c
    net = (relu(xff - (a - d)) - relu(xff - (a + d)) - relu(xff - (b - d)) + relu(xff - (b + d))) / (2 * d)
    if tag != "15":  # the shift-0.15 front is reported, not plotted
        save(f"front{tag}.dat", None, x=xff, T=T, seg=seg, net=net)
    rel = lambda v: np.sqrt(np.trapezoid((v - T)**2, xff) / np.trapezoid(T**2, xff))
    lines.append(f"front shift {c}: stations {100*rel(seg):.1f} %, kinks {100*rel(net):.1f} %")
save("stations32.dat", None, x=np.linspace(0, 1, 32), y=np.zeros(32) - 0.1)

# --- fin readings, kernel bumps, GP mean and band (same data as the chapter) -------------
np.random.seed(3)
Tfin = lambda t: np.exp(-1.5 * t) * (1.0 + 0.4 * np.sin(3 * np.pi * t))
xs = np.array([0.03, 0.12, 0.24, 0.33, 0.45, 0.53, 0.88, 0.97])
sigma = 0.03
ys = Tfin(xs) + sigma * np.random.randn(len(xs))
save("fin_readings.dat", None, x=xs, y=ys)
save("fin_true.dat", None, x=x, T=Tfin(x))
kern = lambda a, b, ell: np.exp(-(a[:, None] - b[None, :])**2 / (2 * ell**2))
for tag, ell in (("15", 0.15), ("04", 0.04)):
    alpha = np.linalg.solve(kern(xs, xs, ell), ys)
    cols = {f"b{i}": alpha[i] * np.exp(-(x - xs[i])**2 / (2 * ell**2)) for i in range(8)}
    cols["sum"] = kern(x, xs, ell) @ alpha
    save(f"bumps{tag}.dat", None, x=x, **cols)
    lines.append(f"kernel interpolant ell = {ell}: weights " + ", ".join(f"{a:.2f}" for a in alpha)
                 + f"; value at 0.7 = {float(kern(np.array([0.7]), xs, ell) @ alpha):.3f}")
for tag, ell in (("15", 0.15), ("075", 0.075), ("31", 0.31)):
    K = kern(xs, xs, ell) + sigma**2 * np.eye(8)
    kq = kern(x, xs, ell)
    mu = kq @ np.linalg.solve(K, ys)
    s2 = 1.0 - np.einsum("ij,ij->i", kq, np.linalg.solve(K, kq.T).T)
    sd = np.sqrt(np.maximum(s2, 0))
    if tag != "075":  # the ell = 0.075 band is reported, not plotted
        save(f"gp{tag}.dat", None, x=x, mu=mu, lo=mu - 2 * sd, hi=mu + 2 * sd)
    gap = (x >= 0.55) & (x <= 0.85)
    lines.append(f"GP ell = {ell}: rel L2 error {np.sqrt(np.trapezoid((mu-Tfin(x))**2, x)/np.trapezoid(Tfin(x)**2, x)):.3f}, "
                 f"max 2sd in gap {2*sd[gap].max():.3f}")

# --- studio labs redrawn: the similarity microscope and the RKHS builder -----------------
# similarity microscope (course page defaults): copies at 0.30 and 0.45, ell = 0.15
ell_m = 0.15
xa, xb = 0.30, 0.45
kk = lambda a, b, ell: np.exp(-(a - b)**2 / (2 * ell**2))
save("kernel_pair.dat", None, x=x, k1=kk(x, xa, ell_m), k2=kk(x, xb, ell_m), prod=kk(x, xa, ell_m) * kk(x, xb, ell_m))
lines.append(f"similarity microscope ell = {ell_m}: k({xa}, {xb}) = {kk(xa, xb, ell_m):.3f} (distance ell), "
             f"k at distance 3 ell = {kk(0.0, 3*ell_m, ell_m):.3f}, at distance 2 ell = {kk(0.0, 2*ell_m, ell_m):.3f}")
# RKHS builder (studio defaults): centers 0.2, 0.5, 0.8, alpha = 0.8, -0.45, 0.65, ell = 0.16, probe 0.61
ell_r = 0.16
centers = np.array([0.2, 0.5, 0.8]); alpha_r = np.array([0.8, -0.45, 0.65]); xstar = 0.72
copies = {f"c{i}": alpha_r[i] * kk(x, centers[i], ell_r) for i in range(3)}
f_r = sum(copies.values())
save("rkhs.dat", None, x=x, **copies, f=f_r, kp=kk(x, xstar, ell_r))
Kc = kk(centers[:, None], centers[None, :], ell_r)
fstar = float(alpha_r @ kk(centers, xstar, ell_r))
norm2 = float(alpha_r @ Kc @ alpha_r)
lines.append(f"RKHS builder ell = {ell_r}, centers {centers.tolist()}, alpha {alpha_r.tolist()}, probe {xstar}: "
             f"f(x*) = {fstar:.3f}, |f|_k^2 = alpha^T K alpha = {norm2:.3f}, bound |f(x*)| <= |f|_k sqrt(k(x*,x*)) = {np.sqrt(norm2):.3f}")


# --- corner against three sines: closest in L2 (= H1 for sines) and closest in sup --------
uk = lambda t: 0.5 * np.minimum(t, 1 - t)
cl2 = np.array([2 * np.sin(k * np.pi / 2) / (k * np.pi)**2 for k in (1, 2, 3)])
csup = np.array([0.2045, 0.0, -0.0318])  # Nelder-Mead on the largest gap, 20001 points
xc = np.linspace(0, 1, 801)
S3 = np.array([np.sin(k * np.pi * xc) for k in (1, 2, 3)])
save("corner_sums.dat", None, x=xc, u=uk(xc), vl2=cl2 @ S3, vsup=csup @ S3, el2=uk(xc) - cl2 @ S3, esup=uk(xc) - csup @ S3)
xd = np.linspace(0, 1, 20001); Sd = np.array([np.sin(k * np.pi * xd) for k in (1, 2, 3)])
dSd = np.array([k * np.pi * np.cos(k * np.pi * xd) for k in (1, 2, 3)]); dud = np.where(xd < 0.5, 0.5, -0.5)
for name, c in (("L2", cl2), ("sup", csup)):
    e = uk(xd) - c @ Sd; de = dud - c @ dSd
    lines.append(f"corner, {name}-closest {np.round(c, 4).tolist()}: sup {100*np.abs(e).max()/0.25:.1f} %, "
                 f"L2 {100*np.sqrt(np.trapezoid(e**2, xd))/np.sqrt(1/48):.1f} %, H1 {100*np.sqrt(np.trapezoid(de**2, xd))/0.5:.1f} %")

# --- Bernstein on the string displacement: n = 8, probe x = 0.25 --------------------------
nb, xp = 8, 0.25
hb = hills(nb, x)
cols = {f"w{k}": u(k / nb) * hb[f"h{k}"] for k in range(nb + 1)}
save("bern_disp8.dat", None, x=x, u=u(x), B=sum(cols.values()), **cols)
from math import comb
kk = np.arange(nb + 1)
save("bern_disp8_probe.dat", None, t=kk / nb, p=np.array([comb(nb, k) * xp**k * (1 - xp)**(nb - k) for k in kk]), r=u(kk / nb))
Bp = float(sum(u(k / nb) * comb(nb, k) * xp**k * (1 - xp)**(nb - k) for k in kk))
lines.append(f"Bernstein string displacement n = 8: B(0.25) = {Bp:.3f} against u(0.25) = {u(np.array([0.25]))[0]:.3f}, "
             f"largest gap {np.max(np.abs(sum(cols.values()) - u(x))):.3f}")

# --- hats on the string (5 stations) and on the square pulse (17 stations) ----------------
pulse = lambda t: ((t >= 0.3) & (t <= 0.7)).astype(float)
xh = np.linspace(0, 1, 1601)
bumpf = lambda t: 1.15 * np.exp(-90 * (t - 0.38)**2) - 0.45 * np.exp(-45 * (t - 0.76)**2)
for tag, f, m in (("string5", u, 5), ("bump17", bumpf, 17), ("pulse17", pulse, 17)):
    xi = np.linspace(0, 1, m); h = 1 / (m - 1)
    colsh = {f"h{i}": f(xi)[i] * np.maximum(0, 1 - np.abs(xh - xi[i]) / h) for i in range(m)}
    save(f"hats_{tag}.dat", None, x=xh, f=f(xh), v=np.interp(xh, xi, f(xi)), **colsh)
    save(f"hats_{tag}_nodes.dat", None, x=xi, y=f(xi))


# --- hats on the four movable nodes of the front, d = 0.02, shifts 0 and 0.3 -------------
for tag, c in (("0", 0.0), ("30", 0.30)):
    a_, b_ = 0.15 + c, 0.45 + c
    N = [0.0, a_ - d, a_ + d, b_ - d, b_ + d, 1.0]
    def nhat(j, t):
        return np.interp(t, [N[j - 1], N[j], N[j + 1]], [0.0, 1.0, 0.0], left=0.0, right=0.0)
    save(f"front_hats{tag}.dat", None, x=xff, h1=nhat(1, xff), h2=nhat(2, xff), h3=nhat(3, xff), h4=nhat(4, xff))


# --- the string problem Lu = f for the test displacement --------------------------------
f_load = lambda t: np.pi**2 * (0.8 * np.sin(np.pi * t) + 1.6 * np.sin(2 * np.pi * t) + 1.8 * np.sin(3 * np.pi * t))
save("string_load.dat", None, x=x, f=f_load(x), u=u(x))
lines.append(f"load f = -u'': max {f_load(x).max():.2f}, min {f_load(x).min():.2f}")

# --- recovering the coefficients from quarter-span readings -------------------------------
xr = np.array([0.25, 0.5, 0.75]); yr = u(xr)
A = np.array([[np.sin(k * np.pi * t) for k in (1, 2, 3)] for t in xr])
ar = np.linalg.solve(A, yr)
save("recover_readings.dat", None, x=xr, y=yr)
lines.append(f"quarter-span readings y = {np.round(yr, 4).tolist()}, recovered a = {np.round(ar, 4).tolist()}, cond(A) = {np.linalg.cond(A):.2f}")

# --- Galerkin with hats on -u'' = f for the test displacement -----------------------------
from numpy.polynomial.legendre import leggauss
gq, gw = leggauss(12)
du_ex = lambda t: 0.8*np.pi*np.cos(np.pi*t) + 0.8*np.pi*np.cos(2*np.pi*t) + 0.6*np.pi*np.cos(3*np.pi*t)
def galerkin(N):
    h = 1 / N; xn = np.linspace(0, 1, N + 1)
    K = (np.diag(2 * np.ones(N - 1)) - np.diag(np.ones(N - 2), 1) - np.diag(np.ones(N - 2), -1)) / h
    F = np.zeros(N - 1)
    for j in range(1, N):
        for lo, hi, phi in ((xn[j-1], xn[j], lambda t: (t - xn[j-1]) / h), (xn[j], xn[j+1], lambda t: (xn[j+1] - t) / h)):
            t = 0.5 * (hi - lo) * gq + 0.5 * (hi + lo)
            F[j-1] += 0.5 * (hi - lo) * np.sum(gw * f_load(t) * phi(t))
    un = np.r_[0, np.linalg.solve(K, F), 0]
    return xn, un
xn4, un4 = galerkin(4)
save("galerkin4.dat", None, x=xn4, uh=un4)
dev = max(np.max(np.abs(galerkin(N)[1] - u(galerkin(N)[0]))) for N in (4, 8, 16))
Ns = [4, 8, 16, 32, 64, 128, 256]; eL2 = []; eH1 = []
xf2 = np.linspace(0, 1, 40001)
for N in Ns:
    xn, un = galerkin(N); vh = np.interp(xf2, xn, un); dvh = np.gradient(vh, xf2)
    eL2.append(np.sqrt(np.trapezoid((u(xf2) - vh)**2, xf2))); eH1.append(np.sqrt(np.trapezoid((du_ex(xf2) - dvh)**2, xf2)))
sL2 = np.polyfit(np.log(Ns[2:]), np.log(eL2[2:]), 1)[0]; sH1 = np.polyfit(np.log(Ns[2:]), np.log(eH1[2:]), 1)[0]
save("galerkin_rates.dat", None, N=np.array(Ns, float), l2=np.array(eL2), h1=np.array(eH1))
lines.append(f"Galerkin hats on -u'' = f: largest nodal deviation over N = 4, 8, 16 = {dev:.1e}; error slopes L2 {sL2:.2f}, energy {sH1:.2f}")

# --- the kernel prior solves -u'' = f (25 collocation points, SE, ell = 0.2) -----------------
ELL, S2 = 0.2, 1.0
kuu = lambda a, b: S2 * np.exp(-(a[:, None] - b[None, :])**2 / (2 * ELL**2))
kuf = lambda a, b: kuu(a, b) * (ELL**2 - (a[:, None] - b[None, :])**2) / ELL**4
kff = lambda a, b: kuu(a, b) * (3*ELL**4 - 6*ELL**2*(a[:, None] - b[None, :])**2 + (a[:, None] - b[None, :])**4) / ELL**8
xc = np.linspace(0, 1, 27)[1:-1]; xb = np.array([0.0, 1.0]); xt = np.linspace(0, 1, 401)
Kobs = np.block([[kff(xc, xc), kuf(xb, xc).T], [kuf(xb, xc), kuu(xb, xb)]]) + 1e-8 * np.eye(27)
yobs = np.concatenate([f_load(xc), np.zeros(2)])
mu_pde = np.hstack([kuf(xt, xc), kuu(xt, xb)]) @ np.linalg.solve(Kobs, yobs)
rel_pde = np.sqrt(np.trapezoid((mu_pde - u(xt))**2, xt) / np.trapezoid(u(xt)**2, xt))
save("gp_poisson.dat", None, x=xt, mu=mu_pde, u=u(xt))
save("gp_poisson_colloc.dat", None, x=xc, y=np.zeros_like(xc))
lines.append(f"kernel prior solving -u'' = f: rel L2 error {rel_pde:.1e}, cond(K_obs) {np.linalg.cond(Kobs):.1e}")


# --- regression before kernels: twelve noisy sine readings (seed 42, as the notebook) -----
rng_state = np.random.get_state()
np.random.seed(42)
xs12 = np.linspace(-3, 3, 12)
ys12 = np.sin(xs12) + np.random.normal(0, 0.15, 12)
np.random.set_state(rng_state)
save("reg_data.dat", None, x=xs12, y=ys12)
xg = np.linspace(-3.5, 3.5, 351)
def poly_fit(deg, lam):
    P = np.vander(xs12 / 3, deg + 1, increasing=True)
    w = np.linalg.solve(P.T @ P + lam * np.eye(deg + 1), P.T @ ys12)
    return w, np.vander(xg / 3, deg + 1, increasing=True) @ w, P @ w
fits = {}
for tag, deg, lam in (("line", 1, 0.0), ("cubic", 3, 0.0), ("deg11", 11, 0.0), ("deg11ridge", 11, 1e-3)):
    w, yg, yd = poly_fit(deg, lam)
    fits[tag] = yg
    inside = (xg >= -3) & (xg <= 3)
    err_true = np.sqrt(np.mean((yg[inside] - np.sin(xg[inside]))**2))
    lines.append(f"regression {tag} (degree {deg}, lambda {lam}): RMSE at data {np.sqrt(np.mean((yd - ys12)**2)):.4f}, "
                 f"RMSE against sin on [-3,3] {err_true:.4f}, max|w| {np.max(np.abs(w)):.3g}, max|f| on [-3.5,3.5] {np.max(np.abs(yg)):.2f}")
save("reg_fits.dat", None, x=xg, s=np.sin(xg), **fits)

# --- regression on m Gaussian bumps (the notebook's visualizer): target sin(1.5x) + 0.5 sin(4x)
tgt = lambda t: np.sin(1.5 * t) + 0.5 * np.sin(4 * t)
xv = np.linspace(-3, 3, 601)
def bump_fit(m, ell, mu=1e-6):
    cs = np.linspace(-3, 3, m)
    Phi = np.exp(-(xv[:, None] - cs[None, :])**2 / (2 * ell**2))
    w = np.linalg.solve(Phi.T @ Phi / len(xv) + mu * np.eye(m), Phi.T @ tgt(xv) / len(xv))
    return cs, w, Phi
for m, ell in ((5, 0.5), (20, 0.5)):
    cs, w, Phi = bump_fit(m, ell)
    cols = {f"b{j}": w[j] * Phi[:, j] for j in range(m)}
    save(f"bumps_m{m}.dat", None, x=xv, f=tgt(xv), sum=Phi @ w, **cols)
    save(f"bumps_m{m}_centers.dat", None, x=cs, y=np.zeros(m))
    lines.append(f"bump regression m = {m}, ell = {ell}: RMSE {np.sqrt(np.mean((Phi @ w - tgt(xv))**2)):.3f}")

# --- kernel ridge with copies at the twelve readings (the notebook's part 1) -------------------
ellk, lamk = 1 / np.sqrt(3), 0.01
Kd = np.exp(-(xs12[:, None] - xs12[None, :])**2 / (2 * ellk**2))
alk = np.linalg.solve(Kd + lamk * np.eye(12), ys12)
xk = np.linspace(-4, 4, 401)
Kx = np.exp(-(xk[:, None] - xs12[None, :])**2 / (2 * ellk**2))
save("krr_copies.dat", None, x=xk, sum=Kx @ alk, s=np.sin(xk), **{f"c{i}": alk[i] * Kx[:, i] for i in range(12)})
lines.append(f"kernel ridge, copies at the 12 readings: alpha range [{alk.min():.3f}, {alk.max():.3f}], "
             f"RMSE at data {np.sqrt(np.mean((Kd @ alk - ys12)**2)):.4f}, against sin at the data {np.sqrt(np.mean((Kd @ alk - np.sin(xs12))**2)):.4f}")


# --- the norms notebook's slid copy: g(x) = u(x - s) + 0.15 sin(6 pi x), s = 0.08 ------------
xs_ = np.linspace(0, 1, 20001)
gsl = lambda t, sh: u(t - sh) + 0.15 * np.sin(6 * np.pi * t)
save("slid_copy.dat", None, x=x, u=u(x), g=gsl(x, 0.08))
d_l2 = np.sqrt(np.trapezoid((u(xs_) - gsl(xs_, 0.08))**2, xs_)); d_int = np.trapezoid(u(xs_) - gsl(xs_, 0.08), xs_)
lines.append(f"slid copy s = 0.08: L2 distance {d_l2:.3f}, signed integral of the gap {d_int:.4f}")

# --- function spaces: members of L2 and H1 ---------------------------------------------------
xp = np.linspace(1e-4, 1, 2000)
save("l2_members.dat", None, x=xp, step=(xp >= 0.5).astype(float), cube=np.minimum(xp**(-1/3), 6), half=np.minimum(xp**(-0.5), 6))
from scipy.integrate import quad
i_cube = quad(lambda t: t**(-2/3), 0, 1)[0]
lines.append(f"int_0^1 x^(-2/3) dx = {i_cube:.4f} (so x^(-1/3) is in L2 with norm {np.sqrt(i_cube):.4f}); int x^(-1) diverges")
xw = np.linspace(0, 1, 4001)
for w in (0.2, 0.05):
    ramp = np.clip((xw - 0.5) / w + 0.5, 0, 1)
    save(f"ramp_w{int(w*100)}.dat", None, x=xw, r=ramp, dr=np.gradient(ramp, xw))
    lines.append(f"ramp width {w}: slope {1/w:.0f}, integral of the squared slope {np.trapezoid(np.gradient(ramp, xw)**2, xw):.2f} (1/w = {1/w:.0f})")
save("corner_slope.dat", None, x=xw, u=0.5 * np.minimum(xw, 1 - xw), du=np.where(xw < 0.5, 0.5, -0.5))
for k in (1, 4, 16):
    save(f"mode{k}.dat", None, x=xw, v=np.sqrt(2) * np.sin(k * np.pi * xw))
    lines.append(f"mode sqrt(2) sin({k} pi x): L2 norm {np.sqrt(np.trapezoid(2*np.sin(k*np.pi*xw)**2, xw)):.3f}, H1 seminorm {np.sqrt(np.trapezoid(2*(k*np.pi*np.cos(k*np.pi*xw))**2, xw)):.2f}")
lines.append(f"distance between two different unit modes: {np.sqrt(np.trapezoid(2*(np.sin(np.pi*xw)-np.sin(2*np.pi*xw))**2, xw)):.4f} (sqrt 2 = {np.sqrt(2):.4f})")
for M, K in ((10, 4), (10, 16)):
    lines.append(f"compactness bound, |u|_H1 <= {M}: tail beyond mode {K} has L2 norm <= M/((K+1) pi) = {M/((K+1)*np.pi):.3f}")

# --- regularity: three loads on the pinned string -----------------------------------------
xr_ = np.linspace(0, 1, 2001)
G = lambda t, s_: np.where(t <= s_, t * (1 - s_), s_ * (1 - t))
fstep = np.where(xr_ < 0.5, 2.0, 0.0)
w_ = np.gradient(xr_); u_step = np.array([np.trapezoid(G(t, xr_) * fstep, xr_) for t in xr_])
save("reg_loads.dat", None, x=xr_,
     up=0.5 * np.minimum(xr_, 1 - xr_), dup=np.where(xr_ < 0.5, 0.5, -0.5),
     us=u_step, dus=np.gradient(u_step, xr_), ddus=-fstep,
     uu=xr_ * (1 - xr_), duu=1 - 2 * xr_, dduu=-2 * np.ones_like(xr_))
lines.append(f"step load 2 on [0, 1/2): displacement peak {u_step.max():.4f} at x = {xr_[u_step.argmax()]:.3f}")


# --- from functions to fields: a membrane on the unit square, -Laplacian(u) = f ------------
um = lambda X, Y: (0.8 * np.sin(np.pi*X) * np.sin(np.pi*Y) + 0.4 * np.sin(2*np.pi*X) * np.sin(np.pi*Y)
                   + 0.2 * np.sin(np.pi*X) * np.sin(3*np.pi*Y))
fm = lambda X, Y: np.pi**2 * (0.8*2 * np.sin(np.pi*X) * np.sin(np.pi*Y) + 0.4*5 * np.sin(2*np.pi*X) * np.sin(np.pi*Y)
                   + 0.2*10 * np.sin(np.pi*X) * np.sin(3*np.pi*Y))
n41 = 41; g1 = np.linspace(0, 1, n41); GX, GY = np.meshgrid(g1, g1, indexing="xy")
def save_grid(name, Z):
    save(name, None, x=GX.ravel(), y=GY.ravel(), z=Z.ravel())
save_grid("membrane_u.dat", um(GX, GY)); save_grid("membrane_f.dat", fm(GX, GY))
fine = np.linspace(0, 1, 401); FX, FY = np.meshgrid(fine, fine, indexing="xy"); UF = um(FX, FY); umax = np.abs(UF).max()
from scipy.interpolate import RegularGridInterpolator
for m in (5, 9, 17):
    gm = np.linspace(0, 1, m); VX, VY = np.meshgrid(gm, gm, indexing="ij")
    rgi = RegularGridInterpolator((gm, gm), um(VX, VY), method="linear")
    V = rgi(np.stack([FX.ravel(), FY.ravel()], -1)).reshape(FX.shape)
    lines.append(f"membrane, bilinear on {m} x {m} = {m*m} values: largest gap {100*np.abs(V-UF).max()/umax:.1f} % of max|u| = {umax:.3f}")
    if m == 5:
        V41 = rgi(np.stack([GX.ravel(), GY.ravel()], -1)).reshape(GX.shape)
        save_grid("membrane_bilinear5.dat", V41)
        save("membrane_nodes5.dat", None, x=VX.ravel(), y=VY.ravel(), z=um(VX, VY).ravel())
lines.append(f"membrane load max {fm(FX, FY).max():.2f}; values per direction 17: line 17, plate {17**2}, solid {17**3}")
for (j, k) in ((1, 1), (2, 1), (1, 3)):
    save_grid(f"mode2d_{j}{k}.dat", np.sin(j*np.pi*GX) * np.sin(k*np.pi*GY))
# a piecewise-linear hat on a triangulated grid, node at the centre, spacing h = 0.25
hh = 0.25; U_ = (GX - 0.5) / hh; V_ = (GY - 0.5) / hh
save_grid("hat2d.dat", np.maximum(0, 1 - np.maximum(np.maximum(np.abs(U_), np.abs(V_)), np.abs(U_ - V_))))

# --- H1_0 and the Poincare inequality on (0,1): ||u||_L2 <= (1/pi) |u|_H1 when u(0) = u(1) = 0 ----
xp = np.linspace(0, 1, 200001)
def l2(v): return np.sqrt(np.trapz(v**2, xp))
pinned = {
    "sin(pi x)": (np.sin(np.pi*xp), np.pi*np.cos(np.pi*xp)),
    "corner min(x,1-x)/2": (np.minimum(xp, 1-xp)/2, np.where(xp < 0.5, 0.5, -0.5)),
    "test displacement": (0.8*np.sin(np.pi*xp) + 0.4*np.sin(2*np.pi*xp) + 0.2*np.sin(3*np.pi*xp),
                          np.pi*(0.8*np.cos(np.pi*xp) + 0.8*np.cos(2*np.pi*xp) + 0.6*np.cos(3*np.pi*xp))),
}
lines.append(f"Poincare constant on (0,1): 1/pi = {1/np.pi:.4f}; norm equivalence factor sqrt(1 + 1/pi^2) = {np.sqrt(1 + 1/np.pi**2):.4f}")
for name, (v, dv) in pinned.items():
    lines.append(f"Poincare ratio ||u||_L2 / |u|_H1 for {name}: {l2(v):.4f} / {l2(dv):.4f} = {l2(v)/l2(dv):.4f}")
lines.append("constant 1 on (0,1): ||u||_L2 = 1, |u|_H1 = 0, so the inequality fails without the pinned ends")
save("poincare.dat", None, x=xp[::2000], sine=np.sin(np.pi*xp[::2000]), corner=np.minimum(xp, 1-xp)[::2000]/2,
     one=np.ones_like(xp[::2000]))

with open(os.path.join(HERE, "build_slide_data-report.md"), "w") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
print("wrote", len(os.listdir(OUT)), "tables to", OUT)
