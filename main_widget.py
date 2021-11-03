# -*- coding: utf-8 -*-
import sys
sys.path.append('./movenet')
import os
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import copy
import numpy as np
import mss
import cv2
import threading
import time
from Tetris import Tetris
from pose_widget import CPoseWidget
from api import Infer
from det_widget import CDetWidget
from threading import Timer
from tetris_widget import CTetrisWidget
import qdarkstyle


# ui配置文件
cUi, cBase = uic.loadUiType("main_widget.ui")

# 主界面
class CMainWidget(QWidget, cUi):
    def __init__(self, main_widget=None):
        # 设置UI
        QMainWindow.__init__(self)
        cUi.__init__(self)
        self.setupUi(self)
        self.setWindowTitle(u'Pose Teris')
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # comboCamera
        self.comboCamera.addItem('camera 0')
        self.comboCamera.addItem('camera 1')
        self.comboCamera.addItem('camera 2')
        self.radioFlip.setChecked(True)

        # game widget
        self.game_widget = CTetrisWidget(self.info_cb) #Tetris()
        vbox = QVBoxLayout()
        vbox.addWidget(self.game_widget)
        self.tab_game.setLayout(vbox)
    
        # pose cfg widget
        self.pose_left_widget = CPoseWidget('pose_left')
        self.pose_right_widget = CPoseWidget('pose_right')
        self.pose_down_widget = CPoseWidget('pose_down')
        self.pose_change_widget = CPoseWidget('pose_change')
        hbox_row1 = QHBoxLayout()
        hbox_row2 = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox_row1.addWidget(self.pose_left_widget)
        hbox_row1.addWidget(self.pose_right_widget)
        hbox_row2.addWidget(self.pose_down_widget)
        hbox_row2.addWidget(self.pose_change_widget)
        vbox.addLayout(hbox_row1)
        vbox.addLayout(hbox_row2)        
        self.tab_config.setLayout(vbox)
        
        # det widget
        self.det_widget = CDetWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.det_widget)
        self.frameDet.setLayout(vbox)
        
        # hide tabWidget's tab
        self.tabWidget.setStyleSheet("QTabBar::tab{width:0px;height:0px;}")       
        #self.btnClose.setIcon(QtGui.QIcon('./exit.png'))
    
        self.status = 'stop' #stop/run/
        self.thread_flag = True
        self.thread_handle = None
        self.infer = Infer()
        self.infer.init()

        self.camera_cap = None
        self.last_cmd_time = 0
        
        self.base_w = 1024
        self.base_h = 640
        self.font_base = 9.0
        
        
        self.move_flag = False
        self.mose_pos = None
         
    def resize_widget(self, ratio):
        self.base_w = int(self.base_w * ratio)
        self.base_h = int(self.base_h * ratio)
        self.font_base = self.font_base * ratio 
        
        self.resize(self.base_w, self.base_h)
        
        widgets = [self.tabWidget, 
                   self.btnAction, 
                   self.labelGame, 
                   self.labelPose, 
                   self.groupBox, 
                   self.frameDet,
                   self.labelCamera,
                   self.comboCamera,
                   self.labelFlip,
                   self.radioFlip,
                   self.btnClose,
                   self.btnSmall,
                   self.btnBig,
                   self.btnCfg,
                   self.btnGame,
                   self.btnInfo]
                   
        font_resize_widgets = [self.labelGame,
                               self.labelPose]
                   
        for widget in widgets:
            o_x = widget.geometry().x()
            o_y = widget.geometry().y()
            w = widget.geometry().width()
            h = widget.geometry().height()
            o_x = int(o_x * ratio)
            o_y = int(o_y * ratio)
            w = int(w * ratio)
            h = int(h * ratio)
            widget.resize(w, h)
            widget.move(o_x, o_y)

        for widget in font_resize_widgets:
            ft = QFont()
            ft.setPointSize(self.font_base)
            widget.setFont(ft)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mose_pos = event.globalPos()
            m_iFlagMLB = 1;
            self.move_flag = True

    def mouseMoveEvent(self, event):
        if self.move_flag:
            mouse_pos = event.globalPos()
            self.move(self.pos().x()+(mouse_pos.x()-self.mose_pos.x()),self.pos().y()+(mouse_pos.y()-self.mose_pos.y()));
            self.mose_pos = mouse_pos;

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.move_flag = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        background = QPixmap("./back.png")
        #painter.drawPixmap(0, 0, int(self.base_w * self.ratio), int(self.base_h* self.ratio), background)
        pass
     
    def info_cb(self, key, value):
        if 'score' == key:
            self.labelGame.setText('SCORE: %d'%value)
        if 'det_cmd' == key:
            self.labelPose.setText('%s'%value)
        if 'det_status' == key:
            self.labelPose.setText('%s'%value)
        if 'pause' == key:
            self.labelGame.setText('PAUSE')
     
    @pyqtSlot()      
    def on_btnAction_clicked(self):
        print('button btnAction clicked') 
        if self.status is 'stop' and self.thread_handle is None:
            self.thread_flag = True
            self.status = 'run'
            self.thread_handle = threading.Thread(target=self.det_thread, args=())
            self.thread_handle.start()
            self.btnAction.setText('停止')
            camera_id = int(self.comboCamera.currentText().split(' ')[-1])
            self.camera_cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
            self.game_widget.pause_resume()
            self.tabWidget.setCurrentIndex(1)
        else:
            self.status = 'stop'
            self.game_widget.pause_resume()
            self.thread_flag = False
            self.thread_handle.join()
            self.thread_handle = None
            self.btnAction.setText('开始')
            self.camera_cap.release()
            self.camera_cap = None

    @pyqtSlot()      
    def on_btnDebug_clicked(self):
        print('button btnDebug clicked') 
        self.game_widget.pause_resume()
        self.game_widget.control(cmd='left')
        
    @pyqtSlot()      
    def on_btnCfg_clicked(self):
        print('btnCfg clicked')
        self.tabWidget.setCurrentIndex(0)
    
    @pyqtSlot()      
    def on_btnGame_clicked(self):
        print('btnGame clicked')
        self.tabWidget.setCurrentIndex(1)
    
    @pyqtSlot()      
    def on_btnInfo_clicked(self):
        print('btnInfo clicked')
        self.tabWidget.setCurrentIndex(2)
      
    @pyqtSlot()  
    def on_btnClose_clicked(self):
        print('btnClose clicked')
        self.closeEvent(None)
        app = QApplication.instance()
        app.quit()

    @pyqtSlot()  
    def on_btnSmall_clicked(self):
        print('btnSmall clicked')
        self.resize_widget(0.8)
        
    @pyqtSlot()  
    def on_btnBig_clicked(self):
        print('btnBig clicked')
        self.resize_widget(1.2)
        
    def det_thread(self):
        print('det thread start')
        while self.thread_flag:            
            #获取摄像头截图
            if self.camera_cap is not None:
                # get a frame
                ret, img = self.camera_cap.read()
                if ret is False:
                    self.on_btnAction_clicked()
                    return

                if self.radioFlip.isChecked():
                    img = cv2.flip(img, 1)
                ##Debug
                #img = cv2.imread('change.jpg')
                ##Debug
                
                #送到网络监测
                kps = self.infer.infer(img)
                score_min = np.array(kps[:, 2]).min()
                show_info = ''
                if score_min < 0.1:
                    print('no total people deted, ignore')
                    show_info = 'no people'
                    self.info_cb('det_status', u'没有检测到完整的人')
                    pass
                else:
                    pose_map = {}
                    pose_map['head'] = [kps[0][1], kps[0][0]] 
                    pose_map['l_shoulder'] = [kps[6][1], kps[6][0]]  
                    pose_map['r_shoulder'] = [kps[5][1], kps[5][0]] 
                    pose_map['l_elbow'] = [kps[8][1], kps[8][0]]  
                    pose_map['r_elbow'] = [kps[7][1], kps[7][0]] 
                    pose_map['l_wrist'] = [kps[10][1], kps[10][0]]
                    pose_map['r_wrist'] = [kps[9][1], kps[9][0]] 
                    pose_map['l_hip'] = [kps[12][1], kps[12][0]] 
                    pose_map['r_hip'] = [kps[11][1], kps[11][0]] 
                    pose_map['l_knee'] = [kps[14][1], kps[14][0]]
                    pose_map['r_knee'] = [kps[13][1], kps[13][0]] 
                    pose_map['l_ankle'] = [kps[16][1], kps[16][0]] 
                    pose_map['r_ankle'] = [kps[15][1], kps[15][0]] 
                    all_score = []
                    all_pos = []
                    max_score = 0
                    max_pos = ''
                    score_left = self.pose_left_widget.calcuate_similar(pose_map)
                    max_score = score_left
                    max_pos = 'left'
                    score = self.pose_right_widget.calcuate_similar(pose_map)
                    if score > max_score:
                        max_score = score
                        max_pos = 'right'
                    score = self.pose_down_widget.calcuate_similar(pose_map)
                    if score > max_score:
                        max_score = score
                        max_pos = 'down'
                    score = self.pose_change_widget.calcuate_similar(pose_map)
                    if score > max_score:
                        max_score = score
                        max_pos = 'change'
                    
                    if max_score > 90:
                        now_time = time.time()
                        if now_time - self.last_cmd_time > 1.5:
                            self.last_cmd_time = now_time
                            self.game_widget.control(max_pos)
                            show_info = 'cmd: ' + max_pos
                            self.info_cb('det_cmd', max_pos)
                        
                self.det_widget.show_det_ret(img, kps, show_info)
            
            #time.sleep(0.1)   
        print('det thread stop')         

    def closeEvent(self,event):
        print('save and close')
        self.pose_left_widget.save_cfg_file()   
        self.pose_right_widget.save_cfg_file()
        self.pose_down_widget.save_cfg_file()
        self.pose_change_widget.save_cfg_file()
        

if __name__ == "__main__":
    cApp = QApplication(sys.argv)   
    cMainWidget = CMainWidget()
    #apply_stylesheet(cApp, theme='dark_teal.xml')
    cApp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    cMainWidget.show()
    sys.exit(cApp.exec_())