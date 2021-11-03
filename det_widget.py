# -*- coding: utf-8 -*-
import sys
import os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import copy
import xml.etree.cElementTree as et
import os
import cv2
import math
from PIL import Image

# ui配置文件
cUi, cBase = uic.loadUiType("det_widget.ui")

# 主界面
class CDetWidget(QWidget, cUi):
    def __init__(self): #, main_widget=None):
        # 设置UI
        QMainWindow.__init__(self)
        cUi.__init__(self)
        self.setupUi(self)
        self.qpixmap = None
        self.kps = None
        self.show_info = ''

        self.color_list = [QColor(255,0,0),
                      QColor(0,255,0),
                      QColor(0,0,255),
                      QColor(0,255,255),
                      QColor(255,0,255),
                      QColor(8,46,84),
                      QColor(199,97,20),
                      QColor(255,227,132),
                      QColor(255,255,0),
                      QColor(128,138,135)]

    def show_det_ret(self, img, kps, infos):
        height, width, bytesPerComponent = img.shape
        bytesPerLine = bytesPerComponent * width
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.qpixmap = QPixmap.fromImage(image) 
        self.kps = kps
        self.show_info = infos
        self.update()

    def draw_infos(self, painter):
        pen = QPen()
        font = QFont("Microsoft YaHei")
        painter.setPen(pen)
        pointsize = font.pointSize()
        font.setPixelSize(pointsize*180/36)
        painter.setFont(font)
        painter.drawText(0, int(0.5 * self.height()), self.show_info)                    
  
    def draw_image(self, painter):
        pen = QPen()
        font = QFont("Microsoft YaHei")
        if self.qpixmap is not None:
            painter.drawPixmap(QtCore.QRect(0, 0, self.width(), self.height()), self.qpixmap)
        
    def draw_background(self, painter):
        pen = QPen()
        pen.setColor(QColor(10, 10, 10))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())
        
    def draw_infer_kp(self, painter):
        if self.kps is None:
            return
            
        x_scale = self.width()# / self.qpixmap.width()
        y_scale = self.height()# / self.qpixmap.height()
        kps = self.kps
        kps[:,0] = kps[:,0] * y_scale
        kps[:,1] = kps[:,1] * x_scale

        nose = kps[0]
        left_shoulder = kps[5]
        right_shoulder = kps[6]
        center_shoulder = (left_shoulder + right_shoulder) / 2
        right_shoulder = kps[6]
        left_elbow = kps[7]
        right_elbow = kps[8]
        left_wrist = kps[9]
        right_wrist = kps[10]
        left_hip = kps[11]
        right_hip = kps[12]
        center_hip = (left_hip + right_hip) / 2
        left_knee = kps[13]
        right_knee = kps[14]
        left_ankle = kps[15]
        right_ankle = kps[16]

        pen = QPen()
        pen.setColor(self.getColor(0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(nose[1], nose[0], center_shoulder[1], center_shoulder[0])
        pen.setColor(self.getColor(1))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(center_shoulder[1], center_shoulder[0], center_hip[1], center_hip[0])
        pen.setColor(self.getColor(2))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(left_shoulder[1], left_shoulder[0], right_shoulder[1], right_shoulder[0])
        pen.setColor(self.getColor(3))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(left_shoulder[1], left_shoulder[0], left_elbow[1], left_elbow[0])
        pen.setColor(self.getColor(4))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(left_elbow[1], left_elbow[0], left_wrist[1], left_wrist[0])
        pen.setColor(self.getColor(5))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(right_shoulder[1], right_shoulder[0], right_elbow[1], right_elbow[0])
        pen.setColor(self.getColor(6))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(right_elbow[1], right_elbow[0], right_wrist[1], right_wrist[0])
        pen.setColor(self.getColor(7))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(left_hip[1], left_hip[0], right_hip[1], right_hip[0])
        pen.setColor(self.getColor(8))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(left_hip[1], left_hip[0], left_knee[1], left_knee[0])
        pen.setColor(self.getColor(9))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(left_knee[1], left_knee[0], left_ankle[1], left_ankle[0])
        pen.setColor(self.getColor(10))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(right_hip[1], right_hip[0], right_knee[1], right_knee[0])
        pen.setColor(self.getColor(11))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(right_knee[1], right_knee[0], right_ankle[1], right_ankle[0])


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.draw_background(painter)
        self.draw_image(painter)
        self.draw_infer_kp(painter)
        self.draw_infos(painter)

    def getColor(self, index):
        return self.color_list[index % len(self.color_list)]
        
if __name__ == "__main__":
    cApp = QApplication(sys.argv)
    cDetWidget = CDetWidget()
    cDetWidget.show()
    sys.exit(cApp.exec_())