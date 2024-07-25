from userface import Ui_Dialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QObject, QThread,pyqtSignal,QTimer
from keras.models import load_model
from sklearn.preprocessing import LabelEncoder
import string
import cv2 as cv 
import os 
import numpy as np
import sys
import time


class realtime(QMainWindow,Ui_Dialog):
    def __init__(self) :
        super().__init__()
        self.setupUi(self) 
        self.cam_port = None
        self.video_capture= cv.VideoCapture(0)
        self.test_clicked_flg= False
        self.frame_toBe_tested = None
        self.pixmap = None
        self.timer= QTimer()
        self.player()
    def player (self):
        self.timer.timeout.connect(self.open_web_cam)
        self.timer.start(30)
        self.test.clicked.connect(self.test_clicked)

    def test_clicked(self,event ):
        self.test_clicked_flg=True

    def open_web_cam(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap_ = QPixmap.fromImage(q_img)
            width=self.camera.width()
            height=self.camera.height()
            pixmap_ = pixmap_.scaled(width, height)
            self.camera.setPixmap(pixmap_)
            if self.test_clicked_flg:
                self.frame_toBe_tested= frame
                self.pixmap= pixmap_
                self.worker1 = worker_Thread(capturing_flg=False,predictioin_flg=True,main_window=self)
                self.worker1.start()
                self.predictioin_flg=False

                self.worker = worker_Thread(capturing_flg=True,predictioin_flg=False,main_window=self)
                self.worker.start()
                self.test_clicked_flg=False

                if self.frame_toBe_tested is None:
                    print("frame is none")
                else :
                    print("here we are ")


        if not self.timer:
            self.timer = self.startTimer(30)

    def timerEvent(self, event):
        self.open_web_cam()




class worker_Thread(QThread):
    def __init__(self,capturing_flg,predictioin_flg,main_window):
        super().__init__()
        self.capturing_flg=capturing_flg
        self.predictioin_flg= predictioin_flg
        self.main_window= main_window
    def run(self):
        if self.capturing_flg==True:
            self.refresh_captureding()
            self.make_prediction()
            self.finished.emit()
            self.capturing_flg=False
        if self.predictioin_flg:
            self.make_prediction()
            self.finished.emit()

    def refresh_captureding(self):
        self.main_window.captured.setPixmap(self.main_window.pixmap)
        self.pixmap=None
        return 
    def make_prediction(self):

        model = load_model(fr'C:\Users\HP\Downloads\feature_extractor\Gesture-Recognition-CNN\the_best_model.h5')
        label_encoder = LabelEncoder()
        label_encoder.fit(['A' ,'B' ,'C', 'D' ,'E' ,'F' ,'G', 'H' ,'I', 'J' ,'K' ,'L', 'M' ,'N' ,'O', 'P', 'R', 'S', 'T', 'U', 'V', 'Y', 'Z'])
        self.to_be_predicted = self.main_window.frame_toBe_tested
        frame_resized = cv.resize(self.to_be_predicted, (64, 64))  
        frame_float32 = frame_resized.astype(np.float32)
        frame_normalized = frame_float32 / 255.0  
        frame_expanded = np.expand_dims(frame_normalized, axis=0) 
        predictions = model.predict(frame_expanded)
        predicted_class = np.argmax(predictions, axis=1)
        self.main_window.prediction_result.setText("")
        if predicted_class >7:
            class_labels = label_encoder.classes_
            #print(class_labels)
            predicted_label = class_labels[predicted_class[0]]
            self.main_window.prediction_result.setText(f"the character is :{predicted_label}")

        else:
            self.main_window.prediction_result.setText("the character is unknown")

        self.to_be_predicted=None
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = realtime()
    window.show()
    sys.exit(app.exec_())