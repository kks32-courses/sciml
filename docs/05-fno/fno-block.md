# The FNO Block

<link rel="stylesheet" href="fno-block.css">

Here is one block of a Fourier neural operator acting on a field $a(x)$ sampled at 64 points around a ring.
The block has two paths.
The upper path changes to Fourier modes, keeps the modes $k\le k_{\max}$, multiplies them by learned matrices $R(k)$, and changes back.
The lower path mixes the channels at each point with a matrix $W$.
The two paths are added and passed through an activation $\sigma$.

Press **Next** to follow the field one operation at a time, or click any box in the diagram.
The thick curves and the bars follow the selected channel.

<div class="fb-root" id="fb-root"></div>

Now try three things.

- **Square wave, $k_{\max}=3$.** The upper path returns a smooth $z(x)$ with only four modes, while the lower path $y(x)$ keeps the corners of the input.
- **$k_{\max}=0$.** The upper path keeps only the mean of each channel, so all the shape in $v_1(x)$ comes from the lower path.
- **Three waves.** The input has modes 0, 1, 3, and 7. After the activation, channel 1 has energy at modes that were zero before, and only $\sigma$ put it there.

The weights here are random, so the output $u(x)$ shows the data flow and solves no equation.
Training chooses $P$, $R(k)$, $W$, and $Q$ so that $u(x)$ matches the solution of a PDE.
The lifting $P$, the local matrix $W$, and the projection $Q$ act at each point, and $R(k)$ acts on each mode.
Which of these weights would change if we sampled the ring at 128 points instead of 64?

<script src="fno-block.js"></script>
