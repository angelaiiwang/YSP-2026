import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Configuration ----------------------------------------------------
EXCEL_FILE = "SerialDataPlotting/arduino_data.xlsx"
SHEET_NAME = "Attenuator Data Reading 2"
X_COLUMN = "Time"
Y_COLUMNS = ["Value"]        # add more column names here to plot multiple lines

GAP_THRESHOLD_MS = 1000
# -------------------------------------------------------------------------


def main():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

    df[X_COLUMN] = pd.to_datetime(df[X_COLUMN], format="%Y-%m-%d %H:%M:%S.%f")
    df = df.sort_values(X_COLUMN).reset_index(drop=True)
    t0 = df[X_COLUMN].iloc[0]
    df[X_COLUMN] = (df[X_COLUMN] - t0).dt.total_seconds() * 1000  # -> ms, float

    fig, ax = plt.subplots(figsize=(10, 5))

    x = df[X_COLUMN].to_numpy()
    y_clean = df[Y_COLUMNS[0]].to_numpy().astype(float)  # raw, no gaps -> safe for FFT

    for col in Y_COLUMNS:
        y = df[col].to_numpy().astype(float)

        # Only used for the *plot* — insert NaNs so gaps aren't visually joined.
        gaps = np.diff(x) > GAP_THRESHOLD_MS
        y_masked = y.copy()
        y_masked[1:][gaps] = np.nan

        ax.plot(x, y_masked, marker="o", markersize=3, linewidth=1, label=col)

    ax.set_xlabel("Time (ms, elapsed since first reading)")
    ax.set_ylabel("Value")
    ax.set_title("Arduino Sensor Data")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("plot.png", dpi=150)
    plt.show()

    return x, y_clean  # (time_ms, values) — both needed for the FFT


if __name__ == "__main__":
    main()