from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QOpenGLWidget, 
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QDockWidget, QTextEdit
)
from PyQt5.QtCore import Qt
import numpy as np 
from OpenGL.GL import *
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_9_BY_15
from OpenGL.GLU import *
import sys
from utility import read_txt
import ctypes

GLUT_BITMAP_HELVETICA_10 = ctypes.c_void_p(5)


class GLWidget(QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.points = [
            [0.000,0.000],
            [0.000,0.500],
            [0.0,-0.5],
            [0.5,0.0],
            [0.5,0.5],
            [0.5,-0.5],
            [-0.5,0.0],
            [-0.5,0.5],
            [-0.5,-0.5],
        ]

        self.camera_x = 1000.0
        self.camera_y = 1000.0
        self.camera_step_x = 50.0
        self.camera_step_y = 40.0
        self.view_size = 1.0
        self.zoom = 1000.0
        self.zoom_step = 50.0
        self.show_labels = False
        self.show_lines = False
        self.record_point = False
        self.recorded_points = []
        self.prediction_curves = []
        self.recording_dock_text = QTextEdit()

        #Allows openGl widget to be focused
        #without it, only focuses on GUI 
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        


    def initializeGL(self):
        glClearColor(0,0,0,1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        
        glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))

        glLoadIdentity()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #update ortho, simulates camera movement with arrow keys 
        variable_size = self.view_size * self.zoom
        gluOrtho2D(-variable_size + self.camera_x, variable_size + self.camera_x, -variable_size + self.camera_y, variable_size + self.camera_y)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glPointSize(5.0)
        glColor3f(1.0, 1.0, 0.0)

        #draw point array
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.points)
        glDrawArrays(GL_POINTS, 0, len(self.points))
        glDisableClientState(GL_VERTEX_ARRAY)
        
        # draw labels
        if self.show_labels:
            glColor3f(1.0, 1.0, 1.0)
            for x, y in self.points:
                label = f"({x:.3f},{y:.3f})"
                self.drawText2D(x - 0.01, y - 0.01, label)


        #save matrices of movable objects         
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        #switch to screen space to draw fixed horizontal line 
        ###################################################################
        glOrtho(0, self.width(), 0, self.height(), -1, 1)


        #draw lines 
        if not self.show_lines:
            glColor3f(1.0,0.0,0.0)

            glBegin(GL_LINES)
            glVertex2f(0, self.height()/2)
            glVertex2f(self.width(), self.height()/2)
            glEnd()

        ###################################################################

        #reload matrices of movable objects 
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
     

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        #record singular point
        if self.record_point:

            left = self.camera_x - variable_size
            right = self.camera_x + variable_size
            bottom = self.camera_y - variable_size
            top = self.camera_y + variable_size

            visible_points = [
                (x,y) for x,y in self.points
                if left <= x <= right and bottom <= y <= top
            ]

            if len(visible_points) == 1:
                print(visible_points)
                self.recorded_points.append(visible_points[0])
                self.recorded_points = list(set(self.recorded_points))
                self.recorded_points.sort(key=lambda x: x[0])
                self.recording_dock_text.clear()
                self.recording_dock_text.append("".join([str(x) + "\n" for x in self.recorded_points]))

        glFlush()
       

    def drawText2D(self, x,y, string):
        glRasterPos(x,y)

        for ch in string:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))


    def keyPressEvent(self, event):
        
        key = event.key()

        if key == Qt.Key.Key_Left:
            self.camera_x += self.camera_step_x
        elif key == Qt.Key.Key_Right:
            self.camera_x -= self.camera_step_x
        elif key == Qt.Key.Key_Up:
            self.camera_y -= self.camera_step_y
        elif key == Qt.Key.Key_Down:
            self.camera_y += self.camera_step_y
        elif key == Qt.Key.Key_Plus:
            self.zoom = max(0.1, self.zoom - self.zoom_step)
        elif key == Qt.Key.Key_Minus:
            self.zoom += self.zoom_step
        

        self.update()

class RecordingDock(QDockWidget):

    def __init__(self, widget):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(widget)

        self.container = QWidget()
        self.container.setLayout(layout)
        self.container.setContentsMargins(0,60,0,0)

        self.setWidget(self.container)
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.setTitleBarWidget(QWidget())
        self.hide()

    def addWidget(self, widget):
        self.widget = widget

    



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEst going")

        #Create dropdown list 
        self.combo = QComboBox(self)
        self.combo.addItems(["Camera Course", "Camera Fine", "Camera Super Fine"])
        self.combo.currentIndexChanged.connect(self.onCameraSpeedSelect)

        
        #Create toggleable button and attaches event handler
        self.coordsToggle = self.create_toggle_button("Toggle Coordinates", self.onToggleLabels, True)

        self.linesToggle = self.create_toggle_button("Toggle Lines", self.onToggleLines, True)

        self.recordToggle = self.create_toggle_button("Toggle Record", self.onToggleRecord, True)

        self.resetRecord = QPushButton(self)
        self.resetRecord.setText("Confirm Record")
        self.resetRecord.clicked.connect(self.onResetToggle)

        self.openRecordings = QPushButton(self)
        self.openRecordings.setText("Open Recordings")
        self.openRecordings.clicked.connect(self.onOpenRecordings)


        #add openGL widget
        self.glWidget = GLWidget(self)

        #horizontal layout
        hLayout1 = QHBoxLayout()
        hLayout1 = self.add_widgets_to_layout(
            hLayout1,
            self.combo,
            self.coordsToggle,
            self.linesToggle, 
        )

        hLayout2 = QHBoxLayout()
        hLayout2 = self.add_widgets_to_layout(
            hLayout2,
            self.recordToggle,
            self.resetRecord,
            self.openRecordings
        )

        #main layout is vertical
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(hLayout1)
        mainLayout.addLayout(hLayout2)
        mainLayout.addWidget(self.glWidget)

        
        self.recording_dock = RecordingDock(self.glWidget.recording_dock_text)
        self.addDockWidget(Qt.RightDockWidgetArea,self.recording_dock)
        self.resizeDocks([self.recording_dock], [int(self.width()* 0.25)], Qt.Horizontal)

        

        main_container = QWidget()
        main_container.setLayout(mainLayout)
        self.setCentralWidget(main_container)

    #helper func
    def create_toggle_button(self, title, eventHandler, checkable):
        toggleButton = QPushButton(self)
        toggleButton.setCheckable(checkable)
        toggleButton.setText(title)
        toggleButton.toggled.connect(eventHandler)

        return toggleButton

    
    
    def add_widgets_to_layout(self, layout, *args):
        for i , args in enumerate(args):
            layout.addWidget(args)

        return layout


    #event handlers
    def onCameraSpeedSelect(self, index):

        if index == 0:
            self.glWidget.camera_step_x = 0.1
            self.glWidget.camera_step_y= 0.1
            self.glWidget.zoom_step = 0.1

        elif index == 1:
            self.glWidget.camera_step_x = 0.01
            self.glWidget.camera_step_y= 0.01
            self.glWidget.zoom_step = 0.01
        
        elif index == 2:
            self.glWidget.camera_step_x = 0.001
            self.glWidget.camera_step_y= 0.001
            self.glWidget.zoom_step = 0.01
            
        
        self.glWidget.update()
    
    def onToggleLabels(self, checked):
        self.glWidget.show_labels = checked
        self.glWidget.update()

    def onToggleLines(self, checked):
        self.glWidget.show_lines = checked
        self.glWidget.update()

    def onToggleRecord(self, checked):
        self.recording_dock.show()
        self.glWidget.record_point = checked
        self.glWidget.update()

    def onResetToggle(self, checked):

        if not self.glWidget.record_point:

            self.recording_dock.hide()

            if len(self.glWidget.recorded_points) > 0:
                self.glWidget.prediction_curves.append(set(self.glWidget.recorded_points))

            self.glWidget.recorded_points.clear()
            self.glWidget.recording_dock_text.clear()
            print(self.glWidget.prediction_curves)
            self.glWidget.update()
    
    def onOpenRecordings(self, checked):
        pass
    #utility func
    def set_coords(self, file1, file2):
        
        x_points = read_txt(file1)
        y_points = read_txt(file2)
        coords = []

        for i, x in enumerate(x_points):
            coords.append([x, y_points[i]])

        self.glWidget.points = coords

        self.glWidget.update()

if __name__ == "__main__":
    
    glutInit()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.set_coords("GetX.TXT", "GetY.TXT")
    window.resize(1000,1000)
    window.show()
    sys.exit(app.exec_())
