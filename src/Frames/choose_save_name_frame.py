import os
import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives
import graphics
from clock import Clock

from Frames.load_playset_frame import LoadPlaysetFrame
from context_data import ContextData

class ChooseSaveNameFrame(Frame):

    def __init__(self, data=None, frame_dim=None, parent_frame=None):

        super().__init__(FrameEnums.CHOOSE_SAVE_NAME_FRAME, data, frame_dim, parent_frame)

        self.highlighted_index = -1
        self.is_typing = False

        self.savefile_name = ""
        self.max_name_length = 20

        self.savefile_name_font = None
        self.savefile_name_font_pos = None

        self.back_text = None
        self.back_pos = None

        self.enter_text = None
        self.enter_pos = None

        self.headline = None
        self.headline_pos = None


        self.go_back_flag = False
        self.load_playset_flag = False

        self.rerender()

    def rerender(self):

        center_pos = (self.width // 2, self.height // 2)

        self.widgets = []
        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        self.typing_frame = pygame.Surface((self.width // 2, self.height // 4))
        self.typing_frame.fill(Colors.WHITE)
        self.typing_frame.set_alpha(127)
        self.typing_frame_pos = (graphics.center_horizontally(self.typing_frame, self.frame_rect),
                                graphics.center_vertically(self.typing_frame, self.frame_rect))

        frame_margin = 5
        selected_frame_size = (self.typing_frame.get_width() + 2*frame_margin, self.typing_frame.get_height() + 2*frame_margin)
        self.typing_selected_frame = pygame.Surface(selected_frame_size)
        self.typing_selected_frame.fill(Colors.WHITE)
        self.typing_selected_frame_pos = graphics.center_at(self.typing_selected_frame, center_pos)

        self.render_text()


    def render_text(self):

        center_pos = (self.width // 2, self.height // 2)

        self.savefile_name_font = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG, self.savefile_name, Colors.BLACK)
        self.savefile_name_font_pos = graphics.center_at(self.savefile_name_font, center_pos)

        self.headline = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE, "Savefile Name", color=Colors.CYAN)
        self.headline_pos = (graphics.center_horizontally(self.headline, self.frame_rect), self.height // 20)

        if self.highlighted_index == 0:
            self.back_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 10, "Back", color=Colors.YELLOW)
        else:
            self.back_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 4, "Back", color=Colors.WHITE)

        self.back_pos = (self.width//20,
                            self.height - self.back_text.get_height() - self.height // 20)

        if self.highlighted_index == 2:
            self.enter_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 10, "Enter", color=Colors.YELLOW)
        else:
            self.enter_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 4, "Enter", color=Colors.WHITE)

        self.enter_pos = (self.width - self.width//20 - self.enter_text.get_width(),
                            self.height - self.enter_text.get_height() - self.height // 20)

    def bind_events(self):

        cdata = {"frame_ref": self}

        self.clear_event_callbacks()

        self.add_pygame_key_callback(pygame.K_ESCAPE, cdata, putback=False, func=self.escape_pressed)

        self.add_pygame_key_callback(pygame.K_LEFT, cdata, putback=False, func=self.left_pressed)
        self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, cdata, putback=False, func=self.left_pressed)

        self.add_pygame_key_callback(pygame.K_RIGHT, cdata, putback=False, func=self.right_pressed)
        self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, cdata, putback=False, func=self.right_pressed)

        self.add_pygame_key_callback(pygame.K_RETURN, cdata, putback=False, func=self.enter_pressed)
        self.add_pygame_key_callback(KeyAlternatives.ENTER_ALTERNATIVE, cdata, putback=False, func=self.enter_pressed)

        self.add_pygame_key_callback(pygame.K_BACKSPACE, cdata, putback=False, func=self.backspace_pressed)

        self.add_pygame_event_callback(pygame.TEXTINPUT, cdata, putback=False, func=self.handle_text_input)

    def handle_text_input(self, event, data):

        ref = data["frame_ref"]

        if ref.is_typing:
            ref.savefile_name += event.text
            if (len(ref.savefile_name)) > ref.max_name_length:
                ref.savefile_name = ref.savefile_name[:ref.max_name_length]
            ref.render_text()


    def escape_pressed(self, event, data):

        ref = data["frame_ref"]

        if ref.is_typing:
            ref.is_typing = False
            pygame.key.stop_text_input()
        else:
            return Frame.CallbackEvent.EXIT


    def left_pressed(self, event, data):

        ref = data["frame_ref"]

        if not ref.is_typing:
            ref.highlighted_index -= 1
            ref.highlighted_index %= 3

            if self.highlighted_index == 1:
                pygame.key.start_text_input()
                ref.is_typing = True

            ref.render_text()

    def right_pressed(self, event, data):

        ref = data["frame_ref"]

        if not ref.is_typing:

            ref.highlighted_index += 1
            ref.highlighted_index %= 3

            if self.highlighted_index == 1:
                pygame.key.start_text_input()
                ref.is_typing = True

            ref.render_text()

    def backspace_pressed(self, event, data):

        ref = data["frame_ref"]

        if ref.is_typing and ref.savefile_name:
            ref.savefile_name = ref.savefile_name[:-1]
            ref.render_text()

    def enter_pressed(self, event, data):

        ref = data["frame_ref"]

        if ref.highlighted_index == 0:
            ref.go_back_flag = True
        if ref.highlighted_index == 2 and len(ref.savefile_name) > 0:
            ref.load_playset_flag = True



    def tick(self):


        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None


        if self.go_back_flag:
            self.go_back_flag = False
            return self.parent_frame

        if self.load_playset_flag:
            self.load_playset_flag = False

            if type(self.data) == ContextData:
                self.data.current_savefile_name = self.savefile_name
            lpframe = LoadPlaysetFrame(self.data, self.frame_dim.copy(), self)
            return lpframe


        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.headline, self.headline_pos)
        if self.is_typing:
            screen.blit(self.typing_selected_frame, self.typing_selected_frame_pos)
        screen.blit(self.typing_frame, self.typing_frame_pos)
        screen.blit(self.savefile_name_font, self.savefile_name_font_pos)
        screen.blit(self.back_text, self.back_pos)
        screen.blit(self.enter_text, self.enter_pos)
