from __future__ import annotations
from typing import Any, Type, Callable, override

from templates.renderable_cardinfo import Renderable_CardInfo
from constants import INFINITE
"""
This class defines a cardgroup class.
A cardgroup is a group of cards with its defining properties.
"""
#group types
type cardlist_t = dict[ Type[Renderable_CardInfo], int ] # (class reference: amount)

type group_t = dict[str, Any] #group type. The data type for a group transformed into a dictionary
type group_dict_t = dict[str, group_t] #name: group

class Cardgroup:

    #==========================
    # GROUP DICT KEYS
    #==========================

    MAX_GROUP_NUMBER_KEY: str = "max_group_number"

    #==========================
    # GROUP KEYS
    #==========================

    IS_COPYLIST_KEY: str = "is_copylist"
    IS_MUTABLE_KEY: str = "mutable"
    IS_RENAMABLE_KEY: str = "renamable" #if the group is renamable or not
    CARDLIST_KEY: str = "cardlist"
    MAX_CARDS_SELECTED_KEY: str = "max_cards_selected"
    MAX_SIZE_KEY: str = "max_size"

    """
    These are the keys used for
    the group.
    """

    @staticmethod
    def copy_cardlist(cardlist: cardlist_t) -> cardlist_t:
        """
        Copies a cardlist.
        """
        return cardlist.copy()

    @staticmethod
    def copy_group(group: group_t) -> group_t:
        """
        Copies a group.
        """

        new_group: group_t = {}
        straight_copies: list[str] = [
                                        Cardgroup.IS_COPYLIST_KEY,
                                        Cardgroup.IS_MUTABLE_KEY,
                                        Cardgroup.IS_RENAMABLE_KEY,
                                        Cardgroup.MAX_CARDS_SELECTED_KEY,
                                        Cardgroup.MAX_SIZE_KEY
                                        ]
        """
        straight_copies defines the keys whose
        values can be copied straight onto the new group.
        """

        new_group[Cardgroup.CARDLIST_KEY] = Cardgroup.copy_cardlist(group[Cardgroup.CARDLIST_KEY])

        for KEY in straight_copies:
            new_group[KEY] = group[KEY]

        return new_group

    @staticmethod
    def copy_group_dict(group_dict: group_dict_t) -> group_dict_t:
        """
        Copies a full group dictionary.
        """

        new_group_dict: group_dict_t = {}

        for (name, group) in group_dict.items():
            new_group_dict[name] = Cardgroup.copy_group(group)

        new_group_dict[Cardgroup.MAX_GROUP_NUMBER_KEY] = group_dict[Cardgroup.MAX_GROUP_NUMBER_KEY]

        return new_group_dict

    @staticmethod
    def add_group(
                    group_dict: group_dict_t,
                    name: str,
                    group: group_t,
                    name_duplication_allowed: bool = False  #if this is true, even if
                                                            #the name already exists.
                                                            # If so, the name will be slightly
                                                            # altered before insertion
                    ) -> bool:

        """
        Returns True if adding was possible, else False.
        """

        if name in group_dict:

            if not name_duplication_allowed:
                return False
            else:
                #modifying the name
                added_num: int = 0
                new_name: str = ""

                while added_num < INFINITE:

                    new_name = f"{name}_COPY_{str(added_num)}"

                    if new_name not in group_dict:
                        break

                    added_num += 1

                if added_num != INFINITE:

                    name = new_name

                else:

                    return False

        group_dict[name] = group

        return True

    @staticmethod
    def create_group(
                    cardlist: cardlist_t = None, #if it is None, it gets created as an empty cardlist
                    is_copylist: bool = False,
                    is_mutable: bool = True,
                    is_renamable: bool = True,
                    max_cards_selected: int = INFINITE,
                    max_size: int = INFINITE


                    ) -> group_t:
        """
        This function returns the group created.
        """


        new_group: group_t = {}

        new_group[Cardgroup.CARDLIST_KEY] = Cardgroup.copy_cardlist(cardlist)
        new_group[Cardgroup.IS_COPYLIST_KEY] = is_copylist
        new_group[Cardgroup.IS_MUTABLE_KEY] = is_mutable
        new_group[Cardgroup.IS_RENAMABLE_KEY] = is_renamable
        new_group[Cardgroup.MAX_CARDS_SELECTED_KEY] = max_cards_selected
        new_group[Cardgroup.MAX_SIZE_KEY] = max_size

        return new_group

    @staticmethod
    def group_dict(
                    max_group_number: int = INFINITE
                    ) -> group_dict_t:
        """
        Returns an empty group dict.
        Group dicts need to be created this way.
        """

        new_group_dict: group_dict_t = {}

        new_group_dict[Cardgroup.MAX_GROUP_NUMBER_KEY] = max_group_number

        return new_group_dict

    #==========================
    # GETTER AND SETTER FUNCTIONS GROUP DICT
    #==========================

    @staticmethod
    def get_groups_from_group_dict(group_dict: group_dict_t) -> dict[str, group_t]:
        """
        Returns a dictionary only containing the group name as key
        and the group as value, i.e. all elements being groups.
        """

        ignore_keys: list[str] = [Cardgroup.MAX_GROUP_NUMBER_KEY]

        back_dict: [str, group_t] = {}

        for (key, value) in group_dict.items():
            if key not in ignore_keys:
                #only returns a copy
                back_dict[key] = Cardgroup.copy_group(value)

        return back_dict

    @staticmethod
    def max_group_number(group_dict: group_dict_t, max_group_number: int = None) -> int:
        """
        If max_group_number is None: Returns max_group_number.
        If max_group_number is not None: max_group_number will be set, and
        the previous max_group_number will be returned.
        """

        ret: int = group_dict[Cardgroup.MAX_GROUP_NUMBER_KEY]

        if max_group_number is not None:
            group_dict[Cardgroup.MAX_GROUP_NUMBER_KEY] = max_group_number

        return ret

    #==========================
    # GETTER AND SETTER FUNCTIONS GROUP
    #==========================

    @staticmethod
    def groupsize(group: group_t) ->  int:
        """
        Returns the groupsize.
        """
        cardlist: cardlist_t = Cardgroup.cardlist(group=group)
        return sum(cardlist.values())

    @staticmethod
    def is_copylist(group: group_t, is_copylist: bool = None) -> bool:
        """
        If is_copylist is None: Returns is_copylist.
        If is_copylist is not None: is_copylist will be set, and
        the previous is_copylist will be returned.
        """

        ret: bool = group[Cardgroup.IS_COPYLIST_KEY]

        if is_copylist is not None:
            group[Cardgroup.IS_COPYLIST_KEY] = is_copylist

        return ret

    @staticmethod
    def is_mutable(group: group_t, is_mutable: bool = None) -> bool:
        """
        If is_mutable is None: Returns is_mutable.
        If is_mutable is not None: is_mutable will be set, and
        the previous is_mutable will be returned.
        """

        ret: bool = group[Cardgroup.IS_MUTABLE_KEY]

        if is_mutable is not None:
            group[Cardgroup.IS_MUTABLE_KEY] = is_mutable

        return ret

    @staticmethod
    def is_renamable(group: group_t, is_renamable: bool = None) -> bool:
        """
        If is_renamable is None: Returns is_renamable.
        If is_renamable is not None: is_renamable will be set, and
        the previous is_renamable will be returned.
        """

        ret: bool = group[Cardgroup.IS_RENAMABLE_KEY]

        if is_renamable is not None:
            group[Cardgroup.IS_RENAMABLE_KEY] = is_renamable

        return ret

    @staticmethod
    def cardlist(group: group_t, cardlist: cardlist_t = None) -> cardlist_t:
        """
        If cardlist is None: Returns cardlist.
        If cardlist is not None: cardlist will be set, and
        the previous cardlist will be returned.

        This only returns a copy.
        """

        ret: cardlist_t = Cardgroup.copy_cardlist(group[Cardgroup.CARDLIST_KEY])

        if cardlist is not None:
            group[Cardgroup.CARDLIST_KEY] = Cardgroup.copy_cardlist(cardlist)

        return ret

    @staticmethod
    def max_cards_selected(group: group_t, max_cards_selected: int = None) -> int:
        """
        If max_cards_selected is None: Returns max_cards_selected.
        If max_cards_selected is not None: max_cards_selected will be set, and
        the previous max_cards_selected will be returned.
        """

        ret: int = group[Cardgroup.MAX_CARDS_SELECTED_KEY]

        if max_cards_selected is not None:
            group[Cardgroup.MAX_CARDS_SELECTED_KEY] = max_cards_selected

        return ret

    @staticmethod
    def max_size(group: group_t, max_size: int = None) -> int:
        """
        If max_size is None: Returns max_size.
        If max_size is not None: max_size will be set, and
        the previous max_size will be returned.
        """

        ret: int = group[Cardgroup.MAX_SIZE_KEY]

        if max_size is not None:
            group[Cardgroup.MAX_SIZE_KEY] = max_size

        return ret
