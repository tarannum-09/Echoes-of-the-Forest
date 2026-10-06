from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class TextRenderer:
    def draw_text(self, x, y, text, r=1, g=1, b=1, font=GLUT_BITMAP_HELVETICA_18):
        glColor3f(r, g, b)
        glRasterPos2f(x, y) 
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def draw_intro_sequence(self, width, height, current_lines):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # 1. Draw Background (Black)
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(width, 0)
        glVertex2f(width, height)
        glVertex2f(0, height)
        glEnd()

       
        glClear(GL_DEPTH_BUFFER_BIT)

        # 3. Draw Text
        start_y = height / 2 + 100 
        line_spacing = 40
        
        if current_lines:
            for i, line in enumerate(current_lines):
                text_width = len(line) * 9
                x = (width - text_width) / 2
                y = start_y - (i * line_spacing)
                
                if "PRESS SPACE" in line.upper():
                    self.draw_text(x, y, line, 1, 0, 0)
                else:
                    self.draw_text(x, y, line, 1, 1, 1)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)