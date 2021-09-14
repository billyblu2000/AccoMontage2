import difflib

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from typing import List, Union
from utils import constants
from utils.structured import major_map_backward, minor_map_backward


# core DP algorithm
class DPTemplateSpan:
    _dp: List[List[Union[float, list]]]
    result: List[Chord]

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression],
                 melody_attention_level=0.5, popular_pattern_trust_level=0.5):

        # init attributes
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates
        self._dp = [[0.0, []]]  # DP memo, type: List[List[Union[float, List[Chord]]]]
        self.result = []  # final result, type: List[Chord]
        self.solved = False

        # init parameters
        self.melody_attention_level = melody_attention_level
        self.popular_pattern_trust_level = popular_pattern_trust_level

        # preprocess attributes
        self._template_span = self.__span_template()  # span template
        self._max_template_length = max([len(i) for i in self._template_span])
        self._pattern_socre = self.__analyze_pattern()  # analyze template pattern

    def solve(self):

        all_chords = self.__get_all_available_chords()
        cursor = 2

        # DP iteration
        while cursor <= len(self.melo):
            melody_seg = self.melo[:cursor]
            candidate_pool = []  # all candidate progressions, waiting to max

            # dp[n-1] -> dp[n]
            for chord in all_chords:
                exploration = self._dp[-1][1] + [chord]
                candidate_pool.append(exploration)

            # dp[n-m] -> dp[n]
            for pos in range(len(self._dp) - 1):
                for template_item in self._template_span:
                    template = template_item[0]
                    if len(template) == len(self._dp) - pos:
                        exploration = self._dp[pos][1] + template
                        candidate_pool.append(exploration)

                # stop when no longer template, that is, let m <= max template length
                if len(self._dp) - pos > self._max_template_length:
                    break

            # max candidate, and store progression into DP memo
            self._dp.append(self.__select_max_candidate(candidate_pool, melody_seg))

            cursor += 2

        self.result = self._dp[-1][1]
        self.solved = True

    # util func, provide all available chords, the spare parts
    def __get_all_available_chords(self) -> List[Chord]:
        # TODO: This is only a toy implementation
        # chord_list = []
        # for i in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
        #     chord = Chord()
        #     chord.root = i
        #     if i in ['C', 'F', 'G']:
        #         chord.type = constants.MAJ_TRIAD
        #     elif i in ['D', 'E', 'A']:
        #         chord.type = constants.MIN_TRIAD
        #     else:
        #         chord.type = constants.DIM_TRIAD
        #     chord_list.append(chord)
        chord_list = [1,2,3,4,5,6,7]
        return chord_list

    # util func to span template
    def __span_template(self) -> (List[List[Union[List[Chord], float]]], List[List[Union[List[Chord], float]]]):
        pass

    # 往两个方向span, 1. 变得更简单,general, 作为最基本的模版
    #               2. 变得更复杂,更短, 作为 modification, 拼凑的原料
        available_templates = []
        for i in self.templates:
            if len(i.progression[0]) == len(self.melo[0]) and i.meta['type'] == self.melo_meta['type'] \
                    and i.meta['mode'] == self.melo_meta['mode']:
                available_templates.append(i)

        # 1
        general_span = []
        min_unit = 2  # half note as the shortest duration
        for template in available_templates:
            duration = len(template.progression[0]) // min_unit
            for i in range(len(template.progression)):
                for t in range(min_unit):
                    slice = template.progression[i][duration * t: duration * (t+1)]
                    result = all(e == slice[0] for e in slice)
                    if result:
                        continue
                    else:
                        break
            general_span.append(template)

        # 2
        ingredient_span = []
        for template in general_span:
            duration = len(template.progression[0]) // min_unit
            for i in range(len(template.progression)):
                template_copy1 = template.progression[i]
                template_copy2 = template.progression[i]
                for t in range(min_unit):
                    template_copy1.progression[i] = [].append(template.progression[i][t * duration])
                    if len(template.progression[0]) == 8:
                        template_copy2.progression[i] = [].append(2 * [template.progression[i][t * duration]])

                ingredient_span.append(template_copy1)
                ingredient_span.append(template_copy2)

        # for template in available_templates:



    # '中观', called in self.__select_max_candidate
    def __match_progression_and_template_span(self, progression: list) -> float:
        if len(progression) == 1:
            return 1
        else:

            max_score = 0.0
            pattern_socre = self._pattern_socre[len(progression)]
            for item in pattern_socre.items():
                sim_socre = difflib.SequenceMatcher(None, item[0], progression).ratio()
                trust_score = item[1]
                score = self.popular_pattern_trust_level * trust_score \
                        + (1 - self.popular_pattern_trust_level) * sim_socre
                if score >= max_score:
                    max_score = score

            return max_score

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

    # max candidate
    def __select_max_candidate(self, candidate_pool: List[List[Chord]], melody: List) \
            -> List[Union[float, List[Chord]]]:
        score_list = []
        melody_attention_level = self.melody_attention_level
        for candidate in candidate_pool:
            micro_match = self.__match_melody_and_chord(melody_list=melody, chord_list=candidate)
            macro_match = self.__match_progression_and_template_span(progression=candidate)
            score = micro_match * melody_attention_level + macro_match * (1 - melody_attention_level)
            score_list.append(score)
        max_score = max(score_list)
        max_progression = candidate_pool[score_list.index(max_score)]
        return [max_score, max_progression]

    # '微观', called in self.__select_max_candidate
    @staticmethod
    def __match_melody_and_chord(melody_list: list, chord_list: list, mode='M') -> float:
        # TODO: This is only a toy implementation
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
        for i in range(len(chord_list)):
            # this_chord = chord_list[i].to_number(tonic='C')
            this_chord = chord_list[i]
            if mode == 'M':
                this_note = [major_map_backward[melody_list[i * 2]], major_map_backward[melody_list[i * 2 + 1]]]
            else:
                this_note = [minor_map_backward[melody_list[i * 2]], minor_map_backward[melody_list[i * 2 + 1]]]
            total_score += musical_knowledge[int(this_chord) - 1][this_note[0]]
            total_score += musical_knowledge[int(this_chord) - 1][this_note[1]]

        return total_score / len(melody_list)

    # output final result
    def get_progression(self) -> ChordProgression:
        if self.solved:
            return ChordProgression()
        else:
            raise Exception("Please call the solve method first!")

    def test(self):
        pass


if __name__ == '__main__':
    melo = [4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    template_1 = [[2, 2, 2, 2, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1, 1, 1]]
    template_2 = [[4, 4, 4, 4, 5, 5, 5, 5, ], [3, 3, 3, 3, 6, 6, 6, 6, ], [4, 4, 4, 4, 5, 5, 5, 5, ],
                  [1, 1, 1, 1, 1, 1, 1, 1, ]]
    cp_1 = ChordProgression()
    cp_1.progression = template_1
    cp_2 = ChordProgression()
    cp_2.progression = template_2
    dp = DPTemplateSpan(melo=melo, melo_meta={}, templates=[cp_1, cp_2])
    dp.solve()
    print(dp.result)
