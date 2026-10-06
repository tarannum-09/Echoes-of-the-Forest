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