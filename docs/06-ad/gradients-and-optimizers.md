# Gradients and Optimizers

<link rel="stylesheet" href="gradients-and-optimizers.css">

Here is a ball launched from the ground with speed $v$ at an angle $a$ above the horizontal.
We observe the top of its arc, and we want the $v$ and $a$ that produced it.
The top of the arc sits at

$$
\mathbf y(v, a) = \left(\frac{v^2 \sin 2a}{2g},\; \frac{v^2 \sin^2 a}{2g}\right),
$$

and we measure the mismatch with the loss

$$
L(v, a) = \tfrac12 \lVert \mathbf y(v, a) - \mathbf y^* \rVert^2 ,
$$

where $\mathbf y^*$ is the observed top, produced here by $v = 20$ m/s and $a = 50°$.
Two separate jobs turn $L$ into an answer.
Automatic differentiation computes the gradient $\nabla L$.
An optimizer decides which step to take with that gradient.

## Where the gradient comes from

The chain rule splits the gradient into a physics part and a mismatch part,

$$
\nabla L = J^T \mathbf r, \qquad J = \frac{\partial \mathbf y}{\partial (v, a)}, \qquad \mathbf r = \mathbf y - \mathbf y^*,
$$

where $J$ is the $2 \times 2$ Jacobian of the top of the arc and $\mathbf r$ is the residual.
How does a program compute $J^T \mathbf r$ when nobody writes $J$ down?
It records the computation of $L$ as a list of elementary operations, the tape, and applies the chain rule one row at a time.
Forward mode pushes a tangent $\dot w$ down the tape next to each value $w$.
Reverse mode records the values first and then pulls an adjoint $\bar w = \partial L / \partial w$ up the tape.

<div class="go-root" id="go-tape"></div>

Drag the dot to change $v$ and $a$, and press **Next row** to apply one row of the chain rule.

- **Forward, seed $v$.** Rows 8 and 9 give $(\dot x, \dot z)$, the rate at which the top of the arc moves as $v$ grows, which is the first column of $J$. The orange arrow is the linear prediction for $\delta v = 2$ m/s, and the dotted arc is the true arc at $v + 2$ m/s. Row 12 returns one number, $\partial L / \partial v$, and $\partial L / \partial a$ needs a second sweep with the seed $a$.
- **Reverse.** Rows 8 and 9 receive the residual, $(\bar x, \bar z) = \mathbf r$, drawn as $-\mathbf r$ from the top of the arc to the target. Rows 1 and 2 return $J^T \mathbf r$, both partial derivatives from one sweep. For a scalar loss of $n$ parameters, forward mode needs $n$ sweeps and reverse mode needs one.
- **Units.** Row 3 converts degrees to radians, and its adjoint multiplies by $\pi/180$. Measuring $a$ in radians would multiply $\partial L/\partial a$ by $180/\pi$ and leave $\partial L / \partial v$ unchanged, so the gradient depends on the units of the parameters. This is the scaling argument of [Physics-based Deep Learning](https://www.physicsbaseddeeplearning.org/physgrad.html). The $-\nabla L$ arrow crosses the contours at a right angle only when 1 m/s and 1° take the same length on the screen.

## Same gradient, different steps

So we have the gradient. What step should we take?
The obvious move goes downhill, $\mathbf x_{k+1} = \mathbf x_k - \eta\, \mathbf g_k$ with $\mathbf g_k = \nabla L(\mathbf x_k)$.
Each optimizer below makes a different guess about the loss near $\mathbf x_k$.
It replaces $L$ by a quadratic bowl in the step $\mathbf d$,

$$
q(\mathbf d) = \mathbf m^T \mathbf d + \tfrac12\, \mathbf d^T B\, \mathbf d ,
$$

and moves to the bottom of the bowl, $\mathbf d = -B^{-1} \mathbf m$.
The optimizers differ in the slope $\mathbf m$ and the curvature $B$ they put into the bowl.

| Optimizer | Slope $\mathbf m$ | Curvature $B$ | Step $\mathbf d$ |
|---|---|---|---|
| Gradient descent | $\mathbf g_k$ | $I/\eta$, a round bowl | $-\eta\, \mathbf g_k$ |
| Adam | $\hat{\mathbf m}_k$, an average of past gradients | $\operatorname{diag}\big(\sqrt{\hat{\mathbf v}_k} + \epsilon\big)/\mathrm{lr}$, a bowl aligned with the axes | $-\mathrm{lr}\; \hat{\mathbf m}_k / \big(\sqrt{\hat{\mathbf v}_k} + \epsilon\big)$ |
| Newton | $\mathbf g_k$ | the Hessian $\nabla^2 L(\mathbf x_k)$ | $-[\nabla^2 L(\mathbf x_k)]^{-1} \mathbf g_k$ |
| L-BFGS | $\mathbf g_k$ | $H_k^{-1}$, estimated from the last $m$ steps | $-t\, H_k\, \mathbf g_k$ |

Adam averages the gradient and its square, coordinate by coordinate, $\mathbf m_k = \beta_1 \mathbf m_{k-1} + (1-\beta_1)\, \mathbf g_k$ and $\mathbf v_k = \beta_2 \mathbf v_{k-1} + (1-\beta_2)\, \mathbf g_k^2$.
It corrects the start-up bias with $\hat{\mathbf m}_k = \mathbf m_k / (1 - \beta_1^k)$ and $\hat{\mathbf v}_k = \mathbf v_k / (1 - \beta_2^k)$, with $\beta_1 = 0.9$, $\beta_2 = 0.999$, and $\epsilon = 10^{-8}$.
L-BFGS stores the last $m$ steps $\mathbf s_i = \mathbf x_{i+1} - \mathbf x_i$ and gradient changes $\mathbf y_i = \mathbf g_{i+1} - \mathbf g_i$.
Each pair measures the curvature along one step, $\mathbf y_i^T \mathbf s_i / \mathbf s_i^T \mathbf s_i$.
The two-loop recursion applies the BFGS update with these pairs to $\gamma I$, where $\gamma = \mathbf s^T \mathbf y / \mathbf y^T \mathbf y$ for the newest pair, so $H_k$ satisfies the secant condition $H_k \mathbf y_{k-1} = \mathbf s_{k-1}$.
The recursion works with the $2m$ stored vectors and never forms an $n \times n$ matrix.
A line search then halves $t$, starting from 1, until $L(\mathbf x_k + t \mathbf d) \le L(\mathbf x_k) + 10^{-4}\, t\, \mathbf g_k^T \mathbf d$.

The surface view draws $L$ as a surface and the bowl of the selected optimizer as a translucent surface through the current point, with its bottom marked ×.
The bowl touches the loss with the same slope for gradient descent, Newton, and L-BFGS, and with Adam's averaged slope $\hat{\mathbf m}_k$ for Adam.
The contour view draws the same bowl as dashed contours, a black arrow along $-\mathbf g_k$, and the colored step, and there you can drag the start.

<div class="go-root" id="go-lab"></div>

Now look at what each guess does.

- **Narrow valley, rotation 0°.** Here $L = \tfrac12(x_1^2 + 64\, x_2^2)$. Newton's bowl is the loss itself, so Newton reaches the minimum in one step. Gradient descent is stable only for $\eta < 2/64$, and with such an $\eta$ it crawls along the valley floor. Adam's first step is $-\mathrm{lr}\, \operatorname{sign}(\mathbf g_1)$, because $\hat{\mathbf m}_1 = \mathbf g_1$ and $\sqrt{\hat{\mathbf v}_1} = |\mathbf g_1|$, so Adam removes the scale of each coordinate and passes gradient descent.
- **Narrow valley, rotation 45°.** The start rotates with the valley, so gradient descent, Newton, and L-BFGS repeat their paths, rotated. Adam's bowl stays aligned with the axes while the valley turns, and Adam falls behind gradient descent.
- **Rosenbrock.** Newton's bowl changes shape at every step. Pure Newton has no line search, so its second step leaves the plot and raises the loss from 4.7 to 1412, and it still reaches $(1, 1)$ in 7 steps. L-BFGS learns the curvature from its pairs and arrives in 42 steps. Gradient descent and Adam are still in the curved valley after 500 steps.
- **Double well.** At the start the Hessian has a negative eigenvalue along $x_1$, so Newton's bowl is a saddle. Newton steps to the saddle point at the origin, where the gradient vanishes, and stops there. The other three reach the minimum at $(1, 0)$.
- **Noise.** The noise slider adds Gaussian noise to every gradient, as a minibatch would. Gradient descent and Adam keep descending until the noise outweighs the gradient, and then they wander near the minimum. Newton multiplies the noise by $[\nabla^2 L]^{-1}$, which is large along the valley floor, and leaves the plot. L-BFGS builds its curvature from differences of noisy gradients, and its line search fails within a few steps.
- **Projectile, top of the arc.** Newton reaches $v = 20$ m/s and $a = 50°$ in 8 steps and L-BFGS in 12. Gradient descent moves mostly in $v$, because $\partial L / \partial v$ is larger than $\partial L / \partial a$ with $a$ in degrees, and after 500 steps it is still creeping along $a$.
- **Projectile, landing distance.** Now one number is observed, and $L = 0$ on the whole curve $v^2 \sin 2a = g R^*$. Each optimizer stops at a different point of this curve, and none returns $a = 50°$. The arcs in the physics panel land at the same distance and differ everywhere else. A loss of zero leaves the parameters undetermined when the data cannot tell them apart.

| Optimizer | Information per step | Extra memory for $n$ parameters | Slow or wrong when |
|---|---|---|---|
| Gradient descent | one gradient | none | the curvature differs between directions |
| Adam | one gradient and two running averages | $2n$ | the valley is not aligned with the coordinate axes |
| Newton | one gradient and one Hessian | $n^2$, plus an $n \times n$ solve | the Hessian is indefinite or singular, or $n$ is large |
| L-BFGS | one gradient, loss values in the line search, and $m$ pairs | $2mn$ | the gradients are noisy, or the curvature changes faster than the memory |

The [AD notebook](06-ad.ipynb) runs Adam and L-BFGS in JAX on a full-waveform inversion, and the [Burgers benchmark](../01-pinns/burgers-optimizers.ipynb) compares second-stage optimizers on a PINN.
With a million parameters and minibatch gradients, which of these bowls can we still compute and store?

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<script src="gradients-and-optimizers.js"></script>
