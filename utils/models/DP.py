import difflib

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from typing import List


# core DP algorithm
class DP:

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates
        self.template_span = self.__span_template()
        self.solved = False
        self.result = []
        self.solve()

    def solve(self):
        pass
        self.solved = True
        pass

    def __span_template(self) -> List[List[List[Chord], float]]:
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

    def get_progression(self) -> ChordProgression:
        if self.solved:
            pass
        else:
            raise Exception("Please call the solve method first!")


if __name__ == '__main__':
    # dp = DP()
    # dp.solve()
    print([1] in [1, 2])
