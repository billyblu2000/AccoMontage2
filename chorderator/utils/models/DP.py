import copy
import pickle
import random
from typing import List, Union
import numpy as np
import pretty_midi

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression, read_progressions, print_progression_list
from utils.string import STATIC_DIR
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
        self.max_num = 10000  # 每一个phrase所对应chord progression的最多数量
        self._dp = np.array(
            [[None] * self.max_num] * len(self.melo))  # replace None by ([], 0) tuple of path index list and score
        self.solved = False
        self.result = None
        self.transition_dict = self.__load_transition_dict()
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
    def pick_templates(self, melo, melo_meta) -> List[List[Union[float, List[ChordProgression]]]]:

        temp_templates = []
        available_templates = []

        if melo_meta['mode'] == 'maj':
            melo_meta['mode'] = 'M'
            maj_temp = pickle.load(open('major_score', 'rb'))
            temp_templates += maj_temp
        elif melo_meta['mode'] == 'min':
            melo_meta['mode'] = 'm'
            min_temp = pickle.load(open('minor_score', 'rb'))
            temp_templates += min_temp

        for template in temp_templates:
            total_temp_length = 0
            for i in template[1]:
                total_temp_length += len(i)
            if total_temp_length == len(melo):
                available_templates.append(template)

        return available_templates

    def __progression_melo_type_match(self, melo_type, prog_type):

        if prog_type == 'unknown' or not prog_type:
            return 0.8

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
        musical_knowledge_M = [  # row: chord; col: melody
            [1, 0.1, 0.4, 0.15, 0.75, 0.7, 0.1, 0.9, 0.1, 0.7, 0.15, 0.2],
            [0.4, 0.1, 1, 0.1, 0.4, 0.75, 0.4, 0.5, 0.1, 0.9, 0.15, 0.4],
            [0.5, 0.1, 0.4, 0.15, 1, 0.3, 0.2, 0.75, 0.2, 0.6, 0.15, 0.9],
            [0.9, 0.1, 0.6, 0.2, 0.5, 1, 0.1, 0.4, 0.4, 0.75, 0.2, 0.2],
            [0.5, 0.1, 0.9, 0.1, 0.5, 0.5, 0.1, 1, 0.1, 0.5, 0.15, 0.75],
            [0.75, 0.1, 0.6, 0.15, 0.9, 0.5, 0.1, 0.4, 0.1, 1, 0.15, 0.4],
            [0.4, 0.1, 0.8, 0.15, 0.6, 0.8, 0.1, 0.6, 0.1, 0.4, 0.15, 1]
        ]

        musical_knowledge_m = [  # row: chord; col: melody
            [1, 0.1, 0.4, 0.75, 0.15, 0.7, 0.1, 0.9, 0.7, 0.1, 0.2, 0.15],
            [0.4, 0.1, 1, 0.4, 0.1, 0.75, 0.4, 0.5, 0.9, 0.1, 0.4, 0.15],
            [0.5, 0.1, 0.4, 1, 0.15, 0.3, 0.2, 0.75, 0.6, 0.2, 0.9, 0.15],
            [0.9, 0.1, 0.6, 0.5, 0.2, 1, 0.1, 0.4, 0.75, 0.4, 0.2, 0.2],
            [0.5, 0.1, 0.9, 0.5, 0.1, 0.5, 0.1, 1, 0.5, 0.1, 0.75, 0.15],
            [0.75, 0.1, 0.6, 0.9, 0.15, 0.5, 0.1, 0.4, 1, 0.1, 0.4, 0.15],
            [0.4, 0.1, 0.8, 0.6, 0.15, 0.8, 0.1, 0.6, 0.4, 0.1, 1, 0.15]
        ]

        total_score = 0.0
        chord_list = progression.get(only_root=True, flattened=True)
        for i in range(len(chord_list)):
            # this_chord = chord_list[i].to_number(tonic='C')
            this_chord = chord_list[i]
            if mode == 'M':
                this_note = [major_map_backward[melody_list[i * 2]], major_map_backward[melody_list[i * 2 + 1]]]
                total_score += musical_knowledge_M[int(this_chord) - 1][this_note[0]] if this_note[0] != -1 else 0.5
                total_score += musical_knowledge_M[int(this_chord) - 1][this_note[1]] if this_note[1] != -1 else 0.5
            else:
                this_note = [minor_map_backward[melody_list[i * 2]], minor_map_backward[melody_list[i * 2 + 1]]]
                total_score += musical_knowledge_m[int(this_chord) - 1][this_note[0]] if this_note[0] != -1 else 0.5
                total_score += musical_knowledge_m[int(this_chord) - 1][this_note[1]] if this_note[1] != -1 else 0.5

        return total_score / len(melody_list)

    # 中观
    def __match_template_and_pattern(self, template: [float, list]) -> float:

        return template[0]


    @staticmethod
    def __load_transition_dict():
        file = open(STATIC_DIR + 'transition_score.mdch', 'rb')
        my_dict = pickle.load(file)
        file.close()
        return my_dict

    # transition prob between i-th phrase and (i-1)-th
    def transition_score(self, i, cur_template, prev_template):
        transition_bars = prev_template.progression[-1] + cur_template.progression[0]
        if tuple(transition_bars) in self.transition_dict:
            return self.transition_dict[tuple(transition_bars)]

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

        # first bar of cur cp and last bar of prev cp 接在一起对这两个小节做中观打分
        # search for the occurrence of such chord sequence, regardless of chord duration

        chord_sequence_prev = [prev_template.progression[-1][0]]
        for i in prev_template.progression[-1]:
            chord_sequence_prev.append(i) if i != chord_sequence_prev[-1] else None

        chord_sequence_cur = [cur_template.progression[-1][0]]
        for i in cur_template.progression[0]:
            chord_sequence_cur.append(i) if i != chord_sequence_cur[-1] else None

        prev_part = [chord_sequence_prev[i:] for i in range(len(chord_sequence_prev))]
        cur_part = [chord_sequence_cur[:i + 1] for i in range(len(chord_sequence_cur))]

        # chord_sequences contains all sequences of chord that contains the transition two chords in the transition bars

        chord_sequences_dup = []
        for i in range(len(prev_part)):
            for j in range(len(cur_part)):
                chord_sequences_dup.append(prev_part[i] + cur_part[j])

        chord_sequences = []
        for c in chord_sequences_dup:
            new = [c[0]]
            for i in c:
                new.append(i) if i != new[-1] else None
            chord_sequences.append(new)

        # search the number of occurrence in the template space
        score = 0
        for template in self.templates:
            unique_temp = [template.get(only_root=True, flattened=True)[0]]
            for i in template.get(only_root=True, flattened=True):
                unique_temp.append(i) if i != unique_temp[-1] else None
            for chord_sequence in chord_sequences:
                # if chord_sequence in unique_temp:
                #     score += 1
                if len(chord_sequence) > len(unique_temp):
                    continue
                all_slices = [unique_temp[i:i + len(chord_sequence)]
                              for i in range(len(unique_temp) - len(chord_sequence) + 1)]
                new = []
                for slc in all_slices:
                    if len(slc) != 1:
                        new.append(slc)
                all_slices = new
                # print(all_slices, chord_sequence)
                for slc in all_slices:
                    if slc == chord_sequence:
                        score += 1
                        break

        # new_score = log_{max_score}(score)

        self.transition_dict[tuple(transition_bars)] = score

        return score / len(self.templates)

    def __split_melody(self, melo):
        if type(melo[0]) is list:
            return melo
        else:
            raise Exception('Model cannot handle melody in this form yet.')

    def __handle_meta(self, melo_meta):
        try:
            if melo_meta['metre'] and melo_meta['mode'] and melo_meta['pos'][0]:
                return melo_meta
        except:
            raise Exception('Model cannot handle melody meta in this form yet.')

    def get(self):
        if not self.solved:
            self.solve()
        picked_prog = [i[1] for i in self.result[0]]
        return picked_prog

    def get_progression_join_as_midi(self, tonic=None):
        progressions = self.get()
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
    my_dp_model = DP(melo=test_melo, melo_meta=test_melo_meta,
                     templates=read_progressions('progressions_representative.pcls'))
    my_dp_model.solve()
    print_progression_list(my_dp_model.get())
