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


if __name__ == "__main__":
    # Single path for the famous long-trajectory seed
    example_path = generate_collatz_vector_path(27)
    print(f"Generated {len(example_path)} vector points for seed 27.")
    plot_single_path(27)

    # Bundle of paths for a range of seeds, to see the branching structure
    plot_multiple_paths(range(1, 201))
