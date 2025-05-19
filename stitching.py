from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QOpenGLWidget, 
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt
import numpy as np 
from OpenGL.GL import *
from OpenGL.GLUT import glutInit, glutBitmapCharacter
from OpenGL.GLU import *
import sys

class GLWidget(QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.points = np.array([
            [0.0,0.0],
            [0.0,0.5],
            [0.0,-0.5],
            [0.5,0.0],
            [0.5,0.5],
            [0.5,-0.5],
            [-0.5,0.0],
            [-0.5,0.5],
            [-0.5,-0.5],
        ], dtype=np.float32)

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_step = 0.1
        self.view_size = 1.0
        self.zoom = 1.0
        self.zoom_step = 0.1
        self.show_labels = False
        self.show_lines = False

        #Allows openGl widget to be focused
        #without it, only focuses on GUI 
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        


    def initializeGL(self):
        glClearColor(0,0,0,1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #update ortho, simulates camera movement with arrow keys 
        variable_size = self.view_size * self.zoom
        gluOrtho2D(-variable_size + self.camera_x, variable_size + self.camera_x, -variable_size + self.camera_y, variable_size + self.camera_y)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glPointSize(5.0)
        glColor3f(1.0, 1.0, 1.0)

        #draw point array
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.points)
        glDrawArrays(GL_POINTS, 0, len(self.points))
        glDisableClientState(GL_VERTEX_ARRAY)

        

        # draw labels
        if self.show_labels:
            glColor3f(1.0, 1.0, 1.0)
            for x, y in self.points:
                label = f"({x:.1f},{y:.1f})"
                self.drawText2D(x - 0.05, y - 0.07, label)


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
       


        glFlush()
       

    def drawText2D(self, x,y, string):
        glRasterPos(x,y)

        for ch in string:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))


    def keyPressEvent(self, event):
        
        key = event.key()

        if key == Qt.Key.Key_Left:
            self.camera_x += self.camera_step
        elif key == Qt.Key.Key_Right:
            self.camera_x -= self.camera_step
        elif key == Qt.Key.Key_Up:
            self.camera_y -= self.camera_step
        elif key == Qt.Key.Key_Down:
            self.camera_y += self.camera_step
        elif key == Qt.Key.Key_Plus:
            self.zoom = max(0.1, self.zoom - self.zoom_step)
        elif key == Qt.Key.Key_Minus:
            self.zoom += self.zoom_step
        

        self.update()



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEst going")

        #Create dropdown list 
        self.combo = QComboBox(self)
        self.combo.addItems(["Camera Course", "Camera Fine", "Camera Super Fine"])
        self.combo.currentIndexChanged.connect(self.cameraSpeedSelect)

        
        #Create toggleable button and attaches event handler
        self.coordsToggle = QPushButton(self)
        self.coordsToggle.setCheckable(True)
        self.coordsToggle.setText("Toggle Coordinates")
        self.coordsToggle.toggled.connect(self.onToggleLabels)

        self.linesToggle = QPushButton(self)
        self.linesToggle.setCheckable(True)
        self.linesToggle.setText("Toggle Lines")
        self.linesToggle.toggled.connect(self.onToggleLines)

        #add openGL widget
        self.glWidget = GLWidget(self)

        #horizontal layout
        hLayout1 = QHBoxLayout()
        hLayout1.addWidget(self.combo)
        hLayout1.addWidget(self.coordsToggle)

        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(self.linesToggle)

        #main layout is vertical
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(hLayout1)
        mainLayout.addLayout(hLayout2)
        mainLayout.addWidget(self.glWidget)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    #event handlers
    def cameraSpeedSelect(self, index):

        if index == 0:
            self.glWidget.camera_step = 0.1
            self.glWidget.zoom_step = 0.1

        elif index == 1:
            self.glWidget.camera_step = 0.01
            self.glWidget.zoom_step = 0.01
        
        elif index == 2:
            self.glWidget.camera_step = 0.001
            self.glWidget.zoom_step = 0.01
            
        
        self.glWidget.update()
    
    def onToggleLabels(self, checked):
        self.glWidget.show_labels = checked
        self.glWidget.update()

    def onToggleLines(self, checked):
        self.glWidget.show_lines = checked
        self.glWidget.update()

if __name__ == "__main__":
    
    glutInit()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600,600)
    window.show()
    sys.exit(app.exec_())
