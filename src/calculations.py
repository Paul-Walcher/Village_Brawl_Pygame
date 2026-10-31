"""
File for calculations and maths
"""
from __future__ import annotations
from typing import Callable, Any

import pygame

from collections.abc import Iterable
import random

def point_collides(point: tuple[int, int], rect: pygame.Rect) -> bool:
    """
    Checks whether the point collides with the rect given.
    """
    x: int = point[0]
    y: int = point[1]

    return (not (
                    x < rect.x or x > rect.x + rect.width\
                    or\
                    y < rect.y or y > rect.y + rect.height
            ))

def rect_collides(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """
    Checks whether the two rectangles collide.
    """
    return (not (
                    rect1.x + rect1.width < rect2.x or rect1.x > rect2.x + rect2.width\
                    or\
                    rect1.y + rect1.height < rect2.y or rect1.y > rect2.y + rect2.height
            ))

class Weightlist(list):
    """
    This class represents a list of weights, from which objects can be randomly drawn.
    The object drawn is represented by a tuple (index, association), where
    association == None if association was not specified.

    This class extends list, and adds functionality to randomly draw a object by using
    the objects weight / sum(all weights) as percentage.

    Additionally functions are added to add weights while keeping the overall sum
    of all weights the same as before the addition.

    Example for keeping the sum stable:

    e.g.
    x = Weightlist([...])
    sx = sum(x)
    x.insert_with_fixed_sum(index, val)
    sx2 = sum(x)
    sx == sx2 -> True
    """

    def __init__(self, iterables: Iterable = (), associations: list = None):
        super().__init__(iterables)
        self.associations: list = (associations if associations is not None else [None] * len(self))
        """
        associations is a list of objects, that will be returned together
        with the index when drawing randomly.
        """

    def _draw_index(self) -> int:
        """
        Protected method, draws an index from the own list
        by using self[index] / sum(self) as the percentage for 'index'.
        Returns the selected index.
        """

        plist: list[float] = self.as_percentages()

        for i in range(1, len(plist)):
            plist[i] += plist[i-1]

        plist.insert(0, 0.0)
        plist[-1] = 1.0

        rnum: float = random.uniform(0, 1.0)

        for i in range(len(plist)-1):

            if rnum >= plist[i] and rnum < plist[i+1]:
                return i


        return len(plist)-1


    def fix_sum_to(self, tsum: float) -> None:
        """
        Sets the sum of the own list to tsum,
        by calculating the percentages, then multiplying the
        percentage by the new sum.
        """

        wsum: float = sum(self)
        diff: float = tsum - wsum

        for i in range(len(self)):
            self[i] += self[i] / wsum * diff


    def insert_with_fixed_sum(self, idx: int, val: float) -> None:
        """
        Inserts the new value while keeping the sum stable.
        """
        wsum: float = sum(self)
        tsum: float = wsum - val
        self.fix_sum_to(tsum)
        self.insert(idx, val)

    def set_to_with_fixed_sum(self, idx: int, val: float) -> None:
        """
        Sets the value at index idx to val,
        while keeping the sum stable
        """
        wsum: float = sum(self) - val
        self[idx] = 0
        self.fix_sum_to(wsum)
        self[idx] = val

    def append_with_fixed_sum(self, val: float) -> None:
        """
        Appends val while keeping the sum stable
        """
        wsum: float = sum(self)
        tsum: float = wsum - val
        self.fix_sum_to(tsum)
        self.append(val)

    def pop_with_fixed_sum(self, idx: int) -> None:
        """
        Pops the index and returns the popped value
        while keeping the sum stable
        """
        wsum: float = sum(self)
        val: float = self[idx]
        tsum: float = wsum
        back: float = self.pop(idx)
        self.fix_sum_to(tsum)
        return back

    def as_percentages(self) -> list[float]:
        """
        Returns the whole list but instead of weights,
        its the percentage of each index being drawn.
        """
        wsum: float = sum(self)
        back: list[float] = []

        for v in self:
            back.append(v / wsum)

        return back

    def draw(self, n: int = 1, zero_drawn_included: bool = False) -> dict[tuple[int, object], int]:
        """
        n: int                      | The amount of draws (All draws are independent)

        zero_drawn_included: bool   | If this is true, the returned dict will
                                      have the indices that were not drawn included with amount drawn == 0

        Draws n times independently, then returns a dictionary where the keys are
        tuples with: (index, associations[index]): times_drawn,
        where the keys are tuples with index and association, and the value is how often it was drawn.
        """

        back: dict[tuple[int, object], int] = {}

        if zero_drawn_included:
            back = {(idx, self.associations[idx]): 0 for i in range(len(self))}

        for i in range(n):
            idx: int = self._draw_index()

            key: tuple[int, object] = (idx, self.associations[idx])
            if key not in back:
                back[key] = 0

            back[key] += 1

        return back
