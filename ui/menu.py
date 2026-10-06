from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Menu:
    def __init__(self):
        # x, y, width, height, action_code, label
        self.buttons = [
            (300, 350, 200, 50, "resume", "RESUME"),
            (300, 280, 200, 50, "restart", "RESTART"),
            (300, 210, 200, 50, "exit", "EXIT")
        ]

    def draw_text(self, x, y, text):
        glColor3f(1, 1, 1) 
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def draw(self):

        self.draw_text(365, 450, "PAUSED")


        for bx, by, bw, bh, action, label in self.buttons:
            # Button Body (Dark Gray)
            glColor3f(0.2, 0.2, 0.2) 
            glBegin(GL_QUADS)
            glVertex2f(bx, by)
            glVertex2f(bx + bw, by)
            glVertex2f(bx + bw, by + bh)
            glVertex2f(bx, by + bh)
            glEnd()
            
            # Button Outline (Light Gray)
            glColor3f(0.7, 0.7, 0.7)
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            glVertex2f(bx, by)
            glVertex2f(bx+bw, by)
            glVertex2f(bx+bw, by+bh)
            glVertex2f(bx, by+bh)
            glEnd()

     
        glClear(GL_DEPTH_BUFFER_BIT)

        # 3. Draw ALL Button Text
        for bx, by, bw, bh, action, label in self.buttons:
            text_width = len(label) * 9 
            tx = bx + (bw - text_width) / 2
            ty = by + (bh / 2) - 5
            
            self.draw_text(tx, ty, label)

    def check_click(self, x, y):
        # Convert Mouse Y (Top-Left 0,0) to OpenGL Y (Bottom-Left 0,0)
        gl_y = 600 - y 
        
        for bx, by, bw, bh, action, label in self.buttons:
            if bx <= x <= bx + bw and by <= gl_y <= by + bh:
                return action
        return None