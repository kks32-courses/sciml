"""Compute the examples and figures used by mlp-slides.tex.

Run from sciml with its environment activated. Numerical results are written
to docs/00-mlp/data/mlp-checks.json; existing figure assets are not modified.
"""

from pathlib import Path
import json
import math

import numpy as np
import torch


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SEED = 32


def table(name, columns):
    names = list(columns)
    values = np.column_stack([columns[key] for key in names])
    np.savetxt(DATA / name, values, header=" ".join(names), comments="", fmt="%.12g")


def relu(x):
    return np.maximum(x, 0.0)


def tent(x):
    return 2 * relu(x) - 4 * relu(x - 0.5) + 2 * relu(x - 1)


def ad_graph_check():
    inputs = torch.tensor([2.0, 3.0], requires_grad=True)
    w1, w2 = inputs.unbind()
    w3 = w1.square()
    w4 = w3 + w2
    gradient = torch.autograd.grad(w4, inputs)[0]
    chain_rule = torch.stack((2 * inputs[0], torch.ones_like(inputs[1]))).detach()
    torch.testing.assert_close(gradient, chain_rule, rtol=0, atol=0)
    figures = [f"figs/ad{step}.png" for step in range(1, 8)]
    assert all((ROOT / figure).is_file() for figure in figures)
    return {
        "inputs": inputs.detach().tolist(),
        "intermediates": [float(value.detach()) for value in (w1, w2, w3, w4)],
        "output": float(w4.detach()),
        "reverse_seed": 1.0,
        "local_derivatives": {"dy_dw4": 1.0, "dw4_dw3": 1.0, "dw4_dw2": 1.0,
                              "dw3_dw1": float(2 * w1.detach())},
        "gradient": gradient.tolist(),
        "figures": figures,
    }


def main():
    DATA.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    torch.set_default_dtype(torch.float64)
    x = np.linspace(0, 1, 2001)
    u = np.sin(np.pi * x)
    sensors = np.linspace(0.05, 0.95, 15)
    y = np.sin(np.pi * sensors) + 0.04 * rng.standard_normal(len(sensors))
    table("observations.dat", {"x": sensors, "y": y})
    profile = {"x": x, "u": u, "f": np.pi**2 * u}
    checks = {"seed": SEED, "noise_std": 0.04, "training_observations": len(sensors)}
    checks["ad_graph"] = ad_graph_check()

    coefficients = np.linalg.lstsq(np.column_stack([np.ones_like(sensors), sensors]), y, rcond=None)[0]
    profile["affine"] = coefficients[0] + coefficients[1] * x
    checks["affine_coefficients"] = coefficients.tolist()
    checks["affine_reference_rmse"] = float(np.sqrt(np.mean((profile["affine"] - u) ** 2)))

    interpolation_checks = {}
    for points in (3, 5, 9):
        knots = np.linspace(0, 1, points)
        values = np.sin(np.pi * knots)
        approximate = np.interp(x, knots, values)
        slopes = np.diff(values) / np.diff(knots)
        hinge_sum = values[0] + slopes[0] * x
        for position, jump in zip(knots[1:-1], np.diff(slopes)):
            hinge_sum += jump * relu(x - position)
        assert np.allclose(hinge_sum, approximate, atol=1e-13)
        profile[f"linear{points}"] = approximate
        interpolation_checks[str(points)] = {
            "knots": knots.tolist(),
            "values": values.tolist(),
            "slopes": slopes.tolist(),
            "slope_jumps": np.diff(slopes).tolist(),
            "sampled_sup_error": float(np.max(np.abs(approximate - u))),
            "curvature_bound": float(np.pi**2 / (8 * (points - 1) ** 2)),
        }
    checks["interpolation"] = interpolation_checks

    # Finite differences use the known load rather than the observations.
    fd_x = np.linspace(0, 1, 9)
    fd_h = fd_x[1] - fd_x[0]
    matrix = (2 * np.eye(7) - np.eye(7, k=1) - np.eye(7, k=-1)) / fd_h**2
    fd_u = np.r_[0, np.linalg.solve(matrix, np.pi**2 * np.sin(np.pi * fd_x[1:-1])), 0]
    profile["fd9"] = np.interp(x, fd_x, fd_u)
    checks["finite_difference"] = {"nodes": 9, "nodal_values": fd_u.tolist(), "reference_grid_rmse": float(np.sqrt(np.mean((profile["fd9"] - u)**2)))}

    bernstein = {"x": x, "u": u}
    checks["bernstein"] = {}
    for degree in (5, 10, 20, 40):
        approx = sum(np.sin(np.pi * k / degree) * math.comb(degree, k) * x**k * (1 - x)**(degree - k) for k in range(degree + 1))
        bernstein[f"b{degree}"] = approx
        checks["bernstein"][str(degree)] = float(np.max(np.abs(approx - u)))
    table("bernstein.dat", bernstein)

    clean_x = torch.linspace(0, 1, 100).reshape(-1, 1)
    clean_y = torch.sin(torch.pi * clean_x)
    polynomial = np.polynomial.Legendre.fit(clean_x.numpy().ravel(), clean_y.numpy().ravel(), 9, domain=[0, 1])
    profile["poly9"] = polynomial(x)
    torch.manual_seed(SEED)
    sigmoid_model = torch.nn.Sequential(torch.nn.Linear(1, 10), torch.nn.Sigmoid(), torch.nn.Linear(10, 1))
    sigmoid_optimizer = torch.optim.Adam(sigmoid_model.parameters(), lr=0.01)
    for _ in range(10000):
        sigmoid_optimizer.zero_grad()
        clean_loss = torch.mean((sigmoid_model(clean_x) - clean_y)**2)
        clean_loss.backward()
        sigmoid_optimizer.step()
    profile["sigmoid10"] = sigmoid_model(torch.as_tensor(x[:, None])).detach().numpy().ravel()
    checks["clean_comparison"] = {
        "training_points": 100, "evaluation_points": len(x), "polynomial_degree": 9,
        "polynomial_sampled_sup_error": float(np.max(np.abs(profile["poly9"] - u))),
        "sigmoid_width": 10, "sigmoid_parameters": 31, "sigmoid_iterations": 10000,
        "sigmoid_sampled_sup_error": float(np.max(np.abs(profile["sigmoid10"] - u))),
        "seed": SEED, "learning_rate": 0.01,
    }

    # Fit one smooth coordinate network to data only. The dense reference grid
    # is used after training, not to optimize the weights or choose a model.
    torch.manual_seed(SEED)
    model = torch.nn.Sequential(torch.nn.Linear(1, 12), torch.nn.Tanh(), torch.nn.Linear(12, 1))
    x_train = torch.as_tensor(sensors[:, None])
    y_train = torch.as_tensor(y[:, None])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    for _ in range(4000):
        optimizer.zero_grad()
        loss = torch.mean((model(x_train) - y_train) ** 2)
        loss.backward()
        optimizer.step()
    x_eval = torch.tensor(x[:, None], requires_grad=True)
    prediction = model(x_eval)
    slope = torch.autograd.grad(prediction.sum(), x_eval, create_graph=True)[0]
    curvature = torch.autograd.grad(slope.sum(), x_eval)[0]
    profile["trained"] = prediction.detach().numpy().ravel()
    profile["trained_slope"] = slope.detach().numpy().ravel()
    profile["slope"] = np.pi * np.cos(np.pi * x)
    profile["residual"] = -curvature.detach().numpy().ravel() - np.pi**2 * u
    checks["data_fit"] = {
        "activation": "tanh", "width": 12, "parameters": sum(p.numel() for p in model.parameters()),
        "optimizer": "Adam", "iterations": 4000, "learning_rate": 0.01,
        "training_rmse": float(np.sqrt(np.mean((model(x_train).detach().numpy().ravel() - y) ** 2))),
        "reference_grid_rmse": float(np.sqrt(np.mean((profile["trained"] - u) ** 2))),
        "reference_grid_slope_rmse": float(np.sqrt(np.mean((profile["trained_slope"] - profile["slope"]) ** 2))),
        "reference_grid_pde_residual_rms": float(np.sqrt(np.mean(profile["residual"] ** 2))),
        "reference_grid_points": len(x),
    }
    # One square-activation layer spans the quadratics, and two layers reach degree four.
    checks["square_activation"] = {}
    for degree, name in ((2, "quad2"), (4, "quart4")):
        fit = np.polynomial.Legendre.fit(x, u, degree, domain=[0, 1])
        profile[name] = fit(x)
        checks["square_activation"][str(degree)] = float(np.max(np.abs(profile[name] - u)))
    table("profile.dat", profile)

    # The small-amplitude oscillation has a large derivative norm.
    derivative_error = np.pi * np.cos(100 * np.pi * x)
    checks["derivative_counterexample"] = {
        "sup_value_error": 0.01,
        "l2_derivative_error": float(np.pi / np.sqrt(2)),
        "sampled_l2_derivative_error": float(np.sqrt(np.trapezoid(derivative_error**2, x))),
    }
    table("derivative-error.dat", {"x": x, "error": 0.01 * np.sin(100 * np.pi * x), "slope_error": derivative_error})

    depth = {"x": x}
    current = x.copy()
    for k in range(1, 5):
        current = tent(current)
        depth[f"tent{k}"] = current.copy()
    table("depth.dat", depth)
    checks["tent_composition"] = [
        {"compositions": k, "affine_intervals_on_unit_interval": 2**k, "interior_breakpoints": 2**k - 1}
        for k in range(1, 5)
    ]

    xor_x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    xor_y = np.array([0, 1, 1, 0])
    s = xor_x.sum(axis=1)
    prediction = (s > 0.5).astype(int)
    exact = relu(s) - 2 * relu(s - 1)
    assert np.array_equal(exact, xor_y)
    checks["xor"] = {"linear_threshold_accuracy": float(np.mean(prediction == xor_y)), "relu_values": exact.tolist()}
    for n in range(1, 13):
        s = np.arange(n + 1)
        parity = relu(s).astype(float)
        for k in range(1, n):
            parity += 2 * (-1)**k * relu(s - k)
        assert np.array_equal(parity, s % 2)
    checks["parity"] = {"verified_dimensions": list(range(1, 13)), "shallow_relu_units": "n"}

    # A one-sample loss gives a checkable reverse-mode differentiation example.
    sample_x, target, w, b, v, c = 0.5, 1.0, 1.0, 0.0, 1.0, 0.0
    z = w * sample_x + b
    h = max(z, 0)
    predicted = v * h + c
    error = predicted - target
    checks["one_sample_gradient"] = {
        "x": sample_x, "target": target, "z": z, "h": h, "prediction": predicted,
        "loss": error**2 / 2,
        "dc": error, "dv": error * h, "db": error * v, "dw": error * v * sample_x,
        "new_v_with_step_0.1": v - 0.1 * error * h,
    }
    checks["parameter_counts"] = {"one_hidden_100": 301, "four_hidden_20": 1321}
    checks["old_rmse_reduction_percent"] = 100 * (0.718 - 0.478) / 0.718

    # Penalty geometry for the loss (w1 - 1.4)^2 + (w2 - 1.4)^2 / 0.25 under unit L1 and L2 constraints.
    center, axes = np.array([1.4, 1.4]), np.array([1.0, 0.5])
    level = lambda p: np.sqrt(np.sum(((p - center[:, None]) / axes[:, None]) ** 2, axis=0))
    s_edge = np.linspace(0, 1, 1000001)
    diamond = np.hstack([np.vstack((1 - s_edge, s_edge)), np.vstack((-s_edge, 1 - s_edge)),
                         np.vstack((s_edge - 1, -s_edge)), np.vstack((s_edge, s_edge - 1))])
    angle = np.linspace(0, 2 * np.pi, 2000001)
    circle = np.vstack((np.cos(angle), np.sin(angle)))
    l1_point = diamond[:, np.argmin(level(diamond))]
    l2_point = circle[:, np.argmin(level(circle))]
    checks["penalty_geometry"] = {
        "loss_center": center.tolist(), "loss_semi_axes": axes.tolist(),
        "l1_minimizer": l1_point.tolist(), "l1_level": float(level(l1_point[:, None])[0]),
        "l2_minimizer": l2_point.tolist(), "l2_level": float(level(l2_point[:, None])[0]),
    }
    DATA.joinpath("mlp-checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    # Readouts are generated from the same report rather than copied manually.
    fitting = checks["data_fit"]
    readouts = {
        "TrainRMSE": fitting["training_rmse"],
        "ReferenceRMSE": fitting["reference_grid_rmse"],
        "SlopeRMSE": fitting["reference_grid_slope_rmse"],
        "ResidualRMS": fitting["reference_grid_pde_residual_rms"],
        "PolynomialGap": checks["clean_comparison"]["polynomial_sampled_sup_error"],
        "SigmoidGap": checks["clean_comparison"]["sigmoid_sampled_sup_error"],
        "QuadGap": checks["square_activation"]["2"],
        "QuartGap": checks["square_activation"]["4"],
        "PenaltyLoneLevel": checks["penalty_geometry"]["l1_level"],
        "PenaltyLtwoLevel": checks["penalty_geometry"]["l2_level"],
        "PenaltyLtwoX": checks["penalty_geometry"]["l2_minimizer"][0],
        "PenaltyLtwoY": checks["penalty_geometry"]["l2_minimizer"][1],
    }
    DATA.joinpath("readouts.tex").write_text("\n".join(f"\\newcommand{{\\{key}}}{{{value:.3g}}}" for key, value in readouts.items()) + "\n")
    print(json.dumps({"data_fit": fitting, "xor": checks["xor"]}, indent=2))


if __name__ == "__main__":
    main()
