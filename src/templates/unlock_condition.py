"""
Unlock condition.
Gets the state of the game, then checks for unlock.
"""
from abc import ABC, abstractmethod
from Frames.frame import Frame
from constants import R_ID

class UnlockCondition:

    """
    This class defines the unlock procedures
    for the cards.
    """

    def __init__(self):
        pass



    @abstractmethod
    def can_be_unlocked(self, gamestate: object) -> bool:
        """
        Receives the gamestate, then returns
        True if the unlock condition is met, else False.
        """
        pass

    @abstractmethod
    def unlock(self, gamestate: object) -> bool:
        """
        Receives the current gamestate, then applies the changes
        to the gamestate necessary to unlock the card with this unlock condition.

        If the unlock condition is not met, this returns False.
        If the process was successful, this returns True.
        """
        pass
