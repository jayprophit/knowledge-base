"""
Natural Sciences Integration: Physics, Chemistry, Biology, Environmental Science
"""
import matplotlib.pyplot as plt
import numpy as np

class NaturalSciencesModule:
    def plot_sine_wave(self):
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.plot(x, y)
        plt.title("Sine Wave")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.grid()
        plt.show()
