from chords.ChordProgression import ChordProgression
from typing import List


class DP:

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates
        self.solve()

    def solve(self) -> ChordProgression:
        pass

    def match_template(self, progression: ChordProgression) -> int:
        pass

    def bar_melody_to_chord_score(self, bar_melody: list) -> dict:
        pass


if __name__ == '__main__':
    dp = DP()
    dp.solve()
