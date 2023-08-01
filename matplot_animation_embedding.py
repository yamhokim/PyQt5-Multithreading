import numpy as np
import sys
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, time_data, ear_data):
        super().__init__()
        self.time_data = time_data
        self.ear_data = ear_data
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        # Configure figure
        self.fig = plt.figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)

        layout.addWidget(self.canvas)
        self.addToolBar(NavigationToolbar(self.canvas, self))

        self.setup()
        self.animate()

    def setup(self):
        self.ax = self.fig.subplots()
        #self.ax.set_aspect('equal')
        #self.ax.grid(True, linestyle='-', color='0.10')
    
    def update(self, i):
        time_data = self.time_data[:60]
        ear_data = self.ear_data[:60]
        self.ax.plot(time_data, ear_data)
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.3)
        plt.title("Test Animation Plot")
        plt.xlabel("X Value")
        plt.ylabel("Y Value")

        self.scat = self.ax.scatter([], [], color=(0.9, 0.1, 0.5), zorder=3)
        self.scat.set_alpha(0.8)

        #self.anim = animation.FuncAnimation(self.fig, self.update, frames=720, interval=10)

    def animate(self):
        self.anim = animation.FuncAnimation(self.fig, self.update, interval=1000)
    

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)

    x_values = []
    y_values = []
    counter = 0
    while counter <= 1000:
        x_values.append(counter)
        y_values.append(counter)
        counter += 1

    app = ApplicationWindow(x_values, y_values)
    app.show()
    qapp.exec_()
