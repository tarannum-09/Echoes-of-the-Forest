from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

class Ghost:
    def __init__(self):
        # Position (Right of Gate), (Gate line), (Standing on floor)
        # z is 25 because the body height is 50, and cubes draw from the center.
        self.pos = [90, 100, 25] 
        self.base_speed = 0.8
        self.has_woken = False # is statue right now
        self.quadric = gluNewQuadric()

    def update(self, player_pos, player_front, is_day):
        # If night comes, the ghost wakes up forever

        if not is_day:
            self.has_woken = True

        if not self.has_woken:
            return

        # CHASE LOGIC (Only runs if woken)
        dx = self.pos[0] - player_pos[0]
        dy = self.pos[1] - player_pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist == 0: 
            return 

        # Vector pointing from player to ghost
        vec_to_ghost_x = dx / dist
        vec_to_ghost_y = dy / dist
        
        # Check if player is looking at the ghost
        view_dot = (player_front[0] * vec_to_ghost_x) + (player_front[1] * vec_to_ghost_y)
        is_seen = view_dot > 0.65
        
        if is_seen:
            current_speed = 0 # Freeze when looked at
        else:
            # Move towards player
            # It's faster at night (1.6 vs 0.8)
            current_speed = self.base_speed * (2.0 if not is_day else 1.0)

        # Move if far enough away
        if dist > 30 and current_speed > 0:
            self.pos[0] -= vec_to_ghost_x * current_speed
            self.pos[1] -= vec_to_ghost_y * current_speed

        # No hover animation. It stays on the ground 

    def draw(self):
        glPushMatrix()
        # Draw at current position
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        
        # Color: Stone Grey (Looks like a statue)
        glColor3f(0.5, 0.55, 0.6) 

        # 1. BODY 
        glPushMatrix()
        glScalef(12, 12, 50) # Width 12, Height 50
        glutSolidCube(1)
        glPopMatrix()
        
        # 2. HEAD 
        glPushMatrix()
        glTranslatef(0, 0, 32) # top of body
        glRotatef(15, 1, 0, 0) # head tilted down
        glScalef(10, 10, 12)   
        glutSolidCube(1)
        glPopMatrix()
        
        # 3. ARMS 
        # Left
        glPushMatrix()
        glTranslatef(-8, 0, 10)
        glScalef(4, 4, 36)     
        glutSolidCube(1)
        glPopMatrix()
        
        # Right
        glPushMatrix()
        glTranslatef(8, 0, 10)
        glScalef(4, 4, 36)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()