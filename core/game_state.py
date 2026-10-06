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