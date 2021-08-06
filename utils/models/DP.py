import difflib

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from typing import List, Union

# core DP algorithm
from utils import constants


class DP:
    _dp: List[List[Union[float, List[Chord]]]]
    result: List[Chord]

    def __init__(self, melo: list, melo_meta: dict, templates: List[ChordProgression], melody_attention_level=0.5):

        # init attributes
        self.melo = melo
        self.melo_meta = melo_meta
        self.templates = templates
        self._dp = [[0.0, []]]  # DP memo, type: List[List[Union[float, List[Chord]]]]
        self.result = []  # final result, type: List[Chord]
        self.solved = False

        # init parameters
        self.melody_attention_level = melody_attention_level

        # preprocess attributes, span template
        self._template_span = self.__span_template()  # span template
        self._max_template_length = max([len(i) for i in self._template_span])

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
        chord_list = []
        for i in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
            chord = Chord()
            chord.root = i
            if i in ['C', 'F', 'G']:
                chord.type = constants.MAJ_TRIAD
            elif i in ['D', 'E', 'A']:
                chord.type = constants.MIN_TRIAD
            else:
                chord.type = constants.DIM_TRIAD
            chord_list.append(chord)
        return chord_list

    # util func to span template
    def __span_template(self) -> List[List[List[Chord], float]]:
        pass

    # '中观', called in self.__select_max_candidate
    def __match_progression_and_template_span(self, progression: list) -> float:
        pass

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
    def __match_melody_and_chord(melody_list: list, chord_list: list) -> float:
        pass

    # output final result
    def get_progression(self) -> ChordProgression:
        if self.solved:
            return ChordProgression()
        else:
            raise Exception("Please call the solve method first!")


if __name__ == '__main__':
    # dp = DP()
    # dp.solve()
    print([1] in [1, 2])
