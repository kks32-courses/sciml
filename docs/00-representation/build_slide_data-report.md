# build_slide_data report

m = 3: largest gap / largest displacement = 73.5 %
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
corner, L2-closest [0.2026, 0.0, -0.0225]: sup 9.9 %, L2 4.8 %, H1 31.5 %
corner, sup-closest [0.2045, 0.0, -0.0318]: sup 5.5 %, L2 6.7 %, H1 33.9 %
Bernstein string displacement n = 8: B(0.25) = 0.810 against u(0.25) = 1.107, largest gap 0.299
load f = -u'': max 36.56, min -13.07
quarter-span readings y = [1.1071, 0.6, 0.3071], recovered a = [0.8, 0.4, 0.2], cond(A) = 1.00
Galerkin hats on -u'' = f: largest nodal deviation over N = 4, 8, 16 = 4.4e-16; error slopes L2 -2.00, energy -1.00
kernel prior solving -u'' = f: rel L2 error 3.2e-07, cond(K_obs) 1.4e+12
regression line (degree 1, lambda 0.0): RMSE at data 0.4835, RMSE against sin on [-3,3] 0.4393, max|w| 0.76, max|f| on [-3.5,3.5] 0.93
regression cubic (degree 3, lambda 0.0): RMSE at data 0.1188, RMSE against sin on [-3,3] 0.0853, max|w| 2.52, max|f| on [-3.5,3.5] 1.09
regression deg11 (degree 11, lambda 0.0): RMSE at data 0.0000, RMSE against sin on [-3,3] 0.1207, max|w| 284, max|f| on [-3.5,3.5] 29.53
regression deg11ridge (degree 11, lambda 0.001): RMSE at data 0.0898, RMSE against sin on [-3,3] 0.0731, max|w| 4.26, max|f| on [-3.5,3.5] 2.76
bump regression m = 5, ell = 0.5: RMSE 0.442
bump regression m = 20, ell = 0.5: RMSE 0.002
kernel ridge, copies at the 12 readings: alpha range [-0.632, 1.129], RMSE at data 0.0051, against sin at the data 0.1134
slid copy s = 0.08: L2 distance 0.246, signed integral of the gap 0.0275
int_0^1 x^(-2/3) dx = 3.0000 (so x^(-1/3) is in L2 with norm 1.7321); int x^(-1) diverges
ramp width 0.2: slope 5, integral of the squared slope 5.00 (1/w = 5)
ramp width 0.05: slope 20, integral of the squared slope 19.95 (1/w = 20)
mode sqrt(2) sin(1 pi x): L2 norm 1.000, H1 seminorm 3.14
mode sqrt(2) sin(4 pi x): L2 norm 1.000, H1 seminorm 12.57
mode sqrt(2) sin(16 pi x): L2 norm 1.000, H1 seminorm 50.27
distance between two different unit modes: 1.4142 (sqrt 2 = 1.4142)
compactness bound, |u|_H1 <= 10: tail beyond mode 4 has L2 norm <= M/((K+1) pi) = 0.637
compactness bound, |u|_H1 <= 10: tail beyond mode 16 has L2 norm <= M/((K+1) pi) = 0.187
step load 2 on [0, 1/2): displacement peak 0.1405 at x = 0.375
membrane, bilinear on 5 x 5 = 25 values: largest gap 22.2 % of max|u| = 0.900
membrane, bilinear on 9 x 9 = 81 values: largest gap 7.1 % of max|u| = 0.900
membrane, bilinear on 17 x 17 = 289 values: largest gap 1.9 % of max|u| = 0.900
membrane load max 34.61; values per direction 17: line 17, plate 289, solid 4913
Poincare constant on (0,1): 1/pi = 0.3183; norm equivalence factor sqrt(1 + 1/pi^2) = 1.0494
Poincare ratio ||u||_L2 / |u|_H1 for sin(pi x): 0.7071 / 2.2214 = 0.3183
Poincare ratio ||u||_L2 / |u|_H1 for corner min(x,1-x)/2: 0.1443 / 0.5000 = 0.2887
Poincare ratio ||u||_L2 / |u|_H1 for test displacement: 0.6481 / 2.8448 = 0.2278
constant 1 on (0,1): ||u||_L2 = 1, |u|_H1 = 0, so the inequality fails without the pinned ends
