# Flow-family revision checks

## Transport and reconstruction

Initial edges 0.15 and 0.45. Transition width 0.01.
Normalized speed 1. Fixed grid has 32 nodes.
Grid spacing 0.03225806.

| Time | Relative L2 reconstruction error | Maximum pointwise gap |
| --- | --- | --- |
| 0.00 | 8.6856% | 0.254291 |
| 0.15 | 6.2706% | 0.233121 |
| 0.30 | 9.5875% | 0.255255 |

301 sampled positions, not a certified continuum bound.
Largest sampled relative L2 grid error 9.9521% at time 0.200.

## Kernel and fixed-space hand calculations

Sensors separated by the length scale. Similarity 0.60653066.
For unit readings, equal interpolation weights 0.62245933.
Threshold similarity eigenvalues [-0.41421356  1.          2.41421356].
Its quadratic form for (1, -sqrt(2), 1) is -1.65685425.
At overlap 0.99, coefficient amplification 100.0.
At overlap 0.99, RKHS norm amplification 14.14213562.
With ridge lambda 0.1, coefficient amplification 9.09090909.
A unit change over distance ell/10 requires norm at least 10.
Three orthogonal spikes. Squared errors to a balanced plane [0.33333333 0.33333333 0.33333333].
Their sum 1.00000000; equal errors 0.57735027.

## Existing measurements retained in the page

Fin interpolation and invalid-similarity calculations are recorded in
sciml_notebook/docs/representations/generate_ch2_kernel_bumps-report.md.
Fin errors and fixed-hyperparameter held-out RMSE are recorded in
sciml_notebook/docs/representations/generate_ch2_fin_choice-report.md.
GP length-scale comparisons and gap half-widths are recorded in
sciml/docs/00-representation/build_slide_data-report.md.
