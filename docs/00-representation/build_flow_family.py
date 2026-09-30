"""Draw the transported profile and its fixed-grid reconstructions.

Run from the activated course environment. The SVG is a course-page asset.
The report records the parameters and all numerical checks used in the revision.
An optional --preview path writes a PNG for visual inspection.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
WIDTH = 0.01
SPEED = 1.0
TIMES = (0.0, 0.15, 0.30)
NODE_COUNT = 32


def front(x, time):
    shift = SPEED * time
    return 0.5 * (
        np.tanh((x - 0.15 - shift) / WIDTH)
        - np.tanh((x - 0.45 - shift) / WIDTH)
    )


def relative_l2(estimate, reference, x):
    return np.sqrt(
        np.trapezoid((estimate - reference) ** 2, x)
        / np.trapezoid(reference**2, x)
    )


def draw(preview=None):
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 12,
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "svg.fonttype": "none",
            "text.usetex": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    x = np.linspace(0, 1, 16001)
    nodes = np.linspace(0, 1, NODE_COUNT)
    colors = ("#18759d", "#c26330", "#39794f")
    reference = [front(x, t) for t in TIMES]
    reconstructed = [np.interp(x, nodes, front(nodes, t)) for t in TIMES]
    errors = [relative_l2(v, f, x) for v, f in zip(reconstructed, reference)]

    fig = plt.figure(figsize=(7.0, 9.2), layout="constrained", facecolor="white")
    axes = fig.subplots(
        5, 1, sharex=True, gridspec_kw={"height_ratios": [1.0, 1.8, 1, 1, 1]}
    )
    pipe, profiles, *grid_axes = axes

    pipe.set_title("The hot region moves along the pipe", loc="left", pad=22)
    for row, (t, f) in enumerate(zip(TIMES, reference)):
        pipe.imshow(
            f[np.newaxis, ::16],
            extent=(0, 1, row + 0.13, row + 0.65),
            aspect="auto",
            cmap="Oranges",
            vmin=0,
            vmax=1,
            interpolation="nearest",
        )
        pipe.plot([0, 1], [row + 0.13] * 2, color="0.65", lw=0.7)
        pipe.plot([0, 1], [row + 0.65] * 2, color="0.65", lw=0.7)
    pipe.set_yticks(np.arange(3) + 0.39, [f"t = {t:.2f}" for t in TIMES])
    pipe.set_ylim(2.85, -0.25)
    pipe.annotate(
        "flow",
        xy=(0.97, 1.14),
        xytext=(0.78, 1.14),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "->", "color": "0.25"},
        va="center",
        annotation_clip=False,
    )
    pipe.spines[["left", "bottom"]].set_visible(False)
    pipe.tick_params(left=False, bottom=False)

    profiles.set_title("Different profiles on the same spatial interval", loc="left")
    for t, f, color in zip(TIMES, reference, colors):
        profiles.plot(x, f, color=color, lw=2.2, label=f"t = {t:.2f}")
    profiles.set_ylabel("temperature")
    profiles.set_ylim(-0.1, 1.45)
    profiles.set_yticks([0, 1])
    profiles.legend(
        loc="upper left", ncols=3, frameon=False, fontsize=11, handlelength=1.6,
        columnspacing=1.2,
    )

    for index, (ax, t, f, v, error, color) in enumerate(
        zip(grid_axes, TIMES, reference, reconstructed, errors, colors)
    ):
        if index == 0:
            ax.set_title("Reconstruction on the same fixed grid", loc="left", pad=27)
        for node in nodes:
            ax.axvline(node, color="0.88", lw=0.65, zorder=0)
        ax.fill_between(x, f, v, color="#e8be38", alpha=0.4)
        ax.plot(x, f, color="0.2", lw=1.3, ls="--", label="exact profile")
        ax.plot(x, v, color=color, lw=1.7, label="grid reconstruction")
        ax.plot(nodes, front(nodes, t), "o", color=color, markersize=3.1)
        ax.set_ylabel(f"t = {t:.2f}")
        ax.set_ylim(-0.13, 1.15)
        ax.set_yticks([0, 1])
        ax.text(
            0.99, 0.97, f"relative $L^2$ error {100 * error:.1f}%",
            transform=ax.transAxes, ha="right", va="top", fontsize=10.5,
        )
    grid_axes[0].legend(
        loc="lower left", bbox_to_anchor=(0, 1.01), ncols=2,
        frameon=False, fontsize=10.5, handlelength=2,
    )
    grid_axes[-1].set_xlabel("position x")
    grid_axes[-1].set_xticks(np.linspace(0, 1, 6))
    for ax in axes:
        ax.set_xlim(0, 1)

    output = HERE / "figs" / "rep-flow-family.svg"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, metadata={"Title": "A transported temperature family on a fixed grid"})
    if preview:
        fig.savefig(preview, dpi=150)
    plt.close(fig)

    report = [
        "# Flow-family revision checks", "",
        "## Transport and reconstruction", "",
        f"Initial edges 0.15 and 0.45. Transition width {WIDTH:.2f}.",
        f"Normalized speed {SPEED:.0f}. Fixed grid has {NODE_COUNT} nodes.",
        f"Grid spacing {1 / (NODE_COUNT - 1):.8f}.", "",
        "| Time | Relative L2 reconstruction error | Maximum pointwise gap |",
        "| --- | --- | --- |",
    ]
    for t, f, v, error in zip(TIMES, reference, reconstructed, errors):
        assert np.allclose(front(x, t), front(x - SPEED * t, 0))
        report.append(
            f"| {t:.2f} | {100 * error:.4f}% | {np.max(np.abs(v - f)):.6f} |"
        )
    dense_times = np.linspace(0, 0.30, 301)
    sweep = np.array([
        relative_l2(np.interp(x, nodes, front(nodes, t)), front(x, t), x)
        for t in dense_times
    ])
    report += [
        "", "301 sampled positions, not a certified continuum bound.",
        f"Largest sampled relative L2 grid error {100 * sweep.max():.4f}% "
        f"at time {dense_times[sweep.argmax()]:.3f}.", "",
        "## Kernel and fixed-space hand calculations", "",
    ]
    rho = np.exp(-0.5)
    alpha = 1 / (1 + rho)
    report += [
        f"Sensors separated by the length scale. Similarity {rho:.8f}.",
        f"For unit readings, equal interpolation weights {alpha:.8f}.",
    ]
    assert np.allclose(np.array([[1, rho], [rho, 1]]) @ [alpha, alpha], [1, 1])
    bad_kernel = np.array([[1, 1, 0], [1, 1, 1], [0, 1, 1]])
    weights = np.array([1, -np.sqrt(2), 1])
    quadratic = weights @ bad_kernel @ weights
    assert np.isclose(quadratic, 4 - 4 * np.sqrt(2))
    report += [
        f"Threshold similarity eigenvalues {np.linalg.eigvalsh(bad_kernel)}.",
        f"Its quadratic form for (1, -sqrt(2), 1) is {quadratic:.8f}.",
        f"At overlap 0.99, coefficient amplification {1 / 0.01:.1f}.",
        f"At overlap 0.99, RKHS norm amplification {np.sqrt(0.02) / 0.01:.8f}.",
        f"With ridge lambda 0.1, coefficient amplification {1 / 0.11:.8f}.",
        "A unit change over distance ell/10 requires norm at least 10.",
    ]
    normal = np.ones(3) / np.sqrt(3)
    projection = np.eye(3) - np.outer(normal, normal)
    squared_errors = np.sum((np.eye(3) - projection) ** 2, axis=0)
    assert np.allclose(squared_errors.sum(), 1)
    report += [
        f"Three orthogonal spikes. Squared errors to a balanced plane {squared_errors}.",
        f"Their sum {squared_errors.sum():.8f}; equal errors {1 / np.sqrt(3):.8f}.",
        "", "## Existing measurements retained in the page", "",
        "Fin interpolation and invalid-similarity calculations are recorded in",
        "sciml_notebook/docs/representations/generate_ch2_kernel_bumps-report.md.",
        "Fin errors and fixed-hyperparameter held-out RMSE are recorded in",
        "sciml_notebook/docs/representations/generate_ch2_fin_choice-report.md.",
        "GP length-scale comparisons and gap half-widths are recorded in",
        "sciml/docs/00-representation/build_slide_data-report.md.",
    ]
    (HERE / "build_flow_family-report.md").write_text("\n".join(report) + "\n")
    print(f"wrote {output}")
    print(f"wrote {HERE / 'build_flow_family-report.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", type=Path)
    draw(parser.parse_args().preview)
