from typing import List, Union

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from utils.dictionary import major_map_backward, minor_map_backward

class DP:

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates

        self._dp = []
        self.result = []


    def solve(self):
        pass

    def __get_all_available_chords(self) -> List[Chord]:
        pass


    def pick_templates(self) -> List[List[Union[float, ChordProgression]]]:
        available_templates = []
        for i in self.templates:
            if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == self.melo_meta['type'] \
                    and i.meta['mode'] == self.melo_meta['mode']:
                template = i
                for j in range(len(template.progression)):
                    duration = len(template.progression[j]) // self.min_unit
                    for t in range(self.min_unit):
                        template.progression[j] = [].append(template.progression[j][t * duration])
                available_templates.append(template)

        return available_templates

    # 微观
    @staticmethod
    def __match_melody_and_chord(melody_list: list, chord_list: list, mode='M') -> float:
       pass

    # 中观
    def __analyze_pattern(self):
        all_patterns = {0: {}, 1: {}, }
        for i in range(2, len(self.melo) // 2 + 1):

            length = i
            count_pattern = {}
            # count pattern
            for cp in self.templates:
                prog = [j for j in cp]
                cursor = 0
                while cursor + length < len(prog):
                    pattern = tuple(prog[cursor:cursor + length])
                    if pattern in count_pattern.keys():
                        count_pattern[pattern] += 1
                    else:
                        count_pattern[pattern] = 1
                    cursor += 1
            # normalize
            max_appears = max(count_pattern.values())
            for key in count_pattern.keys():
                count_pattern[key] /= max_appears

            all_patterns[i] = count_pattern

        return all_patterns

    def transition_score(self):
        pass