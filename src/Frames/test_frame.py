import pygame

from Frames.empty_frame import EmptyFrame
from Frames.frame_enums import FrameEnums

from Frames.widgets.dropdown_menu import DropdownMenu
from Frames.widgets.expandable_dropdown_menu import ExpandableDropdownMenu
from constants import Colors, KeyAlternatives
from clock import Clock
import time

class TestFrame(EmptyFrame):

    def __init__(self, data, frame_dim, parent_frame=None):
        super().__init__(data, frame_dim, parent_frame)

        self.rerender()



        self.key_clock = Clock()
        self.key_delay = 300#ms

        self.key_clock.start()

    def rerender(self):

        self.dropdown_frame = pygame.Rect(self.x + 100, self.y + 100, 800, 500)

        self.surface = pygame.Surface((self.frame_dim.w, self.frame_dim.h))

        options = {
                    ("line 1", "line 2"): {
                                                ("E",): None,
                                                ("RT", "TZ", "IO"): {
                                                                        ("ERERER", "BZTT"): None,
                                                                        ("HBEDZG",): None
                                                                            }
                                            },
                    ("LINE",): None,
                    ("JJ", "JJ", "JJ", "JJ"): None

                    }

        start_options = [["AAA"], ["BBB", "CCC"], ["DDD", "EEE", "FFF"]]

        self.dropdown = DropdownMenu(     self.dropdown_frame,
                                                    start_options
                                                    )

    def tick(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

        keys = pygame.key.get_pressed()

        self.dropdown.tick()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return self.parent_frame

        for event in self.dropdown.poll_events():
            if event.type == ExpandableDropdownMenu.EventTypes.SELECTION_FINISHED_EVENT:
                print(event.data)

        if self.key_clock.elapsed() > self.key_delay:

            if keys[pygame.K_UP] or keys[KeyAlternatives.UP_ALTERNATIVE]:
                self.dropdown.move_up()
                self.key_clock.start()
            elif keys[pygame.K_DOWN] or keys[KeyAlternatives.DOWN_ALTERNATIVE]:
                self.dropdown.move_down()
                self.key_clock.start()
            elif keys[pygame.K_RETURN] or keys[KeyAlternatives.ENTER_ALTERNATIVE]:
                self.dropdown.select()
                self.key_clock.start()
            elif keys[pygame.K_LEFT] or keys[KeyAlternatives.LEFT_ALTERNATIVE]:
                #self.dropdown.move_left()
                self.dropdown.unfocus()
                self.key_clock.start()
            elif keys[pygame.K_RIGHT] or keys[KeyAlternatives.RIGHT_ALTERNATIVE]:
                #self.dropdown.move_right()
                self.dropdown.unfocus()
                self.key_clock.start()

        return self

    def render(self, screen):

        self.surface.fill(Colors.GRAY)

        self.dropdown.render(self.surface)

        screen.blit(self.surface, (self.x, self.y))
