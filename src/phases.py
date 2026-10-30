from __future__ import annotations
from typing import Any, Callable

from enum import Enum, auto
import pygame

class Phases(Enum):

    """
    Enum for phases in the current game.
    """
    ANY_PHASE = auto() #type for any phase.

    TRANSITION_PHASE = auto() #a phase in between two phases, for letting entites adjust accordingly

    START_OF_GAME = auto()
    START_OF_ROUND = auto()
    END_OF_ROUND = auto()
    BEFORE_BIOME_CARD_REVEAL = auto()
    AFTER_BIOME_CARD_REVEAL = auto()
    START_OF_WAVE_BEFORE_DRAW = auto()
    START_OF_WAVE_AFTER_DRAW = auto()
    #gets the information of the card activation, village or explorer
    BEFORE_CARD_ACTIVATION = auto()
    DIRECT_ACTIVATION = auto()
    AFTER_CARD_ACTIVATION = auto()
    BEFORE_ENEMY_CARD_ACTIVATION = auto()
    AFTER_ENEMY_CARD_ACTIVATION = auto()
    #gets the information of the enemy ability
    BEFORE_ENEMY_ABILITY_ACTIVATION = auto()
    AFTER_ENEMY_ABILITY_ACTIVATION = auto()

    BEFORE_SHUFFLE_INTO_DECK = auto()
    AFTER_SHUFFLE_INTO_DECK = auto()
    BEFORE_CARD_DRAWN = auto()
    AFTER_CARD_DRAWN = auto()
    BEFORE_CARD_DISCARDED = auto()
    AFTER_CARD_DISCARDED = auto()

    #Village
    BEFORE_VILLAGE_PHASE = auto()
    BEFORE_BUILDING_ACTIVATION = auto()
    AFTER_BUILDNG_ACTIVATION = auto()
    BEFORE_OBJECTIVE = auto()
    AFTER_OBJECTIVE = auto()

    #misc
    BEFORE_OPENING_PACK = auto()
    AFTER_OPENING_PACK = auto()
    BEFORE_USING_ITEM = auto()
    AFTER_USING_ITEM = auto()
    BEFORE_CRAFTING = auto()
    AFTER_CRAFTING = auto()


all_phases = list(Phases)

"""
Type definitions.
"""
type phase_transition_t = tuple[Phases, Phases]

class PhaseInfo:

    """
    Instances of this class get passed to playset entities
    during tick().

    For each phase, there should be a subclass defined with its own
    phase data.
    """

    def __init__(self,  phase: Phases = None):

        self.phase: Phases = phase

class TransitionPhaseInfo(PhaseInfo):

    """
    Class to use when giving a phase transition update.
    """
    def __init__(self, previous_phase: Phases, next_phase: Phases):

        PhaseInfo.__init__(self, Phases.TRANSITION_PHASE)

        self.previous_phase: Phases = previous_phase
        self.next_phase: Phases = next_phase

        self.phase_transition: phase_transition_t = (previous_phase, next_phase)
