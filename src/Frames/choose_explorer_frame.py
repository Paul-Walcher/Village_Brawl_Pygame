import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.explorer_info_frame import ExplorerInfoFrame
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID
import graphics
from clock import Clock
from modules import Modules
import constants

class ChooseExplorerFrame(Frame):

    def __init__(self, data=None, frame_dim=None, parent_frame=None):

        super().__init__(FrameEnums.CHOOSE_EXPLORER_FRAME, data, frame_dim, parent_frame)

        self.modules = self.data[FrameDataID.MODULES]
        self.stack = self.data[FrameDataID.STACK]

        #getting all explorers
        self.explorer_enums = list(self.modules.enums.ExplorerEnums)
        self.explorer_refs = [self.modules.mappings.explorer_mappings[explorer_enum] for explorer_enum in self.explorer_enums]
        self.explorer_infos = [ref.info() for ref in self.explorer_refs]

        self.explorer_index = (0 if self.stack.size() == 0 else self.stack.pop())


        self.rotating_left = False
        self.rotating_right = False

        self.shift = 0
        self.rotation_duration = 200#ms
        self.rotation_clock = Clock()

        self.key_delay = 200#ms
        self.key_clock = Clock()

        self.key_clock.start()

        self.INFO_FRAME_INACTIVE = 0
        self.INFO_FRAME_SLIDING_IN = 1
        self.INFO_FRAME_ACTIVE = 2
        self.INFO_FRAME_SLIDING_OUT = 3

        self.info_frame_sliding_time = 400#ms
        self.info_frame_clock = Clock()
        self.info_frame_state = self.INFO_FRAME_INACTIVE
        self.info_frame = None
        self.tickframe = None

        self.rerender()

    def rerender(self):

        self.widgets = []

        self.explorer_dimensions = (int(self.height//4 *3 * 0.714), self.height//4 * 3)

        self.headline = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE,
                                            self.explorer_infos[self.explorer_index].name, self.explorer_infos[self.explorer_index].name_color
                                            )
        self.headline_pos = (graphics.center_horizontally(self.headline, self.frame_dim), self.height // 20)

        self.headline_size = self.height // 20 + self.headline.get_height()

        self.explorer_center_frame = pygame.Rect(0, self.headline_size, self.width, self.height-self.headline_size)

        self.explorer_image = graphics.render_image(self.explorer_infos[self.explorer_index].card_image_path, self.explorer_dimensions)
        self.explorer_image_pos = graphics.get_center_with_surface(self.explorer_image, self.explorer_center_frame)

        self.info_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.SMALL, "Press i to see info", Colors.WHITE)
        self.info_text_pos = (self.width - self.width // 20 - self.info_text.get_width(), self.height - self.height//20 - self.info_text.get_height())

        self.second_headline = None
        self.second_headline_pos = (0, 0)

        self.second_explorer_image = None
        self.second_explorer_image_pos = (0, 0)

    def initialize_info_frame(self):


        iframe = pygame.Rect(self.width, 0, self.width // 2, self.height)
        info_frame = ExplorerInfoFrame(self.explorer_enums[self.explorer_index], self.modules, self.data, iframe, self)
        self.info_frame = info_frame
        self.tickframe = info_frame

        self.info_frame_state = self.INFO_FRAME_SLIDING_IN
        self.info_frame_clock.start()

    def deinitialize_info_frame(self):

        self.info_frame_state = self.INFO_FRAME_INACTIVE
        self.info_frame = None
        self.tickframe = None

    def finalize_info_frame(self):

        final_frame = pygame.Rect(self.width//2, 0, self.width//2, self.height)
        self.info_frame.frame_dim = final_frame

        self.info_frame_state = self.INFO_FRAME_ACTIVE

    def initialize_rotation(self):

        shift = 0

        if self.rotating_left:
            self.explorer_index = (self.explorer_index - 1) % len(self.explorer_infos)
            shift = self.width
        elif self.rotating_right:
            self.explorer_index = (self.explorer_index + 1) % len(self.explorer_infos)
            shift = -self.width


        self.second_headline = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE,
                                            self.explorer_infos[self.explorer_index].name, self.explorer_infos[self.explorer_index].name_color
                                            )
        self.second_headline_pos = (graphics.center_horizontally(self.headline, self.frame_dim) + shift, self.height // 20)

        self.second_explorer_image = graphics.render_image(self.explorer_infos[self.explorer_index].card_image_path, self.explorer_dimensions)
        sx, sy = graphics.get_center_with_surface(self.explorer_image, self.explorer_center_frame)
        self.second_explorer_image_pos = (sx + shift, sy)


    def finish_rotation(self):

        self.rotating_left = False
        self.rotating_right = False

        self.shift = 0

        self.explorer_image = self.second_explorer_image
        self.headline = self.second_headline

        self.explorer_image_pos = graphics.get_center_with_surface(self.explorer_image, self.explorer_center_frame)
        self.headline_pos = (graphics.center_horizontally(self.headline, self.frame_dim), self.height // 20)

        self.second_explorer_image = None
        self.second_explorer_image_pos = (0, 0)

        self.second_headline = None
        self.second_headline_pos = (0, 0)

        #if we have an info frame, set the explorer and rerender it
        if self.info_frame is not None:
            self.info_frame.explorer_enum = self.explorer_enums[self.explorer_index]
            self.info_frame.rerender()

    def bind_events(self):

        cdata = {"frame_ref": self}

        if self.is_focused():
            self.add_pygame_key_callback(pygame.K_ESCAPE, cdata, putback=False, func=self.escape_pressed)

            self.add_pygame_key_callback(pygame.K_LEFT, cdata, putback=False, func=self.left_pressed)
            self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, cdata, putback=False, func=self.left_pressed)

            self.add_pygame_key_callback(pygame.K_RIGHT, cdata, putback=False, func=self.right_pressed)
            self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, cdata, putback=False, func=self.right_pressed)

            self.add_pygame_key_callback(pygame.K_i, cdata, putback=False, func=self.i_pressed)

    def escape_pressed(self, event, data):
        return Frame.CallbackEvent.EXIT

    def left_pressed(self, event, data):
        ref = data["frame_ref"]

        if not (ref.rotating_left or ref.rotating_right):

            ref.rotating_left = True
            ref.initialize_rotation()

            ref.rotation_clock.start()

    def right_pressed(self, event, data):
        ref = data["frame_ref"]

        if not (ref.rotating_left or ref.rotating_right):

            ref.rotating_right = True
            ref.initialize_rotation()

            ref.rotation_clock.start()

    def i_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.info_frame_state == ref.INFO_FRAME_INACTIVE:
            ref.initialize_info_frame()



    def tick(self):

        nframe = self

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        if self.tickframe is not None and self.info_frame_state not in [self.INFO_FRAME_SLIDING_IN, self.INFO_FRAME_SLIDING_OUT]:
            tframe = self.tickframe.tick()

            if tframe is None:
                if self.tickframe is self.info_frame:
                    self.info_frame_state = self.INFO_FRAME_SLIDING_OUT
                    self.tickframe = self.info_frame
                    self.info_frame_clock.start()
                elif self.info_frame_state == self.INFO_FRAME_ACTIVE:
                    self.tickframe = self.info_frame
                    self.info_frame.focus()
                else:
                    self.tickframe = None
            else:
                self.tickframe = tframe


        if self.info_frame_state == self.INFO_FRAME_SLIDING_IN:

            if self.info_frame_clock.elapsed() >= self.info_frame_sliding_time:
                self.finalize_info_frame()
            else:
                info_frame_frame = pygame.Rect(int(self.width - (self.info_frame_clock.elapsed() / self.info_frame_sliding_time * self.width//2)), 0, self.width//2, self.height)
                self.info_frame.frame_dim = info_frame_frame

        elif self.info_frame_state == self.INFO_FRAME_SLIDING_OUT:

            if self.info_frame_clock.elapsed() >= self.info_frame_sliding_time:
                self.deinitialize_info_frame()
            else:
                info_frame_frame = pygame.Rect(int(self.width // 2 + (self.info_frame_clock.elapsed() / self.info_frame_sliding_time * self.width//2)), 0, self.width//2, self.height)
                self.info_frame.frame_dim = info_frame_frame

        if self.rotating_left or self.rotating_right:
            if self.rotation_clock.elapsed() > self.rotation_duration:
                self.finish_rotation()
            elif self.rotating_left:
                self.shift = - int((self.rotation_clock.elapsed() / self.rotation_duration) * self.width)
            elif self.rotating_right:
                self.shift = int((self.rotation_clock.elapsed() / self.rotation_duration) * self.width)

        return nframe


    def render(self, screen):


        ex, ey = self.explorer_image_pos
        sex, sey = self.second_explorer_image_pos

        hex, hey = self.headline_pos
        shex, shey = self.second_headline_pos

        screen.fill(Colors.BLACK)

        screen.blit(self.headline, (hex + self.shift, hey))
        screen.blit(self.explorer_image, (ex + self.shift, ey))
        if self.second_explorer_image is not None:
            screen.blit(self.second_headline, (shex + self.shift, shey))
            screen.blit(self.second_explorer_image, (sex + self.shift, sey))
        screen.blit(self.info_text, self.info_text_pos)

        if self.tickframe is not None:
            self.tickframe.render(screen)
