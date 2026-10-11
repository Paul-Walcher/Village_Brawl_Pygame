import pygame
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import Colors, Fonts, Fontsizes, KeyAlternatives
import graphics
from clock import Clock
import time

from Frames.choose_playset_frame import ChoosePlaysetFrame

class IntroMenuFrame(Frame):

    def __init__(self, data=None, frame_dim=None, parent_frame=None):

        super().__init__(FrameEnums.INTRO_MENU_FRAME, data, frame_dim, parent_frame)

        self.new_game_text = None
        self.new_game_pos = None

        self.load_game_text = None
        self.load_game_pos = None

        self.back_text = None
        self.back_pos = None

        self.text_distance = self.height // 10

        self.chosen_index = -1

        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        self.choose_playset_flag = False
        self.go_back_flag = False

        self.render_highlighted()
        self.bind_events()


    def render_highlighted(self):

        if self.chosen_index == 0:
            self.new_game_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 4, "New Game", color=Colors.YELLOW)
        else:
            self.new_game_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE, "New Game", color=Colors.WHITE)

        self.new_game_pos = (graphics.center_horizontally(self.new_game_text, self.frame_rect),
                            graphics.center_vertically(self.new_game_text, self.frame_rect) - self.text_distance // 2)

        if self.chosen_index == 1:
            self.load_game_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 4, "Load Game", color=Colors.YELLOW)
        else:
            self.load_game_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE, "Load Game", color=Colors.WHITE)

        self.load_game_pos = (graphics.center_horizontally(self.load_game_text, self.frame_rect),
                            graphics.center_vertically(self.load_game_text, self.frame_rect) + self.text_distance // 2)

        if self.chosen_index == 2:
            self.back_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 10, "Back", color=Colors.YELLOW)
        else:
            self.back_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 4, "Back", color=Colors.WHITE)

        self.back_pos = (self.width//20,
                            self.height - self.back_text.get_height() - self.height // 20)

    def bind_events(self):

        cdata = {"frame_ref": self}

        self.add_pygame_key_callback(pygame.K_LEFT, cdata, putback=False, func=self.left_pressed)
        self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, cdata, putback=False, func=self.left_pressed)

        self.add_pygame_key_callback(pygame.K_RIGHT, cdata, putback=False, func=self.right_pressed)
        self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, cdata, putback=False, func=self.right_pressed)

        self.add_pygame_key_callback(pygame.K_UP, cdata, putback=False, func=self.up_pressed)
        self.add_pygame_key_callback(KeyAlternatives.UP_ALTERNATIVE, cdata, putback=False, func=self.up_pressed)

        self.add_pygame_key_callback(pygame.K_DOWN, cdata, putback=False, func=self.down_pressed)
        self.add_pygame_key_callback(KeyAlternatives.DOWN_ALTERNATIVE, cdata, putback=False, func=self.down_pressed)

        self.add_pygame_key_callback(pygame.K_RETURN, cdata, putback=False, func=self.enter_pressed)
        self.add_pygame_key_callback(KeyAlternatives.ENTER_ALTERNATIVE, cdata, putback=False, func=self.enter_pressed)


    def left_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.chosen_index != 2:
            ref.chosen_index = 2
            ref.render_highlighted()

    def right_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.chosen_index == 2 or ref.chosen_index == -1:
            ref.chosen_index = 0
            ref.render_highlighted()

    def up_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.chosen_index == -1:
            ref.chosen_index = 0
        else:
            ref.chosen_index -= 1
            ref.chosen_index %= 3

        ref.render_highlighted()

    def down_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.chosen_index == -1:
            ref.chosen_index = 0
        else:
            ref.chosen_index += 1
            ref.chosen_index %= 3

        ref.render_highlighted()

    def enter_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.chosen_index == 2:
            ref.go_back_flag = True
        if ref.chosen_index == 0:
            ref.choose_playset_flag = True



    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        if self.go_back_flag:
            self.go_back_flag = False
            return self.parent_frame

        if self.choose_playset_flag:
            cpframe = ChoosePlaysetFrame(self.data, self.frame_dim.copy(), self)
            self.choose_playset_flag = False
            return cpframe


        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.new_game_text, self.new_game_pos)
        screen.blit(self.load_game_text, self.load_game_pos)
        screen.blit(self.back_text, self.back_pos)
