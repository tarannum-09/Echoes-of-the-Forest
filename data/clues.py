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