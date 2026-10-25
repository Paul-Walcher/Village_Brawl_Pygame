"""
File for calculations and maths
"""
import random


class Weightlist(list):

    def __init__(self, iterables=(), associations=None):
        super().__init__(iterables)
        self.associations = (associations if associations is not None else [None] * len(self))

    def _draw_index(self):

        plist = self.as_percentages()

        for i in range(1, len(plist)):
            plist[i] += plist[i-1]

        plist.insert(0, 0.0)
        plist[-1] = 1.0

        rnum = random.uniform(0, 1.0)

        for i in range(len(plist)-1):

            if rnum >= plist[i] and rnum < plist[i+1]:
                return i


        return len(plist)-1


    def fix_sum_to(self, tsum):

        wsum = sum(self)
        diff = tsum - wsum

        for i in range(len(self)):
            self[i] += self[i] / wsum * diff


    def insert_with_fixed_sum(self, idx, val):

        wsum = sum(self)
        tsum = wsum - val
        self.fix_sum_to(tsum)
        self.insert(idx, val)

    def set_to_with_fixed_sum(self, idx, val):

        wsum = sum(self) - val
        self[idx] = 0
        self.fix_sum_to(wsum)
        self[idx] = val

    def append_with_fixed_sum(self, val):

        wsum = sum(self)
        tsum = wsum - val
        self.fix_sum_to(tsum)
        self.append(val)

    def pop_with_fixed_sum(self, idx):

        wsum = sum(self)
        val = self[idx]
        tsum = wsum
        back = self.pop(idx)
        self.fix_sum_to(tsum)
        return back

    def as_percentages(self):

        wsum = sum(self)
        back = []

        for v in self:
            back.append(v / wsum)

        return back

    def draw(self, n=1, zero_drawn_included=False):

        back = {}

        if zero_drawn_included:
            back = {(idx, self.associations[idx]): 0 for i in range(len(self))}

        for i in range(n):
            idx = self._draw_index()

            key = (idx, self.associations[idx])
            if key not in back:
                back[key] = 0

            back[key] += 1

        return back
