import csv
import numpy as np

CSV_PATH = ".\\MachineLearning\\data.csv"
X_COLUMN = None
Y_COLUMN = None
LEARNING_RATE = 0.01
EPSILON = 1e-6              # stop when epoch-average cost stops improving by more than this
MAX_EPOCHS = 1000         # safety cap: one epoch = one full pass through the data

THETA_PATH = ".\\MachineLearning\\theta_stochastic.npy"
COST_HISTORY_PATH = ".\\MachineLearning\\cost_history.npy"

# --- Load data ---
x_vals = []
y_vals = []

with open(CSV_PATH, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)

    x_idx = 0 if X_COLUMN is None else (
        int(X_COLUMN) if X_COLUMN.isdigit() else header.index(X_COLUMN)
    )
    y_idx = 1 if Y_COLUMN is None else (
        int(Y_COLUMN) if Y_COLUMN.isdigit() else header.index(Y_COLUMN)
    )

    for row in reader:
        if not row:
            continue
        x_vals.append(float(row[x_idx]))
        y_vals.append(float(row[y_idx]))

x = np.array(x_vals)
y = np.array(y_vals)
n = len(x)
print("Total data points:", n)

# --- Stochastic gradient descent ---
theta = np.array([0.0, 0.0])
cost_history = []          # average cost per epoch (for plotting)
rng = np.random.default_rng()

prev_epoch_cost = np.inf
epoch = 0

while epoch < MAX_EPOCHS:
    # Shuffle the order of data points each epoch so updates aren't biased by row order
    indices = rng.permutation(n)

    epoch_cost_sum = 0.0

    for idx in indices:
        xi = x[idx]
        yi = y[idx]

        prediction = theta[0] + theta[1] * xi
        error = prediction - yi

        # Gradient computed from a SINGLE data point (this is what makes it "stochastic")
        grad_intercept = 2 * error
        grad_slope = 2 * error * xi
        gradient = np.array([grad_intercept, grad_slope])

        theta = theta - LEARNING_RATE * gradient

        epoch_cost_sum += error ** 2

    epoch_avg_cost = epoch_cost_sum / n
    cost_history.append(epoch_avg_cost)

    if epoch % 10 == 0:
        print(f"Epoch {epoch}: avg MSE = {epoch_avg_cost:.6f}, theta = {theta}")

    # Convergence check: has the epoch-average cost stopped improving meaningfully?
    if abs(prev_epoch_cost - epoch_avg_cost) < EPSILON:
        print(f"\nConverged after {epoch} epochs (cost change < {EPSILON}).")
        break

    prev_epoch_cost = epoch_avg_cost
    epoch += 1
else:
    print(f"\nStopped after reaching MAX_EPOCHS = {MAX_EPOCHS} without full convergence.")

np.save(THETA_PATH, theta)
np.save(COST_HISTORY_PATH, np.array(cost_history))
print(f"Saved theta to {THETA_PATH}: intercept={theta[0]:.6f}, slope={theta[1]:.6f}")
print(f"Saved cost history to {COST_HISTORY_PATH} ({len(cost_history)} epochs)")

print("\nFinal parameters:")
print(f"Intercept: {theta[0]:.6f}")
print(f"Slope:     {theta[1]:.6f}")