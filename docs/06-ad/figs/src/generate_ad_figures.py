"""Figures and numbers for ad-slides.tex.

Every number quoted on the slides is asserted or printed here, and the printed lines are saved in
generate_ad_figures-report.txt. The optimizers follow gradients-and-optimizers.js line by line, and
page_numbers.js runs that file under Node for the numbers that need its seeded noise.
"""
import base64
import io
import json
import math
from contextlib import redirect_stdout
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import torch
from scipy.integrate import quad
from sklearn.linear_model import Lasso

out = Path(__file__).resolve().parents[1]
root = out.parent
torch.set_default_dtype(torch.float64)
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .15, 'axes.facecolor': 'none',
                     'savefig.transparent': True})
green, purple, orange, ink, blue, gray = '#399e89', '#7251a1', '#db6a20', '#253349', '#4d85ca', '#8a8f98'
OPT_COLORS = {'gd': '#52514e', 'adam': '#2a78d6', 'newton': '#eb6834', 'lbfgs': '#1baf7a'}
OPT_NAMES = {'gd': 'Gradient descent', 'adam': 'Adam', 'newton': 'Newton', 'lbfgs': 'L-BFGS'}
UPDATE_COLORS = {'Gradient descent': '#2f6fb5', 'Newton': '#db6a20',
                 'Inverse gradient': '#7251a1', 'Inverse simulator': '#008577'}
report = io.StringIO()


def say(*args):
    line = ' '.join(str(a) for a in args)
    print(line)
    report.write(line + '\n')


def save(fig, name):
    fig.set_size_inches(fig.get_size_inches()*0.8)     # same fonts on a smaller canvas, to read on a slide
    fig.tight_layout()
    fig.savefig(out/name, dpi=220)
    plt.close(fig)


# =====================================================================================
# 1. The projectile, its tape, and the gradient
# =====================================================================================
G, DEG = 9.81, math.pi/180
V_TRUE, A_TRUE = 20.0, 50.0
V0, A0 = 15.0, 35.0


def apex(v, a_deg):
    t = a_deg*DEG
    return np.array([v*v*np.sin(2*t)/(2*G), v*v*np.sin(t)**2/(2*G)])


APEX_TRUE = apex(V_TRUE, A_TRUE)
TAPE_NAMES = ['v', 'a', 'theta', 's', 'c', 'q', 'p', 'x', 'z', 'r1', 'r2', 'L']


def tape(v, a_deg):
    th = a_deg*DEG
    s, c, q = math.sin(th), math.cos(th), v*v
    p = q*s
    x, z = p*c/G, p*s/(2*G)
    r1, r2 = x - APEX_TRUE[0], z - APEX_TRUE[1]
    val = [v, a_deg, th, s, c, q, p, x, z, r1, r2, 0.5*(r1*r1 + r2*r2)]

    def forward(dv, da):
        dth = da*DEG
        ds, dc, dq = c*dth, -s*dth, 2*v*dv
        dp = dq*s + q*ds
        dx, dz = (dp*c + p*dc)/G, (dp*s + p*ds)/(2*G)
        return [dv, da, dth, ds, dc, dq, dp, dx, dz, dx, dz, r1*dx + r2*dz]

    def reverse():
        bL = 1.0
        br2, br1 = bL*r2, bL*r1
        bz, bx = br2, br1
        bp = bx*c/G + bz*s/(2*G)
        bq, bc, bs = bp*s, bx*p/G, bp*q + bz*p/(2*G)
        bth = bs*c - bc*s
        return [2*v*bq, bth*DEG, bth, bs, bc, bq, bp, bx, bz, br1, br2, bL]

    return val, forward, reverse


def loss_torch(params):
    v, th = params[0], params[1]*DEG
    top = torch.stack([v*v*torch.sin(2*th)/(2*G), v*v*torch.sin(th)**2/(2*G)])
    return 0.5*((top - torch.tensor(APEX_TRUE))**2).sum()


val, forward, reverse = tape(V0, A0)
tangent_v, tangent_a, adjoint = forward(1, 0), forward(0, 1), reverse()
p0 = torch.tensor([V0, A0], requires_grad=True)
grad_torch = torch.autograd.grad(loss_torch(p0), p0)[0].numpy()
hess_torch = torch.autograd.functional.hessian(loss_torch, torch.tensor([V0, A0])).numpy()
assert np.allclose(grad_torch, adjoint[:2], rtol=1e-12)
assert np.allclose([tangent_v[-1], tangent_a[-1]], adjoint[:2], rtol=1e-12)
say('--- projectile tape at v = 15 m/s, a = 35 deg; observed top from v = 20, a = 50')
say(f'observed top = ({APEX_TRUE[0]:.3f}, {APEX_TRUE[1]:.3f}) m, current top = ({val[7]:.3f}, {val[8]:.3f}) m')
say(f'{"row":<6}{"value":>12}{"tangent, seed v":>18}{"tangent, seed a":>18}{"adjoint":>12}')
for name, w, tv, ta, bar in zip(TAPE_NAMES, val, tangent_v, tangent_a, adjoint):
    say(f'{name:<6}{w:>12.4f}{tv:>18.4f}{ta:>18.4f}{bar:>12.4f}')
J = np.array([[tangent_v[7], tangent_a[7]], [tangent_v[8], tangent_a[8]]])
residual = np.array([val[9], val[10]])
assert np.allclose(J.T @ residual, adjoint[:2])
say(f'J = [[{J[0, 0]:.4f}, {J[0, 1]:.4f}], [{J[1, 0]:.4f}, {J[1, 1]:.4f}]], r = ({residual[0]:.3f}, {residual[1]:.3f})')
say(f'grad L = J^T r = ({adjoint[0]:.3f} per m/s, {adjoint[1]:.3f} per degree) = '
    f'({adjoint[0]:.3f}, {adjoint[1]/DEG:.1f} per radian)')
newton_step = -np.linalg.solve(hess_torch, grad_torch)
say(f'Newton step at the start = ({newton_step[0]:.2f} m/s, {newton_step[1]:.2f} deg)')


def arc(v, a_deg, n=200):
    t = np.linspace(0, 2*v*math.sin(a_deg*DEG)/G, n)
    return v*math.cos(a_deg*DEG)*t, v*math.sin(a_deg*DEG)*t - 0.5*G*t**2


def draw_arcs(ax, labels=True):
    ax.plot(*arc(V_TRUE, A_TRUE), color=ink, lw=1.5, ls='--')
    ax.plot(*arc(V0, A0), color=blue, lw=2.2)
    ax.plot(*APEX_TRUE, 'o', color=ink, ms=7)
    ax.plot(val[7], val[8], 'o', color=blue, ms=7)
    if labels:
        ax.annotate('observed top', APEX_TRUE, xytext=(6, 8), textcoords='offset points', color=ink, fontsize=10)
        ax.text(11.2, 0.9, 'top for $v=15$ m/s, $a=35^\\circ$', color=ink, fontsize=10, ha='center')
    ax.set(xlabel='distance (m)', ylabel='height (m)', xlim=(0, 42), ylim=(0, 14), aspect='equal')


fig, ax = plt.subplots(figsize=(7.2, 2.9))
draw_arcs(ax)
ax.annotate('', APEX_TRUE, (val[7], val[8]), arrowprops=dict(arrowstyle='->', color=orange, lw=2))
ax.text(13.0, 8.6, '$-\\mathbf{r}$', color=ink, fontsize=12)
save(fig, 'projectile-arcs.png')

fig, axes = plt.subplots(1, 2, figsize=(11, 3.7), gridspec_kw={'width_ratios': [1.25, 1]})
draw_arcs(axes[0], labels=False)
axes[0].set(xlim=(0, 60))
top = np.array([val[7], val[8]])
for column, scale, color, label in [(J[:, 0], 2, green, '$J\\,\\delta$ for $\\delta v=2$ m/s'),
                                    (J[:, 1], 10, purple, '$J\\,\\delta$ for $\\delta a=10^\\circ$')]:
    axes[0].annotate('', top + scale*column, top, arrowprops=dict(arrowstyle='->', color=color, lw=2.2))
    axes[0].plot([], [], color=color, lw=2.2, label=label)
axes[0].annotate('', APEX_TRUE, top, arrowprops=dict(arrowstyle='->', color=orange, lw=1.6, ls=':'))
axes[0].plot([], [], color=orange, lw=1.6, ls=':', label='$-\\mathbf{r}$')
axes[0].legend(fontsize=9, loc='center right', frameon=False)
axes[0].set_title('The top of the arc moves by $J\\,\\delta$', fontsize=11)
vv, aa = np.meshgrid(np.linspace(5, 35, 181), np.linspace(5, 85, 181))
tops = np.stack([vv*vv*np.sin(2*aa*DEG)/(2*G), vv*vv*np.sin(aa*DEG)**2/(2*G)])
LL = 0.5*((tops - APEX_TRUE[:, None, None])**2).sum(axis=0)
axes[1].contour(vv, aa, LL, levels=np.geomspace(0.5, 4000, 14), colors=ink, linewidths=0.6, alpha=0.45)
axes[1].plot(V_TRUE, A_TRUE, '*', color=ink, ms=12)
axes[1].plot(V0, A0, 'o', color=blue, ms=7)
axes[1].annotate('', (V0 - 0.45*adjoint[0], A0 - 0.45*adjoint[1]), (V0, A0),
                 arrowprops=dict(arrowstyle='->', color=orange, lw=2.2))
axes[1].text(15.4, 26.5, '$-\\nabla L=-J^T\\mathbf{r}$', color=ink, fontsize=10)
axes[1].set(xlabel='$v$ (m/s)', ylabel='$a$ (degrees)', title='The loss $L(v,a)$')
axes[1].title.set_fontsize(11)
save(fig, 'projectile-gradient.png')

# the same descent direction with a in degrees and in radians, and the Newton step
fig, ax = plt.subplots(figsize=(5.6, 3.9))
ax.contour(vv, aa, LL, levels=np.geomspace(0.5, 4000, 14), colors=ink, linewidths=0.6, alpha=0.45)
ax.plot(V_TRUE, A_TRUE, '*', color=ink, ms=12)
ax.plot(V0, A0, 'o', color=blue, ms=7)
step_deg = -np.array(adjoint[:2])                                  # parameters (v, a in degrees)
step_rad = -np.array([adjoint[0], adjoint[1]/DEG/DEG])             # parameters (v, a in radians), drawn in degrees
for vec, color, label in [(step_deg, orange, '$-\\nabla L$ with $a$ in degrees'),
                          (step_rad, purple, '$-\\nabla L$ with $a$ in radians')]:
    shown = vec*(0.28/np.hypot(*(vec/np.array([30, 80]))))           # equal lengths on the plot
    ax.annotate('', (V0 + shown[0], A0 + shown[1]), (V0, A0), arrowprops=dict(arrowstyle='->', color=color, lw=2.2))
    ax.plot([], [], color=color, lw=2.2, label=label)
ax.legend(fontsize=9, loc='lower right', frameon=False)
ax.set(xlabel='$v$ (m/s)', ylabel='$a$ (degrees)', xlim=(5, 35), ylim=(5, 85))
save(fig, 'units-gradient.png')
angle_deg = math.degrees(math.atan2(step_deg[1]/80, step_deg[0]/30))
angle_rad = math.degrees(math.atan2(step_rad[1]/80, step_rad[0]/30))
say(f'descent direction on the plot: {angle_deg:.1f} deg from the v axis with a in degrees, {angle_rad:.1f} deg with a in radians')

# =====================================================================================
# 2. Finite differences and symbolic differentiation
# =====================================================================================
def loss_v(v):
    return tape(v, A0)[0][-1]


exact = adjoint[0]
hs = 10.0**np.linspace(-14, 0, 113)
forward_error = np.array([abs((loss_v(V0 + h) - loss_v(V0))/h - exact)/abs(exact) for h in hs])
central_error = np.array([abs((loss_v(V0 + h) - loss_v(V0 - h))/(2*h) - exact)/abs(exact) for h in hs])
ad_error = max(abs(grad_torch[0] - exact)/abs(exact), 1.1e-16)
fig, ax = plt.subplots(figsize=(6.4, 3.5))
ax.loglog(hs, forward_error, color=blue, lw=1.8, label='forward difference')
ax.loglog(hs, np.maximum(central_error, 1e-17), color=green, lw=1.8, label='central difference')
ax.axhline(1.1e-16, color=orange, lw=1.8, ls='--', label='automatic differentiation')
ax.set(xlabel='step $h$ (m/s)', ylabel='relative error in $\\partial L/\\partial v$', ylim=(1e-17, 10))
ax.legend(fontsize=9, frameon=False, loc='lower left', bbox_to_anchor=(0.0, 0.1))
save(fig, 'fd-error.png')
i_f, i_c = forward_error.argmin(), central_error.argmin()
say('--- finite differences of dL/dv at v = 15, a = 35')
say(f'forward difference: best relative error {forward_error[i_f]:.1e} at h = {hs[i_f]:.0e}')
say(f'central difference: best relative error {central_error[i_c]:.1e} at h = {hs[i_c]:.0e}')
say(f'forward difference at h = 1e-2: {forward_error[np.argmin(abs(hs - 1e-2))]:.1e}, at h = 1e-13: {forward_error[np.argmin(abs(hs - 1e-13))]:.1e}')
say(f'reverse-mode AD against the tape formula: relative difference {abs(grad_torch[0] - exact)/abs(exact):.1e}')

xs = sp.Symbol('x')
expr = xs
say('--- symbolic differentiation of the logistic iterates l_{n+1} = 4 l_n (1 - l_n), l_1 = x')
say(f'{"n":<4}{"operations in l_n":>20}{"operations in dl_n/dx":>24}{"tape rows for AD":>20}')
swell = []
for n in range(1, 8):
    derivative = sp.diff(expr, xs)
    swell.append((n, sp.count_ops(expr), sp.count_ops(derivative), 3*(n - 1)))
    say(f'{n:<4}{swell[-1][1]:>20}{swell[-1][2]:>24}{swell[-1][3]:>20}')
    expr = 4*expr*(1 - expr)

# =====================================================================================
# 3. The adjoint equation of dy/dt = -k y against reverse mode through Euler steps
# =====================================================================================
K_ODE, Y0, T_END, K_DATA = 1.0, 1.0, 2.0, 2.0


def y_exact(t, k=K_ODE):
    return Y0*np.exp(-k*t)


def d_data(t):
    return np.exp(-K_DATA*t)


def p_exact(t):
    # p(t) = integral from t to T of 2 (y - d)(s) exp(-k (s - t)) ds, the solution of -p' = -k p + 2 (y - d), p(T) = 0
    return quad(lambda s: 2*(y_exact(s) - d_data(s))*np.exp(-K_ODE*(s - t)), t, T_END)[0]


cost = lambda k, y0=Y0: quad(lambda t: (y0*np.exp(-k*t) - d_data(t))**2, 0, T_END)[0]
dJ_dk_direct = quad(lambda t: 2*(y_exact(t) - d_data(t))*(-t*y_exact(t)), 0, T_END)[0]
dJ_dk_adjoint = -quad(lambda t: p_exact(t)*y_exact(t), 0, T_END)[0]
dJ_dy0_direct = (cost(K_ODE, Y0 + 1e-6) - cost(K_ODE, Y0 - 1e-6))/2e-6
assert abs(dJ_dk_direct - dJ_dk_adjoint) < 1e-9
assert abs(dJ_dy0_direct - p_exact(0.0)) < 1e-8
say('--- adjoint of dy/dt = -k y, J = int (y - d)^2 dt, k = 1, y0 = 1, T = 2, d = exp(-2t)')
say(f'dJ/dk from the definition = {dJ_dk_direct:.6f}, from -int p y dt = {dJ_dk_adjoint:.6f}')
say(f'dJ/dy0 by finite difference = {dJ_dy0_direct:.6f}, p(0) = {p_exact(0.0):.6f}')


def euler_cost(k, n):
    dt = T_END/n
    y, total = torch.as_tensor(Y0), 0.0
    for i in range(n):
        total = total + dt*(y - math.exp(-K_DATA*i*dt))**2
        y = y - dt*k*y
    return total


for n in [100, 1000]:
    k_t = torch.tensor(K_ODE, requires_grad=True)
    ad = torch.autograd.grad(euler_cost(k_t, n), k_t)[0].item()
    fd = (euler_cost(torch.tensor(K_ODE + 1e-6), n) - euler_cost(torch.tensor(K_ODE - 1e-6), n)).item()/2e-6
    say(f'Euler with {n} steps: reverse mode {ad:.6f}, finite difference {fd:.6f}, '
        f'|AD - FD| = {abs(ad - fd):.1e}, |AD - continuous| = {abs(ad - dJ_dk_direct):.1e}')

ts = np.linspace(0, T_END, 201)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.1))
axes[0].plot(ts, y_exact(ts), color=blue, lw=2, label='$y(t)$, $k=1$')
axes[0].plot(ts, d_data(ts), color=ink, lw=1.5, ls='--', label='data $d(t)$')
axes[0].fill_between(ts, y_exact(ts), d_data(ts), color=blue, alpha=0.12)
axes[0].set(xlabel='time $t$', title='Forward in time')
axes[0].legend(fontsize=9, frameon=False)
axes[1].plot(ts, [p_exact(t) for t in ts], color=orange, lw=2)
axes[1].annotate('', (0.3, 0.07), (1.2, 0.07), arrowprops=dict(arrowstyle='->', color=ink, lw=1.2))
axes[1].text(0.75, 0.085, 'solved backward', color=ink, fontsize=10, ha='center')
axes[1].plot([T_END], [0], 'o', color=orange, ms=6)
axes[1].annotate('$p(T)=0$', (T_END, 0), xytext=(-18, 22), textcoords='offset points', color=ink, fontsize=10,
                 ha='center')
axes[1].set(xlabel='time $t$', title='The adjoint $p(t)$')
for ax in axes:
    ax.title.set_fontsize(11)
save(fig, 'adjoint-ode.png')

# =====================================================================================
# 4. Four optimizers, following gradients-and-optimizers.js
# =====================================================================================
def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]


def norm(a):
    return math.hypot(a[0], a[1])


def matvec(A, x):
    return [A[0][0]*x[0] + A[0][1]*x[1], A[1][0]*x[0] + A[1][1]*x[1]]


def inv2(A):
    d = A[0][0]*A[1][1] - A[0][1]*A[1][0]
    return [[A[1][1]/d, -A[0][1]/d], [-A[1][0]/d, A[0][0]/d]]


def valley(alpha, phi_deg):
    p = phi_deg*DEG
    c, s, l1, l2 = math.cos(p), math.sin(p), 1.0, alpha*alpha
    H = [[l1*c*c + l2*s*s, (l1 - l2)*c*s], [(l1 - l2)*c*s, l1*s*s + l2*c*c]]
    start = [c*-1.6 - s*1.1, s*-1.6 + c*1.1]
    return dict(f=lambda x: 0.5*dot(x, matvec(H, x)), grad=lambda x: matvec(H, x), hess=lambda x: H,
                dom=[[-2, 2], [-2, 2]], start=start, eta=0.025, lr=0.1)


def rosenbrock():
    return dict(f=lambda x: (1 - x[0])**2 + 100*(x[1] - x[0]*x[0])**2,
                grad=lambda x: [-2*(1 - x[0]) - 400*x[0]*(x[1] - x[0]*x[0]), 200*(x[1] - x[0]*x[0])],
                hess=lambda x: [[2 - 400*x[1] + 1200*x[0]*x[0], -400*x[0]], [-400*x[0], 200]],
                dom=[[-2, 2], [-1, 3]], start=[-1.2, 1.0], eta=0.001, lr=0.1)


def double_well():
    return dict(f=lambda x: 0.25*(x[0]*x[0] - 1)**2 + x[1]*x[1],
                grad=lambda x: [x[0]*(x[0]*x[0] - 1), 2*x[1]],
                hess=lambda x: [[3*x[0]*x[0] - 1, 0.0], [0.0, 2.0]],
                dom=[[-2, 2], [-2, 2]], start=[0.3, 1.2], eta=0.3, lr=0.1)


def projectile(mode):
    target = APEX_TRUE if mode == 'apex' else np.array([V_TRUE*V_TRUE*math.sin(2*A_TRUE*DEG)/G])

    def observe(p):
        v, th = p[0], p[1]*DEG
        if mode == 'apex':
            return torch.stack([v*v*torch.sin(2*th)/(2*G), v*v*torch.sin(th)**2/(2*G)])
        return torch.stack([v*v*torch.sin(2*th)/G])

    def f_torch(p):
        return 0.5*((observe(p) - torch.tensor(target))**2).sum()

    def grad(x):
        p = torch.tensor(x, requires_grad=True)
        return torch.autograd.grad(f_torch(p), p)[0].tolist()

    return dict(f=lambda x: f_torch(torch.tensor(x)).item(), grad=grad,
                hess=lambda x: torch.autograd.functional.hessian(f_torch, torch.tensor(x)).tolist(),
                dom=[[5, 35], [5, 85]], start=[15.0, 35.0], eta=0.1, lr=0.5)


def outside(dom, x):
    wx, wy = dom[0][1] - dom[0][0], dom[1][1] - dom[1][0]
    return x[0] < dom[0][0] - wx or x[0] > dom[0][1] + wx or x[1] < dom[1][0] - wy or x[1] > dom[1][1] + wy


def optimize(land, kind, max_steps=500, memory=5):
    """Return the path, the loss history, the final status, and the quadratic model used at each step."""
    f, grad, hess = land['f'], land['grad'], land['hess']
    x, k, status = list(land['start']), 0, 'running'
    path, models = [list(x)], []
    m, v, pairs = [0.0, 0.0], [0.0, 0.0], []
    g = grad(x)
    fx = f(x)

    def finish(x_new):
        nonlocal x, k, status
        x, k = x_new, k + 1
        path.append(list(x))
        value = f(x)
        if not all(map(math.isfinite, [value, *x])):
            status = 'diverged'
        elif outside(land['dom'], x):
            status = 'left the plot'
        elif k >= max_steps:
            status = 'step limit'

    def apply_h(q):
        al, r = [0.0]*len(pairs), list(q)
        for i in reversed(range(len(pairs))):
            s, y, rho = pairs[i]
            al[i] = rho*dot(s, r)
            r = [r[0] - y[0]*al[i], r[1] - y[1]*al[i]]
        gamma = dot(pairs[-1][0], pairs[-1][1])/dot(pairs[-1][1], pairs[-1][1]) if pairs else 1/max(norm(g), 1e-12)
        r = [r[0]*gamma, r[1]*gamma]
        for i, (s, y, rho) in enumerate(pairs):
            b = rho*dot(y, r)
            r = [r[0] + s[0]*(al[i] - b), r[1] + s[1]*(al[i] - b)]
        return r

    while status == 'running':
        if kind == 'gd':
            g = grad(x)
            eta = land['eta']
            d = [-eta*g[0], -eta*g[1]]
            models.append((list(x), g, [[1/eta, 0], [0, 1/eta]], d))
            if norm(g) < 1e-12:
                status = 'stationary point'
            finish([x[0] + d[0], x[1] + d[1]])
        elif kind == 'adam':
            g = grad(x)
            b1, b2, eps, t, lr = 0.9, 0.999, 1e-8, k + 1, land['lr']
            m = [b1*m[0] + (1 - b1)*g[0], b1*m[1] + (1 - b1)*g[1]]
            v = [b2*v[0] + (1 - b2)*g[0]**2, b2*v[1] + (1 - b2)*g[1]**2]
            mh = [m[0]*(1/(1 - b1**t)), m[1]*(1/(1 - b1**t))]
            vh = [v[0]*(1/(1 - b2**t)), v[1]*(1/(1 - b2**t))]
            den = [math.sqrt(vh[0]) + eps, math.sqrt(vh[1]) + eps]
            d = [-lr*mh[0]/den[0], -lr*mh[1]/den[1]]
            models.append((list(x), mh, [[den[0]/lr, 0], [0, den[1]/lr]], d))
            finish([x[0] + d[0], x[1] + d[1]])
        elif kind == 'newton':
            g, H = grad(x), hess(x)
            scale = abs(H[0][0]) + abs(H[1][1]) + abs(H[0][1])
            if abs(H[0][0]*H[1][1] - H[0][1]*H[1][0]) < 1e-12*scale*scale:
                status = 'Hessian singular'
                break
            if norm(g) < 1e-12:
                status = 'stationary point'
                break
            step = matvec(inv2(H), g)
            d = [-step[0], -step[1]]
            models.append((list(x), g, H, d))
            finish([x[0] + d[0], x[1] + d[1]])
        else:
            if norm(g) < 1e-12:
                status = 'stationary point'
                break
            hg = apply_h(g)
            d, reset = [-hg[0], -hg[1]], False
            if dot(g, d) >= 0:
                reset, d = True, [-g[0]/max(norm(g), 1e-12), -g[1]/max(norm(g), 1e-12)]
            if reset:
                Hk = [[1/norm(g), 0], [0, 1/norm(g)]]
            else:
                c1, c2 = apply_h([1.0, 0.0]), apply_h([0.0, 1.0])
                Hk = [[c1[0], c2[0]], [c1[1], c2[1]]]
            slope, t, ok = dot(g, d), 1.0, False
            for _ in range(40):
                xt = [x[0] + d[0]*t, x[1] + d[1]*t]
                ft = f(xt)
                if math.isfinite(ft) and ft <= fx + 1e-4*t*slope:
                    ok = True
                    break
                t *= 0.5
            models.append((list(x), g, inv2(Hk), [d[0]*t, d[1]*t]))
            if reset:
                pairs = []
            if not ok:
                status, k = 'line search failed', k + 1
                path.append(list(x))
                break
            g_new = grad(xt)
            s, y = [xt[0] - x[0], xt[1] - x[1]], [g_new[0] - g[0], g_new[1] - g[1]]
            if dot(s, y) > 1e-10*norm(s)*norm(y):
                pairs.append((s, y, 1/dot(s, y)))
                if len(pairs) > memory:
                    pairs.pop(0)
            g, fx = g_new, ft
            finish(xt)
    values = [f(p) for p in path]
    hit = next((i for i, value in enumerate(values) if value < 1e-6), None)
    return dict(path=np.array(path), values=values, status=status, steps=k, hit=hit, models=models)


def run_all(land):
    return {kind: optimize(land, kind) for kind in OPT_NAMES}


def describe(label, runs):
    say(f'--- {label}')
    for kind, r in runs.items():
        end = r['path'][-1]
        say(f'{OPT_NAMES[kind]:<17} loss < 1e-6 at step {str(r["hit"]):>4}, {r["steps"]:>3} steps, {r["status"]:<17} '
            f'end ({end[0]:.4f}, {end[1]:.4f}), loss {r["values"][-1]:.2e}')


valley0, valley45 = run_all(valley(8, 0)), run_all(valley(8, 45))
describe('narrow valley L = (x1^2 + 64 x2^2)/2, start (-1.6, 1.1), eta = 0.025, lr = 0.1', valley0)
describe('the same valley and start rotated by 45 degrees', valley45)
assert [valley0[k]['hit'] for k in OPT_NAMES] == [278, 132, 1, 8]
assert [valley45[k]['hit'] for k in OPT_NAMES] == [278, 411, 1, 8]
rosen, well = run_all(rosenbrock()), run_all(double_well())
describe('Rosenbrock, start (-1.2, 1), eta = 0.001, lr = 0.1', rosen)
describe('double well L = (x1^2 - 1)^2/4 + x2^2, start (0.3, 1.2), eta = 0.3, lr = 0.1', well)
say('Newton on Rosenbrock, loss by step: ' + ', '.join(f'{value:.3f}' for value in rosen['newton']['values'][:6]))
assert rosen['newton']['steps'] == 7 and rosen['lbfgs']['steps'] == 42
assert abs(rosen['newton']['values'][2] - 1411.845) < 1e-3 and abs(rosen['newton']['values'][1] - 4.732) < 1e-3
assert well['newton']['status'] == 'stationary point' and np.allclose(well['newton']['path'][-1], 0, atol=1e-9)
top_runs, landing_runs = run_all(projectile('apex')), run_all(projectile('landing'))
describe('projectile, top of the arc observed, start (15 m/s, 35 deg), eta = 0.1, lr = 0.5', top_runs)
describe('projectile, landing distance observed', landing_runs)
assert top_runs['newton']['hit'] == 8 and top_runs['lbfgs']['hit'] == 12
first = valley0['gd']['models'][0], valley0['adam']['models'][0], valley0['newton']['models'][0]
say('first steps on the valley: ' + ', '.join(f'{name} ({d[0]:.3f}, {d[1]:.3f})'
                                               for name, (_, _, _, d) in zip(['GD', 'Adam', 'Newton'], first)))


def loss_contours(ax, land, levels, n=241):
    (x_lo, x_hi), (y_lo, y_hi) = land['dom']
    X, Y = np.meshgrid(np.linspace(x_lo, x_hi, n), np.linspace(y_lo, y_hi, n))
    Z = np.vectorize(lambda a, b: land['f']([a, b]))(X, Y)
    ax.contour(X, Y, Z, levels=levels, colors=ink, linewidths=0.6, alpha=0.4)
    ax.set(xlim=(x_lo, x_hi), ylim=(y_lo, y_hi))
    ax.grid(False)


def draw_bowl(ax, model, color, grid=(-2, 2)):
    x, slope, B, d = model
    B = np.array(B)
    bottom = np.array(x) - np.linalg.solve(B, slope)               # bottom of the bowl q(d) = m.d + d.B.d/2
    X, Y = np.meshgrid(np.linspace(*grid, 321), np.linspace(*grid, 321))
    dx, dy = X - bottom[0], Y - bottom[1]
    Q = 0.5*(B[0, 0]*dx*dx + 2*B[0, 1]*dx*dy + B[1, 1]*dy*dy)
    drop = 0.5*(np.array(x) - bottom) @ B @ (np.array(x) - bottom)
    ax.contour(X, Y, Q, levels=drop*np.array([0.04, 0.2, 0.5, 1.0]), colors=color, linewidths=1.1, linestyles='--')
    ax.plot(*bottom, 'x', color=color, ms=8, mew=2)
    ax.annotate('', (x[0] + d[0], x[1] + d[1]), x, arrowprops=dict(arrowstyle='->', color=color, lw=2.2))
    ax.plot(*x, 'o', color=ink, ms=5)


VALLEY_LEVELS = np.geomspace(0.05, 120, 12)
land0 = valley(8, 0)
fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
for ax, kind in zip(axes, ['gd', 'adam', 'newton']):
    loss_contours(ax, land0, VALLEY_LEVELS)
    draw_bowl(ax, valley0[kind]['models'][0], OPT_COLORS[kind])
    ax.plot(0, 0, '+', color=ink, ms=10)
    ax.set(title=OPT_NAMES[kind], xlabel='$x_1$', aspect='equal')
    ax.title.set_fontsize(11)
axes[0].set_ylabel('$x_2$')
save(fig, 'three-bowls.png')

fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
for ax, step in zip(axes, [0, 1, 3]):
    loss_contours(ax, land0, VALLEY_LEVELS)
    draw_bowl(ax, valley0['lbfgs']['models'][step], OPT_COLORS['lbfgs'])
    ax.plot(*valley0['lbfgs']['path'][:step + 1].T, '-', color=OPT_COLORS['lbfgs'], lw=1, alpha=0.6)
    ax.plot(0, 0, '+', color=ink, ms=10)
    ax.set(title=f'L-BFGS, step {step + 1}', xlabel='$x_1$', aspect='equal')
    ax.title.set_fontsize(11)
axes[0].set_ylabel('$x_2$')
save(fig, 'lbfgs-bowls.png')
for step in [0, 1, 3]:
    B = np.array(valley0['lbfgs']['models'][step][2])
    say(f'L-BFGS bowl at step {step + 1}: curvatures {np.round(np.linalg.eigvalsh(B), 2)} (the loss has 1 and 64)')


def draw_paths(ax, runs, shown, labels=True):
    for kind, r in runs.items():
        path = r['path'][:shown.get(kind, len(r['path']))]
        count = f'{r["hit"]} step' + ('' if r['hit'] == 1 else 's')
        label = f'{OPT_NAMES[kind]}, {count}' if labels and r['hit'] else OPT_NAMES[kind]
        ax.plot(*path.T, 'o-', ms=2.5, lw=1.1, color=OPT_COLORS[kind], label=label)


fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
for ax, phi, runs in [(axes[0], 0, valley0), (axes[1], 45, valley45)]:
    loss_contours(ax, valley(8, phi), VALLEY_LEVELS)
    draw_paths(ax, runs, {'gd': 60, 'adam': 200})
    ax.plot(0, 0, '+', color=ink, ms=10)
    ax.set(title=f'Valley rotated by {phi}°', xlabel='$x_1$', ylabel='$x_2$', aspect='equal')
    ax.title.set_fontsize(11)
    ax.legend(fontsize=8.5, loc='upper right', frameon=True, framealpha=0.85, edgecolor='none')
save(fig, 'valley-paths.png')

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
loss_contours(axes[0], rosenbrock(), np.geomspace(0.05, 2500, 14))
draw_paths(axes[0], rosen, {}, labels=False)
axes[0].plot(1, 1, '+', color=ink, ms=10)
axes[0].set(title='Rosenbrock', xlabel='$x_1$', ylabel='$x_2$')
loss_contours(axes[1], double_well(), np.linspace(0.02, 4, 14))
draw_paths(axes[1], well, {}, labels=False)
axes[1].plot([-1, 1], [0, 0], '+', color=ink, ms=10)
axes[1].plot(0, 0, 'x', color=ink, ms=8)
axes[1].annotate('saddle', (0, 0), xytext=(6, -14), textcoords='offset points', color=ink, fontsize=9)
axes[1].set(title='Double well', xlabel='$x_1$', ylabel='$x_2$', aspect='equal')
for ax in axes:
    ax.title.set_fontsize(11)
axes[0].legend(fontsize=8.5, loc='upper left', frameon=True, framealpha=0.85, edgecolor='none')
save(fig, 'rosenbrock-doublewell.png')

land_landing = projectile('landing')
R_TRUE = V_TRUE*V_TRUE*math.sin(2*A_TRUE*DEG)/G
fig, ax = plt.subplots(figsize=(6.0, 4.0))
LL_landing = 0.5*(vv*vv*np.sin(2*aa*DEG)/G - R_TRUE)**2
ax.contour(vv, aa, LL_landing, levels=np.geomspace(1, 6000, 12), colors=ink, linewidths=0.6, alpha=0.4)
angles = np.linspace(10, 80, 200)
ax.plot(np.sqrt(G*R_TRUE/np.sin(2*angles*DEG)), angles, color=ink, lw=2, ls='--', label='$L=0$')
ax.plot(V_TRUE, A_TRUE, '*', color=ink, ms=13, label='true $v$, $a$')
ax.plot(15, 35, 'o', color=ink, ms=5)
for kind, r in landing_runs.items():
    ax.plot(*r['path'].T, '-', lw=1, color=OPT_COLORS[kind], alpha=0.7)
    ax.plot(*r['path'][-1], 'o', color=OPT_COLORS[kind], ms=7, label=OPT_NAMES[kind])
ax.set(xlabel='$v$ (m/s)', ylabel='$a$ (degrees)', xlim=(5, 35), ylim=(5, 85))
ax.grid(False)
ax.legend(fontsize=8.5, loc='lower left', frameon=False)
save(fig, 'landing-minima.png')
say(f'landing distance R* = {R_TRUE:.2f} m')

# =====================================================================================
# 5. Scale and inverse updates (inverse-updates.ipynb)
# =====================================================================================
def steps_to_tolerance(update, x0, tol=1e-3, limit=10_000):
    x, path = np.array(x0, float), [np.array(x0, float)]
    while np.linalg.norm(x) >= tol and len(path) <= limit:
        x = update(x)
        path.append(x)
    return len(path) - 1, np.array(path)


grid = np.linspace(-1.2, 1.2, 241)
X1, X2 = np.meshgrid(grid, grid)
counts = []
fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
for ax, alpha in zip(axes, [1, 3, 10]):
    eta = 1/(1 + alpha**2)
    n_gd, gd_path = steps_to_tolerance(lambda x: x - eta*np.array([2*x[0], 2*alpha**2*x[1]]), [1, 1])
    n_inv, inv_path = steps_to_tolerance(lambda x: 0.5*x, [1, 1])
    counts.append((alpha, n_gd, n_inv))
    ax.contour(X1, X2, X1**2 + alpha**2*X2**2, levels=np.geomspace(0.01, 2*alpha**2, 12),
               colors=ink, linewidths=0.5, alpha=0.4)
    ax.plot(*gd_path[:40].T, 'o-', ms=3, lw=1, color=UPDATE_COLORS['Gradient descent'],
            label=f'Gradient descent, {n_gd} step' + ('' if n_gd == 1 else 's'))
    ax.plot(*inv_path.T, 's-', ms=3, lw=1, color=UPDATE_COLORS['Inverse simulator'],
            label=f'Inverse simulator, {n_inv} steps')
    ax.plot(0, 0, 'k+', ms=10)
    ax.set(title=f'$\\alpha$ = {alpha}', xlabel='$x_1$', aspect='equal')
    ax.title.set_fontsize(11)
    ax.grid(False)
    ax.legend(fontsize=8, loc='upper left', frameon=False)
axes[0].set_ylabel('$x_2$')
save(fig, 'scaled-simulator.png')
assert counts == [(1, 1, 11), (3, 33, 11), (10, 363, 11)]
say('--- scaled simulator, steps to |x| < 1e-3 from (1, 1): ' + ', '.join(f'alpha {a}: GD {g}, inverse {i}' for a, g, i in counts))
say(f'error factor per gradient step at alpha = 10: {(100 - 1)/(100 + 1):.4f}')

UPDATES = {
    'Gradient descent': lambda x: np.array([x[0] - 0.01*2*x[0], x[1] - 0.01*4*x[1]**3]),
    'Newton': lambda x: np.array([(1 - 1/3)*x[0], (1 - 1/9)*x[1]]),
    'Inverse gradient': lambda x: np.array([(1 - 0.3)*x[0], (1 - 0.15)*x[1]]),
    'Inverse simulator': lambda x: np.array([(1 - 0.3)*x[0], math.sqrt(1 - 0.3)*x[1]]),
}
paths = {}
for name, update in UPDATES.items():
    x, path = np.array([3.0, 3.0]), [np.array([3.0, 3.0])]
    for _ in range(10):
        x = update(x)
        path.append(x)
    paths[name] = np.array(path)
x_t = torch.tensor([3.0, 3.0], requires_grad=True)
grad_start = torch.autograd.grad((torch.stack([x_t[0], x_t[1]**2])**2).sum(), x_t)[0].numpy()
assert np.allclose(grad_start, [6, 108])
say('--- nonlinear simulator y = (x1, x2^2), L = |y|^2, start (3, 3), gradient (6, 108); after 10 steps')
distances = {}
for name, path in paths.items():
    end = path[-1]
    distances[name] = np.linalg.norm(end)
    say(f'{name:<18} end ({end[0]:.3f}, {end[1]:.3f}), distance {distances[name]:.3f}, loss {end[0]**2 + end[1]**4:.4f}')
assert np.allclose([distances[n] for n in UPDATES], [2.633, 0.925, 0.597, 0.511], atol=5e-4)
grid = np.linspace(-0.3, 3.3, 241)
X1, X2 = np.meshgrid(grid, grid)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.1))
axes[0].contour(X1, X2, X1**2 + X2**4, levels=np.geomspace(0.01, 160, 14), colors=ink, linewidths=0.5, alpha=0.4)
for name, path in paths.items():
    axes[0].plot(*path.T, 'o-', ms=3.5, lw=1.2, color=UPDATE_COLORS[name], label=name)
    axes[1].plot(path[:, 0], path[:, 1]**2, 'o-', ms=3.5, lw=1.2, color=UPDATE_COLORS[name])
axes[0].set(title='Paths in the parameters $\\mathbf{x}$', xlabel='$x_1$', ylabel='$x_2$', aspect='equal')
axes[1].set(title='The same paths in the output $\\mathbf{y}$', xlabel='$y_1$', ylabel='$y_2$')
axes[0].legend(fontsize=8.5, loc='lower right', frameon=False)
for ax in axes:
    ax.plot(0, 0, 'k+', ms=10)
    ax.title.set_fontsize(11)
    ax.grid(False)
save(fig, 'four-updates.png')
heat_factor = math.exp(0.091*12**2)
assert abs(heat_factor - 4.91e5) < 1e3
say(f'inverse heat factor at k = 12 with nu T = 0.091: {heat_factor:.2e}')

# =====================================================================================
# 6. Kinks and subgradients (subgradients.ipynb)
# =====================================================================================
def derivative_at(f, x0):
    x = torch.tensor(float(x0), requires_grad=True)
    f(x).backward()
    return x.grad.item()


kinks = {'torch.abs(x)': torch.abs, 'torch.relu(x)': torch.relu,
         'torch.clamp(x, min=0)': lambda x: torch.clamp(x, min=0),
         'torch.maximum(x, 0)': lambda x: torch.maximum(x, torch.tensor(0.0))}
kink_values = {name: derivative_at(f, 0.0) for name, f in kinks.items()}
assert list(kink_values.values()) == [0.0, 0.0, 1.0, 0.5]
identity = derivative_at(lambda x: torch.relu(x) - torch.relu(-x), 0.0)
root_square = derivative_at(lambda x: torch.sqrt(x**2), 0.0)
assert identity == 0.0 and math.isnan(root_square)
say('--- derivatives PyTorch returns at x = 0: ' + ', '.join(f'{n} {v:g}' for n, v in kink_values.items()))
say(f'relu(x) - relu(-x) at 0: {identity:g} (the function is x, with derivative 1); sqrt(x^2) at 0: {root_square}')

z = np.linspace(-1.5, 1.5, 301)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4), sharey=True)
axes[0].plot(z, np.abs(z), color=ink, lw=2.5)
for slope in [-1, -0.5, 0, 0.5, 1]:
    axes[0].plot(z, slope*z, '--', color=blue, lw=1, alpha=0.85)
axes[0].set(title='Lines below $|x|$ through the kink, slopes $-1$ to $1$', xlabel='$x$', ylim=(-0.6, 1.6))
axes[1].plot(z, np.maximum(z, 0), color=ink, lw=2.5, label='relu($x$)')
for slope, label, color in [(0, 'torch.relu, slope 0', blue), (0.5, 'torch.maximum, slope 0.5', orange),
                            (1, 'torch.clamp, slope 1', green)]:
    axes[1].plot(z, slope*z, '--', lw=1.5, color=color, label=label)
axes[1].set(title='The values PyTorch returns for the ReLU at 0', xlabel='$x$')
axes[1].legend(fontsize=8.5, loc='upper left', frameon=False)
for ax in axes:
    ax.axhline(0, color=ink, lw=0.5)
    ax.axvline(0, color=ink, lw=0.5)
    ax.title.set_fontsize(11)
save(fig, 'subgradient-lines.png')


def subgradient_method(x0, step, n_steps):
    x, path = x0, [x0]
    for k in range(1, n_steps + 1):
        x = x - step(k)*np.sign(x)
        path.append(x)
    return np.array(path)


rules = {'fixed, 0.1': lambda k: 0.1, r'$0.1/\sqrt{k}$': lambda k: 0.1/np.sqrt(k), '$0.1/k$': lambda k: 0.1/k}
runs = {name: subgradient_method(1.05, step, 1000) for name, step in rules.items()}
ends = [abs(path[-1]) for path in runs.values()]
assert np.allclose(ends, [0.05, 0.0032, 0.3015], atol=5e-5)
say('--- subgradient method on |x| from 1.05, |x| after 1000 steps: fixed 0.1 -> '
    f'{ends[0]:.4f}, 0.1/sqrt(k) -> {ends[1]:.4f}, 0.1/k -> {ends[2]:.4f}')
say('fixed step, x_9 to x_13: ' + ', '.join(f'{value:.2f}' for value in runs['fixed, 0.1'][9:14]))
fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4))
for (name, path), color in zip(runs.items(), [blue, green, orange]):
    axes[0].plot(path[:61], 'o-', ms=2.5, lw=1, color=color)
    window = np.array([np.abs(path[max(0, k - 9):k + 1]).max() for k in range(len(path))])
    axes[1].semilogy(window, color=color, lw=1.5)
    axes[1].text(990, window[-1]*1.25, f'step {name}', color=ink, fontsize=9, ha='right', va='bottom')
axes[0].axhline(0, color=ink, lw=0.5)
axes[0].set(xlabel='step $k$', ylabel='$x_k$', title='The first 60 steps')
axes[1].set(xlabel='step $k$', ylabel='largest $|x_i|$ in the last 10 steps', title='1000 steps')
for ax in axes:
    ax.title.set_fontsize(11)
save(fig, 'subgradient-steps.png')

rng = np.random.default_rng(0)
n_samples, n_features, lam = 50, 20, 0.1
X = rng.normal(size=(n_samples, n_features))
w_true = np.zeros(n_features)
w_true[[2, 7, 11, 16]] = [1.5, -2.0, 1.0, 0.8]
y_obs = X @ w_true + 0.1*rng.normal(size=n_samples)
objective = lambda w: 0.5/n_samples*np.sum((X @ w - y_obs)**2) + lam*np.sum(np.abs(w))
smooth_gradient = lambda w: X.T @ (X @ w - y_obs)/n_samples
lipschitz = np.linalg.eigvalsh(X.T @ X/n_samples).max()
w, best, w_sub = np.zeros(n_features), np.inf, np.zeros(n_features)
for k in range(1, 20_001):
    w = w - (0.5/lipschitz)/np.sqrt(k)*(smooth_gradient(w) + lam*np.sign(w))
    if objective(w) < best:
        best, w_sub = objective(w), w.copy()
w_ista = np.zeros(n_features)
for _ in range(5000):
    step = w_ista - smooth_gradient(w_ista)/lipschitz
    w_ista = np.sign(step)*np.maximum(np.abs(step) - lam/lipschitz, 0)
reference = Lasso(alpha=lam, fit_intercept=False, tol=1e-12, max_iter=100_000).fit(X, y_obs).coef_
zeros = [int(np.sum(w == 0)) for w in (w_sub, w_ista, reference)]
assert zeros == [0, 15, 15] and np.abs(w_ista - reference).max() < 1e-11
say('--- lasso, 50 samples, 20 features, lambda = 0.1')
say(f'objective: subgradient {objective(w_sub):.5f}, ISTA {objective(w_ista):.5f}, scikit-learn {objective(reference):.5f}')
say(f'exact zeros: subgradient {zeros[0]}, ISTA {zeros[1]}, scikit-learn {zeros[2]}; '
    f'subgradient coefficients below 1e-3: {int(np.sum(np.abs(w_sub) < 1e-3))}; max |ISTA - scikit-learn| = {np.abs(w_ista - reference).max():.1e}')
fig, ax = plt.subplots(figsize=(9, 3.0))
index = np.arange(n_features)
ax.bar(index - 0.27, w_true, width=0.27, color=ink, label='true')
ax.bar(index, w_sub, width=0.27, color=blue, label='subgradient method')
ax.bar(index + 0.27, w_ista, width=0.27, color=green, label='ISTA')
ax.axhline(0, color=ink, lw=0.5)
ax.set(xlabel='coefficient index', ylabel='value', xticks=index)
ax.legend(fontsize=9, frameon=False, ncol=3, loc='lower right')
save(fig, 'lasso-coefficients.png')

# =====================================================================================
# 7. The waveform inversion result stored in 06-ad.ipynb
# =====================================================================================
notebook = json.loads((root/'06-ad.ipynb').read_text())
for cell in notebook['cells']:
    source = ''.join(cell['source'])
    if cell['cell_type'] == 'code' and 'Wave Solutions at t=2.5' in source:
        text = ''.join(''.join(o.get('text', '')) for o in cell['outputs'] if o['output_type'] == 'stream')
        image = next(o['data']['image/png'] for o in cell['outputs'] if 'image/png' in o.get('data', {}))
        (out/'fwi-linear-profile.png').write_bytes(base64.b64decode(image))
        assert 'result = optax_adam(params, 1000)' in source
        say('--- waveform inversion in 06-ad.ipynb (stored output, Adam, 1000 steps): '
            + ' '.join(text.split()))
say(f'time loop: 5000 steps of 1000 grid values = {5000*1000:,} stored values per field')

(Path(__file__).with_name('generate_ad_figures-report.txt')).write_text(report.getvalue())
