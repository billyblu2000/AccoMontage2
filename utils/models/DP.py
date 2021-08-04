import difflib

from chords.ChordProgression import ChordProgression
from typing import List


# core DP algorithm
class DP:

    def __init__(self, melo: list, melo_meta: dict, templates: List[list]):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates
        self.template_span = self.__span_template()
        self.solved = False
        self.solve()

    def solve(self) -> list:
        pass
        self.solved = True
        pass

    def __span_template(self) -> List[list]:
        pass

    def __match_template(self, progression: list) -> int:
        pass

    def __bar_melody_to_chord_score(self, bar_melody: list) -> dict:
        if bar_melody == [1]:
            chord_score = {1: 1, 2: 0.5, 3: 0.5, 4: 0.9, 5: 0.5, 6: 0.8, 7: 0.5}
        elif bar_melody == [2]:
            chord_score = {1: 0.5, 2: 1, 3: 0.5, 4: 0.5, 5: 0.9, 6: 0.5, 7: 0.8}
        elif bar_melody == [3]:
            chord_score = {1: 0.8, 2: 0.5, 3: 1, 4: 0.5, 5: 0.5, 6: 0.9, 7: 0.5}
        elif bar_melody == [4]:
            chord_score = {1: 0.5, 2: 0.8, 3: 0.5, 4: 1, 5: 0.5, 6: 0.5, 7: 0.9}
        elif bar_melody == [5]:
            chord_score = {1: 0.9, 2: 0.5, 3: 0.8, 4: 0.5, 5: 1, 6: 0.5, 7: 0.5}
        elif bar_melody == [6]:
            chord_score = {1: 0.5, 2: 0.9, 3: 0.5, 4: 0.8, 5: 0.5, 6: 1, 7: 0.5}
        elif bar_melody == [7]:
            chord_score = {1: 0.5, 2: 0.5, 3: 0.9, 4: 0.5, 5: 0.8, 6: 0.5, 7: 1}
        else:
            chord_score = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
        return chord_score

    def get_progression(self) -> List[list]:
        if self.solved:
            pass
        else:
            raise Exception("Please call the solve method first!")


# Adapter: DP <--> ChordProgression
class MyDPModel(DP):

    def __init__(self, melo: list, melo_meta: dict, templates: list):
        # TODO: add adapter
        pass
        super().__init__(melo, melo_meta, templates)

    def get_progression(self):
        # TODO: add adapter
        pass


if __name__ == '__main__':
    # dp = DP()
    # dp.solve()
    print([1] in [1, 2])
