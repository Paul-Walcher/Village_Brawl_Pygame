import pygame
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import Colors, Fonts, Fontsizes, KeyAlternatives
import graphics
from clock import Clock

class IntroMenuFrame(Frame):

    def __init__(self, data=None, frame_dim=None):

        super().__init__(FrameEnums.INTRO_MENU_FRAME, data, frame_dim)

        self.new_game_text = None
        self.new_game_pos = None

        self.load_game_text = None
        self.load_game_pos = None

        self.back_text = None
        self.back_pos = None

        self.text_distance = self.height // 10

        self.chosen_index = -1

        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        self.clock = Clock()
        self.key_delay = 100#ms

        self.render_highlighted()

        self.clock.start()


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




    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return (None, None)

        if (keys[pygame.K_UP] or keys[KeyAlternatives.UP_ALTERNATIVE]) and self.clock.elapsed() > self.key_delay:

            if self.chosen_index == -1:
                self.chosen_index = 0
            else:
                self.chosen_index -= 1
                self.chosen_index %= 3

            self.render_highlighted()
            self.clock.start()

        if (keys[pygame.K_DOWN] or keys[KeyAlternatives.DOWN_ALTERNATIVE]) and self.clock.elapsed() > self.key_delay:

            if self.chosen_index == -1:
                self.chosen_index = 0
            else:
                self.chosen_index += 1
                self.chosen_index %= 3

            self.render_highlighted()
            self.clock.start()

        if (keys[pygame.K_LEFT] or keys[KeyAlternatives.LEFT_ALTERNATIVE]) and self.clock.elapsed() > self.key_delay:

            if self.chosen_index != 2:
                self.chosen_index = 2
                self.render_highlighted()
                self.clock.start()

        if (keys[pygame.K_RIGHT] or keys[KeyAlternatives.RIGHT_ALTERNATIVE]) and self.clock.elapsed() > self.key_delay:

            if self.chosen_index == 2 or self.chosen_index == -1:
                self.chosen_index = 0
                self.render_highlighted()
                self.clock.start()

        if keys[pygame.K_RETURN] or keys[KeyAlternatives.ENTER_ALTERNATIVE]:
            if self.chosen_index == 2:
                return (FrameEnums.INTRO_FRAME, self.data)

            if self.chosen_index == 0:
                return (FrameEnums.CHOOSE_PLAYSET_FRAME, self.data)


        return (FrameEnums.INTRO_MENU_FRAME, self.data)

    def draw(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.new_game_text, self.new_game_pos)
        screen.blit(self.load_game_text, self.load_game_pos)
        screen.blit(self.back_text, self.back_pos)
