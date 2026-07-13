import csv
import sys

import matplotlib.pyplot as plt

# ==== EDIT THESE ====
CSV_PATH = "/MachineLearning/data.csv"      # <-- put your CSV file path here
X_COLUMN = "X"            # e.g. "time" or "0" (None = first column)
Y_COLUMN = "Y"            # e.g. "value" or "1" (None = second column)
OUTPUT_PATH = "/MachineLearning/plot.png"         # e.g. "plot.png" (None = show plot in a window)
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

    # Resolve column references (name or index) against the header
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
            # Skip rows with non-numeric data
            continue

    return xs, ys, header[x_idx], header[y_idx]


def main():
    parser = argparse.ArgumentParser(description="Plot points from a CSV file.")
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument("--x", default=None, help="X column name or index (default: first column)")
    parser.add_argument("--y", default=None, help="Y column name or index (default: second column)")
    parser.add_argument("--output", default=None, help="Save plot to this file instead of showing it")
    args = parser.parse_args()

    try:
        xs, ys, x_label, y_label = load_points(args.csv_path, args.x, args.y)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not xs:
        print("No valid numeric point data found.", file=sys.stderr)
        sys.exit(1)

    plt.figure(figsize=(8, 6))
    plt.scatter(xs, ys)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f"{y_label} vs {x_label}")
    plt.grid(True, alpha=0.3)

    if args.output:
        plt.savefig(args.output, dpi=150, bbox_inches="tight")
        print(f"Plot saved to {args.output}")
    else:
        plt.show()


if __name__ == "__main__":
    main()