import sys
from PyQt5 import QtGui, QtWidgets, QtCore
import numpy as np
import time
import pyaudio
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation


class Window(QtWidgets.QMainWindow):

  def __init__(self):  # sort of template for rest of GUI, is always there, menubar/ mainmenu eg.
      super(Window, self).__init__()
      self.setGeometry(50, 50, 1500, 900)
      self.setWindowTitle("PyQt Tutorial!")

      self.centralwidget = QtWidgets.QWidget(self)
      self.centralwidget.setObjectName("centralwidget")

      self.channels = 2
      self.fs = 44100  # samplerate
      self.Chunks = 1024

      self.tapeLength = 2  # seconds
      self.tape = np.empty(self.fs * self.tapeLength) * np.nan  # tapes where recorded audio is stored

      self.home()

  def home(self):
      btn = QtWidgets.QPushButton("Stream and Plot", self)  # Button to start streaming
      btn.clicked.connect(self.plot)
      btn.resize(btn.sizeHint())
      btn.move(100, 100)

      self.scrollArea = QtWidgets.QScrollArea(self)
      self.scrollArea.move(75, 400)
      self.scrollArea.resize(600, 300)
      self.scrollArea.setWidgetResizable(False)

      self.scrollArea2 = QtWidgets.QScrollArea(self)
      self.scrollArea2.move(775, 400)
      self.scrollArea2.resize(600, 300)
      self.scrollArea2.setWidgetResizable(False)
      self.scrollArea.horizontalScrollBar().valueChanged.connect(self.scrollArea2.horizontalScrollBar().setValue)
      self.scrollArea2.horizontalScrollBar().valueChanged.connect(self.scrollArea.horizontalScrollBar().setValue)

      self.figure = Figure((15, 2.8), dpi=100)  # figure instance (to plot on) F(width, height, ...)
      self.canvas = FigureCanvas(self.figure)
      self.scrollArea.setWidget(self.canvas)
      self.toolbar = NavigationToolbar(self.canvas, self.scrollArea)

      self.canvas2 = FigureCanvas(self.figure)
      self.scrollArea2.setWidget(self.canvas2)
      self.toolbar2 = NavigationToolbar(self.canvas2, self.scrollArea2)

      self.gs = gridspec.GridSpec(1, 1)
      self.ax = self.figure.add_subplot(self.gs[0])
      self.ax2 = self.figure.add_subplot(self.gs[0])
      self.figure.subplots_adjust(left=0.05)

      self.ax.clear()

  def start_streamsignal(self, start=True):
  # open and start the stream
      if start is True:
          print("start Signals")

          self.p = pyaudio.PyAudio()
          self.stream = self.p.open(format=pyaudio.paFloat32, channels=self.channels, rate=self.fs, input_device_index=1,
                         output_device_index=5, input=True, frames_per_buffer=self.Chunks)
          print("recording...")

  def start_streamread(self):
      data = self.stream.read(self.Chunks)
      npframes2 = np.array(data).flatten()
      npframes2 = np.fromstring(npframes2, dtype=np.float32)

      norm_audio2 = (npframes2 / np.max(np.abs(npframes2)))  # normalize
      left2 = norm_audio2[::2]
      right2 = norm_audio2[1::2]
      print(norm_audio2)
      return left2, right2

  def tape_add(self):
      self.tape[:-self.Chunks] = self.tape[self.Chunks:]
      self.taper = self.tape
      self.tapel = self.tape
      self.taper[-self.Chunks:], self.tape[-self.Chunks:] = self.start_streamread()

  def plot(self, use_blit=True):
  # Plot the Tape and update chunks
      print('Plotting')
      self.start_streamsignal(start=True)
      start = True

      for duration in range(0, 15, 1):
          QtWidgets.QApplication.processEvents()
          plotsec = 1
          time.sleep(2)
          self.timeArray = np.arange(self.tape.size)
          self.timeArray = (self.timeArray / self.fs) * 1000  # scale to milliseconds
          self.tape_add()

          while start is True and plotsec < 3:

              self.ax.plot(self.taper, '-b')
              self.canvas.draw()

              self.ax2.clear()
              self.ax2.plot(self.tapel, 'g-')
              self.canvas2.draw()

              plotsec += 1


def main():
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())

main()