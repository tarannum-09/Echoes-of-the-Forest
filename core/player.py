import math
from OpenGL.GLU import gluLookAt

class Player:
    def __init__(self):
        # Position
        self.pos = [0.0, -200.0, 40.0] 
        self.yaw = 90.0   
        self.front = [0.0, 0.0, 0.0]
        
        # --- RESTORED: FLASHLIGHT ATTRIBUTE ---
        self.flashlight_on = False # Start with it off (press 'F' to toggle)
        # --------------------------------------

        # --- PHYSICS VARIABLES ---
        self.velocity = [0.0, 0.0] 
        self.ang_velocity = 0.0    
        self.accel = 1.5           
        self.max_speed = 6.0       
        self.friction = 0.85       
        self.turn_speed = 3.0      

        self.update_camera_vectors()

    def update_camera_vectors(self):
        rad_yaw = math.radians(self.yaw)
        self.front[0] = math.cos(rad_yaw)
        self.front[1] = math.sin(rad_yaw)
        self.front[2] = 0 

    def update_camera(self):
        gluLookAt(self.pos[0], self.pos[1], self.pos[2],  
                  self.pos[0] + self.front[0],            
                  self.pos[1] + self.front[1],            
                  self.pos[2] + self.front[2],            
                  0, 0, 1)                                

    def update_physics(self, forest_map):
        # Friction
        self.velocity[0] *= self.friction
        self.velocity[1] *= self.friction
        self.ang_velocity *= self.friction

        if abs(self.velocity[0]) < 0.1: self.velocity[0] = 0
        if abs(self.velocity[1]) < 0.1: self.velocity[1] = 0
        if abs(self.ang_velocity) < 0.1: self.ang_velocity = 0

        # Rotation
        self.yaw += self.ang_velocity
        self.update_camera_vectors()

        # Movement
        next_x = self.pos[0] + self.velocity[0]
        next_y = self.pos[1] + self.velocity[1]

        if not forest_map.check_collision(next_x, next_y):
            self.pos[0] = next_x
            self.pos[1] = next_y
        else:
            self.velocity = [0.0, 0.0]

    def add_movement(self, direction):
        rad = math.radians(self.yaw)
        dx = 0; dy = 0
        if direction == 'forward':
            dx = math.cos(rad) * self.accel
            dy = math.sin(rad) * self.accel
        elif direction == 'backward':
            dx = -math.cos(rad) * self.accel
            dy = -math.sin(rad) * self.accel
        self.velocity[0] += dx
        self.velocity[1] += dy
        
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        if speed > self.max_speed:
            ratio = self.max_speed / speed
            self.velocity[0] *= ratio
            self.velocity[1] *= ratio

    def add_rotation(self, direction):
        if direction == 'left':
            self.ang_velocity += self.turn_speed * 0.5
        elif direction == 'right':
            self.ang_velocity -= self.turn_speed * 0.5