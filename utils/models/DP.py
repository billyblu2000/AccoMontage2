import difflib

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from typing import List


# core DP algorithm
class DP:
    _dp: List[List[float, List[Chord]]]
    result: List[Chord]

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates
        self.template_span = self.__span_template()
        self.max_template_length = max([len(i) for i in self.template_span])
        self.solved = False
        self._dp = [[0.0, []]]
        self.result = []

        self.solve()

    def solve(self):
        all_chords = self.__get_all_available_chords()
        cursor = 2
        while cursor <= len(self.melo):
            melody_seg = self.melo[:cursor]
            candidate_pool = []
            for chord in all_chords:
                exploration = self._dp[(cursor - 2) // 2][1] + [chord]
                candidate_pool.append(exploration)
            for i in range(len(self._dp)):


        self.solved = True
        pass

    def __get_all_available_chords(self) -> List[Chord]:
        pass

    def __span_template(self) -> List[List[List[Chord], float]]:
        pass

    def __match_progression_and_template_span(self, progression: list) -> float:
        pass

    @staticmethod
    def __match_melody_and_chord(melody_list: list, chord_list: list) -> float:
        pass

    def get_progression(self) -> ChordProgression:
        if self.solved:
            pass
        else:
            raise Exception("Please call the solve method first!")


if __name__ == '__main__':
    # dp = DP()
    # dp.solve()
    print([1] in [1, 2])