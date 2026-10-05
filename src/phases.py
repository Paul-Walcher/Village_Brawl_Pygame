from enum import Enum, auto
import pygame

class Phases(Enum):

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

class PhaseInfo:

    #gets the data passed from the frames

    def __init__(self, data=None, phase=None, previous_screen=None):

        self.data = data
        self.phase = phase
        self.previous_screen = previous_screen

class CardActivationPhaseInfo(PhaseInfo):

    def __init__(self, data=None, phase=None, previous_screen=None, activated_card=None, activation_location=None, activating_entity=None):

        super().__init__(data, phase, previous_screen)

        self.activated_card = activated_card
        self.activation_location = activation_location
        self.activating_entity = activating_entity

class CardDiscardPhaseInfo(PhaseInfo):

    def __init__(self, data=None, phase=None, previous_screen=None,discarded_card=None, discarding_location=None, discarding_entity=None):

        super().__init__(data, phase, previous_screens)

        self.discarded_card = discarded_card
        self.discarding_location = discarding_location
        self.discarding_entity = discarding_entity
