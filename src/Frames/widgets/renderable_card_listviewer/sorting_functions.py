"""
This file provides the sorting functions used
on the the listviewer_cardlist in renderable_card_listviewer.
"""
from __future__ import annotations
from typing import Any, Type, Callable, override, TYPE_CHECKING

import random
if TYPE_CHECKING:
    from Frames.widgets.renderable_card_listviewer.group_functions\
    import (
            listviewer_cardlist_element_t,
            listviewer_cardlist_t
            )



# ==================================
# SORTING FUNCTIONS
# ==================================

type cardlist_sorting_function_t = Callable[[listviewer_cardlist_t], listviewer_cardlist_t]

class SortingFunctions:
    """
    Functions to sort cardlists.
    Each cardlist is: [(RenderableCard (Class), amount)]
    """

    @staticmethod
    def no_order(cardlist: listviewer_cardlist_t) -> listviewer_cardlist_t:
        """
        Returns the cardlist in the same order as
        it was before.
        """
        return cardlist

    @staticmethod
    def randomized(cardlist: listviewer_cardlist_t) -> listviewer_cardlist_t:
        """
        Returns the cardlist after a random shuffle.
        """
        cardlist_copy = cardlist.copy()
        random.shuffle(cardlist_copy)
        return cardlist_copy

    @staticmethod
    def name_descending(cardlist: listviewer_cardlist_t) -> listviewer_cardlist_t:
        """
        Sorts by name descending.
        """
        clist = cardlist.copy()
        clist.sort(key=lambda x: x[0].info().name)
        return clist

    @staticmethod
    def name_ascending(cardlist: listviewer_cardlist_t) -> listviewer_cardlist_t:
        """
        Sorts by name ascending.
        """
        clist = cardlist.copy()
        clist.sort(key=lambda x: x[0].info().name)
        clist.reverse()
        return clist

    @staticmethod
    def amount_descending(cardlist: listviewer_cardlist_t) -> listviewer_cardlist_t:
        """
        Sorts by amount descending.
        """
        clist = cardlist.copy()
        clist.sort(key=lambda x: x[1])
        return clist

    @staticmethod
    def amount_ascending(cardlist: listviewer_cardlist_t) -> listviewer_cardlist_t:
        """
        Sorts by amount ascending.
        """
        clist = cardlist.copy()
        clist.sort(key=lambda x: x[1])
        clist.reverse()
        return clist
