import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets
import cv2
import mediapipe as mp
import math
from EAR import EAR
from MAR import MAR
from WebcamVideoStream import WebcamVideoStream
import time
import imutils

# Fix the blocking that occurs in here

class MatplotlibWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.temp_ear_data = []
        self.temp_time_data = []
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        # Configure figure
        self.fig = plt.figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)

        layout.addWidget(self.canvas)

        self.setup()

    def change_data(self, new_time_data, new_ear_data):
        self.temp_ear_data = new_ear_data
        self.temp_time_data = new_time_data

    def setup(self):
        self.ax = self.fig.subplots()
        self.animate()
    
    def update(self, i):
        time_data = self.temp_time_data[-30:]
        ear_data = self.temp_ear_data[-30:]
        self.ax.clear()
        self.ax.plot(time_data, ear_data)
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.3)
        plt.title("Test Animation Plot")
        plt.xlabel("X Value")
        plt.ylabel("Y Value")
        self.canvas.draw()
        print("blah")

    def animate(self):
        self.anim = animation.FuncAnimation(self.fig, self.update, interval=100, cache_frame_data=False)


class MainWindow(QWidget):
    def __init__(self, time_secs, ear_vals, mar_vals, ear_and_mar_vals, blink_list, yawn_list, temp_ear_data, temp_time_data, ear_threshold, ear_open_value, perclos_vals):
        super(MainWindow, self).__init__()
        self.time_secs= time_secs
        self.ear_vals = ear_vals
        self.mar_vals = mar_vals
        self.ear_and_mar_vals = ear_and_mar_vals
        self.blink_list = blink_list
        self.yawn_list = yawn_list
        self.temp_ear_data = temp_ear_data
        self.temp_time_data = temp_time_data
        self.ear_threshold = ear_threshold
        self.ear_open_value = ear_open_value
        self.perclos_vals = perclos_vals

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.Worker1 = Worker1(self.time_secs, self.ear_vals, self.mar_vals, self.ear_and_mar_vals, self.blink_list, self.yawn_list, self.temp_ear_data, self.temp_time_data, self.ear_threshold, self.ear_open_value, self.perclos_vals)

        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setLayout(self.VBL)

        self.MatplotlibSubWidget = MatplotlibWidget()
        self.Worker1.PlotUpdate.connect(self.MatplotlibSubWidget.change_data)
        self.VBL.addWidget(self.MatplotlibSubWidget)


    def ImageUpdateSlot(self, image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(image))


class Worker1(QThread):

    def __init__(self, time_secs, ear_vals, mar_vals, ear_and_mar_vals, blink_list, yawn_list, temp_ear_data, temp_time_data, ear_threshold, ear_open_value, perclos_vals):
        super().__init__()
        self.time_secs = time_secs
        self.ear_vals = ear_vals
        self.mar_vals = mar_vals
        self.ear_and_mar_vals = ear_and_mar_vals
        self.blink_list = blink_list
        self.yawn_list = yawn_list
        self.temp_ear_data = temp_ear_data
        self.temp_time_data = temp_time_data
        self.ear_threshold = ear_threshold
        self.ear_open_value = ear_open_value
        self.perclos_vals = perclos_vals

    ImageUpdate = pyqtSignal(QImage)
    PlotUpdate = pyqtSignal(list, list)

    def run(self):
        start1 = time.time()  
        start2 = time.time()  # For the perclos stuff
        mp_face_mesh = mp.solutions.face_mesh

        perclos = 0
        MAR_threshold = 0.7   # Customize to whatever you want/need
        blink_frame_counter = 0
        yawn_frame_counter = 0
        blink_frame_threshold = 1
        yawn_frame_threshold = 20
        scale = 30            # for purpose of scaling the video (zooming in/out)

        closed_frame_counter = 0
        total_frame_counter = 0
        interval_counter = 0

        # Initialize a face_mesh object
        face_mesh_images = mp_face_mesh.FaceMesh(static_image_mode=False, 
                                                refine_landmarks=True,
                                                max_num_faces=1,
                                                min_detection_confidence=0.5, 
                                                min_tracking_confidence=0.5)
        
        vs = WebcamVideoStream(src=0).start()
        
        counter = 0 # DELETE LATER

        if (vs.stream.isOpened() == False):
            print("There was an error opening the mp4 file")

        else:
            with face_mesh_images as face_mesh:
                while (vs.stream.isOpened()):
                    frame = vs.read() # read the frame
                    
                    if True:
                        start_time = time.time()
                        # All of this is for resizing the image
                        # ---------------------------------------------------------------
                        height, width, channels = frame.shape
                        centerX,centerY=int(height/2),int(width/3) #For laptop screen
                        #centerX,centerY=int(height/2),int(width/2)  # For desktop screen
                        radiusX,radiusY= int(scale*height/100),int(scale*width/100)
                        minX,maxX=centerX-radiusX,centerX+radiusX
                        minY,maxY=centerY-radiusY,centerY+radiusY
                        cropped = frame[minX:maxX, minY:maxY]
                        resized_cropped = cv2.resize(cropped, (width, height))
                        resized_cropped = imutils.resize(frame, width=700)
                        image = cv2.cvtColor(resized_cropped, cv2.COLOR_BGR2RGB)  
                        flippedImage = cv2.flip(image, 1)
                        # ---------------------------------------------------------------
                        results = face_mesh.process(flippedImage)
                        right_eye_landmarks = [(0,33), (1,160), (2,158), (3,133), (4,153), (5,144)]     # coords to be used to calculate right EAR
                        left_eye_landmarks = [(0,362), (1,385), (2,387), (3,263), (4,373), (5,380)]     # coords to be used to calculate left EAR
                        mouth_landmarks = [(0,76), (1,41), (2,12), (3,271), (4,306), (5,403), (6,15), (7,179)]  # coords to be used to calculate MAR

                        right_counter = 0
                        left_counter = 0
                        mouth_counter = 0

                        if results.multi_face_landmarks == None:
                            current_time = time.time()
                            time_elapsed = current_time - start1
                            time_elapsed_temp = current_time - start2 # To be used for the PERCLOS stuff
                            self.time_secs.append(time_elapsed)
                            self.mar_vals.append(0)
                            self.ear_vals.append(0)
                            self.ear_and_mar_vals.append([time_elapsed, 0, 0, 0, 0])
                            self.blink_list.append(0)
                            self.yawn_list.append(0)
                            total_frame_counter += 1
                            print(f"Total Frames: {total_frame_counter}")
                            print(f"Closed Frames: {closed_frame_counter}")
                            # For the animation function
                            # --------------------------
                            self.temp_time_data.append(time_elapsed)
                            self.temp_ear_data.append(0)
                            #---------------------------
                            cv2.putText(flippedImage, "MAR: N/A", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(flippedImage, "EAR: N/A", (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(flippedImage, f"EAR Threshold: {str(math.ceil(ear_threshold*10000)/10000)}", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(flippedImage, f"PERCLOS: {str(round(perclos, 4))}", (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            convertToQtFormat = QImage(flippedImage.data, flippedImage.shape[1], flippedImage.shape[0], QImage.Format_RGB888)
                            pic = convertToQtFormat.scaled(1280, 960, Qt.KeepAspectRatio)
                            self.ImageUpdate.emit(pic)
                            self.PlotUpdate.emit(temp_time_data, temp_ear_data)
                            print(counter)
                            counter += 1
                        else:
                            blinked = 0 # value to keep track of whether the participant blinked, used for logging data into csv file
                            yawned = 0  # value to keep track of whether the participant blinked, used for logging data into csv file
                            for face_landmarks in results.multi_face_landmarks:
                                current_time = time.time()
                                time_elapsed = current_time - start1
                                time_elapsed_temp = current_time - start2
                                total_frame_counter += 1

                                right_eye_coord_list = []
                                if right_counter == 0:
                                    for place, idx in right_eye_landmarks:
                                        loc_x = int(face_landmarks.landmark[idx].x * resized_cropped.shape[1])
                                        loc_y = int(face_landmarks.landmark[idx].y * resized_cropped.shape[0])
                                        right_eye_coord_list.append((loc_x, loc_y))
                                        cv2.circle(flippedImage,(loc_x, loc_y), radius=1, color=(255,255,255), thickness=1)
                                    right_counter = 1
                                else:
                                    for place, idx in right_eye_landmarks:
                                        loc_x = int(face_landmarks.landmark[idx].x * resized_cropped.shape[1])
                                        loc_y = int(face_landmarks.landmark[idx].y * resized_cropped.shape[0])
                                        right_eye_coord_list[place] = (loc_x, loc_y)
                                        cv2.circle(flippedImage,(loc_x, loc_y), radius=1, color=(255,255,255), thickness=1)
                                rightEar = EAR(right_eye_coord_list)

                                left_eye_coord_list = []
                                if left_counter == 0:
                                    for place, idx in left_eye_landmarks:
                                        loc_x = int(face_landmarks.landmark[idx].x * resized_cropped.shape[1])
                                        loc_y = int(face_landmarks.landmark[idx].y * resized_cropped.shape[0])
                                        left_eye_coord_list.append((loc_x, loc_y))
                                        cv2.circle(flippedImage,(loc_x, loc_y), radius=1, color=(255,255,255), thickness=1)
                                    left_counter = 1
                                else:
                                    for place, idx in left_eye_landmarks:
                                        loc_x = int(face_landmarks.landmark[idx].x * resized_cropped.shape[1])
                                        loc_y = int(face_landmarks.landmark[idx].y * resized_cropped.shape[0])
                                        left_eye_coord_list[place] = (loc_x, loc_y)
                                        cv2.circle(flippedImage,(loc_x, loc_y), radius=1, color=(255,255,255), thickness=1)
                                leftEar = EAR(left_eye_coord_list)

                                mouth_coord_list = []
                                if mouth_counter == 0:
                                    for place, idx in mouth_landmarks:
                                        loc_x = int(face_landmarks.landmark[idx].x * resized_cropped.shape[1])
                                        loc_y = int(face_landmarks.landmark[idx].y * resized_cropped.shape[0])
                                        mouth_coord_list.append((loc_x, loc_y))
                                        cv2.circle(flippedImage,(loc_x, loc_y), radius=1, color=(255,255,255), thickness=1)
                                    mouth_counter = 1
                                else:
                                    for place, idx in mouth_landmarks:
                                        loc_x = int(face_landmarks.landmark[idx].x * resized_cropped.shape[1])
                                        loc_y = int(face_landmarks.landmark[idx].y * resized_cropped.shape[0])
                                        mouth_coord_list[place] = (loc_x, loc_y)
                                        cv2.circle(flippedImage,(loc_x, loc_y), radius=1, color=(255,255,255), thickness=1)
                                mar = MAR(mouth_coord_list)      

                                avgEar = (rightEar + leftEar) / 2         
                            
                                time_secs.append(time_elapsed)
                                mar_vals.append(mar)
                                ear_vals.append(avgEar)

                                # For the animation function
                                # --------------------------
                                temp_ear_data.append(avgEar)
                                temp_time_data.append(time_elapsed)


                                # --------------------------

                                cv2.putText(flippedImage, f"MAR: {str(math.ceil(mar*10000)/10000)}", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                cv2.putText(flippedImage, f"EAR: {str(math.ceil(avgEar*10000)/10000)}", (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                cv2.putText(flippedImage, f"EAR Threshold: {str(math.ceil(ear_threshold*10000)/10000)}", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                cv2.putText(flippedImage, f"PERCLOS: {str(round(perclos, 4))}", (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            
                                # Cases for determining PERCLOS
                                # -----------------------------------------
                                if avgEar < (0.3 * ear_open_value): # If the eye is 70%> closed, increment the closed frame counter by 1, along with the total frame counter
                                    closed_frame_counter += 1
                                    #print("Total Frames: ", total_frame_counter)
                                    #print("Closed Frames: ", closed_frame_counter)

                                if time_elapsed_temp >= 10:  # 1 minute has passed, we are finished the interval
                                    #print("10 seconds has passed")
                                    perclos = round(closed_frame_counter / total_frame_counter, 5) * 100
                                    #print(perclos)
                                    perclos_vals.append((interval_counter, perclos))
                                    cv2.putText(flippedImage, f"PERCLOS: {str(round(perclos, 4))}", (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    closed_frame_counter = 0
                                    total_frame_counter = 0
                                    interval_counter += 1
                                    start2 = time.time()
                                # -----------------------------------------

                                # Cases for Blinking and Yawning
                                # -----------------------------------------
                                if avgEar < ear_threshold and mar > MAR_threshold:
                                    blink_frame_counter += 1  
                                    yawn_frame_counter += 1

                                    if blink_frame_counter >= blink_frame_threshold:
                                        cv2.putText(flippedImage, "Blink!", (220, 220), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
                                        blink_list.append(1)
                                        blinked = 1
                                    else:
                                        blink_list.append(0)
                                        blinked = 0

                                    if yawn_frame_counter >= yawn_frame_threshold:
                                        cv2.putText(flippedImage, "Yawn!", (300, 300), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                                        yawn_list.append(1)
                                        yawned = 1
                                    else:
                                        yawn_list.append(0)
                                        yawned = 0

                                elif avgEar < ear_threshold and mar < MAR_threshold:
                                    blink_frame_counter += 1
                                    yawn_frame_counter = 0
                                    yawned = 0
                                    yawn_list.append(0)

                                    if blink_frame_counter >= blink_frame_threshold:
                                        cv2.putText(flippedImage, "Blink!", (220, 220), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
                                        blink_list.append(1)
                                        blinked = 1
                                    else:
                                        blink_list.append(0)
                                        blinked = 0

                                elif mar > MAR_threshold and avgEar > ear_threshold:
                                    yawn_frame_counter += 1
                                    blink_frame_counter = 0
                                    blinked = 0
                                    blink_list.append(0)
                                    if yawn_frame_counter >= yawn_frame_threshold:
                                        cv2.putText(flippedImage, "Yawn!", (300, 300), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                                        yawn_list.append(1)
                                        yawned = 1
                                    else:
                                        yawn_list.append(0)
                                        yawned = 0
                            
                                elif mar < MAR_threshold and avgEar > ear_threshold:
                                    yawn_frame_counter = 0
                                    blink_frame_counter = 0
                                    blinked = 0
                                    yawned = 0
                                    blink_list.append(0)
                                    yawn_list.append(0)

                                ear_and_mar_vals.append([time_elapsed, avgEar, mar, blinked, yawned]) 
                                # -----------------------------------------

                            """ cv2.imshow("image", flippedImage)
                            if cv2.waitKey(1) & 0xFF == ord('x'):
                                break """
                            convertToQtFormat = QImage(flippedImage.data, flippedImage.shape[1], flippedImage.shape[0], QImage.Format_RGB888)
                            pic = convertToQtFormat.scaled(1280, 960, Qt.KeepAspectRatio)
                            self.ImageUpdate.emit(pic)
                            self.PlotUpdate.emit(temp_time_data, temp_ear_data)
                            print(counter)
                            counter += 1

        end_time = time.time()
        time_elapsed_total = end_time - start_time
        
        vs.stop()
        cv2.destroyAllWindows()


    def stop(self):
        self.ThreadActive = False
        self.quit()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    time_secs = []          # Keeps track of the time in seconds
    ear_vals = []           # Keeps track of EAR value as a ratio
    mar_vals = []           # Keeps track of MAR value as a ratio
    ear_and_mar_vals = []   # List containining the time data, EAR data, and MAR data as a tuple; (time, EAR, MAR), to be used for csv file
    blink_list = []         # Keeps track of blinks throughout runtime
    yawn_list = []          # Keeps track of yawns throughout runtime
    perclos_vals = []
    # Lists holding values for the animation plotting function
    # --------------------------------------------------------
    temp_ear_data = []      # Copy of the ear_vals list
    temp_time_data = []     # Copy of the tixxxxxxxme_secs list
    # --------------------------------------------------------
    ear_threshold = 0.15
    ear_open_value = 0.7

    root = MainWindow(time_secs, ear_vals, mar_vals, ear_and_mar_vals, blink_list, yawn_list, temp_ear_data, temp_time_data, ear_threshold, ear_open_value, perclos_vals)
    root.show()
    sys.exit(App.exec())