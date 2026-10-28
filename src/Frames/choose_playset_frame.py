import os
import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives
import graphics
from clock import Clock
from Frames.choose_save_name_frame import ChooseSaveNameFrame
from context_data import ContextData

class ChoosePlaysetFrame(Frame):

    def __init__(self, data=None, frame_dim=None, parent_frame=None, focus_group=""):

        super().__init__(FrameEnums.CHOOSE_PLAYSET_FRAME, data=data, frame_dim=frame_dim, parent_frame=parent_frame, focus_group=focus_group)

        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        self.playsets = [x for x in os.listdir(PLAYSETS_FOLDER) if os.path.isdir(os.path.join(PLAYSETS_FOLDER, x))]

        self.playsets_shown = 5

        self.back_text = None
        self.back_pos = None

        self.back_focused = False
        self.playsets_focused = False

        self.playset_index = min(len(self.playsets), self.playsets_shown // 2)

        self.parent_frame_flag = False
        self.choose_save_name_flag = False

        self.rerender()

    def rerender(self):

        self.widgets = []

        self.headline = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE, "Playsets", Colors.CYAN)
        self.headline_pos = (graphics.center_horizontally(self.headline, self.frame_rect), self.height // 20)

        self.playset_texts = [] #list of tuples (playset font, position)

        self.render_text()

    def render_text(self):

        if self.back_focused:
            self.back_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 10, "Back", color=Colors.YELLOW)
        else:
            self.back_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.AVERAGE + 4, "Back", color=Colors.WHITE)

        self.back_pos = (self.width//20,
                            self.height - self.back_text.get_height() - self.height // 20)

        #rendering the middle playset

        font_decrease = 25
        text_distance = 40#px

        rect = pygame.Rect(0, self.height // 4, self.width, self.height // 4 * 3)

        middle_playset = None
        if self.playsets_focused:
            middle_playset = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG+8, self.playsets[self.playset_index], color=Colors.YELLOW)
        else:
            middle_playset = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG, self.playsets[self.playset_index], color=Colors.WHITE)


        middle_playset_pos = (graphics.center_horizontally(middle_playset, self.frame_rect), graphics.center_vertically(middle_playset, rect))
        #rendering the other playsets

        self.playset_texts = [(middle_playset, middle_playset_pos)]

        pshown = self.playsets_shown - 1

        playsets_above = pshown // 2
        playsets_below = pshown - playsets_above

        font_above = Fontsizes.BIG - font_decrease
        idx = self.playset_index - 1

        above_y = middle_playset_pos[1]

        while (font_above > 0) and (idx >= 0) and (playsets_above > 0):

            rendered_text = graphics.render_text(Fonts.MINECRAFT, font_above, self.playsets[idx], Colors.WHITE)
            above_y -= rendered_text.get_height() + text_distance

            rendered_pos = (graphics.center_horizontally(rendered_text, rect), above_y)

            self.playset_texts.append((rendered_text, rendered_pos))


            playsets_above -= 1
            idx -= 1
            font_above -= font_decrease

        font_below = Fontsizes.BIG - font_decrease
        idx = self.playset_index + 1

        above_y = middle_playset_pos[1] + middle_playset.get_height() + text_distance

        while (font_below > 0) and (idx < len(self.playsets)) and (playsets_below > 0):

            rendered_text = graphics.render_text(Fonts.MINECRAFT, font_below, self.playsets[idx], Colors.WHITE)

            rendered_pos = (graphics.center_horizontally(rendered_text, rect), above_y)

            above_y += rendered_text.get_height() + text_distance

            self.playset_texts.append((rendered_text, rendered_pos))

            playsets_below -= 1
            idx += 1
            font_below -= font_decrease

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

        if not ref.back_focused:
            ref.back_focused = True
            ref.playsets_focused = False
            ref.render_text()

    def right_pressed(self, event, data):

        ref = data["frame_ref"]

        if not ref.playsets_focused:
            ref.back_focused = False
            ref.playsets_focused = True
            ref.render_text()

    def up_pressed(self, event, data):

        ref = data["frame_ref"]

        if ref.playsets_focused and ref.playset_index > 0:
            ref.playset_index -= 1
            ref.render_text()

    def down_pressed(self, event, data):

        ref = data["frame_ref"]

        if ref.playsets_focused and ref.playset_index < len(ref.playsets) - 1:
            ref.playset_index += 1
            ref.render_text()

    def enter_pressed(self, event, data):
        ref = data["frame_ref"]

        if ref.back_focused:
            ref.parent_frame_flag = True
        if ref.playsets_focused:
            ref.choose_save_name_flag = True

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        if self.parent_frame_flag:
            self.parent_frame_flag = False
            self.parent_frame.focus()
            self.parent_frame.rerender()
            return self.parent_frame

        if self.choose_save_name_flag:
            self.choose_save_name_flag = False

            if type(self.data) == ContextData:
                self.data.current_playset = self.playsets[self.playset_index]

            csnframe = ChooseSaveNameFrame(self.data, self.frame_dim.copy(), self)

            return csnframe

        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.headline, self.headline_pos)

        for (text, pos) in self.playset_texts:

            screen.blit(text, pos)

        screen.blit(self.back_text, self.back_pos)
