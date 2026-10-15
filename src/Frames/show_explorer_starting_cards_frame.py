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

        self.card = self.modules.mappings.explorer_cards_mappings[self.modules.enums.ExplorerCardEnums.SMALL_REST]
        self.cardinfo = self.card.info()

        self.cardlistviewer = RenderableCardListviewer(
                                                        self.frame_dim.copy(),
                                                        {self.card.info(): 10},
                                                        {"Deck": {"cardlist": {self.card.info(): i for i in range(1000)}, "mutable": True}},
                                                        shown_group="Deck",
                                                        trunk_shown=False
                                                        )

        self.widgets.append(self.cardlistviewer)

        self.rerender()

    def rerender(self):
        pass

    def bind_events(self):
        pass

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None


        self.widgets_tick()

        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)
        self.render_widgets(screen)
