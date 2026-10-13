import os
import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID
import graphics
from clock import Clock

from widgets.text_input import TextInput

class ShowExplorerStartingCardsFrame(Frame):

    def __init__(self, explorer_enum, data=None, frame_dim=None, parent_frame=None):

        super().__init__(FrameEnums.SHOW_EXPLORER_STARTING_CARDS_FRAME, data, frame_dim, parent_frame)

        self.modules = self.data[FrameDataID.MODULES]
        self.explorer_enum = explorer_enum

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.input_widget_frame_dim = pygame.Rect(100, 100, 500, 100)
        self.input_widget = TextInput(self.input_widget_frame_dim)
        self.input_widget.start_input()
        self.widgets.append(self.input_widget)

        self.bind_events()
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
