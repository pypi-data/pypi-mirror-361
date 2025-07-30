# iLaplace/plots.py

import matplotlib.pyplot as plt

def plot_results(t_values, v_values, title="Inverse Laplace Result", xlabel="Time (s)", ylabel="Value"):

    plt.figure(figsize=(8, 4))
    plt.plot(t_values, v_values, 'b-', label='f(t)')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
