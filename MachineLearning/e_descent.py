# import csv
# import numpy as np

# CSV_PATH = ".\\MachineLearning\\data.csv"
# X_COLUMN = None
# Y_COLUMN = None
# LEARNING_RATE = 0.01
# EPSILON = 1e-6
# MAX_ITERATIONS = 2_000_000

# CONST_C = 1e-6   # <-- the "c" in c - log(exp(-(y-yhat)^2) + c)

# THETA_PATH = ".\\MachineLearning\\theta_e.npy"
# COST_HISTORY_PATH = ".\\MachineLearning\\cost_history.npy"

# # --- Load data ---
# x_vals = []
# y_vals = []

# with open(CSV_PATH, 'r') as file:
#     reader = csv.reader(file)
#     header = next(reader)

#     x_idx = 0 if X_COLUMN is None else (
#         int(X_COLUMN) if X_COLUMN.isdigit() else header.index(X_COLUMN)
#     )
#     y_idx = 1 if Y_COLUMN is None else (
#         int(Y_COLUMN) if Y_COLUMN.isdigit() else header.index(Y_COLUMN)
#     )

#     for row in reader:
#         if not row:
#             continue
#         x_vals.append(float(row[x_idx]))
#         y_vals.append(float(row[y_idx]))

# x = np.array(x_vals)
# y = np.array(y_vals)
# n = len(x)
# print("Total data points:", n)

# # --- Gradient descent ---
# theta = np.array([0.0, 0.0])
# cost_history = []

# iteration = 0
# while iteration < MAX_ITERATIONS:
#     predictions = theta[0] + theta[1] * x
#     errors = y - predictions          # e = y - yhat
#     exp_term = np.exp(-(errors ** 2)) # exp(-(y-yhat)^2)

#     # Cost: c - log(exp(-(y-yhat)^2) + c), averaged over samples
#     per_sample_cost = CONST_C - np.log(exp_term + CONST_C)
#     cost = np.mean(per_sample_cost)
#     cost_history.append(cost)

#     # Gradient: dL/dtheta = -2*e*exp(-e^2) / (exp(-e^2) + c)
#     common_factor = -2 * errors * exp_term / (exp_term + CONST_C)
#     grad_intercept = np.mean(common_factor)
#     grad_slope = np.mean(common_factor * x)
#     gradient = np.array([grad_intercept, grad_slope])

#     theta = theta - LEARNING_RATE * gradient

#     if iteration % 100 == 0:
#         print(f"Iteration {iteration}: Cost = {cost:.6f}, theta = {theta}, |grad| = {np.linalg.norm(gradient):.8f}")

#     if np.linalg.norm(gradient) < EPSILON:
#         print(f"\nConverged after {iteration} iterations (|grad| < {EPSILON}).")
#         break

#     iteration += 1
# else:
#     print(f"\nStopped after reaching MAX_ITERATIONS = {MAX_ITERATIONS} without full convergence.")

# np.save(THETA_PATH, theta)
# np.save(COST_HISTORY_PATH, np.array(cost_history))
# print(f"Saved theta to {THETA_PATH}: intercept={theta[0]:.6f}, slope={theta[1]:.6f}")
# print(f"Saved cost history to {COST_HISTORY_PATH} ({len(cost_history)} iterations)")

# print("\nFinal parameters:")
# print(f"Intercept: {theta[0]:.6f}")
# print(f"Slope:     {theta[1]:.6f}")

import csv
import numpy as np

CSV_PATH = ".\\MachineLearning\\data.csv"
X_COLUMN = None
Y_COLUMN = None
LEARNING_RATE = 0.01
EPSILON = 1e-6
MAX_ITERATIONS = 1000

CONST_C = 0.1   # <-- raised from 1e-6; keeps exp(-e^2)+c from being ~pure numerical zero

THETA_PATH = ".\\MachineLearning\\theta_e.npy"
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

x_raw = np.array(x_vals)
y_raw = np.array(y_vals)
n = len(x_raw)
print("Total data points:", n)

# --- Standardize x and y (critical fix: keeps initial errors O(1) so exp(-e^2) doesn't underflow) ---
x_mean, x_std = x_raw.mean(), x_raw.std()
y_mean, y_std = y_raw.mean(), y_raw.std()

x = (x_raw - x_mean) / x_std
y = (y_raw - y_mean) / y_std

# --- Diagnostic: check initial error scale before training starts ---
initial_errors = y - 0.0   # theta starts at [0,0], so predictions start at 0
print(f"\n[Diagnostic] Initial (standardized) error range: min={initial_errors.min():.4f}, "
      f"max={initial_errors.max():.4f}, mean|e|={np.mean(np.abs(initial_errors)):.4f}")
print(f"[Diagnostic] exp(-e^2) at init: min={np.exp(-initial_errors**2).min():.6e}, "
      f"max={np.exp(-initial_errors**2).max():.6e}\n")

# --- Gradient descent (on standardized data) ---
theta = np.array([0.0, 0.0])
cost_history = []

iteration = 0
while iteration < MAX_ITERATIONS:
    predictions = theta[0] + theta[1] * x
    errors = y - predictions          # e = y - yhat
    exp_term = np.exp(-(errors ** 2)) # exp(-(y-yhat)^2)

    # Cost: c - log(exp(-(y-yhat)^2) + c), averaged over samples
    per_sample_cost = CONST_C - np.log(exp_term + CONST_C)
    cost = np.mean(per_sample_cost)
    cost_history.append(cost)

    # Gradient: dL/dtheta = -2*e*exp(-e^2) / (exp(-e^2) + c)
    common_factor = -2 * errors * exp_term / (exp_term + CONST_C)
    grad_intercept = np.mean(common_factor)
    grad_slope = np.mean(common_factor * x)
    gradient = np.array([grad_intercept, grad_slope])

    theta = theta - LEARNING_RATE * gradient

    if iteration % 100 == 0:
        print(f"Iteration {iteration}: Cost = {cost:.6f}, theta(std) = {theta}, |grad| = {np.linalg.norm(gradient):.8f}")

    if np.linalg.norm(gradient) < EPSILON:
        print(f"\nConverged after {iteration} iterations (|grad| < {EPSILON}).")
        break

    iteration += 1
else:
    print(f"\nStopped after reaching MAX_ITERATIONS = {MAX_ITERATIONS} without full convergence.")

# --- Convert theta back from standardized space to original (raw x, y) scale ---
# In standardized space: y_std = theta0_std + theta1_std * x_std
# where x_std = (x_raw - x_mean)/x_std_dev, y_std = (y_raw - y_mean)/y_std_dev
# Solving back out:
theta1_raw = theta[1] * (y_std / x_std)
theta0_raw = y_mean + theta[0] * y_std - theta1_raw * x_mean
theta_raw = np.array([theta0_raw, theta1_raw])

np.save(THETA_PATH, theta_raw)
np.save(COST_HISTORY_PATH, np.array(cost_history))
print(f"\nSaved theta (original scale) to {THETA_PATH}: intercept={theta_raw[0]:.6f}, slope={theta_raw[1]:.6f}")
print(f"Saved cost history to {COST_HISTORY_PATH} ({len(cost_history)} iterations)")

print("\nFinal parameters (original scale):")
print(f"Intercept: {theta_raw[0]:.6f}")
print(f"Slope:     {theta_raw[1]:.6f}")