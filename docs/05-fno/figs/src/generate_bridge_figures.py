"""Figures and numbers for the Green's function to Fourier layer slides in fno-slides.tex."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .15, 'axes.facecolor': 'none',
                     'savefig.transparent': True})
green, purple, orange, ink, blue = '#399e89', '#7251a1', '#db6a20', '#253349', '#4d85ca'
NU_T = 0.14*0.65


def save(fig, name):
    fig.tight_layout()
    fig.savefig(out/name, dpi=220)
    plt.close(fig)


# ---------- the string's Green's matrix and the ring's heat matrix ----------
M = 64
xs = (np.arange(M) + 1)/(M + 1)
X, Y = np.meshgrid(xs, xs, indexing='ij')
g_string = np.where(X <= Y, X*(1 - Y), Y*(1 - X))
xr = 2*np.pi*np.arange(M)/M
k = np.arange(M//2 + 1)
column = np.fft.irfft(np.exp(-NU_T*k**2), n=M)*M/(2*np.pi)     # heat kernel density on the ring
g_ring = np.stack([np.roll(column, j) for j in range(M)], axis=1)
assert np.allclose(g_ring[:, 5], np.roll(g_ring[:, 4], 1))

for name, matrix, title, ticks, labels in [
        ('string-matrix.png', g_string, 'String: column j is the tent for a load at $y_j$',
         [0, M - 1], ['0', '1']),
        ('ring-matrix.png', g_ring, 'Ring: every column is the same bump, shifted',
         [0, M - 1], ['0', '2π'])]:
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    image = ax.imshow(matrix, cmap='viridis', origin='upper')
    for j in [M//6, M//2, 5*M//6]:
        ax.axvline(j, color=orange, lw=1.2, ls='--')
    ax.set(title=title, xlabel='load position $y_j$ (column)', ylabel='output position $x_i$ (row)',
           xticks=ticks, xticklabels=labels, yticks=ticks, yticklabels=labels)
    ax.title.set_fontsize(10)
    ax.grid(False)
    fig.colorbar(image, ax=ax, shrink=0.8)
    save(fig, name)

# ---------- the three slide-15 filters on one wave and their responses ----------
N_VIEW = 32
h = 2*np.pi/N_VIEW
filters = {'Blur': [1/3, 1/3, 1/3], 'Shift': [0, 0, 1], 'Sharpen': [-1, 3, -1]}   # (w_-1, w_0, w_1)


def response(weights, kk, n):
    r = np.array([-1, 0, 1])[:, None]
    return (np.asarray(weights)[:, None]*np.exp(-2j*np.pi*r*np.asarray(kk, float)/n)).sum(axis=0)


dense = np.linspace(0, 2*np.pi, 1025)
fig, axes = plt.subplots(1, 3, figsize=(10, 2.6), sharey=True)
for ax, (name, w) in zip(axes, filters.items()):
    ax.plot(dense, np.sin(7*dense), '--', color=ink, alpha=.45, label='input')
    ax.plot(dense, sum(wr*np.sin(7*(dense - r*h)) for r, wr in zip([-1, 0, 1], w)), color=green, lw=2,
            label='output')
    ax.set(title=f'{name}, wave $\\sin 7x$', xlabel='position x', xticks=[0, np.pi, 2*np.pi],
           xticklabels=['0', 'π', '2π'], ylim=(-2.9, 2.9))
axes[0].legend(fontsize=9, loc='lower left')
save(fig, 'filters-on-a-wave.png')

kc = np.linspace(0, N_VIEW/2, 200)
fig, axes = plt.subplots(1, 3, figsize=(10, 2.6))
axes[0].plot(kc, response(filters['Blur'], kc, N_VIEW).real, color=green, lw=2)
axes[0].set(title='Blur: R(k)', ylabel='multiplier')
axes[1].plot(kc, np.angle(response(filters['Shift'], kc, N_VIEW)), color=green, lw=2)
axes[1].set(title='Shift: angle of R(k)', ylabel='radians')
axes[2].plot(kc, response(filters['Sharpen'], kc, N_VIEW).real, color=green, lw=2)
axes[2].set(title='Sharpen: R(k)', ylabel='multiplier')
for ax in axes:
    ax.axhline(0, color=ink, lw=.6)
    ax.plot([7], [0], alpha=0)
    ax.set_xlabel('mode k on 32 points')
for ax, name in zip(axes, filters):
    value = response(filters[name], [7], N_VIEW)[0]
    value = np.angle(value) if name == 'Shift' else value.real
    ax.plot([7], [value], 'o', color=orange, ms=7)
save(fig, 'filter-responses.png')
blur7 = response(filters['Blur'], [7], N_VIEW)[0].real
sharpen7 = response(filters['Sharpen'], [7], N_VIEW)[0].real
print(f'theta_7 = {2*np.pi*7/N_VIEW:.2f}, cos = {np.cos(2*np.pi*7/N_VIEW):.2f}, '
      f'blur R(7) = {blur7:.2f}, sharpen R(7) = {sharpen7:.2f}')

# ---------- heat pairs on 128 points, CNN fits, learned multipliers, grid transfer ----------
N, K_MAX, N_TRAIN = 128, 12, 64
retained = np.arange(K_MAX + 1)
heat = np.exp(-NU_T*retained**2)
rng = np.random.default_rng(17)
coeffs = 0.15*(rng.normal(size=(96, K_MAX + 1)) + 1j*rng.normal(size=(96, K_MAX + 1)))
coeffs[:, 0] = coeffs[:, 0].real


def profiles(a, n):
    padded = np.zeros((len(a), n//2 + 1), complex)
    padded[:, :K_MAX + 1] = a
    return np.fft.irfft(padded, n=n, norm='forward')


def convolve(u, w):
    m = len(w)//2
    return sum(wr*np.roll(u, r, axis=-1) for r, wr in zip(range(-m, m + 1), w))


def fit(inputs, targets, width):
    m = width//2
    A = np.stack([np.roll(inputs, r, axis=-1).ravel() for r in range(-m, m + 1)], axis=1)
    return np.linalg.lstsq(A, targets.ravel(), rcond=None)[0]


def error(p, t):
    return np.mean(np.linalg.norm(p - t, axis=-1)/np.linalg.norm(t, axis=-1))


u0, uT = profiles(coeffs, N), profiles(coeffs*heat, N)
tr_u, te_u, tr_y, te_y = u0[:N_TRAIN], u0[N_TRAIN:], uT[:N_TRAIN], uT[N_TRAIN:]
widths = {w: error(convolve(te_u, fit(tr_u, tr_y, w)), te_y) for w in [3, 9, 17, 25]}
print('CNN held-out error by width:', {w: f'{e:.2g}' for w, e in widths.items()})
sigma = np.sqrt(2*NU_T)
print(f'heat kernel std = {sigma:.2f} = {sigma/(2*np.pi/N):.1f} spacings on 128, '
      f'{sigma/(2*np.pi/256):.1f} on 256')

kernel = np.fft.irfft(np.exp(-NU_T*np.arange(N//2 + 1)**2), n=N)
offset = np.arange(N) - N//2
fig, ax = plt.subplots(figsize=(7, 2.5))
ax.axvspan(-8, 8, color=green, alpha=.12, label='reach of 17 weights')
ax.axvspan(-1, 1, color=green, alpha=.4, label='reach of 3 weights')
ax.plot(offset, np.fft.fftshift(kernel), color=purple, lw=2, label='heat kernel')
ax.set(xlabel='offset in grid points, 128 points', ylabel='weight', xlim=(-30, 30))
ax.legend(fontsize=9)
save(fig, 'cnn-reach.png')

a, b = np.fft.rfft(tr_u, norm='forward')[:, :K_MAX + 1], np.fft.rfft(tr_y, norm='forward')[:, :K_MAX + 1]
learned = np.sum(a.conj()*b, axis=0)/np.sum(np.abs(a)**2, axis=0)
assert np.allclose(learned, heat, atol=1e-13)
cnn3 = fit(tr_u, tr_y, 3)
fig, axes = plt.subplots(1, 2, figsize=(9.5, 2.9), gridspec_kw={'width_ratios': [1.25, 1]})
for mode, color in [(1, blue), (3, orange), (7, purple)]:
    axes[0].scatter(a[:, mode].imag, b[:, mode].imag, s=10, color=color, label=f'mode {mode}')
axes[0].set(xlabel='input coefficient $a_k$', ylabel='output coefficient $b_k$', title='One mode, 64 pairs')
axes[0].legend(fontsize=9)
kk = np.arange(21)
axes[1].plot(kk, np.exp(-NU_T*kk**2), color=purple, lw=2, label='heat flow $e^{-\\nu k^2T}$')
axes[1].plot(retained, learned.real, 'o', color=orange, ms=5, label='13 learned multipliers')
axes[1].plot(kk, response(cnn3, kk, N).real, '--', color=green, label='best 3-weight CNN')
axes[1].axhline(0, color=ink, lw=.6)
axes[1].set(xlabel='mode k', ylabel='R(k)', title='Learned slopes')
axes[1].legend(fontsize=8)
save(fig, 'learned-multipliers.png')


def fourier_layer(u):
    c = np.fft.rfft(u, axis=-1, norm='forward')
    o = np.zeros_like(c)
    o[..., :K_MAX + 1] = learned*c[..., :K_MAX + 1]
    return np.fft.irfft(o, n=u.shape[-1], axis=-1, norm='forward')


cnn17 = fit(tr_u, tr_y, 17)
print(f'Fourier layer held-out error: {error(fourier_layer(te_u), te_y):.1e}')
for n in [128, 256, 512]:
    s = (n//N)**2
    inp = profiles(coeffs[N_TRAIN:], n)
    t_T = profiles(coeffs[N_TRAIN:]*heat, n)
    t_s = profiles(coeffs[N_TRAIN:]*np.exp(-NU_T*retained**2/s), n)
    out_cnn = convolve(inp, cnn17)
    print(f'{n}: Fourier {error(fourier_layer(inp), t_T):.1e}, CNN vs T {error(out_cnn, t_T):.2g}, '
          f'CNN vs T/{s} {error(out_cnn, t_s):.2g}')
print('FNO layer, 64 channels and 16 modes:', 64*64*16, 'complex multipliers')

# ---------- one operator in two coordinate systems ----------
from scipy.linalg import expm

M2 = 64
xg = 2*np.pi*np.arange(M2)/M2
dx = 2*np.pi/M2


def diffusion_matrix(kappa):
    # Periodic finite volumes for (kappa u_x)_x, kappa sampled at the half points.
    k_half = kappa(xg + dx/2)
    A = np.zeros((M2, M2))
    for i in range(M2):
        A[i, (i + 1) % M2] += k_half[i]/dx**2
        A[i, (i - 1) % M2] += k_half[i - 1]/dx**2
        A[i, i] -= (k_half[i] + k_half[i - 1])/dx**2
    return A


F = np.fft.fft(np.eye(M2), norm='ortho')            # unitary DFT matrix: heights -> waves
order = np.fft.fftshift(np.arange(M2))
P_const = expm(0.65*0.14*diffusion_matrix(lambda s: np.ones_like(s)))
P_var = expm(0.65*0.14*diffusion_matrix(lambda s: 1 + 0.5*np.sin(s)))
in_waves = {name: (F @ P @ F.conj().T)[np.ix_(order, order)] for name, P in
            [('const', P_const), ('var', P_var)]}
off_const = np.abs(in_waves['const'] - np.diag(np.diag(in_waves['const']))).max()
off_var = np.abs(in_waves['var'] - np.diag(np.diag(in_waves['var']))).max()
print(f'largest off-diagonal entry in waves: constant {off_const:.1e}, variable {off_var:.2f}')
assert off_const < 1e-12

fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
panels = [(P_const, 'Heat flow in heights', 'position', 'linear'),
          (np.abs(in_waves['const']), 'Heat flow in waves', 'mode k', 'log'),
          (np.abs(in_waves['var']), 'Conductivity 1 + ½ sin x, waves', 'mode k', 'log')]
for ax, (matrix, title, label, scale) in zip(axes, panels):
    if scale == 'log':
        image = ax.imshow(np.log10(np.maximum(matrix, 1e-6)), cmap='viridis', vmin=-6, vmax=0,
                          extent=[-M2/2 - .5, M2/2 - .5, M2/2 - .5, -M2/2 - .5])
        bar = fig.colorbar(image, ax=ax, shrink=.8)
        bar.set_label('log10 |entry|')
    else:
        image = ax.imshow(matrix, cmap='viridis')
        fig.colorbar(image, ax=ax, shrink=.8)
    ax.set(title=title, xlabel=f'input {label}', ylabel=f'output {label}')
    ax.title.set_fontsize(10)
    ax.grid(False)
save(fig, 'operator-in-two-bases.png')
