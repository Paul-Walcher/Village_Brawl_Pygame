import pygame
from Frames.frame import Frame
from constants import Colors
from constants import Fonts, Fontsizes, KeyAlternatives
from constants import SIMAGE, CIMAGE, INTRO_IMAGES
import graphics
import clock
import random
from Frames.frame_enums import FrameEnums

class IntroFrame(Frame):

    def __init__(self, width, height, data=None):
        super().__init__(FrameEnums.INTRO_FRAME, width, height, data)


        self.num_headlines = 20
        self.village_brawl_headlines = [graphics.render_text(Fonts.MINECRAFT, Fontsizes.BIG_HEADLINE + i, "Village Brawl", Colors.WHITE) for i in range(self.num_headlines)]
        self.village_brawl_pos = [(graphics.center_horizontally(self.village_brawl_headlines[i], pygame.Rect(0, 0, self.width, self.height)), self.height // 20) for i in range(self.num_headlines)]

        self.headline_index = 0
        self.clock = clock.Clock()
        self.headline_change_time = 50#ms
        self.headline_index_going_right = True

        self.center_image_size = (self.height // 2, self.height // 2)
        self.center_image = graphics.render_image(random.choice(INTRO_IMAGES), self.center_image_size)
        self.center_image_pos = (graphics.center_horizontally(self.center_image, pygame.Rect(0, 0, self.width, self.height)),
                                graphics.center_vertically(self.center_image, pygame.Rect(0, self.height // 4, self.width, self.height//4 * 3))
        )

        self.press_text = graphics.render_text(Fonts.MINECRAFT, Fontsizes.SMALL, "Press enter to continue...", Colors.WHITE)
        self.press_text_pos = (20, self.height - 20)

        self.image_clock = clock.Clock()
        self.image_alpha = 255
        self.fading = True
        self.fade_duration = 2000.0

        self.clock.start()
        self.image_clock.start()

        self.entry_delay_clock = clock.Clock()
        self.entry_delay = 500#ms
        self.entry_delay_clock.start()

    def tick(self):


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None, None)

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_ESCAPE]):
            return (None, None)

        if (keys[pygame.K_RETURN] or keys[KeyAlternatives.ENTER_ALTERNATIVE]) and self.entry_delay_clock.elapsed() > self.entry_delay:

            return (FrameEnums.INTRO_MENU_FRAME, self.data)

        #setting opacity
        if self.fading:

            percent_faded = self.image_clock.elapsed() / self.fade_duration

            if percent_faded >= 1.0:

                self.image_alpha = 0
                self.fading = False

                self.center_image = graphics.render_image(random.choice(INTRO_IMAGES), self.center_image_size)
                self.image_clock.start()
            else:

                self.image_alpha = int(255 - percent_faded*255)

        else:

            percent_faded = self.image_clock.elapsed() / self.fade_duration

            if percent_faded >= 1.0:

                self.image_alpha = 255
                self.fading = True
                self.image_clock.start()

            else:

                self.image_alpha = int(percent_faded*255)

        self.center_image.set_alpha(self.image_alpha)




        if self.clock.elapsed() > self.headline_change_time:

            if self.headline_index_going_right:
                if self.headline_index == (len(self.village_brawl_headlines)-1):
                    self.headline_index -= 1
                    self.headline_index_going_right = False
                else:
                    self.headline_index += 1
            else:
                if (self.headline_index == 0):
                    self.headline_index += 1
                    self.headline_index_going_right = True
                else:
                    self.headline_index -= 1

            self.clock.start()


        return (self.frame_enum, self.data)

    def draw(self, screen):

        screen.fill(Colors.BLACK)

        screen.blit(self.village_brawl_headlines[self.headline_index], self.village_brawl_pos[self.headline_index])
        screen.blit(self.center_image, self.center_image_pos)
        screen.blit(self.press_text, self.press_text_pos)

        pygame.display.flip()
