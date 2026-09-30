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
for m in (5, 9, 17):
    xi = np.linspace(0, 1, m)
    save(f"readings{m}.dat", None, x=xi, u=u(xi))
    v = np.interp(x, xi, u(xi))
    save(f"segments{m}.dat", None, x=x, v=v, gap=u(x) - v)
    lines.append(f"m = {m}: largest gap / largest displacement = {100*np.max(np.abs(u(x)-v))/umax:.1f} %")
# gap bars at m = 5 on a coarse grid
xb = np.linspace(0, 1, 41)
xi5 = np.linspace(0, 1, 5)
save("gaps5.dat", None, x=xb, u=u(xb), v=np.interp(xb, xi5, u(xi5)))
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
save("parab_interp.dat", None, x=np.r_[0, nodes, 1], v=np.r_[0, nodes * (1 - nodes), 0])
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
    save(f"front{tag}.dat", None, x=xff, T=T, seg=seg, net=net)
    rel = lambda v: np.sqrt(np.trapezoid((v - T)**2, xff) / np.trapezoid(T**2, xff))
    lines.append(f"front shift {c}: stations {100*rel(seg):.1f} %, kinks {100*rel(net):.1f} %")
save("stations32.dat", None, x=np.linspace(0, 1, 32), y=np.zeros(32) - 0.1)
save("kinks.dat", None, c=np.array([0.0, 0.15, 0.30]), k1=0.15 - d + np.array([0.0, 0.15, 0.30]),
     k2=0.15 + d + np.array([0.0, 0.15, 0.30]), k3=0.45 - d + np.array([0.0, 0.15, 0.30]), k4=0.45 + d + np.array([0.0, 0.15, 0.30]))

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

with open(os.path.join(HERE, "build_slide_data-report.md"), "w") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
print("wrote", len(os.listdir(OUT)), "tables to", OUT)
