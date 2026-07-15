# """
# Plot points from a CSV file using matplotlib.

# Just set CSV_PATH below to your file's location and run:
#     python plot_csv_points.py

# By default, the script assumes the CSV has a header row and uses the
# first two columns as x and y. Change X_COLUMN / Y_COLUMN below to use
# different columns (either column names or 0-based indices as strings,
# e.g. "0" or "2").
# """

# import csv
# import sys
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd

# # ==== EDIT THESE ====
# CSV_PATH = ".\\MachineLearning\\data.csv"      # <-- put your CSV file path here
# THETA_PATH = ".\\MachineLearning\\theta.npy"  # <-- put your theta.npy file path here
# X_COLUMN = None            # e.g. "time" or "0" (None = first column)
# Y_COLUMN = None            # e.g. "value" or "1" (None = second column)
# OUTPUT_PATH = ".\\MachineLearning\\plot.png"         # e.g. "plot.png" (None = show plot in a window)
# # =====================

# def load_points(csv_path, x_col, y_col):
#     xs, ys = [], []

#     with open(csv_path, newline="") as f:
#         reader = csv.reader(f)
#         rows = list(reader)

#     if not rows:
#         raise ValueError("CSV file is empty")

#     header = rows[0]
#     data_rows = rows[1:]

#     # Resolve column references (name or index) against the header
#     def resolve(col, default_idx):
#         if col is None:
#             return default_idx
#         if col.isdigit():
#             return int(col)
#         try:
#             return header.index(col)
#         except ValueError:
#             raise ValueError(f"Column '{col}' not found in header: {header}")

#     x_idx = resolve(x_col, 0)
#     y_idx = resolve(y_col, 1)

#     for row in data_rows:
#         if not row or len(row) <= max(x_idx, y_idx):
#             continue
#         try:
#             xs.append(float(row[x_idx]))
#             ys.append(float(row[y_idx]))
#         except ValueError:
#             # Skip rows with non-numeric data
#             continue

#     return xs, ys, header[x_idx], header[y_idx]


# def main():
#     try:
#         xs, ys, x_label, y_label = load_points(CSV_PATH, X_COLUMN, Y_COLUMN)
#     except (ValueError, FileNotFoundError) as e:
#         print(f"Error: {e}", file=sys.stderr)
#         sys.exit(1)

#     if not xs:
#         print("No valid numeric point data found.", file=sys.stderr)
#         sys.exit(1)

#     plt.figure(figsize=(8, 6))
#     plt.scatter(xs, ys)
#     plt.xlabel(x_label)
#     plt.ylabel(y_label)
#     plt.title(f"{y_label} vs {x_label}")
#     plt.grid(True, alpha=0.3)

#     if OUTPUT_PATH:
#         plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
#         print(f"Plot saved to {OUTPUT_PATH}")
#     else:
#         plt.show()

# # ... inside main(), before drawing the line ...
#     try:
#         theta = np.load(THETA_PATH)
#         intercept, slope = theta[0], theta[1]
#     except FileNotFoundError:
#         print(f"Error: {THETA_PATH} not found. Run the training script first.", file=sys.stderr)
#         sys.exit(1)
#     df = pd.read_csv('data.csv')

#     # Get min and max from the 'x' column
#     x_min = df['x'].min()
#     x_max = df['x'].max()
#     line_x = np.linspace(x_min, x_max, 100)
#     line_y = intercept + slope * line_x
#     plt.plot(line_x, line_y, color="red", linewidth=2, label="Predicted line")

# if __name__ == "__main__":
#     main()

# cost function value vs. iterations 

"""
Plot points from a CSV file using matplotlib, along with a predicted
regression line loaded from theta.npy.

Just set CSV_PATH below to your file's location and run:
    python plot_csv_points.py
"""

import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

# ==== EDIT THESE ====
CSV_PATH = ".\\MachineLearning\\data.csv"
THETA_PATH = ".\\MachineLearning\\theta.npy"




X_COLUMN = None
Y_COLUMN = None
OUTPUT_PATH = ".\\MachineLearning\\plot.png"
# =====================


def load_points(csv_path, x_col, y_col):
    xs, ys = [], []

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV file is empty")

    header = rows[0]
    data_rows = rows[1:]

    def resolve(col, default_idx):
        if col is None:
            return default_idx
        if col.isdigit():
            return int(col)
        try:
            return header.index(col)
        except ValueError:
            raise ValueError(f"Column '{col}' not found in header: {header}")

    x_idx = resolve(x_col, 0)
    y_idx = resolve(y_col, 1)

    for row in data_rows:
        if not row or len(row) <= max(x_idx, y_idx):
            continue
        try:
            xs.append(float(row[x_idx]))
            ys.append(float(row[y_idx]))
        except ValueError:
            continue

    return xs, ys, header[x_idx], header[y_idx]


def main():
    try:
        xs, ys, x_label, y_label = load_points(CSV_PATH, X_COLUMN, Y_COLUMN)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not xs:
        print("No valid numeric point data found.", file=sys.stderr)
        sys.exit(1)

    # --- Load trained parameters BEFORE building the figure ---
    try:
        theta = np.load(".\\MachineLearning\\theta.npy")
        intercept, slope = theta[0], theta[1]
        
        theta_epsilon = np.load(".\\MachineLearning\\theta_epsilon.npy")
        intercept_epsilon, slope_epsilon = theta_epsilon[0], theta_epsilon[1]

        theta_stochastic = np.load(".\\MachineLearning\\theta_stochastic.npy")
        intercept_stochastic, slope_stochastic = theta_stochastic[0], theta_stochastic[1]

        theta_mae = np.load(".\\MachineLearning\\theta_mae.npy")
        intercept_mae, slope_mae = theta_mae[0], theta_mae[1]

        theta_e = np.load(".\\MachineLearning\\theta_e.npy")
        intercept_e, slope_e = theta_e[0], theta_e[1]
                
    except FileNotFoundError:
        print(f"Error: {THETA_PATH} not found. Run the training script first.", file=sys.stderr)
        sys.exit(1)

    # --- Build the figure ---
    plt.figure(figsize=(8, 6))
    plt.scatter(xs, ys, label="Data points")
    
    # --- Draw the predicted line ---
    x_min, x_max = min(xs), max(xs)
    line_x = np.linspace(x_min, x_max, 100)
    line_y = intercept + slope * line_x
    plt.plot(line_x, line_y, color="red", linewidth=2, label="Predicted line")

    x_min, x_max = min(xs), max(xs)
    epsilon_line_x = np.linspace(x_min, x_max, 100)
    epsilon_line_y = intercept_epsilon + slope_epsilon * epsilon_line_x
    plt.plot(epsilon_line_x, epsilon_line_y, color="green", linewidth=2, label="Epsilon Predicted line")

    stochastic_line_x = np.linspace(x_min, x_max, 100)
    stochastic_line_y = intercept_stochastic + slope_stochastic * stochastic_line_x
    plt.plot(stochastic_line_x, stochastic_line_y, color="blue", linewidth=2, label="Stochastic Predicted line")

    mae_line_x = np.linspace(x_min, x_max, 100)
    mae_line_y = intercept_mae + slope_mae * mae_line_x
    plt.plot(mae_line_x, mae_line_y, color="orange", linewidth=2, label="MAE Predicted line")

    e_line_x = np.linspace(x_min, x_max, 100)
    e_line_y = intercept_e + slope_e * e_line_x
    plt.plot(e_line_x, e_line_y, color="purple", linewidth=2, label="E Predicted line")

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f"{y_label} vs {x_label}")
    plt.grid(True, alpha=0.3)
    plt.legend()

    if OUTPUT_PATH:
        plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
        print(f"Plot saved to {OUTPUT_PATH}")
    else:
        plt.show()


if __name__ == "__main__":
    main()