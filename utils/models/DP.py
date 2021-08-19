from typing import List, Union

import numpy as np
from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from utils.utils import MIDILoader




class DP:

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        self.melo = melo  # melo : List(List) 是整首歌的melo
        # self.melo_meta = melo_meta
        self.templates = templates
        self.max_num = 200  # 每一个phrase所对应chord progression的最多数量
        self._dp = np.array([0] * self.max_num * len(self.melo))
        self.result = []

        # melo分段的数据

    def solve(self):
        for i in range(len(self.melo)):
            melo = self.melo[i]
            melo_meta = {}
            templates = self.pick_templates(melo, melo_meta)
            if i == 0:
                for j in range(len(templates)):
                    self._dp[i][j] = self.phrase_template_score(self.melo[i], templates[j])
            for j in range(len(templates)):
                self._dp[i][j] = self.phrase_template_score(self.melo[i], templates[j]) + \
                                 max([self._dp[i-1][t] + self.transition_score(i, j, t) for t in range(self.max_num)])


    def __get_all_available_chords(self) -> List[Chord]:
        pass


    # input是分好段的melo
    def pick_templates(self, melo, melo_meta) -> List[List[Union[float, ChordProgression]]]:
        available_templates = []
        for i in self.templates:
            if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == melo_meta['type'] \
                    and i.meta['mode'] == melo_meta['mode']:
                # template = i
                # for j in range(len(template.progression)):
                #     duration = len(template.progression[j]) // self.min_unit
                #     for t in range(self.min_unit):
                #         template.progression[j] = [].append(template.progression[j][t * duration])
                available_templates.append(i)

        return available_templates

    # 微观 + 中观
    def phrase_template_score(self, melo, chord, weight):
        return weight * self.__analyze_pattern() + (1 - weight) * self.__match_melody_and_chord(melo, chord)


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

    # transition prob between i-th phrase and (i-1)-th
    def transition_score(self, i, cur_template, prev_template):
        pass

    def __split_melody(self, melo):
        if type(melo[0]) is list:
            return melo
        else:
            split = [[]]
            pass
            return split

if __name__ == '__main__':

        # load midi
        my_midis = MIDILoader()  # load every midi files in the midi folder
        melo_name = input()
        get_midi = my_midis.get(name=melo_name)

        # transform get_midi into melo (list of lists)