from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

class Child:
    def __init__(self, hiding_x, hiding_y):
        # Final destination (where you find them in the maze)
        self.hiding_pos = [hiding_x, hiding_y, 0]
        
        # Initial position (At the Gate)
        self.pos = [0, -150, 0] 
        
        # States: WAITING, RUNNING, HIDDEN, FOLLOWING
        self.state = "WAITING"
        self.run_speed = 4.0
        self.fade_dist = 0
        
        # Bobbing animation frame
        self.frame = 0

    def draw_cube_manual(self):
        # Draws a 1x1x1 cube using GL_QUADS (No GLUT)
        glBegin(GL_QUADS)
        # Front
        glVertex3f(-0.5, -0.5, 0.5); glVertex3f( 0.5, -0.5, 0.5)
        glVertex3f( 0.5,  0.5, 0.5); glVertex3f(-0.5,  0.5, 0.5)
        # Back
        glVertex3f(-0.5, -0.5, -0.5); glVertex3f(-0.5,  0.5, -0.5)
        glVertex3f( 0.5,  0.5, -0.5); glVertex3f( 0.5, -0.5, -0.5)
        # Left
        glVertex3f(-0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5,  0.5)
        glVertex3f(-0.5,  0.5,  0.5); glVertex3f(-0.5,  0.5, -0.5)
        # Right
        glVertex3f( 0.5, -0.5, -0.5); glVertex3f( 0.5,  0.5, -0.5)
        glVertex3f( 0.5,  0.5,  0.5); glVertex3f( 0.5, -0.5,  0.5)
        # Top
        glVertex3f(-0.5,  0.5, -0.5); glVertex3f(-0.5,  0.5,  0.5)
        glVertex3f( 0.5,  0.5,  0.5); glVertex3f( 0.5,  0.5, -0.5)
        # Bottom
        glVertex3f(-0.5, -0.5, -0.5); glVertex3f( 0.5, -0.5, -0.5)
        glVertex3f( 0.5, -0.5,  0.5); glVertex3f(-0.5, -0.5,  0.5)
        glEnd()

    def draw_sphere_manual(self, radius):
        """ Draws a sphere using GL_POINTS (No GLU/GLUT) """
        glBegin(GL_POINTS)
        for i in range(0, 180, 10): # Latitude
            lat = math.radians(i)
            for j in range(0, 360, 10): # Longitude
                lon = math.radians(j)
                x = radius * math.sin(lat) * math.cos(lon)
                y = radius * math.sin(lat) * math.sin(lon)
                z = radius * math.cos(lat)
                glVertex3f(x, y, z)
        glEnd()

    def trigger_run(self):
        if self.state == "WAITING":
            self.state = "RUNNING"
            print("The child sees you and runs into the forest!")

    def start_following(self):
        # Allow following if hidden (found in maze) or already waiting in forest
        if self.state == "HIDDEN" or self.state == "WAITING_IN_FOREST":
            self.state = "FOLLOWING"
            print("The child is following you!")

    def update(self, player_pos):
        self.frame += 1
        
        # RUNNING (Away from player at start)
        if self.state == "RUNNING":
            self.pos[1] += self.run_speed # Run North
            self.fade_dist += 1
            
            # After running for a bit, teleport to hiding spot
            if self.fade_dist > 100: 
                self.state = "HIDDEN"
                self.pos = self.hiding_pos[:] 

        # HIDDEN (Waiting in the maze)
        elif self.state == "HIDDEN":
            # Just bob up and down to be visible
            self.pos[2] = math.sin(self.frame * 0.1) * 2

        # FOLLOWING (Towards player after found) 
        elif self.state == "FOLLOWING":
            self.pos[2] = math.sin(self.frame * 0.1) * 2
            
            dx = player_pos[0] - self.pos[0]
            dy = player_pos[1] - self.pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Move towards player if far away, stop if close (distance > 40)
            if dist > 40:
                speed = 2.5 
                dir_x = dx / dist
                dir_y = dy / dist
                self.pos[0] += dir_x * speed
                self.pos[1] += dir_y * speed

    def draw(self, player_pos=None):
        # Flicker effect while running away to simulate vanishing
        if self.state == "RUNNING" and self.fade_dist > 80:
            if (self.fade_dist // 5) % 2 == 0: return 

        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        
        # If following or hiding, rotate to face player
        if player_pos and self.state in ["HIDDEN", "FOLLOWING"]:
             to_player_x = player_pos[0] - self.pos[0]
             to_player_y = player_pos[1] - self.pos[1]
             angle = math.degrees(math.atan2(to_player_y, to_player_x))
             glRotatef(angle + 90, 0, 0, 1)

        # 1. Yellow Raincoat Body 
        glColor3f(1.0, 0.9, 0.0) 
        glPushMatrix()
        glTranslatef(0, 0, 12)
        glScalef(4, 4, 12) 
        self.draw_cube_manual() 
        glPopMatrix()

        # 2. Head 
        glColor3f(0.9, 0.8, 0.7) 
        glPushMatrix()
        glTranslatef(0, 0, 21)
        self.draw_sphere_manual(3.5) 
        glPopMatrix()

        # 3. Legs 
        glColor3f(0.2, 0.2, 0.2) 
        # Leg 1
        glPushMatrix()
        glTranslatef(-1.5, 0, 6)
        glScalef(1.5, 1.5, 12)
        self.draw_cube_manual()
        glPopMatrix()
        # Leg 2
        glPushMatrix()
        glTranslatef(1.5, 0, 6)
        glScalef(1.5, 1.5, 12)
        self.draw_cube_manual()
        glPopMatrix()

        glPopMatrix()