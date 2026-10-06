# camera.py
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
        

#game_state.py

class GameState:
    def __init__(self):
        self.current_state = "INTRO" # Options: INTRO, PLAYING, GAME_OVER

        self.current_story_text = ""
        
        # Intro Sequence
        self.intro_timer = 0
        self.intro_phase = 0
        self.intro_lines = [
            "October 31st, 1987.",
            "My daughter, Lily...",
            "She ran into the Silent Forest.",
            "They say spirits wander there.",
            "I have to find her.",
            "PRESS SPACE TO ENTER"
        ]

        self.visible_lines = []

    def toggle_pause(self):
        if self.current_state == "PLAYING":
            self.current_state = "PAUSED"
        elif self.current_state == "PAUSED":
            self.current_state = "PLAYING"

    def start_game(self):
        self.current_state = "PLAYING"

    def update_intro(self):
        if self.current_state != "INTRO":
            return

        self.intro_timer += 1
        
        #  new line every 200 frames 
        if self.intro_timer % 200 == 0:
            if self.intro_phase < len(self.intro_lines):
                self.visible_lines.append(self.intro_lines[self.intro_phase])
                self.intro_phase += 1

# input.py

from OpenGL.GLUT import *

class InputHandler:
    def __init__(self):
        self.keys = {}
        self.l_pressed = False 

    def keyboardListener(self, key, x, y):
        # Store key state
        self.keys[key] = True

    def keyboardUpListener(self, key, x, y):
        self.keys[key] = False

    def process_input(self, player, forest):
        
        if self.keys.get(b'w'):
            player.move('forward', forest)
                
        if self.keys.get(b's'):
            player.move('backward', forest)

        if self.keys.get(b'a'):
            player.rotate('left')
            player.update_camera_vectors() 
            
        if self.keys.get(b'd'):
            player.rotate('right')
            player.update_camera_vectors() 
        
        else:
            self.l_pressed = False


# player.py

import math
from OpenGL.GLU import gluLookAt

class Player:
    def __init__(self):
        # Position
        self.pos = [0.0, -200.0, 40.0] 
        self.yaw = 90.0   
        self.front = [0.0, 0.0, 0.0]

        self.flashlight_on = False 

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


# clues.py

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

class Clue:
    def __init__(self, x, y, text, clue_type="GENERIC"):
        self.pos = [x, y, 2] 
        self.text = text
        self.clue_type = clue_type
        self.triggered = False
        self.radius = 80 
        self.quadric = gluNewQuadric()
    
    def check_trigger(self, player_pos):
        if self.triggered:
            return False
        
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.radius:
            self.triggered = True
            return True
        return False
    
    def draw(self):
        if self.triggered: return
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        
        if self.clue_type == "SHOE":
            glColor3f(0.5, 0.3, 0.1)
            glScalef(6, 3, 2)
            glutSolidCube(1)
        elif self.clue_type == "TOY":
            glColor3f(1.0, 0.2, 0.2) 
            gluSphere(self.quadric, 5, 10, 10)
        elif self.clue_type == "NOTE":
            glColor3f(1.0, 1.0, 1.0)
            glScalef(8, 0.5, 6)
            glutSolidCube(1)
        elif self.clue_type == "CLOTH":
            glColor3f(0.7, 0.3, 0.8)
            glScalef(6, 6, 0.5)
            glutSolidCube(1)
        
        glPopMatrix()


class ClueManager:
    def __init__(self, game_state, path_coords):
        self.clues = []
        self.game_state = game_state
        self.display_timer = 0
        
        # We pass the full path_coords list from Forest
        self.create_path_clues(path_coords)
    
    def create_path_clues(self, path):
      
        
        descriptions = [
            ("A small shoe... she went this way.", "SHOE"),
            ("Her red ball. She dropped it running.", "TOY"),
            ("Small footprints in the mud.", "SHOE"),
            ("A piece of cloth caught on a branch.", "CLOTH"),
            ("A drawing she made... 'Help'.", "NOTE"),
            ("I hear sobbing just ahead!", "NOTE")
        ]
        
        num_clues = len(descriptions)
        path_len = len(path)
        
        # If path is too short, just place randoms 
        if path_len < 10:
            return 
            
        # We want to skip the first ~15% of the path so clues don't spawn at the gate
        start_index = int(path_len * 0.15)
        usable_path = path[start_index:]
        usable_len = len(usable_path)
        
        for i in range(num_clues):
            # Calculate index in the usable path
            # i=0 -> beginning of usable path
            # i=5 -> near the end
            idx = int((i / num_clues) * usable_len)
            
            idx = min(idx, usable_len - 1)
            
          
            pos = usable_path[idx]
            
            text, c_type = descriptions[i]
            
            # Create clue at this exact path location
            self.clues.append(Clue(pos[0], pos[1], text, c_type))
    
    def update(self, player):
        for clue in self.clues:
            if clue.check_trigger(player.pos):
                self.game_state.current_story_text = clue.text
                self.display_timer = 300 
                break 
        
        if self.display_timer > 0:
            self.display_timer -= 1
            if self.display_timer == 0:
                self.game_state.current_story_text = ""
    
    def draw(self):
        for clue in self.clues:
            clue.draw()


# story.py

INTRO_LINES = [
    "You looked away for just a second...",
    "",
    "That was all it took.",
    "",
    "Now the forest is too quiet.",
    "But you are not alone.",
    "",
    "Don't let the guilt catch you.",
    "",
    "Find him.",
    "",
    "[ PRESS SPACE TO START ]"
]


# hud.py

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



# menu.py

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
    

# text.py

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


# child.py

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


# environment.py

import time
import math

class Environment:
    def __init__(self):
        self.start_time = time.time()
        

        self.day_duration = 120.0 # Seconds for a full Day/Night cycle
        self.day_count = 1
        
        self.brightness = 1.0
        self.is_day = True
        

        self.timer = 0 


    def update(self):
        # 1. Calculate Time Passed
        elapsed = time.time() - self.start_time
        
        # 2. Calculate current Day Count 
        self.day_count = int(1 + (elapsed / self.day_duration))
        
        # 3. Calculate Brightness Cycle (Sine Wave)
        cycle_progress = (elapsed % self.day_duration) / self.day_duration
        angle = cycle_progress * 2 * math.pi
        

        raw_val = math.cos(angle) # Range: -1 to 1
        
        # Normalize to 0.0 - 1.0 range
        normalized = (raw_val + 1) / 2 
        
        # Scale to our brightness range (0.2 to 1.0)
        self.brightness = 0.2 + (0.8 * normalized)
        
        # 4. Determine Day/Night State
        self.is_day = self.brightness > 0.45
        
        # Update timer variable for the HUD
        # This gives a number (0 to 120) representing seconds in the cycle
        self.timer = int(elapsed % self.day_duration)
        # ----------------------------------------------

    def get_sky_color(self):
        # Scale sky color based on brightness
        intensity = max(0.0, (self.brightness - 0.2) / 0.8)
        
        # Light Blue (Day) to Black (Night)
        r = 0.4 * intensity
        g = 0.7 * intensity
        b = 1.0 * intensity
        
        return (r, g, b, 1.0)
    

# forest.py

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import math
import collections

class Forest:
    def __init__(self):
        self.CELL_SIZE = 120
        self.GRID_W = 40 
        self.GRID_H = 40
        self.MAX_VIEW_DIST = 1400 
        self.FADE_START = 500     

        self.cheat_mode = False
        
        self.map = [[1 for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        self.tree_data = [[None for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        
        print("Generating Forest Maze...")
        start_x = self.GRID_W // 2
        self.generate_maze_iterative(start_x, 0)
        self.generate_details()
        self.clear_entrance()
        
        self.exit_x, self.exit_y, self.path_traces = self.find_path_with_traces(start_x, 0, steps=40)
        print(f"Child hidden deep in forest at: {self.exit_x}, {self.exit_y}")

        self.fireflies = []
        for _ in range(100):
            self.fireflies.append([random.randint(-1000,1000), random.randint(0,2000), random.randint(20,80), 0])

        self.gate_y = 100
        self.quadric = gluNewQuadric()

    def generate_maze_iterative(self, sx, sy):
        stack = [(sx, sy)]
        self.map[sy][sx] = 0
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        while stack:
            cx, cy = stack[-1]
            random.shuffle(dirs)
            found = False
            for dx, dy in dirs:
                nx, ny = cx + dx*2, cy + dy*2
                if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                    if self.map[ny][nx] == 1:
                        self.map[cy+dy][cx+dx] = 0
                        self.map[ny][nx] = 0
                        stack.append((nx, ny))
                        found = True
                        break
            if not found: 
                stack.pop()

    def find_path_with_traces(self, start_x, start_y, steps=40):
        q = collections.deque([(start_x, start_y)])
        came_from = {(start_x, start_y): None} 
        last_valid = (start_x, start_y)
        while q:
            cx, cy = q.popleft()
            dist = abs(cx - start_x) + abs(cy - start_y)
            if dist >= steps:
                last_valid = (cx, cy); break
            last_valid = (cx, cy)
            neighbors = [(0,1), (0,-1), (1,0), (-1,0)]
            random.shuffle(neighbors)
            for dx, dy in neighbors:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                    if self.map[ny][nx] == 0 and (nx, ny) not in came_from:
                        came_from[(nx, ny)] = (cx, cy)
                        q.append((nx, ny))
        path_coords = []
        curr = last_valid
        while curr:
            off_x = -(self.GRID_W * self.CELL_SIZE) / 2
            off_y = -200
            wx = off_x + curr[0] * self.CELL_SIZE
            wy = off_y + curr[1] * self.CELL_SIZE
            path_coords.append((wx, wy))
            curr = came_from[curr]
        return path_coords[0][0], path_coords[0][1], path_coords

    def generate_details(self):
        for r in range(self.GRID_H):
            for c in range(self.GRID_W):
                if self.map[r][c] == 1: self.tree_data[r][c] = (random.uniform(1.2, 1.8), random.uniform(0, 360))

    def clear_entrance(self):
        mid = self.GRID_W // 2
        for r in range(0, 6):
            for c in range(mid-2, mid+3):
                if 0 <= c < self.GRID_W: self.map[r][c] = 0

    def animate_fireflies(self):
        for f in self.fireflies:
            f[2] += math.sin(f[3]) * 0.2
            f[3] += 0.05
            f[0] += math.sin(f[3]*0.5) * 0.5

    # KEY LIGHTING LOGIC 
    def get_lit_color(self, base_col, obj_x, obj_y, dist, env_brightness, player):
        # Calculating color based on distance AND flashlight
        final_brightness = env_brightness

        # FLASHLIGHT MATH
        if player.flashlight_on and dist < 600: # Range
            # vector for player to obj
            to_obj_x = obj_x - player.pos[0]
            to_obj_y = obj_y - player.pos[1]
            
            # Normalize vector
            d = math.sqrt(to_obj_x**2 + to_obj_y**2)
            if d > 0:
                to_obj_x /= d
                to_obj_y /= d
                
                # Dot product (compare direction vs look direction) If dot is close to 1.0, object is directly in front

                dot = to_obj_x * player.front[0] + to_obj_y * player.front[1]
                
                # Cone check 
                if dot > 0.85: 
                    intensity = (dot - 0.85) / 0.15 # Smooth edge
                    final_brightness += intensity * 0.8 # Boost brightness
        
        # Clamp brightness 
        final_brightness = min(1.0, final_brightness)
        
        # Distance Fade 
        if dist > self.MAX_VIEW_DIST: return (0,0,0)
        
        r, g, b = [c * final_brightness for c in base_col]
        
        if dist > self.FADE_START:
            vis = 1.0 - ((dist - self.FADE_START) / (self.MAX_VIEW_DIST - self.FADE_START))
            r *= vis
            g *= vis
            b *= vis
            
        return (r, g, b)

    def draw_scratched_text(self, text):
        letters = {'S':[(1,2,0,2),(0,2,0,1),(0,1,1,1),(1,1,1,0),(1,0,0,0)],'I':[(0.5,2,0.5,0),(0,2,1,2),(0,0,1,0)],'L':[(0,2,0,0),(0,0,1,0)],'E':[(1,2,0,2),(0,2,0,0),(0,0,1,0),(0,1,0.8,1)],'N':[(0,0,0,2),(0,2,1,0),(1,0,1,2)],'T':[(0.5,2,0.5,0),(0,2,1,2)],'F':[(1,2,0,2),(0,2,0,0),(0,1,0.8,1)],'O':[(0,0,0,2),(0,2,1,2),(1,2,1,0),(1,0,0,0)],'R':[(0,0,0,2),(0,2,1,2),(1,2,1,1),(1,1,0,1),(0,1,1,0)],' ':[]}
        glLineWidth(3.0)
        glBegin(GL_LINES)
        for i, char in enumerate(text):
            if char in letters:
                off_x = i*1.5; [glVertex3f(l[0]+off_x,0,l[1],) or glVertex3f(l[2]+off_x,0,l[3]) for l in letters[char]]
        glEnd()
        glLineWidth(1.0)

    def draw_gate(self, brightness, px, py):
        dist = math.sqrt(px**2 + (self.gate_y - py)**2)
        r,g,b = [c*brightness for c in (0.45, 0.3, 0.15)]
        glColor3f(r,g,b)
        for x in [-60, 60]: 
            glPushMatrix(); glTranslatef(x, self.gate_y, 0); glScalef(12, 12, 100); glutSolidCube(1); glPopMatrix()
            glPushMatrix(); glTranslatef(0, self.gate_y, 60); glScalef(160, 10, 25); glutSolidCube(1); glPopMatrix()
            glPushMatrix(); glTranslatef(-65, self.gate_y - 6, 52); glScalef(6, 1, 6); glColor3f(0.9*brightness, 0.9*brightness, 0.8*brightness); self.draw_scratched_text("SILENT FOREST"); glPopMatrix()

    def draw_tree(self, x, y, col, s):
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(s, s, s)
        glColor3f(*col) # Trunk Color
        gluCylinder(self.quadric, 10, 8, 40, 8, 1)
        
        # Leaves
        leaf_col = (col[0]*0.2, col[1]*1.5, col[2]*0.2)
        glColor3f(*leaf_col)
        for h, rad in [(30, 45), (50, 40), (70, 30)]:
            glPushMatrix(); glTranslatef(0, 0, h); gluCylinder(self.quadric, rad, 0, 40, 8, 1); glPopMatrix()
        glPopMatrix()

    def draw(self, brightness, player):
        px, py = player.pos[0], player.pos[1]
        self.draw_gate(brightness, px, py)

        # Fireflies
        glPointSize(3); glBegin(GL_POINTS)
        for f in self.fireflies:
            d = math.sqrt((f[0]-px)**2 + (f[1]-py)**2)
            if d < self.MAX_VIEW_DIST: glColor3f(1.0, 1.0, 0.0); glVertex3f(f[0], f[1], f[2])
        glEnd()

        # Blood Traces
        if self.cheat_mode:
            glBegin(GL_QUADS)
            for tx, ty in self.path_traces:
                dist = math.sqrt((tx-px)**2 + (ty-py)**2)
                if dist < 450: 
                    # Flashlight applies here
                    col = self.get_lit_color((0.8, 0.0, 0.0), tx, ty, dist, brightness, player)
                    glColor3f(*col)
                    glVertex3f(tx-4, ty-4, 1); glVertex3f(tx+4, ty-4, 1); glVertex3f(tx+4, ty+4, 1); glVertex3f(tx-4, ty+4, 1)
            glEnd()

        off_x = -(self.GRID_W * self.CELL_SIZE) / 2
        off_y = -200
        p_col = int((px - off_x) / self.CELL_SIZE)
        p_row = int((py - off_y) / self.CELL_SIZE)
        rad = 14 
        min_r, max_r = max(0, p_row-rad), min(self.GRID_H, p_row+rad)
        min_c, max_c = max(0, p_col-rad), min(self.GRID_W, p_col+rad)

        for r in range(min_r, max_r):
            for c in range(min_c, max_c):
                wx = off_x + c*self.CELL_SIZE
                wy = off_y + r*self.CELL_SIZE
                dist = math.sqrt((wx-px)**2 + (wy-py)**2)
                if dist > self.MAX_VIEW_DIST: 
                    continue

                # calculating Color with Flashlight Logic
                if self.map[r][c] == 1:
                    if self.tree_data[r][c]:
                        base = (0.25, 0.15, 0.1)
                        col = self.get_lit_color(base, wx, wy, dist, brightness, player)
                        self.draw_tree(wx, wy, col, self.tree_data[r][c][0])
                else:
                    base = (0.2, 0.18, 0.15) 
                    col = self.get_lit_color(base, wx, wy, dist, brightness, player)
                    glColor3f(*col)
                    glPushMatrix(); glTranslatef(wx, wy, 0); sz = self.CELL_SIZE / 2
                    glBegin(GL_QUADS)
                    glVertex3f(-sz, -sz, 0.1) 
                    glVertex3f(sz, -sz, 0.1)
                    glVertex3f(sz, sz, 0.1)
                    glVertex3f(-sz, sz, 0.1)
                    glEnd()
                    glPopMatrix()
    
    def check_collision(self, x, y):
        if 90 < y < 110 and ((-70 < x < -50) or (50 < x < 70)): return True
        off_x = -(self.GRID_W * self.CELL_SIZE) / 2
        off_y = -200
        c = int((x - off_x + self.CELL_SIZE/2) / self.CELL_SIZE)
        r = int((y - off_y + self.CELL_SIZE/2) / self.CELL_SIZE)
        if c < 0 or c >= self.GRID_W or r < 0 or r >= self.GRID_H:
             if r < 0 and -100 < x < 100: 
                 return False
             return True
        return self.map[r][c] == 1
    

# ghost.py

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


# ground.py

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


# main.py

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math 
import sys 

from core.player import Player
from core.input import InputHandler
from core.game_state import GameState
from world.forest import Forest
from world.ground import Ground
from world.environment import Environment
from world.ghost import Ghost
from world.child import Child 
from ui.text import TextRenderer
from ui.hud import HUD
from data.clues import ClueManager 
from ui.menu import Menu

state_manager = None
text_renderer = None
player = None
input_handler = None
forest = None
ground = None
env = None
ghost = None
hud = None
child = None
clue_manager = None 
menu = None

def init_game_objects():
    global state_manager, text_renderer, player, forest, ground, env, ghost, hud, child, clue_manager, menu

    print("Initializing World...")
    if state_manager is None: state_manager = GameState()
    
    text_renderer = TextRenderer()
    player = Player()
    env = Environment()
    ground = Ground()
    hud = HUD()
    forest = Forest()
    ghost = Ghost()
    child = Child(forest.exit_x, forest.exit_y)
    clue_manager = ClueManager(state_manager, forest.path_traces)
    
    if menu is None: menu = Menu()

def draw_end_screen(title, subtitle, color):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600) 
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    glColor3f(*color) 
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(800, 0); glVertex2f(800, 600); glVertex2f(0, 600)
    glEnd()
    
    text_renderer.draw_text(350, 350, title, 1, 1, 1)
    text_renderer.draw_text(280, 300, subtitle, 1, 1, 1)
    text_renderer.draw_text(320, 250, "Press ESC to Exit", 1, 1, 1)
    
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def showScreen():
    global env, player, ghost, clue_manager, child, menu
    
    if state_manager.current_state == "GAME_OVER":
        draw_end_screen("GAME OVER", "The Spirit Has Taken You.", (0.5, 0.0, 0.0)); glutSwapBuffers(); return
    if state_manager.current_state == "GAME_WIN":
        draw_end_screen("ESCAPED", "You saved the child.", (0.0, 0.5, 0.2)); glutSwapBuffers(); return
    if state_manager.current_state == "INTRO":
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        text_renderer.draw_intro_sequence(800, 600, state_manager.visible_lines)
        glutSwapBuffers(); return

    # Draw 3D World 
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    player.update_camera()
    
    sky_r = 0.05 + (0.45 * env.brightness)
    sky_g = 0.05 + (0.65 * env.brightness)
    sky_b = 0.08 + (0.92 * env.brightness)
    glClearColor(sky_r, sky_g, sky_b, 1.0) 

    ground.draw(env.brightness, player.pos)
    forest.draw(env.brightness, player)
    child.draw(player.pos)
    clue_manager.draw() 
    ghost.draw()

    # Clear Depth for UI. this separates 3D world from 2D UI
  
    glClear(GL_DEPTH_BUFFER_BIT)

    # Draw UI / Menu 
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

    if state_manager.current_story_text:
        text_renderer.draw_text(50, 100, state_manager.current_story_text, 1, 1, 1)

    hud.draw_clock(env.day_count, env.is_day, env.timer)

    if not env.is_day:
        gx, gy = ghost.pos[0], ghost.pos[1]
        px, py = player.pos[0], player.pos[1]
        dist = math.sqrt((gx - px)**2 + (gy - py)**2)
        if dist < 800: 
            intensity = 1.0 - (dist / 800.0)
            hud.draw_danger_bar(max(0.0, min(1.0, intensity)))

    if state_manager.current_state == "PAUSED":
        menu.draw()

    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
    glutSwapBuffers()

def idle():
    global state_manager, child, clue_manager, ghost, player, env

    if state_manager.current_state == "INTRO":
        state_manager.update_intro()

    if state_manager.current_state == "PLAYING":
        env.update()
        player.update_physics(forest)
        clue_manager.update(player)
        ghost.update(player.pos, player.front, env.is_day)
        forest.animate_fireflies()
        child.update(player.pos) 
        
        px, py = player.pos[0], player.pos[1]
        
        # Run Away Logic
        dist_to_child_start = math.sqrt((px - 0)**2 + (py - (-150))**2)
        if dist_to_child_start < 250 and child.state == "WAITING":
            child.trigger_run()
            state_manager.current_story_text = "The child ran into the woods! Find her!"

        # Rescue Logic
        dist_to_child = math.sqrt((px - child.pos[0])**2 + (py - child.pos[1])**2)
        if child.state == "HIDDEN" and dist_to_child < 80:
            child.start_following()
            state_manager.current_story_text = "She is following you. Return to the Gate!"

        # Win Logic
        if child.state == "FOLLOWING" and math.sqrt((px - 0)**2 + (py - (-150))**2) < 150:
            state_manager.current_state = "GAME_WIN"

        # Game Over Logic
        if not (env.day_count == 1 and env.is_day):
            dist_ghost = math.sqrt((ghost.pos[0] - px)**2 + (ghost.pos[1] - py)**2)
            if dist_ghost < 50:
                state_manager.current_state = "GAME_OVER"
    
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global player, forest, state_manager
    
    if key == b'\x1b': 
        if state_manager.current_state == "PLAYING":
            state_manager.toggle_pause()
        elif state_manager.current_state == "PAUSED":
            state_manager.toggle_pause()
        else:
            print("Exiting...")
            sys.exit(0)
            
    elif state_manager.current_state == "INTRO":
        if key == b' ': state_manager.start_game()
    
    elif state_manager.current_state == "PLAYING":
        if key == b'c': 
            forest.cheat_mode = not forest.cheat_mode
            print(f"Cheat Mode: {forest.cheat_mode}")
        elif key == b'w': player.add_movement('forward')
        elif key == b's': player.add_movement('backward')
        elif key == b'a': player.add_rotation('left')
        elif key == b'd': player.add_rotation('right')
        elif key == b'f': player.flashlight_on = not player.flashlight_on

def mouseListener(button, state, x, y):
    global state_manager, menu
    
    if state_manager.current_state == "PAUSED" and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        action = menu.check_click(x, y)
        if action == "resume":
            state_manager.toggle_pause()
        elif action == "restart":
            print("Restarting Game...")
            init_game_objects()
            state_manager.current_state = "PLAYING"
        elif action == "exit":
            print("Exiting...")
            sys.exit(0)

def main():
    global state_manager, text_renderer, player, forest, ground, env, ghost, hud, child, clue_manager, menu

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Echoes of the Forest")
    glEnable(GL_DEPTH_TEST) 
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(60, 1.33, 0.1, 1500.0); glMatrixMode(GL_MODELVIEW)

    init_game_objects()

    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()

if __name__ == "__main__":
    main()