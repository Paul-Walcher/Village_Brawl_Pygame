"""
This file provides functions to easily map between
PlaysetEntities, identifiers and tags.
"""

from __future__ import annotations
from typing import Type, Any, Callable, override, TYPE_CHECKING

from templates.renderable_cardinfo import Renderable_CardInfo
from templates.playset_entity import PlaysetEntity
from templates.tag_template import Tag_Template
from templates.type_enums import card_enum_t, type_enum_t, identifier_t

def identifier(obj: Renderable_CardInfo) -> identifier_t:
    """
    Returns an identifier from the info given.
    """
    return (obj.type_enum, obj.card_enum)

def identifier_to_playset_entity(identifier: identifier_t) -> Type[PlaysetEntity]:
    """
    Returns the playset entity for the identifier.
    """
    if identifier not in Renderable_CardInfo.identifier_to_playset_entity:
        return None

    return Renderable_CardInfo.identifier_to_playset_entity[identifier]

#abbreviation
idf_to_pe: Callable[[identifier_t], Type[PlaysetEntity]] = identifier_to_playset_entity

def tag_to_playset_entities(tag: type[Tag_Template]) -> list[ Type[PlaysetEntity] ]:
    """
    This function returns a list of all
    PlaysetEntity classes that are tagged with the given tag.
    """

    if tag not in Renderable_CardInfo.tag_to_identifier:
        return []

    identifier_set: set[identifier_t] = Renderable_CardInfo.tag_to_identifier[tag]
    #now mapping
    playset_entity_list: list[ Type[PlaysetEntity] ] = list(map(lambda pid: Renderable_CardInfo.identifier_to_playset_entity[pid], identifier_set )))

    return playset_entity_list

#abbreviation
tag_to_pes: Callable[[type[Tag_Template]], list[Type[PlaysetEntity]]] = tag_to_playset_entities
