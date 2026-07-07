import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Configuration ----------------------------------------------------
EXCEL_FILE = "arduino_data.xlsx"
SHEET_NAME = "Attenuator Data Reading 2"
X_COLUMN = "Time"
Y_COLUMNS = ["Value"]        # add more column names here to plot multiple lines

# If the gap between two consecutive readings exceeds this many milliseconds,
# treat them as separate bursts and don't draw a connecting line between them.
GAP_THRESHOLD_MS = 1000
# -------------------------------------------------------------------------


def main():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

    # The Time column holds text timestamps like "2026-07-07 14:10:29.123".
    # Parse them, then convert to milliseconds elapsed since the first
    # reading so the x-axis is a plain millisecond number starting at 0.
    df[X_COLUMN] = pd.to_datetime(df[X_COLUMN], format="%Y-%m-%d %H:%M:%S.%f")
    df = df.sort_values(X_COLUMN).reset_index(drop=True)
    t0 = df[X_COLUMN].iloc[0]
    df[X_COLUMN] = (df[X_COLUMN] - t0).dt.total_seconds() * 1000  # -> ms, float

    fig, ax = plt.subplots(figsize=(10, 5))

    for col in Y_COLUMNS:
        x = df[X_COLUMN].to_numpy()
        y = df[col].to_numpy().astype(float)

        # Break the line wherever there's a large time gap, so separate
        # bursts of readings aren't visually joined by a connecting line.
        gaps = np.diff(x) > GAP_THRESHOLD_MS
        y_masked = y.copy()
        y_masked[1:][gaps] = np.nan  # insert a break right after each gap

        ax.plot(x, y_masked, marker="o", markersize=3, linewidth=1, label=col)

    ax.set_xlabel("Time (ms, elapsed since first reading)")
    ax.set_ylabel("Value")
    ax.set_title("Arduino Sensor Data")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("plot.png", dpi=150)   # saves a copy to disk
    plt.show()                          # opens an interactive window


if __name__ == "__main__":
    main()