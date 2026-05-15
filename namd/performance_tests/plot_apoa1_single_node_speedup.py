import os
import re

import pandas as pd
import matplotlib.pyplot as plt


LOG_DIR = "./logs"
OUTPUT_DIR = "../figures"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_wallclock_logs():
    """
    Read NAMD WallClock values from ApoA1 single-node log files.

    Expected log filename pattern:
        single_<cpu>.log

    Example:
        single_8.log
        single_16.log
    """

    records = []

    for filename in os.listdir(LOG_DIR):
        if not filename.startswith("single_") or not filename.endswith(".log"):
            continue

        match = re.search(r"single_(\d+)", filename)
        if not match:
            continue

        cpu = int(match.group(1))
        path = os.path.join(LOG_DIR, filename)

        with open(path, "r") as file:
            for line in file:
                if "WallClock:" in line:
                    wallclock = float(line.split()[1])
                    records.append([cpu, wallclock])
                    break

    df = pd.DataFrame(records, columns=["cpu", "wallclock"])

    if df.empty:
        raise ValueError("No matching log files found in ./logs")

    return df.sort_values("cpu").reset_index(drop=True)


def calculate_speedup_and_efficiency(df):
    """
    Calculate speedup and efficiency using the smallest CPU count as baseline.
    """

    df = df.copy()

    baseline_cpu = df["cpu"].min()
    baseline_time = df[df["cpu"] == baseline_cpu]["wallclock"].values[0]

    df["speedup"] = baseline_time / df["wallclock"]
    df["efficiency"] = df["speedup"] / (df["cpu"] / baseline_cpu)

    return df


def style_axis(axis):
    axis.set_facecolor("#f2f2f2")
    axis.grid(True, linestyle="--", alpha=0.6, color="#bdbdbd")

    for spine in axis.spines.values():
        spine.set_color("#555555")

    axis.tick_params(colors="#222222", labelsize=9)
    axis.title.set_color("#111111")
    axis.xaxis.label.set_color("#111111")
    axis.yaxis.label.set_color("#111111")


def add_annotations(axis, df):
    for _, row in df.iterrows():
        label = (
            f"T={row['wallclock']:.1f}s\n"
            f"S={row['speedup']:.2f}\n"
            f"E={row['efficiency']:.2f}"
        )

        axis.annotate(
            label,
            (row["cpu"], row["wallclock"]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
            bbox=dict(boxstyle="round", fc="white", alpha=0.9),
        )


def add_table(axis, display_df):
    axis.axis("off")

    table = axis.table(
        cellText=display_df.values,
        colLabels=["CPU", "Wall Clock", "Speedup", "Efficiency"],
        loc="center",
        cellLoc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.3)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9dde3")
            cell.set_text_props(weight="bold", color="#111111")
        else:
            cell.set_facecolor("#f7f7f7")
            cell.set_text_props(color="#111111")

        cell.set_edgecolor("#b0b0b0")


def plot_single_node_speedup(df):
    color_main = "#1f3b73"
    ideal_color = "#6c757d"

    fig = plt.figure(figsize=(20, 8), facecolor="#e9ecef")
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=[3.2, 1.2],
        hspace=0.35,
        wspace=0.25,
    )

    wallclock_axis = fig.add_subplot(grid[0, 0])
    speedup_axis = fig.add_subplot(grid[0, 1])
    efficiency_axis = fig.add_subplot(grid[0, 2])
    table_axis = fig.add_subplot(grid[1, :])

    style_axis(wallclock_axis)
    wallclock_axis.plot(
        df["cpu"],
        df["wallclock"],
        marker="o",
        linewidth=2.5,
        color=color_main,
    )
    add_annotations(wallclock_axis, df)
    wallclock_axis.set_title("Wall Clock vs CPU (Single Node)", fontsize=11)
    wallclock_axis.set_xlabel("CPU", fontsize=10)
    wallclock_axis.set_ylabel("Wall Clock (s)", fontsize=10)

    style_axis(speedup_axis)
    speedup_axis.plot(
        df["cpu"],
        df["speedup"],
        marker="o",
        linewidth=2.5,
        color=color_main,
        label="Measured",
    )

    ideal_speedup = df["cpu"] / df["cpu"].min()
    speedup_axis.plot(
        df["cpu"],
        ideal_speedup,
        linestyle="--",
        color=ideal_color,
        label="Ideal",
    )

    speedup_axis.set_title("Speedup vs CPU", fontsize=11)
    speedup_axis.set_xlabel("CPU", fontsize=10)
    speedup_axis.set_ylabel("Speedup", fontsize=10)
    speedup_axis.legend()

    style_axis(efficiency_axis)
    efficiency_axis.plot(
        df["cpu"],
        df["efficiency"],
        marker="o",
        linewidth=2.5,
        color=color_main,
    )
    efficiency_axis.set_title("Efficiency vs CPU", fontsize=11)
    efficiency_axis.set_xlabel("CPU", fontsize=10)
    efficiency_axis.set_ylabel("Efficiency", fontsize=10)

    display_df = df.copy()
    display_df["wallclock"] = display_df["wallclock"].map(lambda value: f"{value:.2f}")
    display_df["speedup"] = display_df["speedup"].map(lambda value: f"{value:.2f}")
    display_df["efficiency"] = display_df["efficiency"].map(lambda value: f"{value:.2f}")

    add_table(table_axis, display_df)

    output_path = os.path.join(OUTPUT_DIR, "apoa1_single_node_speedup.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = read_wallclock_logs()
    df = calculate_speedup_and_efficiency(df)

    print("\n=== RESULTS ===")
    print(df)

    plot_single_node_speedup(df)


if __name__ == "__main__":
    main()
