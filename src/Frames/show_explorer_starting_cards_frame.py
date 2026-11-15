import os
import pygame

from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, WIDTH, HEIGHT
import graphics
from clock import Clock

import constants
from cardgroup import Cardgroup, group_t, group_dict_t, cardlist_t
from context_data import ContextData

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.cardinfo_frame import CardinfoFrame
from Frames.widgets.text_input import TextInput
from Frames.widgets.renderable_card_listviewer import RenderableCardListviewer

class ShowExplorerStartingCardsFrame(Frame):

    def __init__(
                    self,
                    explorer_enum,
                    data=None,
                    frame_dim=None,
                    parent_frame=None,
                    focus_group="",
                    has_focus=True
                    ):

        super().__init__(
                            frame_enum=FrameEnums.SHOW_EXPLORER_STARTING_CARDS_FRAME,
                            data=data,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=focus_group,
                            has_focus=has_focus

                        )

        self.modules = None
        if type(self.data) == ContextData:
            self.modules = self.data.modules

        self.explorer_enum = explorer_enum

        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        self.rerender()

    def rerender(self):

        self.widgets = []

        self.card = self.modules.mappings.explorer_cards_mappings[self.modules.enums.ExplorerCardEnums.SMALL_REST]
        self.cardinfo = self.card.info()

        #getting the groups
        group_dict: group_dict_t = Cardgroup.group_dict()

        #getting the cardlists
        full_cardlist: cardlist_t = {
                                        self.card: 100,
                                        self.modules.explorer_cards_module.Example_Card_1: 500,
                                        self.modules.explorer_cards_module.Example_Card_2: 200,
                                        self.modules.explorer_cards_module.Example_Card_4: 500,
                                        self.modules.explorer_cards_module.Example_Card_3: 300,
                                        self.modules.explorer_cards_module.Example_Card_5: 500,
                                        self.modules.explorer_cards_module.Example_Card_6: 100,
                                        self.modules.explorer_cards_module.Example_Card_7: 700

                                    }

        cardlist_1: cardlist_t =  {
                                        self.card: 10,
                                        self.modules.explorer_cards_module.Example_Card_1: 5,
                                        self.modules.explorer_cards_module.Example_Card_2: 2,
                                        self.modules.explorer_cards_module.Example_Card_3: 3,
                                        self.modules.explorer_cards_module.Example_Card_4: 5,
                                        self.modules.explorer_cards_module.Example_Card_5: 5,
                                        self.modules.explorer_cards_module.Example_Card_6: 1,
                                        self.modules.explorer_cards_module.Example_Card_7: 7

                                    }

        cardlist_2: cardlist_t = {
                                    self.card: 5,
                                    self.modules.explorer_cards_module.Example_Card_1: 0,
                                    self.modules.explorer_cards_module.Example_Card_2: 2,
                                    self.modules.explorer_cards_module.Example_Card_3: 0,
                                    self.modules.explorer_cards_module.Example_Card_4: 5,
                                    self.modules.explorer_cards_module.Example_Card_5: 5,
                                    self.modules.explorer_cards_module.Example_Card_6: 0,
                                    self.modules.explorer_cards_module.Example_Card_7: 5

                                }

        cardlist_3: cardlist_t = {
                                    self.card: 5,
                                    self.modules.explorer_cards_module.Example_Card_1: 0,
                                    self.modules.explorer_cards_module.Example_Card_2: 2,
                                    self.modules.explorer_cards_module.Example_Card_3: 0,
                                    self.modules.explorer_cards_module.Example_Card_4: 5,
                                    self.modules.explorer_cards_module.Example_Card_5: 5,
                                    self.modules.explorer_cards_module.Example_Card_6: 0,
                                    self.modules.explorer_cards_module.Example_Card_7: 5

                                }


        group_1: group_t = Cardgroup.create_group(
                                                    cardlist=cardlist_1,
                                                    is_copylist=False,
                                                    is_mutable=True,
                                                    is_renamable=True
                                                    )
        group_2: group_t = Cardgroup.create_group(
                                                    cardlist=cardlist_2,
                                                    is_copylist=False,
                                                    is_mutable=True,
                                                    is_renamable=False
                                                    )
        group_3: group_t = Cardgroup.create_group(
                                                    cardlist=cardlist_3,
                                                    is_copylist=False,
                                                    is_mutable=True,
                                                    is_renamable=True
                                                    )

        #adding all groups
        Cardgroup.add_group(group_dict, name="Deck 1", group=group_1)
        Cardgroup.add_group(group_dict, name="EEE", group=group_2)
        Cardgroup.add_group(group_dict, name="Deck ABC", group=group_3)

        self.cardlistviewer = RenderableCardListviewer(
                                                        self.frame_dim.copy(),

                                                        full_cardlist=full_cardlist,
                                                        groups=group_dict,
                                                        shown_group="Deck 1",
                                                        parent_frame=self,
                                                        focus_group=self.focus_group,
                                                        has_focus=self.is_focused()
                                                        )

    def bind_events(self):
        self.clear_event_callbacks()

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        ret = self.cardlistviewer.tick()

        if ret is None:
            if self.key_pressed(pygame.K_ESCAPE):
                self.raise_exit_flag()

        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)
        self.cardlistviewer.render(screen)
