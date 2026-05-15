import os
import re

import pandas as pd
import matplotlib.pyplot as plt


LOG_DIR = "./logs"
OUTPUT_DIR = "../figures"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_wallclock_logs():
    """
    Read NAMD WallClock values from ApoA1 multi-node log files.

    Expected log filename pattern:
        <case>_<nodes>n_<cpu_per_node>ppn.log

    Example:
        apoa1_1n_8ppn.log
        apoa1_2n_16ppn.log
    """

    records = []

    for filename in os.listdir(LOG_DIR):
        if not filename.endswith(".log"):
            continue

        match = re.search(r"_(\d+)n_(\d+)ppn", filename)
        if not match:
            continue

        nodes = int(match.group(1))
        cpu_per_node = int(match.group(2))
        path = os.path.join(LOG_DIR, filename)

        with open(path, "r") as file:
            for line in file:
                if "WallClock:" in line:
                    wallclock = float(line.split()[1])
                    records.append([nodes, cpu_per_node, wallclock])
                    break

    df = pd.DataFrame(
        records,
        columns=["nodes", "cpu_per_node", "wallclock"],
    )

    if df.empty:
        raise ValueError("No matching log files found in ./logs")

    return df.sort_values(by=["cpu_per_node", "nodes"]).reset_index(drop=True)


def calculate_speedup_and_efficiency(df):
    """
    Calculate speedup and efficiency for each CPU-per-node series.
    Each series is normalized to its single-node runtime.
    """

    df = df.copy()
    df["total_cpu"] = df["nodes"] * df["cpu_per_node"]
    df["speedup"] = 0.0
    df["efficiency"] = 0.0

    for cpu_per_node in df["cpu_per_node"].unique():
        baseline = df[
            (df["cpu_per_node"] == cpu_per_node) & (df["nodes"] == 1)
        ]

        if baseline.empty:
            continue

        baseline_time = baseline["wallclock"].values[0]
        mask = df["cpu_per_node"] == cpu_per_node

        df.loc[mask, "speedup"] = baseline_time / df.loc[mask, "wallclock"]
        df.loc[mask, "efficiency"] = df.loc[mask, "speedup"] / df.loc[mask, "nodes"]

    return df


COLORS = {
    8: "#1f3b73",
    16: "#7a1f1f",
}

IDEAL_COLOR = "#6c757d"


def style_axis(axis):
    axis.set_facecolor("#f2f2f2")
    axis.grid(True, linestyle="--", alpha=0.6, color="#bdbdbd")

    for spine in axis.spines.values():
        spine.set_color("#555555")

    axis.tick_params(colors="#222222", labelsize=9)
    axis.title.set_color("#111111")
    axis.xaxis.label.set_color("#111111")
    axis.yaxis.label.set_color("#111111")


def add_annotation(axis, subset, above=True):
    for _, row in subset.iterrows():
        offset_y = 12 if above else -40
        vertical_alignment = "bottom" if above else "top"

        label = (
            f"T={row['wallclock']:.1f}s\n"
            f"S={row['speedup']:.2f}\n"
            f"E={row['efficiency']:.2f}\n"
            f"Total CPU={int(row['total_cpu'])}"
        )

        axis.annotate(
            label,
            (row["nodes"], row["wallclock"]),
            textcoords="offset points",
            xytext=(0, offset_y),
            ha="center",
            va=vertical_alignment,
            fontsize=7.6,
            color="#111111",
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#cccccc", alpha=0.9),
        )


def add_table(axis, display_df):
    axis.axis("off")

    table = axis.table(
        cellText=display_df.values,
        colLabels=[
            "Nodes",
            "CPU per Node",
            "Wall Clock",
            "Speedup",
            "Efficiency",
            "Total CPU",
        ],
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8.2)
    table.scale(1, 1.15)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9dde3")
            cell.set_text_props(weight="bold", color="#111111")
        else:
            cell.set_facecolor("#f7f7f7")
            cell.set_text_props(color="#111111")

        cell.set_edgecolor("#b0b0b0")


def plot_cpu_per_node_comparison(df):
    df_8 = df[df["cpu_per_node"] == 8].sort_values("nodes")
    df_16 = df[df["cpu_per_node"] == 16].sort_values("nodes")

    fig = plt.figure(figsize=(20, 8), facecolor="#e9ecef")
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=[3.0, 1.0],
        hspace=0.30,
        wspace=0.22,
    )

    axis_8 = fig.add_subplot(grid[0, 0])
    axis_16 = fig.add_subplot(grid[0, 1])
    comparison_axis = fig.add_subplot(grid[0, 2])
    table_axis = fig.add_subplot(grid[1, :])

    style_axis(axis_8)
    axis_8.plot(
        df_8["nodes"],
        df_8["wallclock"],
        marker="o",
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[8],
    )
    add_annotation(axis_8, df_8, above=True)
    axis_8.set_title("Wall Clock vs Nodes (8 CPU per Node)", fontsize=11)
    axis_8.set_xlabel("Nodes", fontsize=10)
    axis_8.set_ylabel("Wall Clock (s)", fontsize=10)
    axis_8.set_xticks(df_8["nodes"])

    style_axis(axis_16)
    axis_16.plot(
        df_16["nodes"],
        df_16["wallclock"],
        marker="o",
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[16],
    )
    add_annotation(axis_16, df_16, above=True)
    axis_16.set_title("Wall Clock vs Nodes (16 CPU per Node)", fontsize=11)
    axis_16.set_xlabel("Nodes", fontsize=10)
    axis_16.set_ylabel("Wall Clock (s)", fontsize=10)
    axis_16.set_xticks(df_16["nodes"])

    style_axis(comparison_axis)
    comparison_axis.plot(
        df_8["nodes"],
        df_8["wallclock"],
        marker="o",
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[8],
        label="8 CPU per Node",
    )
    comparison_axis.plot(
        df_16["nodes"],
        df_16["wallclock"],
        marker="o",
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[16],
        label="16 CPU per Node",
    )

    if not df_8.empty:
        nodes = df_8["nodes"]
        baseline_time = df_8[df_8["nodes"] == 1]["wallclock"].values[0]
        ideal_wallclock = baseline_time / nodes

        comparison_axis.plot(
            nodes,
            ideal_wallclock,
            linestyle="--",
            linewidth=1.8,
            color=IDEAL_COLOR,
            label="Ideal scaling",
        )

    add_annotation(comparison_axis, df_8, above=True)
    add_annotation(comparison_axis, df_16, above=False)

    comparison_axis.set_title("Comparison + Ideal Scaling", fontsize=11)
    comparison_axis.set_xlabel("Nodes", fontsize=10)
    comparison_axis.set_ylabel("Wall Clock (s)", fontsize=10)
    comparison_axis.set_xticks(sorted(df["nodes"].unique()))

    legend = comparison_axis.legend(frameon=True, fontsize=9)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor("#cccccc")

    display_df = df[
        ["nodes", "cpu_per_node", "wallclock", "speedup", "efficiency", "total_cpu"]
    ].copy()

    display_df["wallclock"] = display_df["wallclock"].map(lambda value: f"{value:.2f}")
    display_df["speedup"] = display_df["speedup"].map(lambda value: f"{value:.2f}")
    display_df["efficiency"] = display_df["efficiency"].map(lambda value: f"{value:.2f}")

    add_table(table_axis, display_df)

    output_path = os.path.join(OUTPUT_DIR, "apoa1_speedup_8_vs_16_cpu_per_node.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = read_wallclock_logs()
    df = calculate_speedup_and_efficiency(df)

    print("\n=== RESULTS ===")
    print(df)

    plot_cpu_per_node_comparison(df)


if __name__ == "__main__":
    main()
