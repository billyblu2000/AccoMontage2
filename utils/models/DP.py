import copy
import random
from typing import List, Union
import numpy as np
import pretty_midi

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression, read_progressions, print_progression_list
from utils.utils import MIDILoader, Logging, listen, combine_ins
from utils.structured import major_map_backward, minor_map_backward


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
            'pos': List[str]   # list of string, each indicating the type (position)
                               # of the corresponding melody phrase
        }
        The meta info of the input melody.
    templates : List[ChordProgression]
        Template database. List of ChordProgressions.
    """

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression]):
        Logging.debug('init DP model...')
        self.melo = self.__split_melody(melo)  # melo : List(List) 是整首歌的melo
        self.melo_meta = self.__handle_meta(melo_meta)
        self.templates = templates
        self.max_num = 700  # 每一个phrase所对应chord progression的最多数量
        self._dp = np.array(
            [[None] * self.max_num] * len(self.melo))  # replace None by ([], 0) tuple of path index list and score
        self.solved = False
        self.result = None
        self.all_patterns = self.__analyze_pattern()
        Logging.debug('init DP model done')

    def solve(self):
        Logging.info('Melody length {l}, generate progression with {n} templates'.format(l=len(self.melo),
                                                                                         n=len(self.templates)))
        templates = []
        weight = 0.5
        for i in range(len(self.melo)):
            melo = self.melo[i]
            melo_meta = copy.copy(self.melo_meta)
            melo_meta['pos'] = self.melo_meta['pos'][i]
            # TODO: template now contains a confidence level, some codes to be change
            templates.append(self.pick_templates(melo, melo_meta))
            for j in range(len(templates[i])):
                if i == 0:
                    self._dp[i][j] = ([j], self.phrase_template_score(self.melo[i], templates[i][j][1]))
                else:
                    # max_previous = max([self._dp[i - 1][t]
                    #                     + self.transition_score(i, templates[i][j], templates[i][t]) for t in range(self.max_num)])
                    previous = [weight * self._dp[i - 1][t][1]
                                + (1 - weight) * self.transition_score(melo_meta['pos'], templates[i][j][1],
                                                                       templates[i - 1][t][1])
                                for t in range(min([self.max_num, len(templates[i - 1])]))]
                    max_previous = max(previous)
                    max_previous_index = previous.index(max(previous))
                    path_l = copy.copy(self._dp[i - 1][max_previous_index][0])
                    path_l.append(j)
                    self._dp[i][j] = (
                        path_l, self.phrase_template_score(self.melo[i], templates[i][j][1]) + max_previous)
            Logging.debug('dp with i = {}: '.format(i), self._dp[i])

        # 记录生成和弦进行的分数用于定量横向比较生成和弦的质量（不同旋律间对比），除以乐段数量因为每一段都会加分
        max_score = max([self._dp[-1][i][1] for i in range(min([self.max_num, len(templates[-1])]))])
        best_score = max_score / len(self.melo)
        # find the path，
        last_index = [self._dp[-1][i][1] for i in range(min([self.max_num, len(templates[-1])]))].index(max_score)
        result_path_index = self._dp[-1][last_index][0]
        result_path = []
        for i in range(len(self.melo)):
            index = result_path_index[i]
            result_path.append(templates[i][index])

        # 不管下面了，直接在dp里记录了路径

        # TODO: This is not the actual path...?
        # TODO: 算法应该选择使 dp[-1]=max 的路径，而不是每轮dp迭代的最优路径?
        # last_index = self._dp[-1].index(max(self._dp[-1]))
        # result_path = [templates[-1][last_index]]
        # i = len(self.melo) - 1
        # while i >= 0:
        #     i -= 1
        #     index = self._dp[i].index(max(self._dp[i]))
        #     result_path.append(templates[i][index])
        self.solved = True
        self.result = (result_path, best_score)
        return result_path, best_score

    def __get_all_available_chords(self) -> List[Chord]:
        pass

    # input是分好段的melo
    def pick_templates(self, melo, melo_meta) -> List[List[Union[float, ChordProgression]]]:

        if melo_meta['mode'] == 'maj':
            melo_meta['mode'] = 'M'
        elif melo_meta['mode'] == 'min':
            melo_meta['mode'] = 'm'

        available_templates = []

        for i in self.templates:
            if len(i) * 2 == len(melo) \
                    and i.meta['metre'] == melo_meta['metre'] \
                    and i.meta['mode'] == melo_meta['mode']:
                confidence_level = self.__progression_melo_type_match(melo_meta['pos'], i.meta['type'])
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
        return weight * self.__match_template_and_pattern(chord) + (1 - weight) * self.__match_melody_and_chord(melo,
                                                                                                                chord)

    # 微观
    @staticmethod
    def __match_melody_and_chord(melody_list: list, progression: ChordProgression, mode='M') -> float:
        musical_knowledge = [  # row: chord; col: melody
            [1, 0.1, 0.4, 0.15, 0.75, 0.7, 0.1, 0.9, 0.1, 0.7, 0.15, 0.2],
            [0.4, 0.1, 1, 0.1, 0.4, 0.75, 0.4, 0.5, 0.1, 0.9, 0.15, 0.4],
            [0.5, 0.1, 0.4, 0.15, 1, 0.3, 0.2, 0.75, 0.2, 0.6, 0.15, 0.9],
            [0.9, 0.1, 0.6, 0.2, 0.5, 1, 0.1, 0.4, 0.4, 0.75, 0.2, 0.2],
            [0.5, 0.1, 0.9, 0.1, 0.5, 0.5, 0.1, 1, 0.1, 0.5, 0.15, 0.75],
            [0.75, 0.1, 0.6, 0.15, 0.9, 0.5, 0.1, 0.4, 0.1, 1, 0.15, 0.4],
            [0.4, 0.1, 0.8, 0.15, 0.6, 0.8, 0.1, 0.6, 0.1, 0.4, 0.15, 1],
        ]

        total_score = 0.0
        chord_list = progression.get(only_root=True, flattened=True)
        for i in range(len(chord_list)):
            # this_chord = chord_list[i].to_number(tonic='C')
            this_chord = chord_list[i]
            if mode == 'M':
                this_note = [major_map_backward[melody_list[i * 2]], major_map_backward[melody_list[i * 2 + 1]]]
            else:
                this_note = [minor_map_backward[melody_list[i * 2]], minor_map_backward[melody_list[i * 2 + 1]]]
            total_score += musical_knowledge[int(this_chord) - 1][this_note[0]] if this_note[0] != -1 else 0.5
            total_score += musical_knowledge[int(this_chord) - 1][this_note[1]] if this_note[1] != -1 else 0.5

        return total_score / len(melody_list)

    # 中观
    def __match_template_and_pattern(self, cp: ChordProgression) -> float:

        # final_score = 0
        # max_length = min([len(cp), max([len(i) for i in self.templates])])
        # weight_denominator = (max_length ** 2 + max_length - 2) // 2
        # for length in range(2, max_length + 1):
        #     cursor = 0
        #     prog = cp.get(only_root=True, flattened=True)
        #     length_total_score = 0
        #     while cursor + length <= len(prog):
        #         pattern = tuple(prog[cursor:cursor + length])
        #         if pattern in self.all_patterns[length].keys():
        #             length_total_score += self.all_patterns[length][pattern]
        #         cursor += 1
        #     length_avg_score = length_total_score / cursor
        #     final_score += (length / weight_denominator) * length_avg_score
        return 0.5

    def __analyze_pattern(self):
        Logging.debug('analyze pattern...')
        all_patterns = {0: {}, 1: {}}
        # max_length = max([len(i) for i in self.templates])
        # for i in range(2, max_length + 1):
        #
        #     length = i
        #     count_pattern = {}
        #     # count pattern
        #     for cp in self.templates:
        #         prog = cp.get(only_root=True, flattened=True)
        #         cursor = 0
        #         while cursor + length <= len(prog):
        #             pattern = tuple(prog[cursor:cursor + length])
        #             if pattern in count_pattern.keys():
        #                 count_pattern[pattern] += 1
        #             else:
        #                 count_pattern[pattern] = 1
        #             cursor += 1
        #     # normalize
        #     max_appears = max(count_pattern.values())
        #     for key in count_pattern.keys():
        #         count_pattern[key] /= max_appears
        #
        #     all_patterns[i] = count_pattern
        Logging.debug('analyze pattern done')
        return all_patterns

    # transition prob between i-th phrase and (i-1)-th
    def transition_score(self, i, cur_template, prev_template):
        return 0.4 + random.random() / 0.5

        # 计算和弦变换速度是否匹配
        # prev_duration = 1
        # for i in range(len(prev_template.progression[-1])):
        #     if prev_template.progression[-1][i] == prev_template.progression[-1][i - 1]:
        #         prev_duration += 1
        #     else:
        #         break
        #
        # cur_duration = 1
        # for i in range(len(cur_template.progression[0])):
        #     if cur_template.progression[0][i] == cur_template.progression[0][i - 1]:
        #         cur_duration += 1
        #     else:
        #         break
        #
        # duration_match = cur_duration - prev_duration
        #
        # # first bar of cur cp and last bar of prev cp 接在一起对这两个小节做中观打分
        # transition_bars = prev_template.progression[-1] + cur_template.progression[0]

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

    def get_progression(self):
        if not self.solved:
            self.solve()
        picked_prog = [i[1] for i in self.result[0]]
        return picked_prog

    def get_progression_join_as_midi(self, tonic=None):
        progressions = self.get_progression()
        if not tonic:
            tonic = self.melo_meta['tonic']
        if tonic == '':
            Logging.error('DP.get_progression_join_as_midi: Cannot convert progressions into midi until tonic is '
                          'assigned!')
            return None
        midis = [progression.to_midi(tonic=tonic) for progression in progressions]
        lens = [len(progression) for progression in progressions]
        ins = pretty_midi.Instrument(program=0)
        shift = 0
        for i in range(len(midis)):
            notes = midis[i].instruments[0].notes
            for note in notes:
                note.start += shift
                note.end += shift
                ins.notes.append(note)
            shift += lens[i] * 0.25
        return ins


if __name__ == '__main__':
    # load midi
    pop909_loader = MIDILoader(files='POP909')
    pop909_loader.config(output_form='number')
    melo_source_name = MIDILoader.auto_find_pop909_source_name(start_with='114')[:5]
    test_melo = [pop909_loader.get(name=i) for i in melo_source_name]
    test_melo_meta = {
        'tonic': '',
        'metre': '4/4',
        'mode': 'maj',
        'pos': [name[6] for name in melo_source_name]
    }
    my_dp_model = DP(melo=test_melo, melo_meta=test_melo_meta, templates=read_progressions())
    my_dp_model.solve()
    print_progression_list(my_dp_model.get_progression())
    chord_ins = my_dp_model.get_progression_join_as_midi(tonic='C')
    melo_ins = MIDILoader.melo_to_midi([i for seg in test_melo for i in seg])
    combine_ins(melo_ins,chord_ins).write('test2.mid')
