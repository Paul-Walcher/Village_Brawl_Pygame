import os
import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID, WIDTH, HEIGHT
import graphics
from clock import Clock

from Frames.widgets.text_input import TextInput
from Frames.widgets.renderable_card_listviewer import RenderableCardListviewer
import constants

from Frames.cardinfo_frame import CardinfoFrame

class ShowExplorerStartingCardsFrame(Frame):

    def __init__(self, explorer_enum, data=None, frame_dim=None, parent_frame=None):

        super().__init__(FrameEnums.SHOW_EXPLORER_STARTING_CARDS_FRAME, data, frame_dim, parent_frame)

        self.modules = self.data[FrameDataID.MODULES]
        self.explorer_enum = explorer_enum

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.rerender()

    def rerender(self):

        self.widgets = []

        self.card = self.modules.mappings.explorer_cards_mappings[self.modules.enums.ExplorerCardEnums.SMALL_REST]
        self.cardinfo = self.card.info()

        self.cardlistviewer = RenderableCardListviewer(
                                                        self.frame_dim.copy(),
                                                        {self.card: 10,
                                                        self.modules.explorer_cards_module.Example_Card_1: 5,
                                                        self.modules.explorer_cards_module.Example_Card_2: 2,
                                                        self.modules.explorer_cards_module.Example_Card_4: 5,
                                                        self.modules.explorer_cards_module.Example_Card_3: 3,
                                                        self.modules.explorer_cards_module.Example_Card_5: 5,
                                                        self.modules.explorer_cards_module.Example_Card_6: 1,
                                                        self.modules.explorer_cards_module.Example_Card_7: 7

                                                        },
                                                        {"Deck": {
                                                        "cardlist": {
                                                                        self.card: 10,
                                                                        self.modules.explorer_cards_module.Example_Card_1: 5,
                                                                        self.modules.explorer_cards_module.Example_Card_2: 2,
                                                                        self.modules.explorer_cards_module.Example_Card_3: 3,
                                                                        self.modules.explorer_cards_module.Example_Card_4: 5,
                                                                        self.modules.explorer_cards_module.Example_Card_5: 5,
                                                                        self.modules.explorer_cards_module.Example_Card_6: 1,
                                                                        self.modules.explorer_cards_module.Example_Card_7: 7

                                                        },

                                                        "mutable": True, "is_copylist": False}},

                                                        shown_group="Deck"
                                                        )

    def bind_events(self):
        self.clear_event_callbacks()

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        ret = self.cardlistviewer.tick()

        if ret is None:
            if self.key_pressed(pygame.K_ESCAPE):
                self.raise_exit_flag()

        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)
        self.cardlistviewer.render(screen)
