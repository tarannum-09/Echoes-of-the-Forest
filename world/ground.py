from OpenGL.GL import *

class Ground:
    def __init__(self, width=6000, length=6000):
        self.width = width
        self.length = length

    def draw(self, brightness, player_pos):

        g_val = 0.15 * brightness
        glColor3f(0.05, g_val, 0.05)
        
        glBegin(GL_QUADS)
        glVertex3f(-self.width, -self.length, 0)
        glVertex3f(self.width, -self.length, 0)
        glVertex3f(self.width, self.length, 0)
        glVertex3f(-self.width, self.length, 0)
        glEnd()