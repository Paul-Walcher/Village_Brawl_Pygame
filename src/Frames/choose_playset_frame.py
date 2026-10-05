import os
import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, FrameDataID
import graphics
from clock import Clock
from gameinfo import Gameinfo


class ChoosePlaysetFrame(Frame):

    def __init__(self, data=None, frame_dim=None):

        super().__init__(FrameEnums.CHOOSE_PLAYSET_FRAME, data, frame_dim)

        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        self.playsets = [x for x in os.listdir(PLAYSETS_FOLDER) if os.path.isdir(os.path.join(PLAYSETS_FOLDER, x))]

        self.playsets_shown = 5

        self.headline = graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE, "Playsets", Colors.CYAN)
        self.headline_pos = (graphics.center_horizontally(self.headline, self.frame_rect), self.height // 20)

        self.playset_texts = [] #list of tuples (playset font, position)

        self.back_text = None
        self.back_pos = None

        self.back_focused = False
        self.playsets_focused = False

        self.playset_index = min(len(self.playsets), self.playsets_shown // 2)

        self.key_buffer_time = 200#ms
        self.keyclock = Clock()
        self.keyclock.start()

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



    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if self.keyclock.elapsed() > self.key_buffer_time:

            if keys[pygame.K_ESCAPE]:
                return (None, None)

            if keys[pygame.K_RETURN] or keys[KeyAlternatives.ENTER_ALTERNATIVE]:

                if self.back_focused:
                    return (FrameEnums.INTRO_MENU_FRAME, self.data)
                if self.playsets_focused:
                    ginfo = Gameinfo()
                    ginfo.playset = self.playsets[self.playset_index]
                    data = {}
                    if self.data:
                        self.data[FrameDataID.GAMEINFO] = ginfo
                        data = self.data
                    else:
                        data = {FrameDataID.GAMEINFO: ginfo}
                    return (FrameEnums.CHOOSE_SAVE_NAME_FRAME, data)


            if keys[pygame.K_LEFT] or keys[KeyAlternatives.LEFT_ALTERNATIVE]:

                if not self.back_focused:
                    self.back_focused = True
                    self.playsets_focused = False
                    self.render_text()
                    self.keyclock.start()

            if keys[pygame.K_RIGHT] or keys[KeyAlternatives.RIGHT_ALTERNATIVE]:

                if not self.playsets_focused:
                    self.back_focused = False
                    self.playsets_focused = True
                    self.render_text()
                    self.keyclock.start()

            if keys[pygame.K_UP] or keys[KeyAlternatives.UP_ALTERNATIVE]:

                if self.playsets_focused and self.playset_index > 0:
                    self.playset_index -= 1
                    self.render_text()
                    self.keyclock.start()

            if keys[pygame.K_DOWN] or keys[KeyAlternatives.DOWN_ALTERNATIVE]:

                if self.playsets_focused and self.playset_index < len(self.playsets)-1:
                    self.playset_index += 1
                    self.render_text()
                    self.keyclock.start()

        return (FrameEnums.CHOOSE_PLAYSET_FRAME, self.data)

    def draw(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.headline, self.headline_pos)

        for (text, pos) in self.playset_texts:

            screen.blit(text, pos)

        screen.blit(self.back_text, self.back_pos)

        pygame.display.flip()
