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
             
LANGE_TRANS_MAP = {'pose_left': u'左移',
                   'pose_right': u'右移',
                   'pose_down': u'向下',
                   'pose_change': u'变形',
                   'similar score': u'相似度得分:'} 
             
# ui配置文件
cUi, cBase = uic.loadUiType("pose_widget.ui")

# 主界面
class CPoseWidget(QWidget, cUi):
    def __init__(self, pose_name):
        # 设置UI
        QMainWindow.__init__(self)
        cUi.__init__(self)
        self.setupUi(self)
        
        self.sliderAccu.setMinimum(1)
        self.sliderAccu.setMaximum(100)
        self.sliderAccu.setSingleStep(1)
        self.sliderAccu.setValue(90)
        self.editAccu.setText('90%')
        self.label.hide()
        self.sliderAccu.hide()
        self.editAccu.hide()
        
        self.setMouseTracking(True)
        self.pose_name = pose_name
        self.labelTitle.setText(LANGE_TRANS_MAP[self.pose_name])
        self.reset_cfg_file = './cfgs/' + self.pose_name + '_reset.json'
        self.modify_cfg_file = './cfgs/' + self.pose_name + '_modify.json'
        self.reset_map = None
        self.point_map = None    
        self.catched_point = None
        self.catched_line = -1
        self.modify_flag = False
        self.load_cfg_file()
        
        
    def on_sliderAccu_valueChanged(self):
        value = self.sliderAccu.value()
        print('now value is:', value)
        self.editAccu.setText('%d%%'%value)
        
    def load_cfg_file(self):
        with open(self.reset_cfg_file, 'r') as f:
            self.reset_map = json.load(f)
        with open(self.modify_cfg_file, 'r') as f:
            self.point_map = json.load(f)
       
    def save_cfg_file(self):
        save_map = copy.deepcopy(self.point_map)
        if 'key_score' in save_map.keys():
            del save_map['key_score']
        with open(self.modify_cfg_file, 'w') as f:
            json.dump(save_map, f)
        
    def _get_lines(self, pos_map):
        c_shoulder = (np.array(pos_map['l_shoulder']) + np.array(pos_map['r_shoulder'])) / 2.0
        line0 = [pos_map['head'], c_shoulder] 
        line1 = [pos_map['l_shoulder'], pos_map['r_shoulder']] 
        line2 = [pos_map['l_hip'], pos_map['r_hip']]  
        line3 = [pos_map['l_shoulder'], pos_map['l_elbow']] 
        line4 = [pos_map['l_elbow'], pos_map['l_wrist']] 
        line5 = [pos_map['l_shoulder'], pos_map['l_hip']] 
        line6 = [pos_map['l_hip'], pos_map['l_knee']] 
        line7 = [pos_map['l_knee'], pos_map['l_ankle']] 
        line8 = [pos_map['r_shoulder'], pos_map['r_elbow']] 
        line9 = [pos_map['r_elbow'], pos_map['r_wrist']] 
        line10 = [pos_map['r_shoulder'], pos_map['r_hip']] 
        line11 = [pos_map['r_hip'], pos_map['r_knee']]    
        line12 = [pos_map['r_knee'], pos_map['r_ankle']] 
        return [line0,line1,line2,line3,line4,line5,line6,line7,line8,line9,line10,line11,line12]

    def _check_distance(self, point1, point2, radio):
        if abs(point1[0] - point2[0]) >= (0-radio) and abs(point1[0] - point2[0]) <= radio \
            and abs(point1[1] - point2[1]) >= (0-radio) and abs(point1[1] - point2[1]) <= radio:
            return True
        else:
            return False    

    def calcuate_similar(self, pos_map):           
        std_lines = self._get_lines(self.point_map)
        cmp_lines = self._get_lines(pos_map)
        
        key_lines = self.point_map['key_line']
        self.point_map['key_score'] = []
        for key_line_id in key_lines:
            std_line = std_lines[key_line_id]
            cmp_line = cmp_lines[key_line_id]
            angle = GetAngle(std_line, cmp_line)
            #line_score = 1.0 - angle / 180.0
            #self.point_map['key_score'].append(line_score)
            self.point_map['key_score'].append(angle)
           
        score_mean = 100.0 - (np.array(self.point_map['key_score']).mean() * 100.0 / 180.0)
        self.update()
        return score_mean
        
    def closeEvent(self, event):
        pass

    def set_info(self, point_map=None):
        if point_map is None:
            self.point_map = self.reset_map
        else:
            self.point_map = point_map
        self.update()
        
    def get_info(self):
        print('pose map:')
        print('\'head\':       [%.2f, %.2f],'%(self.reset_map['head'][0], self.reset_map['head'][1]))
        print('\'l_shoulder\': [%.2f, %.2f],'%(self.reset_map['l_shoulder'][0], self.reset_map['l_shoulder'][1]))
        print('\'l_elbow\':    [%.2f, %.2f],'%(self.reset_map['l_elbow'][0], self.reset_map['l_elbow'][1]))
        print('\'l_wrist\':    [%.2f, %.2f],'%(self.reset_map['l_wrist'][0], self.reset_map['l_wrist'][1]))
        print('\'r_shoulder\': [%.2f, %.2f],'%(self.reset_map['r_shoulder'][0], self.reset_map['r_shoulder'][1]))
        print('\'r_elbow\':    [%.2f, %.2f],'%(self.reset_map['r_elbow'][0], self.reset_map['r_elbow'][1]))
        print('\'r_wrist\':    [%.2f, %.2f],'%(self.reset_map['r_wrist'][0], self.reset_map['r_wrist'][1]))
        print('\'l_hip\':      [%.2f, %.2f],'%(self.reset_map['l_hip'][0], self.reset_map['l_hip'][1]))
        print('\'l_knee\':     [%.2f, %.2f],'%(self.reset_map['l_knee'][0], self.reset_map['l_knee'][1]))
        print('\'l_ankle\':    [%.2f, %.2f],'%(self.reset_map['l_ankle'][0], self.reset_map['l_ankle'][1]))
        print('\'r_hip\':      [%.2f, %.2f],'%(self.reset_map['r_hip'][0], self.reset_map['r_hip'][1]))
        print('\'r_knee\':     [%.2f, %.2f],'%(self.reset_map['r_knee'][0], self.reset_map['r_knee'][1]))
        print('\'r_ankle\':    [%.2f, %.2f],'%(self.reset_map['r_ankle'][0], self.reset_map['r_ankle'][1]))
        return self.point_map
        
    def mouse_catch_point(self, mouse_x, mouse_y, radio=0.01):          
        for key in self.point_map.keys():
            if key == 'key_line' or key == 'key_score':
                continue
            point_x, point_y = self.point_map[key]
            if self._check_distance([mouse_x, mouse_y], [point_x, point_y], radio=radio):
                self.catched_point = key
                return
        self.catched_point = None
        
    def mouse_catch_line(self, mouse_x, mouse_y, radio=0.01):
        std_lines = self._get_lines(self.point_map)
        for i,line in enumerate(std_lines):
            line_center = (np.array(line[0]) + np.array(line[1])) / 2.0
            if self._check_distance([mouse_x, mouse_y], line_center, radio):
                self.catched_line = i
                return
        self.catched_line = -1

    def draw_background(self, painter):
        pen = QPen()
        pen.setColor(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())
        
    def draw_pose_info(self, painter):
        def draw_pose_line(line, painter):
            point1, point2 = line
            point1_x = point1[0] * self.width()
            point1_y = point1[1] * self.height()
            point2_x = point2[0] * self.width()
            point2_y = point2[1] * self.height()
            qpoint1 = QPoint(point1_x, point1_y)
            qpoint2 = QPoint(point2_x, point2_y)
            painter.drawLine(qpoint1, qpoint2)
            
        # draw point
        for key in self.point_map.keys():
            if key != 'key_line' and key != 'key_score':
                point_x, point_y = self.point_map[key]
                pen = QPen()
                if self.catched_point is not None and self.catched_point == key:
                    pen.setColor(QColor(255, 100, 100))
                    pen.setWidth(8)
                else:
                    pen.setColor(QColor(100, 100, 255))
                    pen.setWidth(5)
                
                painter.setPen(pen)
                painter.drawPoint(point_x* self.width(), point_y* self.height())
        
        # draw line
        pen = QPen()
        lines = self._get_lines(self.point_map)
        for i, line in enumerate(lines):
            pen.setColor(QColor(100, 100, 255))
            pen.setWidth(1)

            if i == self.catched_line:
                pen.setColor(QColor(255, 100, 100))
                pen.setWidth(3)
            
            if 'key_line' in self.point_map.keys() and i in self.point_map['key_line']:
                pen.setColor(QColor(255, 100, 100))
                pen.setWidth(3)
                
            painter.setPen(pen)
            draw_pose_line(line, painter)
               
    def draw_score(self, painter):
        if 'key_score' in self.point_map.keys() and len(self.point_map['key_score']) > 0:
            all_lines = self._get_lines(self.point_map)
            for key_line_seq, key_line_score in zip(self.point_map['key_line'], self.point_map['key_score']):
                line = all_lines[key_line_seq]
                line_center = (np.array(line[0]) + np.array(line[1])) / 2.0
                pen = QPen()
                font = QFont("Microsoft YaHei")
                painter.setPen(pen)
                pointsize = font.pointSize()
                font.setPixelSize(pointsize*180/180)
                painter.setFont(font)
                painter.drawText(line_center[0]*self.width(), line_center[1]*self.height(), '%.2f'%(key_line_score))

            score = 100.0 - (np.array(self.point_map['key_score']).mean() * 100.0 / 180.0)
            #font.setPixelSize(pointsize*180/32)
            #painter.setFont(font)
            #painter.drawText(0, 0.5*self.height(), '%d分'%(score))
            self.labelTitle.setText(LANGE_TRANS_MAP[self.pose_name] + ' ' + LANGE_TRANS_MAP['similar score'] + ' %d'%score)


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.draw_background(painter)
        self.draw_pose_info(painter)
        self.draw_score(painter)

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            if not self.modify_flag and self.catched_line != -1:
                print('----> set line: ', self.catched_line)
                if 'key_line' not in self.point_map.keys():
                    self.point_map['key_line'] = []
                self.point_map['key_line'].append(self.catched_line)
            if self.modify_flag:
                return
            elif self.catched_point is None:
                return
            else:
                self.modify_flag = True

        if e.button() == QtCore.Qt.RightButton:
            if not self.modify_flag and self.catched_line != -1:
                print('----> un set line: ', self.catched_line)
                if 'key_line' not in self.point_map.keys():
                    return 
                else:
                    if self.catched_line in self.point_map['key_line']:
                        self.point_map['key_line'].remove(self.catched_line)
        self.update()

    def mouseMoveEvent(self, e):
        mouse_x = float(e.pos().x()) / self.width()
        mouse_y = float(e.pos().y()) / self.height()
        if self.modify_flag:
            self.point_map[self.catched_point] = [mouse_x, mouse_y]
        else:
            self.mouse_catch_point(mouse_x, mouse_y, radio=0.02)
            self.mouse_catch_line(mouse_x, mouse_y, radio=0.02)
        self.update()
          
    def mouseReleaseEvent(self, e):
        if self.modify_flag:
            self.modify_flag = False
        
    
    @pyqtSlot()  
    def on_btnReset_clicked(self):
        print('button btnReset clicked') 
        self.point_map = self.reset_map
        self.save_cfg_file()
        self.update()
        
    @pyqtSlot()      
    def on_btnDebug_clicked(self):
        print('button btnDebug clicked') 
        #self.get_info()
        #self.calcuate_similar(POSE_ACTION_RIGHT)
        self.save_cfg_file()
   
if __name__ == "__main__":
    cApp = QApplication(sys.argv)
    cPoseWidget = CPoseWidget('pose_left')
    cPoseWidget.show()
    sys.exit(cApp.exec_())


    
    
    