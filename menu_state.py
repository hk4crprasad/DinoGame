from enum import Enum

class GameMode(Enum):
    MENU = 0
    PLAYER = 1
    TRAIN_AI = 2
    PLAY_AI = 3

class MenuState:
    def __init__(self):
        self.current_mode = GameMode.MENU
        self.training_target_gen = 50
        self.player = None
        # Add GameMode to instance for easy access
        self.GameMode = GameMode

# Create and export the global state
state = MenuState()

# Make both GameMode and state available for import
__all__ = ['GameMode', 'state']
