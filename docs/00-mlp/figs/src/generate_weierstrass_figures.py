#!/usr/bin/env python3
"""Generate Weierstrass approximation figures with transparent backgrounds"""

import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
import torch
import torch.nn as nn
import torch.optim as optim
from scipy.special import comb

# Set up matplotlib for transparent backgrounds
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True

# Target function
target_func = lambda x: np.sin(np.pi * x)

# Figure 1: Polynomial Approximation of sin(πx)
def generate_polynomial_approximation():
    """Generate figure showing polynomial approximations of increasing degree"""
    
    x = np.linspace(0, 1, 200)
    y_true = target_func(x)
    
    plt.figure(figsize=(12, 8))
    
    degrees = [3, 5, 7, 9]
    for i, degree in enumerate(degrees):
        plt.subplot(2, 2, i + 1)
        
        # Fit polynomial
        poly = Polynomial.fit(np.linspace(0, 1, 100), 
                              target_func(np.linspace(0, 1, 100)), degree)
        y_approx = poly(x)
        
        # Calculate error
        error = np.max(np.abs(y_true - y_approx))
        
        # Plot
        plt.plot(x, y_true, 'b-', linewidth=2, label='Target: $\\sin(\\pi x)$', alpha=0.7)
        plt.plot(x, y_approx, 'r--', linewidth=2, label=f'Polynomial (degree {degree})')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(f'Degree {degree} Approximation\nMax Error: {error:.4f}')
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        plt.xlim(0, 1)
        plt.ylim(-0.2, 1.2)
    
    plt.suptitle('Polynomial Approximation of $\\sin(\\pi x)$ (Weierstrass)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('../polynomial-approximation-sinpi.png', dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    print("Generated: polynomial-approximation-sinpi.png")

# Figure 2: Bernstein Polynomial Approximation
def generate_bernstein_approximation():
    """Generate figure showing Bernstein polynomial convergence"""
    
    def bernstein_polynomial(f, n, x):
        """Compute n-th Bernstein polynomial approximation"""
        result = np.zeros_like(x)
        for k in range(n + 1):
            # Bernstein basis polynomial
            basis = comb(n, k) * (x ** k) * ((1 - x) ** (n - k))
            # Weight by function value at k/n
            result += f(k / n) * basis
        return result
    
    plt.figure(figsize=(12, 4))
    
    x = np.linspace(0, 1, 200)
    y_true = target_func(x)
    
    degrees = [5, 10, 20, 40]
    for i, n in enumerate(degrees):
        plt.subplot(1, 4, i + 1)
        y_bernstein = bernstein_polynomial(target_func, n, x)
        
        plt.plot(x, y_true, 'b-', linewidth=2, label='$\\sin(\\pi x)$', alpha=0.7)
        plt.plot(x, y_bernstein, 'r--', linewidth=2, label=f'Bernstein n={n}')
        
        error = np.max(np.abs(y_true - y_bernstein))
        plt.title(f'n = {n}\nError: {error:.4f}')
        plt.xlabel('x')
        if i == 0:
            plt.ylabel('y')
        plt.legend(loc='upper right', fontsize=8)
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.2, 1.2)
    
    plt.suptitle('Bernstein Polynomial Approximation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('../bernstein-approximation.png', dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    print("Generated: bernstein-approximation.png")

# Figure 3: Polynomial vs Neural Network Comparison
def generate_polynomial_vs_nn():
    """Generate comparison between polynomial and neural network approximation"""
    
    # Simple neural network
    class SimpleNN(nn.Module):
        def __init__(self, hidden_size):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(1, hidden_size),
                nn.Sigmoid(),
                nn.Linear(hidden_size, 1)
            )
        
        def forward(self, x):
            return self.net(x)
    
    # Train neural network
    def train_nn(hidden_size=10, epochs=10000):
        x_train = torch.linspace(0, 1, 200).reshape(-1, 1)
        y_train = torch.tensor([target_func(x.item()) for x in x_train], 
                               dtype=torch.float32).reshape(-1, 1)
        
        model = SimpleNN(hidden_size)
        optimizer = optim.Adam(model.parameters(), lr=0.1)
        criterion = nn.MSELoss()
        
        # Train with early stopping
        best_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            y_pred = model(x_train)
            loss = criterion(y_pred, y_train)
            loss.backward()
            optimizer.step()
            
            # Early stopping
            if loss.item() < best_loss:
                best_loss = loss.item()
                patience_counter = 0
            else:
                patience_counter += 1
                
            if patience_counter > 500 or loss.item() < 1e-6:
                break
        
        return model
    
    # Generate comparison plot
    plt.figure(figsize=(12, 5))
    
    x_test = np.linspace(0, 1, 200)
    y_true = target_func(x_test)
    
    # Polynomial approximation
    poly_degree = 9
    poly = Polynomial.fit(np.linspace(0, 1, 100), 
                          target_func(np.linspace(0, 1, 100)), poly_degree)
    y_poly = poly(x_test)
    poly_params = poly_degree + 1
    
    # Neural network approximation
    nn_hidden = 10
    model = train_nn(nn_hidden, epochs=10000)
    x_test_torch = torch.tensor(x_test.reshape(-1, 1), dtype=torch.float32)
    with torch.no_grad():
        y_nn = model(x_test_torch).numpy().flatten()
    nn_params = 1 * nn_hidden + nn_hidden + nn_hidden * 1 + 1  # weights + biases
    
    # Plot comparison
    plt.subplot(1, 3, 1)
    plt.plot(x_test, y_true, 'k-', linewidth=3, label='Target', alpha=0.8)
    plt.plot(x_test, y_poly, 'b--', linewidth=2, label=f'Polynomial (deg {poly_degree})')
    plt.plot(x_test, y_nn, 'r:', linewidth=2, label=f'Neural Net ({nn_hidden} hidden)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Function Approximation')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.plot(x_test, np.abs(y_true - y_poly), 'b-', linewidth=2, 
             label=f'Polynomial ({poly_params} params)')
    plt.plot(x_test, np.abs(y_true - y_nn), 'r-', linewidth=2, 
             label=f'Neural Net ({nn_params} params)')
    plt.xlabel('x')
    plt.ylabel('|Error|')
    plt.title('Approximation Error')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    plt.subplot(1, 3, 3)
    errors_comparison = {
        'Polynomial\n(10 params)': np.max(np.abs(y_true - y_poly)),
        f'Neural Net\n({nn_params} params)': np.max(np.abs(y_true - y_nn))
    }
    bars = plt.bar(errors_comparison.keys(), errors_comparison.values(), 
                   color=['blue', 'red'], alpha=0.7)
    plt.ylabel('Maximum Error')
    plt.title('Error Comparison')
    for bar, error in zip(bars, errors_comparison.values()):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0001,
                 f'{error:.4f}', ha='center', fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Weierstrass (Polynomial) vs Universal Approximation (Neural Network)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('../polynomial-vs-nn-comparison.png', dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    print("Generated: polynomial-vs-nn-comparison.png")

# Figure 4: Convergence plot
def generate_convergence_plot():
    """Generate convergence plot for polynomial approximation"""
    
    x = np.linspace(0, 1, 100)
    y_true = target_func(x)
    
    degrees = range(1, 15)
    errors = []
    
    for degree in degrees:
        poly = Polynomial.fit(x, y_true, degree)
        y_approx = poly(x)
        error = np.max(np.abs(y_true - y_approx))
        errors.append(error)
    
    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(degrees, errors, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Polynomial Degree')
    plt.ylabel('Maximum Approximation Error')
    plt.title('Weierstrass Convergence')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    plt.subplot(1, 2, 2)
    # Show multiple approximations overlaid
    x_fine = np.linspace(0, 1, 200)
    y_true_fine = target_func(x_fine)
    plt.plot(x_fine, y_true_fine, 'k-', linewidth=3, label='$\\sin(\\pi x)$', alpha=0.8)
    
    for degree in [3, 5, 9]:
        poly = Polynomial.fit(x, y_true, degree)
        plt.plot(x_fine, poly(x_fine), '--', linewidth=2, label=f'Degree {degree}', alpha=0.7)
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Multiple Polynomial Approximations')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-1.5, 1.5)
    
    plt.tight_layout()
    plt.savefig('../polynomial-convergence.png', dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    print("Generated: polynomial-convergence.png")

if __name__ == "__main__":
    print("Generating Weierstrass approximation figures...")
    generate_polynomial_approximation()
    generate_bernstein_approximation()
    generate_polynomial_vs_nn()
    generate_convergence_plot()
    print("All figures generated successfully!")