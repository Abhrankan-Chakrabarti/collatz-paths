# Collatz Paths

A small Python visualizer that turns Collatz ("3n+1") trajectories into 2D spatial paths. Each step in a sequence becomes a point in the plane: odd steps (3n+1) and even steps (n/2) turn in opposite directions, and the radius grows logarithmically with the current value — producing the branching, coral-like patterns commonly associated with Collatz visualizations.

## Preview

![Single Collatz path for seed 27](collatz_27.png)
*Trajectory for n = 27 — 112 steps, one of the most famous "surprisingly long" examples for small starting values.*

![Bundle of Collatz paths for seeds 1–200](collatz_bundle.png)
*Overlaid trajectories for seeds 1–200, colored by seed. All paths converge toward the origin as they reach 1.*

![Dense cached bundle for 5000 seeds](collatz_galaxy.png)
*5000 overlaid trajectories rendered with the shared step cache, dark background, and inferno colormap — the density and shared sub-paths near convergence create a glowing, galaxy-like structure.*

## The Collatz Conjecture

For any positive integer n: if n is even, divide by 2; if n is odd, compute 3n+1. Repeat. The conjecture states every starting value eventually reaches 1. It remains unproven despite verification for all n up to very large bounds.

A companion project, [`collatz.sh`](https://github.com/Abhrankan-Chakrabarti/pari-gp-scripts), computes trajectory *statistics* (step counts, peak values) across a range of starting values from the command line via PARI/GP. This repo visualizes individual trajectories geometrically instead.

## Installation

```bash
git clone https://github.com/Abhrankan-Chakrabarti/collatz-paths.git
cd collatz-paths
pip install -r requirements.txt
```

`requirements.txt`:
```
numpy
matplotlib
```

## Usage

```bash
python collatz.py
```

By default this generates and saves `collatz_27.png` (a single path) and `collatz_bundle.png` (seeds 1–200 overlaid).

```python
from collatz import generate_collatz_vector_path, plot_single_path, plot_multiple_paths

# Just the coordinates, no plotting
path = generate_collatz_vector_path(27)

# Save a single trajectory plot
plot_single_path(97)

# Save an overlay of many trajectories
plot_multiple_paths(range(1, 501))
```

## API

### `generate_collatz_vector_path(start_num, alpha=0.25, beta=-0.15, scale=5.0)`

Computes the Collatz sequence for `start_num`, then maps it to 2D coordinates:

- **`alpha`** — angular turn (radians) applied on each odd step (3n+1)
- **`beta`** — angular turn (radians) applied on each even step (n/2); negative by default so odd and even steps curve in opposite directions
- **`scale`** — multiplier on the logarithmic radius `log(n+1) * scale`, controlling overall plot size

Returns an `(steps, 2)` NumPy array of `(x, y)` coordinates.

### `plot_single_path(start_num, ax=None, **kwargs)`

Plots one trajectory with start (green) and end-at-1 (red) markers. If `ax` is provided, draws onto an existing matplotlib axis instead of creating a new figure — useful for building custom grids of multiple plots. `**kwargs` are passed through to `generate_collatz_vector_path`.

### `plot_multiple_paths(seeds, **kwargs)`

Overlays trajectories for an iterable of seeds, colored by seed order via a viridis gradient. Saves `collatz_bundle.png`. `**kwargs` are passed through to `generate_collatz_vector_path`. Best for smaller seed ranges (up to a few hundred) where individual paths are still meant to be distinguishable.

### `generate_cached_path(start_num, alpha=0.25, beta=-0.15, scale=5.0)`

Equivalent to `generate_collatz_vector_path`, but reads and writes a shared module-level cache (`COLLATZ_CACHE`) keyed by value. Since the next step and angular delta for a given `n` depend only on `n`'s parity — never on which seed reached it or in what order — caching is safe and avoids recomputing shared sub-paths across large seed batches, where many trajectories converge onto common suffixes.

### `plot_optimized_bundle(seeds, filename="collatz_galaxy.png", **kwargs)`

Renders large seed bundles (thousands of seeds) using `generate_cached_path`, a dark background, thin low-alpha lines, and an inferno colormap — producing a dense, glowing effect where overlapping shared sub-paths blend together. Best for large seed ranges (1000+) where the aggregate structure matters more than distinguishing individual trajectories.

```python
plot_optimized_bundle(range(1, 5001))
# Saved collatz_galaxy.png (cache size: 10871 nodes)
```

## Customizing the Look

Try different `alpha`/`beta` combinations for different visual signatures:

```python
plot_multiple_paths(range(1, 300), alpha=0.5, beta=-0.3, scale=3.0)
```

Larger `alpha`/`beta` magnitudes produce tighter spirals; a larger `scale` spreads the paths out more.

## License

MIT — see [LICENSE](LICENSE) for details.
