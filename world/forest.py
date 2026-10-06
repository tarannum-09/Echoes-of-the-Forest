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