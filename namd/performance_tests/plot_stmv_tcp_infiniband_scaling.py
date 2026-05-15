import os
import re

import pandas as pd
import matplotlib.pyplot as plt


LOG_DIR = "./logs"
OUTPUT_DIR = "../figures"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_wallclock_logs():
    """
    Read NAMD WallClock values from log files.

    Expected log filename patterns:
        single_namd3_tcp16.log
        single_namd3_inf16.log
    """

    pattern = re.compile(r"^single_namd3_(tcp|inf)(\d+)\.log$")
    records = []

    for filename in os.listdir(LOG_DIR):
        match = pattern.match(filename)
        if not match:
            continue

        communication_type = match.group(1)
        total_cpu = int(match.group(2))
        path = os.path.join(LOG_DIR, filename)

        with open(path, "r") as file:
            for line in file:
                if "WallClock:" in line:
                    wallclock = float(line.split()[1])
                    records.append(
                        [communication_type, total_cpu, wallclock, filename]
                    )
                    break

    df = pd.DataFrame(
        records,
        columns=["comm", "total_cpu", "wallclock", "file"],
    )

    if df.empty:
        raise ValueError("No matching log files found in ./logs")

    return df.sort_values(by=["comm", "total_cpu"]).reset_index(drop=True)


def calculate_speedup_and_efficiency(df):
    """
    Calculate speedup and efficiency separately for each communication type.
    Each communication type is normalized to its own smallest CPU count.
    """

    df = df.copy()
    df["speedup"] = 0.0
    df["efficiency"] = 0.0
    df["baseline_cpu"] = 0
    df["baseline_time"] = 0.0

    for comm in df["comm"].unique():
        subset = df[df["comm"] == comm].sort_values("total_cpu")

        baseline_cpu = subset["total_cpu"].min()
        baseline_time = subset[subset["total_cpu"] == baseline_cpu]["wallclock"].values[0]

        mask = df["comm"] == comm
        df.loc[mask, "baseline_cpu"] = baseline_cpu
        df.loc[mask, "baseline_time"] = baseline_time
        df.loc[mask, "speedup"] = baseline_time / df.loc[mask, "wallclock"]
        df.loc[mask, "efficiency"] = df.loc[mask, "speedup"] / (
            df.loc[mask, "total_cpu"] / baseline_cpu
        )

    return df


COLORS = {
    "tcp": "#7a1f1f",
    "inf": "#1f3b73",
}

MARKERS = {
    "tcp": "s",
    "inf": "o",
}

LABELS = {
    "tcp": "TCP",
    "inf": "InfiniBand",
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


def add_table(axis, display_df, column_labels):
    axis.axis("off")

    table = axis.table(
        cellText=display_df.values,
        colLabels=column_labels,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.0)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9dde3")
            cell.set_text_props(weight="bold", color="#111111")
        else:
            cell.set_facecolor("#f7f7f7")
            cell.set_text_props(color="#111111")

        cell.set_edgecolor("#b0b0b0")


def plot_single_communication(df, comm_name, output_filename):
    subset = df[df["comm"] == comm_name].sort_values("total_cpu")

    if subset.empty:
        print(f"No data found for {LABELS[comm_name]}")
        return

    fig = plt.figure(figsize=(24, 10), facecolor="#e9ecef")
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=[3.0, 1.8],
        hspace=0.42,
        wspace=0.28,
    )

    wallclock_axis = fig.add_subplot(grid[0, 0])
    speedup_axis = fig.add_subplot(grid[0, 1])
    efficiency_axis = fig.add_subplot(grid[0, 2])
    table_axis = fig.add_subplot(grid[1, :])

    style_axis(wallclock_axis)
    wallclock_axis.plot(
        subset["total_cpu"],
        subset["wallclock"],
        marker=MARKERS[comm_name],
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[comm_name],
        label=LABELS[comm_name],
    )
    wallclock_axis.set_title(
        f"{LABELS[comm_name]} - Wall Clock vs Total CPU",
        fontsize=11,
    )
    wallclock_axis.set_xlabel("Total CPU", fontsize=10)
    wallclock_axis.set_ylabel("Wall Clock (s)", fontsize=10)
    wallclock_axis.legend(frameon=True, fontsize=8)

    style_axis(speedup_axis)
    speedup_axis.plot(
        subset["total_cpu"],
        subset["speedup"],
        marker=MARKERS[comm_name],
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[comm_name],
        label=LABELS[comm_name],
    )

    baseline_cpu = subset["total_cpu"].min()
    ideal_speedup = subset["total_cpu"] / baseline_cpu

    speedup_axis.plot(
        subset["total_cpu"],
        ideal_speedup,
        linestyle="--",
        linewidth=1.5,
        color=COLORS[comm_name],
        alpha=0.35,
        label="Ideal",
    )

    speedup_axis.set_title(
        f"{LABELS[comm_name]} - Speedup vs Total CPU",
        fontsize=11,
    )
    speedup_axis.set_xlabel("Total CPU", fontsize=10)
    speedup_axis.set_ylabel("Speedup", fontsize=10)
    speedup_axis.legend(frameon=True, fontsize=8)

    style_axis(efficiency_axis)
    efficiency_axis.plot(
        subset["total_cpu"],
        subset["efficiency"],
        marker=MARKERS[comm_name],
        linewidth=2.3,
        markersize=6.5,
        color=COLORS[comm_name],
        label=LABELS[comm_name],
    )
    efficiency_axis.set_title(
        f"{LABELS[comm_name]} - Efficiency vs Total CPU",
        fontsize=11,
    )
    efficiency_axis.set_xlabel("Total CPU", fontsize=10)
    efficiency_axis.set_ylabel("Efficiency", fontsize=10)
    efficiency_axis.legend(frameon=True, fontsize=8)

    display_df = subset[
        ["total_cpu", "wallclock", "speedup", "efficiency", "file"]
    ].copy()

    display_df["wallclock"] = display_df["wallclock"].map(lambda value: f"{value:.2f}")
    display_df["speedup"] = display_df["speedup"].map(lambda value: f"{value:.2f}")
    display_df["efficiency"] = display_df["efficiency"].map(lambda value: f"{value:.2f}")

    add_table(
        table_axis,
        display_df,
        ["Total CPU", "Wall Clock", "Speedup", "Efficiency", "File"],
    )

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_comparison(df):
    df_tcp = df[df["comm"] == "tcp"].sort_values("total_cpu")
    df_inf = df[df["comm"] == "inf"].sort_values("total_cpu")

    fig = plt.figure(figsize=(24, 10), facecolor="#e9ecef")
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=[3.0, 1.8],
        hspace=0.42,
        wspace=0.28,
    )

    wallclock_axis = fig.add_subplot(grid[0, 0])
    speedup_axis = fig.add_subplot(grid[0, 1])
    efficiency_axis = fig.add_subplot(grid[0, 2])
    table_axis = fig.add_subplot(grid[1, :])

    for axis in [wallclock_axis, speedup_axis, efficiency_axis]:
        style_axis(axis)

    for comm_name, subset in [("tcp", df_tcp), ("inf", df_inf)]:
        if subset.empty:
            continue

        wallclock_axis.plot(
            subset["total_cpu"],
            subset["wallclock"],
            marker=MARKERS[comm_name],
            linewidth=2.3,
            markersize=6.5,
            color=COLORS[comm_name],
            label=LABELS[comm_name],
        )

        speedup_axis.plot(
            subset["total_cpu"],
            subset["speedup"],
            marker=MARKERS[comm_name],
            linewidth=2.3,
            markersize=6.5,
            color=COLORS[comm_name],
            label=LABELS[comm_name],
        )

        baseline_cpu = subset["total_cpu"].min()
        ideal_speedup = subset["total_cpu"] / baseline_cpu

        speedup_axis.plot(
            subset["total_cpu"],
            ideal_speedup,
            linestyle="--",
            linewidth=1.3,
            color=COLORS[comm_name],
            alpha=0.30,
        )

        efficiency_axis.plot(
            subset["total_cpu"],
            subset["efficiency"],
            marker=MARKERS[comm_name],
            linewidth=2.3,
            markersize=6.5,
            color=COLORS[comm_name],
            label=LABELS[comm_name],
        )

    wallclock_axis.set_title("STMV - Wall Clock Comparison", fontsize=11)
    wallclock_axis.set_xlabel("Total CPU", fontsize=10)
    wallclock_axis.set_ylabel("Wall Clock (s)", fontsize=10)
    wallclock_axis.legend(frameon=True, fontsize=8)

    speedup_axis.set_title("STMV - Speedup Comparison", fontsize=11)
    speedup_axis.set_xlabel("Total CPU", fontsize=10)
    speedup_axis.set_ylabel("Speedup", fontsize=10)
    speedup_axis.legend(frameon=True, fontsize=8)

    efficiency_axis.set_title("STMV - Efficiency Comparison", fontsize=11)
    efficiency_axis.set_xlabel("Total CPU", fontsize=10)
    efficiency_axis.set_ylabel("Efficiency", fontsize=10)
    efficiency_axis.legend(frameon=True, fontsize=8)

    display_df = df[
        ["comm", "total_cpu", "wallclock", "speedup", "efficiency"]
    ].copy()

    display_df["comm"] = display_df["comm"].map(LABELS)
    display_df["wallclock"] = display_df["wallclock"].map(lambda value: f"{value:.2f}")
    display_df["speedup"] = display_df["speedup"].map(lambda value: f"{value:.2f}")
    display_df["efficiency"] = display_df["efficiency"].map(lambda value: f"{value:.2f}")

    add_table(
        table_axis,
        display_df,
        ["Communication", "Total CPU", "Wall Clock", "Speedup", "Efficiency"],
    )

    output_path = os.path.join(OUTPUT_DIR, "stmv_tcp_vs_infiniband.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = read_wallclock_logs()
    df = calculate_speedup_and_efficiency(df)

    print("\n=== RESULTS ===")
    print(df[["comm", "total_cpu", "wallclock", "speedup", "efficiency", "file"]])

    plot_single_communication(df, "tcp", "stmv_tcp_scaling.png")
    plot_single_communication(df, "inf", "stmv_infiniband_scaling.png")
    plot_comparison(df)


if __name__ == "__main__":
    main()
