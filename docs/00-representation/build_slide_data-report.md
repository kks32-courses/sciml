# build_slide_data report

m = 5: largest gap / largest displacement = 20.1 %
m = 9: largest gap / largest displacement = 6.3 %
m = 17: largest gap / largest displacement = 1.6 %
aliasing: max change in the 17 readings = 1.6e-15, crest move 0.3 = 27 % of largest displacement
m = 5 error: sup 0.223, L2 0.093, H1 1.20, energy 0.72
projection: c1* = 8/pi^3 = 0.2580, min squared error 2.51e-06
Gibbs N = 9: overshoot 0.091
Gibbs N = 33: overshoot 0.090
Gibbs N = 129: overshoot 0.089
Bernstein n = 2: gap at corner 0.250, 0.4/sqrt(n) = 0.283
Bernstein n = 8: gap at corner 0.137, 0.4/sqrt(n) = 0.141
Bernstein n = 32: gap at corner 0.070, 0.4/sqrt(n) = 0.071
front shift 0.0: stations 8.7 %, kinks 4.9 %
front shift 0.15: stations 6.3 %, kinks 4.9 %
front shift 0.3: stations 9.6 %, kinks 4.9 %
kernel interpolant ell = 0.15: weights 1.97, -2.39, 4.30, -3.75, 2.38, -0.90, 0.59, -0.25; value at 0.7 = 0.216
kernel interpolant ell = 0.04: weights 1.03, 1.06, 0.86, 0.49, 0.28, 0.23, 0.34, 0.21; value at 0.7 = 0.000
GP ell = 0.15: rel L2 error 0.102, max 2sd in gap 0.901
GP ell = 0.075: rel L2 error 0.232, max 2sd in gap 1.988
GP ell = 0.31: rel L2 error 0.032, max 2sd in gap 0.117
similarity microscope ell = 0.15: k(0.3, 0.45) = 0.607 (distance ell), k at distance 3 ell = 0.011, at distance 2 ell = 0.135
RKHS builder ell = 0.16, centers [0.2, 0.5, 0.8], alpha [0.8, -0.45, 0.65], probe 0.72: f(x*) = 0.403, |f|_k^2 = alpha^T K alpha = 1.041, bound |f(x*)| <= |f|_k sqrt(k(x*,x*)) = 1.020
