import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def run_lwlr(file_path, tau=0.5):
    data = pd.read_csv(file_path)

    X_train = np.array(data['total_bill'])[:, np.newaxis]
    y_train = np.array(data['tip'])

    print("Training input length:", len(X_train))

    X_test = np.array([i / 10 for i in range(500)])[:, np.newaxis]
    y_test = []

    for r in range(len(X_test)):
        # Compute weights
        wts = np.exp(-np.sum((X_train - X_test[r]) ** 2, axis=1) / (2 * tau ** 2))
        W = np.diag(wts)

        # Compute parameters theta
        try:
            theta = np.linalg.inv(X_train.T @ W @ X_train) @ X_train.T @ W @ y_train
            prediction = X_test[r] @ theta
            y_test.append(prediction)
        except np.linalg.LinAlgError:
            y_test.append(0)  # Fallback if matrix is non-invertible

    print("Prediction count:", len(y_test))

    # Plotting results
    plt.figure(figsize=(10, 6))
    plt.plot(X_train.squeeze(), y_train, 'o', label="Training Data")
    plt.plot(X_test.squeeze(), y_test, '-', label="LWLR Prediction")
    plt.xlabel("Total Bill")
    plt.ylabel("Tip")
    plt.title("Locally Weighted Linear Regression")
    plt.legend()
    plt.grid(True)
    plt.show()

def lwlr(*args, **kwargs):
    return run_lwlr(*args, **kwargs)
