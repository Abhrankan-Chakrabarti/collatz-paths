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
# Shared-tree rendering path (v1.2.0+)
#
# For thousands of seeds, many trajectories converge onto the same
# intermediate values on their way to 1. GEOMETRY_CACHE maps each value n
# directly to an *absolute* (theta, x, y) — computed once, relative to the
# fixed anchor n=1 at the origin. This guarantees every path that reaches a
# given n arrives at exactly the same point in space, producing a true
# shared tree rather than approximately-overlapping copies.
#
# (An earlier version cached each value's *relative* angle delta and
# accumulated it per-path via cumsum — but two different-length paths
# reaching the same n would accumulate different absolute angles, so the
# same number landed in different places depending on which path visited
# it. That produced a denser but geometrically inconsistent "galaxy" look.
# Anchoring every value's angle to n=1 fixes this.)
#
# compute_spatial_node is iterative rather than recursive: Python's default
# recursion limit (1000) can be exceeded by individual Collatz trajectories,
# which are empirically unbounded and reach into the thousands of steps for
# some starting values.
# ---------------------------------------------------------------------------

GEOMETRY_CACHE = {1: {"theta": 0.0, "x": 0.0, "y": 0.0}}


def compute_spatial_node(n, alpha=0.25, beta=-0.15, scale=5.0):
    """Computes and caches the absolute angle and coordinates for n."""
    # Walk forward from n, collecting the chain of uncached values
    chain = []
    current = n
    while current not in GEOMETRY_CACHE:
        chain.append(current)
        current = current // 2 if current % 2 == 0 else 3 * current + 1

    # Walk the chain backwards, computing each node from its known parent
    parent = GEOMETRY_CACHE[current]
    for value in reversed(chain):
        delta_theta = beta if value % 2 == 0 else alpha
        absolute_theta = parent["theta"] + delta_theta
        r = np.log(value + 1) * scale
        node = {
            "theta": absolute_theta,
            "x": r * np.cos(absolute_theta),
            "y": r * np.sin(absolute_theta),
        }
        GEOMETRY_CACHE[value] = node
        parent = node

    return GEOMETRY_CACHE[n]


def generate_cached_path(start_num, alpha=0.25, beta=-0.15, scale=5.0):
    """Generates a path using the shared geometry cache — faster and
    geometrically consistent for large seed batches."""
    current = start_num
    path_coords = []

    while True:
        node = compute_spatial_node(current, alpha, beta, scale)
        path_coords.append([node["x"], node["y"]])
        if current == 1:
            break
        current = current // 2 if current % 2 == 0 else 3 * current + 1

    return np.array(path_coords)


def plot_optimized_bundle(seeds, filename="collatz_galaxy.png", alpha=0.25, beta=-0.15, scale=5.0):
    """
    Renders large seed bundles (thousands of seeds) using the shared
    geometry cache, a dark background, and a low-alpha inferno colormap.
    Because every shared value maps to one fixed point, paths visually
    fuse into common trunks rather than forming separate near-overlapping
    strands — best suited for large seed ranges (1000+) where the aggregate
    tree structure matters more than distinguishing individual trajectories.
    """
    for seed in seeds:
        compute_spatial_node(seed, alpha, beta, scale)

    fig, ax = plt.subplots(figsize=(12, 12), facecolor="#0B0B10")
    ax.set_facecolor("#0B0B10")

    colors = cm.inferno(np.linspace(0.25, 0.9, len(seeds)))

    for seed, color in zip(seeds, colors):
        path = generate_cached_path(seed, alpha, beta, scale)
        ax.plot(path[:, 0], path[:, 1], color=color, linewidth=0.3, alpha=0.25)

    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(filename, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    print(f"Saved {filename} ({len(GEOMETRY_CACHE)} unique structural nodes)")
    plt.close(fig)


if __name__ == "__main__":
    # Single path for the famous long-trajectory seed
    example_path = generate_collatz_vector_path(27)
    print(f"Generated {len(example_path)} vector points for seed 27.")
    plot_single_path(27)

    # Bundle of paths for a range of seeds, to see the branching structure
    plot_multiple_paths(range(1, 201))

    # Large-scale shared-tree render for a unified, fused "galaxy" effect
    plot_optimized_bundle(range(1, 10001), alpha=0.21, beta=-0.13, scale=8.0)
