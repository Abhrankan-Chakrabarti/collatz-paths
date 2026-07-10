import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def generate_collatz_vector_path(start_num, alpha=0.25, beta=-0.15, scale=5.0):
    """
    Generates a 2D spatial path for a single Collatz sequence.
    Returns an array of (x, y) coordinates.
    """
    current = start_num
    path_num = [current]

    # 1. Compute the standard Collatz sequence
    while current > 1:
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1
        path_num.append(current)

    # 2. Map numbers to spatial coordinates
    coordinates = []
    current_theta = 0.0

    for n in path_num:
        # Determine angular drift based on parity
        if n % 2 == 0:
            current_theta += beta
        else:
            current_theta += alpha

        # Logarithmic radius scaling to compress data density
        r = np.log(n + 1) * scale

        # Convert Polar (r, theta) to Cartesian (x, y)
        x = r * np.cos(current_theta)
        y = r * np.sin(current_theta)

        coordinates.append([x, y])

    return np.array(coordinates)


def plot_single_path(start_num, ax=None, **kwargs):
    """Plot a single Collatz vector path."""
    path = generate_collatz_vector_path(start_num, **kwargs)
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(path[:, 0], path[:, 1], color="steelblue", linewidth=1)
    ax.scatter(path[0, 0], path[0, 1], color="green", s=30, zorder=5, label="start")
    ax.scatter(path[-1, 0], path[-1, 1], color="red", s=30, zorder=5, label="end (1)")
    ax.set_title(f"Collatz path: n = {start_num} ({len(path)} steps)")
    ax.set_aspect("equal")
    ax.legend()

    if standalone:
        plt.tight_layout()
        plt.savefig(f"collatz_{start_num}.png", dpi=150)
        print(f"Saved collatz_{start_num}.png")
        plt.close(fig)


def plot_multiple_paths(seeds, **kwargs):
    """Overlay multiple Collatz paths on one plot, colored by seed."""
    fig, ax = plt.subplots(figsize=(10, 10))
    colors = cm.viridis(np.linspace(0, 1, len(seeds)))

    for seed, color in zip(seeds, colors):
        path = generate_collatz_vector_path(seed, **kwargs)
        ax.plot(path[:, 0], path[:, 1], color=color, linewidth=0.8, alpha=0.8)

    ax.set_title(f"Collatz vector paths for seeds {min(seeds)}\u2013{max(seeds)}")
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig("collatz_bundle.png", dpi=150)
    print("Saved collatz_bundle.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Cached / large-scale rendering path
#
# For thousands of seeds, many trajectories share long common suffixes
# (all paths converge toward 1, and intermediate values repeat across
# different starting seeds). Caching each visited value's next step and
# angular delta avoids recomputing shared sub-paths, and is safe because
# the next step and angle for a given n depend only on n's parity — never
# on which starting seed reached it or in what order.
# ---------------------------------------------------------------------------

COLLATZ_CACHE = {1: (1, 0.0)}


def get_next_collatz_step(n, alpha=0.25, beta=-0.15):
    """Retrieves next step and angle drift, using a shared cache."""
    if n in COLLATZ_CACHE:
        return COLLATZ_CACHE[n]

    if n % 2 == 0:
        next_n = n // 2
        delta_theta = beta
    else:
        next_n = 3 * n + 1
        delta_theta = alpha

    COLLATZ_CACHE[n] = (next_n, delta_theta)
    return next_n, delta_theta


def generate_cached_path(start_num, alpha=0.25, beta=-0.15, scale=5.0):
    """Generates a path using the shared step cache — faster for large seed batches."""
    current = start_num
    path_nums = [current]
    angle_deltas = [0.0]

    while current > 1:
        current, delta = get_next_collatz_step(current, alpha, beta)
        path_nums.append(current)
        angle_deltas.append(delta)

    path_nums = np.array(path_nums)
    cum_theta = np.cumsum(angle_deltas)

    r = np.log(path_nums + 1) * scale
    x = r * np.cos(cum_theta)
    y = r * np.sin(cum_theta)

    return np.column_stack((x, y))


def plot_optimized_bundle(seeds, filename="collatz_galaxy.png", **kwargs):
    """
    Renders large, dense seed bundles (thousands of seeds) efficiently using
    the shared step cache, a dark background, and a low-alpha inferno
    colormap. Produces a denser, more glowing effect than plot_multiple_paths
    — best suited for large seed ranges (1000+) where individual trajectories
    aren't meant to be distinguished, only the aggregate structure.
    """
    fig, ax = plt.subplots(figsize=(12, 12), facecolor="#111111")
    ax.set_facecolor("#111111")

    colors = cm.inferno(np.linspace(0.3, 0.95, len(seeds)))

    for seed, color in zip(seeds, colors):
        path = generate_cached_path(seed, **kwargs)
        # Low alpha + thin lines create a glowing filament effect where paths overlap
        ax.plot(path[:, 0], path[:, 1], color=color, linewidth=0.4, alpha=0.3)

    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(filename, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    print(f"Saved {filename} (cache size: {len(COLLATZ_CACHE)} nodes)")
    plt.close(fig)


if __name__ == "__main__":
    # Single path for the famous long-trajectory seed
    example_path = generate_collatz_vector_path(27)
    print(f"Generated {len(example_path)} vector points for seed 27.")
    plot_single_path(27)

    # Bundle of paths for a range of seeds, to see the branching structure
    plot_multiple_paths(range(1, 201))

    # Large-scale cached render for a dense, glowing "galaxy" effect
    plot_optimized_bundle(range(1, 5001))
