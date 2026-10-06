from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class HUD:
    def draw_text(self, x, y, text):
        glColor3f(1, 1, 1)
        glRasterPos2f(x, y) 
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def draw_clock(self, day, is_day, timer):
        # 1. Background (Deep at Z = -0.5)
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex3f(650, 550, -0.5) 
        glVertex3f(780, 550, -0.5) 
        glVertex3f(780, 590, -0.5) 
        glVertex3f(650, 590, -0.5) 
        glEnd()

        # 2. Text (Front at Z = 0.0)
        time_str = f"Day {day}"
        if not is_day: 
            time_str += " (Night)"
        self.draw_text(660, 560, time_str)


    def draw_danger_bar(self, intensity):
        # Bar Dimensions
        x, y = 10, 560
        w, h = 200, 20

        # Background 
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(x, y, -0.5)
        glVertex3f(x + w, y, -0.5)
        glVertex3f(x + w, y + h, -0.5)
        glVertex3f(x, y + h, -0.5)
        glEnd()

        # Red Danger Fill 
        if intensity > 0:
            fill_width = w * intensity
            glColor3f(0.8, 0, 0) # Red
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0.0)
            glVertex3f(x + fill_width, y, 0.0)
            glVertex3f(x + fill_width, y + h, 0.0)
            glVertex3f(x, y + h, 0.0)
            glEnd()

        # Outline using GL_LINES 
        glColor3f(1, 1, 1)
        glLineWidth(2)
        glBegin(GL_LINES)
        
        # Bottom Line
        glVertex3f(x, y, 0.0)
        glVertex3f(x + w, y, 0.0)
        
        # Right Line
        glVertex3f(x + w, y, 0.0)
        glVertex3f(x + w, y + h, 0.0)
        
        # Top Line
        glVertex3f(x + w, y + h, 0.0)
        glVertex3f(x, y + h, 0.0)
        
        # Left Line
        glVertex3f(x, y + h, 0.0)
        glVertex3f(x, y, 0.0)
        
        glEnd()

        self.draw_text(x, y - 20, "DANGER")