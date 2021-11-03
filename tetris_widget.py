# -*- coding: utf-8 -*-
import sys
import os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import cv2
import numpy as np
from Utils import GetAngle
import json
import copy
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QKeyEvent, QPen
import sys, random
from Tetris import Board
             
# ui配置文件
cUi, cBase = uic.loadUiType("tetris_widget.ui")

# 主界面
class CTetrisWidget(QWidget, cUi):
    def __init__(self, info_cb):
        # 设置UI
        QMainWindow.__init__(self)
        cUi.__init__(self)
        self.setupUi(self)
        
        self.tboard = Board(self)
        self.info_cb = info_cb
        
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.tboard)
        self.frame.setLayout(self.vbox)
        self.reset_widget_size()

        self.tboard.msg2Statusbar[str].connect(self.slot_get_message)

        self.tboard.start()
        self.tboard.pause()
        
        #self.center()
        self.setWindowTitle('Tetris')
        self.show()
        
    def paintEvent(self, event):
        self.reset_widget_size()

    def slot_get_message(self, message):
        if message.isdigit():
            self.info_cb('score', int(message))
        else:
            self.info_cb('pause', '')
    
    def reset_widget_size(self):
        std_scale = 1.8
        y = int(self.height() * 1.0)
        x = int(float(y) / std_scale)
        x_offset = int((self.width() - x) / 2.0)
        self.frame.resize(x, y)
        self.frame.move(x_offset,0)
        #self.labelScore.resize(int((self.width() - x) * 0.6), int(y / 3.0))
        #self.labelStatus.resize(int((self.width() - x) * 0.6), int(y / 3.0))
        

    def start(self):
        self.tboard.start()
        
    def pause_resume(self):
        self.tboard.pause()
        
    def control(self, cmd='left'): #left/right/down/change
        self.tboard.control(cmd)
 
if __name__ == "__main__":
    cApp = QApplication(sys.argv)
    cTetrisWidget = CTetrisWidget()
    cTetrisWidget.show()
    sys.exit(cApp.exec_())


    
    
    