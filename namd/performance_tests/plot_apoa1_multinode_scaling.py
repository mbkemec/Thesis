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

    Expected log filename patterns:
        single_8.log
        two_16.log
        four_32.log
    """

    pattern = re.compile(r"^(single|two|four)_(\d+)\.log$")
    records = []

    for filename in os.listdir(LOG_DIR):
        match = pattern.match(filename)
        if not match:
            continue

        series = match.group(1)
        cpu_per_node = int(match.group(2))
        path = os.path.join(LOG_DIR, filename)

        with open(path, "r") as file:
            for line in file:
                if "WallClock:" in line:
                    wallclock = float(line.split()[1])
                    records.append([series, cpu_per_node, wallclock])
                    break

    df = pd.DataFrame(
        records,
        columns=["series", "cpu_per_node", "wallclock"],
    )

    if df.empty:
        raise ValueError("No matching log files found in ./logs")

    return df


def prepare_dataframe(df):
    series_to_nodes = {
        "single": 1,
        "two": 2,
        "four": 4,
    }

    series_order = {
        "single": 1,
        "two": 2,
        "four": 3,
    }

    df = df.copy()
    df["nodes"] = df["series"].map(series_to_nodes)
    df["total_cpu"] = df["nodes"] * df["cpu_per_node"]
    df["series_order"] = df["series"].map(series_order)

    df = df.sort_values(
        by=["series_order", "cpu_per_node"],
    ).reset_index(drop=True)

    df["speedup"] = 0.0
    df["efficiency"] = 0.0

    for series in df["series"].unique():
        subset = df[df["series"] == series].sort_values("cpu_per_node")

        baseline_cpu = subset["cpu_per_node"].min()
        baseline_time = subset[
            subset["cpu_per_node"] == baseline_cpu
        ]["wallclock"].values[0]

        mask = df["series"] == series
        df.loc[mask, "speedup"] = baseline_time / df.loc[mask, "wallclock"]
        df.loc[mask, "efficiency"] = df.loc[mask, "speedup"] / (
            df.loc[mask, "cpu_per_node"] / baseline_cpu
        )

    return df


COLORS = {
    "single": "#1f3b73",
    "two": "#7a1f1f",
    "four": "#1f6f3b",
}

MARKERS = {
    "single": "o",
    "two": "s",
    "four": "^",
}

LABELS = {
    "single": "1 node",
    "two": "2 nodes",
    "four": "4 nodes",
}


def style_axis(axis):
    axis.set_facecolor("#f2f2f2")
    axis.grid(True, linestyle="--", alpha=0.6, color="#bdbdbd")

    for spine in axis.spines.values():
        spine.set_color("#555555")

    axis.tick_params(colors="#222222", labelsize=9)
    axis.title.set_color("#111111")
    axis.xaxis.label.set_color("#111111")
    axis.yaxis.label.set_color("#111111")


def add_table(axis, display_df):
    axis.axis("off")

    table = axis.table(
        cellText=display_df.values,
        colLabels=[
            "Series",
            "Nodes",
            "CPU per Node",
            "Total CPU",
            "Wall Clock",
            "Speedup",
            "Efficiency",
        ],
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1, 0.9)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9dde3")
            cell.set_text_props(weight="bold", color="#111111")
        else:
            cell.set_facecolor("#f7f7f7")
            cell.set_text_props(color="#111111")

        cell.set_edgecolor("#b0b0b0")


def plot_scaling(df):
    df_single = df[df["series"] == "single"].sort_values("cpu_per_node")
    df_two = df[df["series"] == "two"].sort_values("cpu_per_node")
    df_four = df[df["series"] == "four"].sort_values("cpu_per_node")

    fig = plt.figure(figsize=(26, 11), facecolor="#e9ecef")
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=[3.0, 1.8],
        hspace=0.45,
        wspace=0.28,
    )

    wallclock_axis = fig.add_subplot(grid[0, 0])
    speedup_axis = fig.add_subplot(grid[0, 1])
    efficiency_axis = fig.add_subplot(grid[0, 2])
    table_axis = fig.add_subplot(grid[1, :])

    for axis in [wallclock_axis, speedup_axis, efficiency_axis]:
        style_axis(axis)

    for series, subset in [
        ("single", df_single),
        ("two", df_two),
        ("four", df_four),
    ]:
        if subset.empty:
            continue

        wallclock_axis.plot(
            subset["cpu_per_node"],
            subset["wallclock"],
            marker=MARKERS[series],
            linewidth=2.2,
            markersize=6.2,
            color=COLORS[series],
            label=LABELS[series],
        )

        speedup_axis.plot(
            subset["cpu_per_node"],
            subset["speedup"],
            marker=MARKERS[series],
            linewidth=2.2,
            markersize=6.2,
            color=COLORS[series],
            label=LABELS[series],
        )

        baseline_cpu = subset["cpu_per_node"].min()
        ideal_speedup = subset["cpu_per_node"] / baseline_cpu

        speedup_axis.plot(
            subset["cpu_per_node"],
            ideal_speedup,
            linestyle="--",
            linewidth=1.5,
            color=COLORS[series],
            alpha=0.35,
        )

        efficiency_axis.plot(
            subset["cpu_per_node"],
            subset["efficiency"],
            marker=MARKERS[series],
            linewidth=2.2,
            markersize=6.2,
            color=COLORS[series],
            label=LABELS[series],
        )

    wallclock_axis.set_title("Wall Clock vs CPU per Node", fontsize=11)
    wallclock_axis.set_xlabel("CPU per Node", fontsize=10)
    wallclock_axis.set_ylabel("Wall Clock (s)", fontsize=10)
    wallclock_axis.legend(frameon=True, fontsize=8)

    speedup_axis.set_title("Speedup vs CPU per Node", fontsize=11)
    speedup_axis.set_xlabel("CPU per Node", fontsize=10)
    speedup_axis.set_ylabel("Speedup", fontsize=10)
    speedup_axis.legend(frameon=True, fontsize=8)

    efficiency_axis.set_title("Efficiency vs CPU per Node", fontsize=11)
    efficiency_axis.set_xlabel("CPU per Node", fontsize=10)
    efficiency_axis.set_ylabel("Efficiency", fontsize=10)
    efficiency_axis.legend(frameon=True, fontsize=8)

    display_df = df[
        [
            "series",
            "nodes",
            "cpu_per_node",
            "total_cpu",
            "wallclock",
            "speedup",
            "efficiency",
        ]
    ].copy()

    display_df["series"] = display_df["series"].map(LABELS)
    display_df["wallclock"] = display_df["wallclock"].map(lambda value: f"{value:.2f}")
    display_df["speedup"] = display_df["speedup"].map(lambda value: f"{value:.2f}")
    display_df["efficiency"] = display_df["efficiency"].map(lambda value: f"{value:.2f}")

    add_table(table_axis, display_df)

    output_path = os.path.join(OUTPUT_DIR, "apoa1_cpu_scaling_multinode.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = read_wallclock_logs()
    df = prepare_dataframe(df)

    print("\n=== RESULTS ===")
    print(
        df[
            [
                "series",
                "nodes",
                "cpu_per_node",
                "total_cpu",
                "wallclock",
                "speedup",
                "efficiency",
            ]
        ]
    )

    plot_scaling(df)


if __name__ == "__main__":
    main()
