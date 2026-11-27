"""
Provides the functions to operate on groups inside the renderable card listviewer.
"""
from __future__ import annotations
from typing import Any, Type, Callable, override

type listviewer_cardlist_element_t = tuple[Type[Renderable_CardInfo], int]
type listviewer_cardlist_t = list[listviewer_cardlist_element_t]
