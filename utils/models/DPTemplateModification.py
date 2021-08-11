from typing import List, Any, Union

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression


class DPTemplateModification:

    _dp: List[List[Union[float, List[Any]]]]

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression],
                 min_unit:int, termination:int):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates

        self.min_unit = min_unit
        self.termination = termination

        self._dp = [[0.0, []]]
        self.result = []

    def solve(self):
        pass

    def pick_templates(self) -> List[List[Union[float, ChordProgression]]]:
        pass

    # 微观
    @staticmethod
    def __match_melody_and_chord(melody_list: list, chord_list: list, mode='M') -> float:
        pass

    # 中观
    def __evaluate_modification(self, progression: list) -> float:
        pass

    def __select_max_candidate(self, candidate_pool: List[List[Chord]], melody: List) \
            -> List[Union[float, List[Chord]]]:
        pass

    def int_to_chord(self, int_list: List[int]) -> List[Chord]:
        pass

    def get_progression(self) -> ChordProgression:
        pass

