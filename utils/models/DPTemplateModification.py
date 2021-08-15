from typing import List, Any, Union

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from utils.structured import major_map_backward, minor_map_backward


class DPTemplateModification:

    _dp: List[List[Union[float, List[Any]]]]

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression],
                 min_unit: int, termination: int):
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates

        self.min_unit = min_unit
        self.termination = termination

        self._dp = [[0.0, []]]
        self.result = []

    def solve(self):

        available_chords = self.__get_all_available_chords()
        available_templates = self.pick_templates()

        mod = 0

        while mod < self.termination:
            candidate_pool = []

            for chord in available_chords:
                for i in len(available_templates[0]):
                    new = self._dp[mod][1]
                    new[i] = chord
                    candidate_pool.append(new)

            self._dp.append(self.__select_max_candidate(candidate_pool, self.melo))

            mod += 1

        self.result = self._dp[-1][1]


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


    # pick and modify templates to match the min_unit
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
        musical_knowledge = [  # row: chord; col: melody
            [1.0, 0.1, 0.6, 0.1, 0.7, 0.8, 0.1, 0.9, 0.1, 0.7, 0.15, 0.5],
            [0.5, 0.1, 1.0, 0.1, 0.3, 0.7, 0.1, 0.9, 0.1, 0.7, 0.15, 0.4],
            [0.7, 0.1, 0.4, 0.1, 1.0, 0.3, 0.1, 0.6, 0.1, 0.8, 0.15, 0.8],
            [0.7, 0.1, 0.5, 0.1, 0.4, 1.0, 0.1, 0.4, 0.1, 0.6, 0.20, 0.3],
            [0.9, 0.1, 0.8, 0.1, 0.5, 0.7, 0.1, 1.0, 0.1, 0.5, 0.15, 0.7],
            [0.5, 0.1, 0.7, 0.1, 0.7, 0.6, 0.1, 0.4, 0.1, 1.0, 0.15, 0.4],
            [0.5, 0.1, 0.5, 0.1, 0.9, 0.7, 0.1, 0.5, 0.1, 0.4, 0.15, 1.0],
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

    # 中观
    def __evaluate_modification(self, progression: list) -> float:
        pass

        # available_templates = self.pick_templates()
        # n = len(progression)
        # result = []
        # for template in available_templates:
        #     dp = [[0] * n for i in range(n)]
        #     dp[0][0] = 0
        #     for i in range(1, n):
        #         dp[i][0] = dp[i - 1][0] + 1
        #     for j in range(1, n):
        #         dp[0][j] = dp[0][j - 1] + 1
        #
        #     for i in range(1, n):
        #         for j in range(1, n):
        #             if progression[i - 1] == template[j - 1]:
        #                 dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j] + 1, dp[i][j - 1] + 1)
        #             else:
        #                 dp[i][j] = min(dp[i - 1][j - 1] + 1, dp[i - 1][j] + 1, dp[i][j - 1] + 1)
        #     result.append([dp[n - 1][n - 1], template])
        # return max(result)


    def __select_max_candidate(self, candidate_pool: List[List[Chord]], melody: List) \
            -> List[Union[float, List[Chord]]]:
        pass

    def int_to_chord(self, int_list: List[int]) -> List[Chord]:
        pass

    def get_progression(self) -> ChordProgression:
        pass

