"""
Unlock condition.
Gets the state of the game, then checks for unlock.
"""
from abc import ABC, abstractmethod
from Frames.frame import Frame
from constants import R_ID

class UnlockCondition(Frame):

    class EventTypes:
        UNLOCK_ANIMATION_FINISHED = R_ID()

    def __init__(self):
        self._unlock_animation_playing = False

    def bind_events(self):
        self.clear_event_callbacks()

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        return self

    def render(self, screen):
        pass

    @abstractmethod
    def can_be_unlocked(self, gamestate):
        #should return True if yes,
        #False if no
        pass

    @abstractmethod
    def unlock(self, gamestate):
        #should apply the cost incurred, then start the animation
        pass
