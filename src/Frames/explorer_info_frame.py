import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.empty_frame import EmptyFrame
from Frames.test_frame import TestFrame
from Frames.show_explorer_starting_cards_frame import ShowExplorerStartingCardsFrame
from Frames.cardinfo_frame import CardinfoFrame
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, Alpha, IIMAGE, STANDARD_BACKSIDES, R_ID
import graphics
from clock import Clock
from modules import Modules
import constants
from Frames.widgets.textbox import Textbox
from Frames.widgets.image_slider import ImageSlider
from Frames.widgets.text_slider import TextSlider
from Frames.widgets.labeled_image_slider import LabeledImageSlider

from context_data import ContextData

class ExplorerInfoFrame(Frame):

    NO_FOCUS = R_ID()
    DESCRIPTION_FOCUSED = R_ID()
    MENU_FOCUSED = R_ID()

    def __init__(self, explorer_enum, data=None, frame_dim=None, parent_frame=None):

        super().__init__(FrameEnums.CHOOSE_EXPLORER_FRAME, data, frame_dim, parent_frame)

        self.explorer_enum = explorer_enum
        self.modules = None

        if type(self.data) == ContextData:
            self.modules = self.data.modules

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.focused_outline_size = 5
        self.f_outline_d = 0.1

        self.icon_imgs = [IIMAGE("Deck_Icon.png"), IIMAGE("Supporter_Icon.png"),
                        IIMAGE("Item_Icon.png"), IIMAGE("Blueprint_Icon.png"),
                        IIMAGE("Pack_Icon.png"), IIMAGE("Villager_Icon.png"),
                        IIMAGE("Terrain_Icon.png")
                ]

        self.slider_labels = [["Cards"], ["Supporters"], ["Items"], ["Blueprints"], ["Packs"], ["Villagers"], ["Terrain"]]


        self.key_delay = 200#ms
        self.key_clock = Clock()

        self.state = ExplorerInfoFrame.NO_FOCUS

        #getting the frame
        self.full_hmargin = 0.2
        self.full_vmargin = 0.1

        self.info_page_percentage = 0.7
        self.dividing_percentage = 0.05
        self.label_slider_percentage = 0.25

        self.inner_frame = graphics.apply_margins(pygame.Rect(0, 0, self.width, self.height), self.full_hmargin, self.full_hmargin)

        self.info_page_frame, _, self.slider_frame = graphics.split_rect_vertically(self.inner_frame, [self.info_page_percentage, self.dividing_percentage, self.label_slider_percentage])

        self.slider_border_frame = self.slider_frame.copy()
        self.slider_frame = graphics.apply_margins(self.slider_frame, 0.1, 0.1)
        sx, sy = graphics.get_center_with_rect(self.slider_border_frame, self.slider_frame)
        self.slider_frame.x = sx
        self.slider_frame.y = sy
        self.surface = None

        self.full_image_shown = False

        #rendering
        self.rerender()

        self.key_clock.start()

    def get_selected_index(self):
        return self.slider_menu.get_selected_index()


    def render_slider_menu(self):

        self.slider_menu = LabeledImageSlider(  self.icon_imgs,
                                                self.slider_labels,
                                                self.slider_frame,
                                                text_location=LabeledImageSlider.BOTTOM,
                                                text_color=Colors.WHITE,
                                                max_slides=3,
                                                text_width_to_height_ratio=9/5
                                                )


    def rerender(self):

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.info_page_parts = self.explorer_info.get_info_page_parts(
                                                                        frame_dim=self.info_page_frame,
                                                                        hmargin=0.0,
                                                                        vmargin=0.0
                                                                        )
        self.textbox = self.info_page_parts.textbox
        self.textbox.set_outline_size(0)

        self.render_slider_menu()


    def bind_events(self):

        self.clear_event_callbacks()

        if self.is_focused():
            self.add_pygame_key_callback(pygame.K_LEFT, None, putback=False, func=self.left_pressed)
            self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, None, putback=False, func=self.left_pressed)

            self.add_pygame_key_callback(pygame.K_RIGHT, None, putback=False, func=self.right_pressed)
            self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, None, putback=False, func=self.right_pressed)

            self.add_pygame_key_callback(pygame.K_UP, None, putback=False, func=self.up_pressed)
            self.add_pygame_key_callback(KeyAlternatives.UP_ALTERNATIVE, None, putback=False, func=self.up_pressed)

            self.add_pygame_key_callback(pygame.K_DOWN, None, putback=False, func=self.down_pressed)
            self.add_pygame_key_callback(KeyAlternatives.DOWN_ALTERNATIVE, None, putback=False, func=self.down_pressed)

            self.add_pygame_key_callback(pygame.K_RETURN, None, putback=False, func=self.enter_pressed)
            self.add_pygame_key_callback(KeyAlternatives.ENTER_ALTERNATIVE, None, putback=False, func=self.enter_pressed)

            self.add_pygame_key_callback(pygame.K_ESCAPE, None, putback=False, func=self.escape_pressed)
            self.add_pygame_key_callback(KeyAlternatives.BACK_KEY, None, putback=False, func=self.escape_pressed)

            self.add_pygame_event_callback(pygame.KEYDOWN, None, False, self.keydown)
            self.add_pygame_event_callback(pygame.KEYUP, None, False, self.keyup)

    def escape_pressed(self, event, data):
        self.raise_exit_flag()

    def left_pressed(self, event, data):

        if self.state == ExplorerInfoFrame.NO_FOCUS:
            self.state = ExplorerInfoFrame.DESCRIPTION_FOCUSED
            self.textbox.set_outline_size(self.focused_outline_size)
        elif self.state == ExplorerInfoFrame.DESCRIPTION_FOCUSED:
            self.textbox.prev_page()
            self.key_clock.start()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.slide_right()
            self.key_clock.start()

        return None

    def right_pressed(self, event, data):

        if self.state == ExplorerInfoFrame.NO_FOCUS:
            self.state = ExplorerInfoFrame.DESCRIPTION_FOCUSED
            self.textbox.set_outline_size(self.focused_outline_size)
        elif self.state == ExplorerInfoFrame.DESCRIPTION_FOCUSED:
            self.textbox.next_page()
            self.key_clock.start()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.slide_left()
            self.key_clock.start()

        return None

    def up_pressed(self, event, data):

        if self.state == ExplorerInfoFrame.NO_FOCUS or self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.state = ExplorerInfoFrame.DESCRIPTION_FOCUSED
            self.textbox.set_outline_size(self.focused_outline_size)

        return None

    def down_pressed(self, event, data):

        if self.state == ExplorerInfoFrame.NO_FOCUS or self.state == ExplorerInfoFrame.DESCRIPTION_FOCUSED:
            self.state = ExplorerInfoFrame.MENU_FOCUSED
            self.textbox.set_outline_size(0)

        return None

    def enter_pressed(self, event, data):

        if self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.play_select_animation()

        return None

    def keydown(self, event, data):

        if event.key == KeyAlternatives.SHOW_IMAGE_KEY:
            self.full_image_shown = True

    def keyup(self, event, data):

        if event.key == KeyAlternatives.SHOW_IMAGE_KEY:
            self.full_image_shown = False

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        self.slider_menu.tick()
        slider_events = self.slider_menu.poll_events()

        for event in slider_events:

            if event.type == LabeledImageSlider.EventTypes.SELECT_ANIMATION_ENDED:

                if self.slider_menu.get_selected_index() == 0:

                    secframe = ShowExplorerStartingCardsFrame(self.explorer_enum, self.data, constants.FULLSCREEN, self.parent_frame)
                    return secframe
                else:

                    eframe = TestFrame(data=None, frame_dim=pygame.Rect(0, 0, constants.WIDTH, constants.HEIGHT), parent_frame=self.parent_frame)
                    return eframe

        return self


    def render(self, screen):


        if self.surface is not None:

            background_color = (*Colors.BLACK, 210)
            self.surface.fill(background_color)

            self.explorer_info.render_info_page_parts(
                                                        screen=self.surface,
                                                        info_page_part_container=self.info_page_parts,
                                                        background_color=background_color,
                                                        full_image_shown=self.full_image_shown
                                                        )
            self.slider_menu.render(self.surface)

            if self.state == ExplorerInfoFrame.MENU_FOCUSED:
                pygame.draw.rect(self.surface, (*Colors.WHITE, 255), self.slider_border_frame, width=self.focused_outline_size)


            screen.blit(self.surface, (self.x, self.y))
