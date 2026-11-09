# Changelog

## Unreleased

### Added

- Add `docs/05-fno/fno-intuition.ipynb`, now 15 cells, that develops Fourier operators through heat flow, shape-preserving sine modes, Fourier coordinates, known spectral multipliers, and multipliers learned from field pairs. Introduce nonlinear mode coupling and the pseudospectral connection only after the linear example.
- Add `docs/05-fno/heat-mode-explorer.html`, a shared interactive display of the temperature field, its individual sine components, and their amplitudes. Playback, a time slider, and selectable initial fields support the first four sections without changing the example.
- Add an equal-amplitude, side-by-side diffusion comparison, linked selection of component curves and Fourier bars, initial-amplitude outlines, and explicit decay multipliers. Ask students to observe spatial shape preservation before revealing the derivative and eigenfunction explanation.
- Add `fourier-learning-lab.html` and `fourier-nonlinearity-lab.html`. Students first adjust three heat multipliers, then fit them from observed pairs, and test the inability of a linear multiplier to create a missing frequency before applying a pointwise square.
- Embed all display sources in the introductory notebook, removing its runtime dependence on local HTML files or GitHub downloads. Identify the noiseless heat fit as a controlled linear demonstration and compare pseudospectral and FNO operations side by side.
- Expand Sections 3–6 with pointwise wave reconstruction, the meaning and recovery of sine amplitudes, a step-by-step modal heat derivation, amplitude-versus-multiplier examples, the shared input-output fitting calculation, and separate walkthroughs of pseudospectral evaluation and each FNO branch. Keep the six-section sequence and existing interactions.
- Connect the heat Green's function, spatial influence kernel, translation-invariant convolution, and Fourier eigenvalues in the intuition notebook. Add a point-response/multiplier figure and verify that direct circular convolution agrees with spectral evaluation.
- Expand the LaTeX FNO slides with the same kernel connection, a global truncated-kernel example, channel-wise Fourier weights, nonlinear mode creation, a pseudospectral comparison, and the coefficient-dependent Darcy Green's function. Add reproducible heat and mode figures while preserving the existing Beamer theme.
- Rebuild `docs/05-fno/fno-cnn-comparisons.ipynb` to introduce the CNN first. It shows the Module 6 deck's convolution, stride, and pooling animations, checks the slide 14 output by hand, and applies the slide 15 blur, shift, and sharpening filters to a test image. Three new animations slide the filters along a ring, pass single waves through each filter beside its frequency response, and turn the convolution into one multiplication per Fourier mode. Two-dimensional response maps explain why the blur erases stripes with a period of 3 pixels. The heat-flow comparisons of CNN weights and Fourier multipliers, the wide-filter table, and the 128-, 256-, and 512-point transfer follow. Aliasing remains an exercise.
- Add the deck's stride and pooling GIFs to `docs/05-fno/figs/` for the comparisons notebook.
- Keep Burgers training in the existing `docs/05-fno/fno.ipynb` and link to it from the intuition lesson.
- Add course-navigation entries for the introductory lesson and its CNN and discretization companion.

### Fixed

- Sample a periodic interval without a duplicate endpoint and use a symmetric frequency mask for the Fourier truncation demonstrations in the existing FNO lesson and exercise notebooks.
- Relabel slide 15's center-5 kernel as sharpening in the supplied local CNN deck. Its weights sum to one and preserve constants.
- Use a consistent periodic Fourier normalization in the slides, correct the CNN equivariance terminology and resolution-transfer claims, and resize overflowing slide content. Rebuild the compiled slide PDF with the source changes.
