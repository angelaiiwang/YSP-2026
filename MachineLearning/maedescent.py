import csv
import numpy as np

CSV_PATH = ".\\MachineLearning\\data.csv"
X_COLUMN = None
Y_COLUMN = None
LEARNING_RATE = 0.01
EPSILON = 1e-6
MAX_ITERATIONS = 2_000

THETA_PATH = ".\\MachineLearning\\theta_mae.npy"
COST_HISTORY_PATH = ".\\MachineLearning\\cost_history.npy"   # <-- new

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

# --- Gradient descent ---
theta = np.array([0.0, 0.0])
cost_history = []   # <-- tracks MAE at every iteration

iteration = 0
while iteration < MAX_ITERATIONS:
    predictions = theta[0] + theta[1] * x
    errors = predictions - y

    mae = np.mean(np.abs(errors))   # <-- changed: MAE instead of MSE
    cost_history.append(mae)

    # Gradient of MAE uses sign(errors) instead of errors directly
    signs = np.sign(errors)
    grad_intercept = (1 / n) * np.sum(signs)
    grad_slope = (1 / n) * np.sum(signs * x)
    gradient = np.array([grad_intercept, grad_slope])

    theta = theta - LEARNING_RATE * gradient

    if iteration % 100 == 0:
        print(f"Iteration {iteration}: MAE = {mae:.6f}, theta = {theta}, |grad| = {np.linalg.norm(gradient):.8f}")

    if np.linalg.norm(gradient) < EPSILON:
        print(f"\nConverged after {iteration} iterations (|grad| < {EPSILON}).")
        break

    iteration += 1
else:
    print(f"\nStopped after reaching MAX_ITERATIONS = {MAX_ITERATIONS} without full convergence.")

np.save(THETA_PATH, theta)
np.save(COST_HISTORY_PATH, np.array(cost_history))
print(f"Saved theta to {THETA_PATH}: intercept={theta[0]:.6f}, slope={theta[1]:.6f}")
print(f"Saved cost history to {COST_HISTORY_PATH} ({len(cost_history)} iterations)")

print("\nFinal parameters:")
print(f"Intercept: {theta[0]:.6f}")
print(f"Slope:     {theta[1]:.6f}")