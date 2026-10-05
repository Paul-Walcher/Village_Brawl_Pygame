import os
import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID
import graphics
from clock import Clock

class ChooseSaveNameFrame(Frame):

    def __init__(self, data=None, frame=None):

        super().__init__(FrameEnums.CHOOSE_SAVE_NAME_FRAME, data, frame)


        center_pos = (self.width // 2, self.height // 2)

        self.highlighted_index = -1
        self.is_typing = False

        self.savefile_name = ""
        self.max_name_length = 20

        self.savefile_name_font = None
        self.savefile_name_font_pos = None

        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        self.back_text = None
        self.back_pos = None

        self.enter_text = None
        self.enter_pos = None

        self.headline = None
        self.headline_pos = None

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

        self.key_delay_clock = Clock()
        self.key_delay = 200#ms

        self.render_text()
        self.key_delay_clock.start()


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



    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

            if self.is_typing and event.type == pygame.TEXTINPUT:
                self.savefile_name += event.text
                if len(self.savefile_name) > self.max_name_length:
                    self.savefile_name = self.savefile_name[:self.max_name_length]
                self.render_text()

        keys = pygame.key.get_pressed()

        if self.key_delay_clock.elapsed() > self.key_delay:

            if keys[pygame.K_ESCAPE]:

                if self.is_typing:
                    pygame.key.stop_text_input()
                    self.is_typing = False
                    self.highlighted_index = 1
                    self.key_delay_clock.start()
                else:
                    return (None, None)

            if keys[pygame.K_BACKSPACE]:
                if self.is_typing and self.savefile_name:
                    self.savefile_name = self.savefile_name[:-1]
                    self.render_text()
                    self.key_delay_clock.start()

            if keys[pygame.K_LEFT] or (keys[KeyAlternatives.LEFT_ALTERNATIVE] and not self.is_typing):

                self.highlighted_index -= 1
                self.highlighted_index %= 3

                if self.is_typing and self.highlighted_index != 1:
                    pygame.key.stop_text_input()
                    self.is_typing = False
                elif not self.is_typing and self.highlighted_index == 1:
                    pygame.key.start_text_input()
                    self.is_typing = True

                self.render_text()
                self.key_delay_clock.start()

            if keys[pygame.K_RIGHT] or (keys[KeyAlternatives.RIGHT_ALTERNATIVE] and not self.is_typing):

                self.highlighted_index += 1
                self.highlighted_index %= 3

                if self.is_typing and self.highlighted_index != 1:
                    pygame.key.stop_text_input()
                    self.is_typing = False
                elif not self.is_typing and self.highlighted_index == 1:
                    pygame.key.start_text_input()
                    self.is_typing = True

                self.render_text()
                self.key_delay_clock.start()


            if keys[pygame.K_RETURN] or keys[KeyAlternatives.ENTER_ALTERNATIVE]:

                if self.highlighted_index == 0:
                    return (FrameEnums.CHOOSE_PLAYSET_FRAME, self.data)
                if self.highlighted_index == 2 and len(self.savefile_name) > 0:
                    self.data[FrameDataID.GAMEINFO].savefile_name = self.savefile_name
                    return (FrameEnums.LOAD_PLAYSET_FRAME, self.data)


        return (FrameEnums.CHOOSE_SAVE_NAME_FRAME, self.data)

    def draw(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.headline, self.headline_pos)
        if self.is_typing:
            screen.blit(self.typing_selected_frame, self.typing_selected_frame_pos)
        screen.blit(self.typing_frame, self.typing_frame_pos)
        screen.blit(self.savefile_name_font, self.savefile_name_font_pos)
        screen.blit(self.back_text, self.back_pos)
        screen.blit(self.enter_text, self.enter_pos)

        pygame.display.flip()
