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