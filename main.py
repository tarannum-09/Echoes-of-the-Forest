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