import math
from OpenGL.GLU import *

class Camera:
    def __init__(self):
        self.pos = [0.0, -400.0, 50.0] 
        self.yaw = 90.0   # direction angle
        self.pitch = 0.0  # look angle

        # Vectors
        self.front = [0.0, 1.0, 0.0]
        self.up = [0.0, 0.0, 1.0]

    def update_vectors(self):
        # converting spherical to cartesian for rotation
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        self.front[0] = math.cos(rad_yaw) * math.cos(rad_pitch)
        self.front[1] = math.sin(rad_yaw) * math.cos(rad_pitch)
        self.front[2] = math.sin(rad_pitch)

    def apply(self):
        gluLookAt(self.pos[0], self.pos[1], self.pos[2],
                  self.pos[0] + self.front[0], 
                  self.pos[1] + self.front[1], 
                  self.pos[2] + self.front[2],
                  0, 0, 1)