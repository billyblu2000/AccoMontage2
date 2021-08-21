from typing import List, Union

import numpy as np
from chords.Chord import Chord
from chords.ChordProgression import ChordProgression, read_progressions
from utils.utils import MIDILoader


class DP:
    """
    Dynamic programming model to generate progression.

    Attributes
    ----------
    melo : List[List[int]]
        The input melody, a list of melody phrases, each melody
        phrase is also a list of int, indicating the note pitch.
    melo_meta : dict
        dict{
            'tonic': str,      # string indicating the tonic, e.g., 'C'
            'metre': str,      # string indicating the metre, e.g., '4/4'
            'mode': str,       # possible values: ['M', 'm', 'maj', 'min']
            'pos': List[str]   # list of string, each indication the type (position)
                               # of the corresponding melody phrase
        }
        The meta info of the input melody.
    templates : List[ChordProgression]
        Template database. List of ChordProgressions.
    """

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        self.melo = self.__split_melody(melo)  # melo : List(List) 是整首歌的melo
        self.melo_meta = self.__handle_meta(melo_meta)
        self.templates = templates
        self.max_num = 200  # 每一个phrase所对应chord progression的最多数量
        self._dp = np.array([[0] * self.max_num] * len(self.melo))
        self.result = []

    def solve(self):
        templates = []
        for i in range(len(self.melo)):
            melo = self.melo[i]
            melo_meta = self.melo_meta
            melo_meta['pos'] = melo_meta['pos'][i]
            # TODO: template now contains a confidence level, some codes to be change
            templates.append(self.pick_templates(melo, melo_meta))

            for j in range(len(templates)):
                if i == 0:
                    self._dp[i][j] = self.phrase_template_score(self.melo[i], templates[j])
                else:
                    # max_previous = max([self._dp[i - 1][t]
                    #                     + self.transition_score(i, templates[i][j], templates[i][t]) for t in range(self.max_num)])
                    max_previous = max([self._dp[i - 1][t]
                                        + self.transition_score(melo_meta['pos'], templates[i][j], templates[i - 1][t])
                                        for t in range(self.max_num)])
                    self._dp[i][j] = self.phrase_template_score(self.melo[i], templates[j]) + max_previous

        # 记录生成和弦进行的分数用于定量横向比较生成和弦的质量（不同旋律间对比），除以乐段数量因为每一段都会加分
        best_score = max(self._dp[-1]) / len(self.melo)

        # find the path

        result_path = []

        # TODO: This is not the actual path...
        # TODO: 算法应该选择使 dp[-1]=max 的路径，而不是每轮dp迭代的最优路径
        # last_index = self._dp[-1].index(max(self._dp[-1]))
        # result_path = [templates[-1][last_index]]
        # i = len(self.melo) - 1
        # while i >= 0:
        #     i -= 1
        #     index = self._dp[i].index(max(self._dp[i]))
        #     result_path.append(templates[i][index])

        return result_path, best_score

    def __get_all_available_chords(self) -> List[Chord]:
        pass

    # input是分好段的melo
    def pick_templates(self, melo, melo_meta) -> List[List[Union[float, ChordProgression]]]:

        available_templates = []
        for i in self.templates:
            if len(i.progression) == len(melo) \
                    and i.meta['metre'] == melo_meta['metre'] \
                    and i.meta['mode'] == melo_meta['mode']:
                confidence_level = self.__progression_melo_type_match(melo_meta['pso'], i.meta['type'])
                available_templates.append([confidence_level, i])

        return available_templates

    def __progression_melo_type_match(self, melo_type, prog_type):

        family = ['i', 'a', 'b', 'c', 'o', 'x']
        progression_type_family = {
            'i': ['fadein', 'intro', 'intro-b', 'pre-verse'],
            'a': ['verse'],
            'b': ['prechorus', 'pre-chorus', 'refrain', 'chorus'],
            'c': ['trans', 'transition', 'bridge'],
            'o': ['fadeout', 'outro', 'coda', 'ending'],
            'x': ['instrumental', 'interlude', 'solo']
        }
        family_shift_confidence_level = [
            [1, 0.7, 0.3, 0.4, 0.9, 0.3],
            [0.7, 1, 0.6, 0.6, 0.7, 0.5],
            [0.3, 0.4, 1, 0.6, 0.3, 0.5],
            [0.3, 0.4, 0.6, 1, 0.3, 0.5],
            [0.9, 0.7, 0.3, 0.4, 1, 0.3],
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        ]
        for item in progression_type_family.items():
            if prog_type in item[1]:
                prog_family = item[0]
                break
        else:
            raise Exception('prog_type value error')

        return family_shift_confidence_level[family.index(melo_type.lower())][family.index(prog_family)]

    # 微观 + 中观
    def phrase_template_score(self, melo, chord, weight=0.5):
        return weight * self.__analyze_pattern(chord) + (1 - weight) * self.__match_melody_and_chord(melo, chord)

    # 微观
    @staticmethod
    def __match_melody_and_chord(melody_list: list, chord_list: list, mode='M') -> float:
        pass

    # 中观
    def __analyze_pattern(self, chord_list):
        # TODO
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
        return 0

    def __split_melody(self, melo):
        if type(melo[0]) is list:
            return melo
        else:
            raise Exception('Model cannot handle melo in this form yet.')

    def __handle_meta(self, melo_meta):
        try:
            if melo_meta['metre'] and melo_meta['mode'] and melo_meta['pos'][0]:
                return melo_meta
        except:
            raise Exception('Model cannot handle melo meta in this form yet.')


if __name__ == '__main__':
    # load midi
    pop909_loader = MIDILoader(files='POP909')
    pop909_loader.config(output_form='number')
    melo_source_name = ['00301_i8',
                        '00302_A4',
                        '00303_A4',
                        '00304_B4',
                        '00305_B4',
                        ]
    test_melo = [pop909_loader.get(name=i) for i in melo_source_name]
    test_melo_meta = {
        'tonic': '',
        'metre': '4/4',
        'mode': 'maj',
        'pos': [name[6] for name in melo_source_name]
    }
    my_dp_model = DP(melo=test_melo, melo_meta=test_melo_meta, templates=read_progressions())
    my_dp_model.solve()
