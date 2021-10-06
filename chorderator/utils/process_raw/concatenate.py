import pickle
from typing import List
from chords.ChordProgression import ChordProgression, read_progressions
from utils.string import STATIC_DIR


class Concatenate:
    concat_rule = {
        4: [[4]],
        8: [[4, 4], [8]],
        12: [[4, 4, 4], [4, 8], [8, 4]],
        16: [[8, 8], [16]],
        24: [[8, 8, 8], [16, 8], [8, 16]],
        32: [[16, 16]]
    }

    def __init__(self, templates: List[ChordProgression], transition_score: dict):
        self.templates = templates
        self.threshold = 0  # 每个接合允许的最低分数
        self.transition_score = transition_score
        self.max_score = 1  # 对于不拼接的 打满分

    def compute_transition(self, prog_list):
        if len(prog_list) == 1:
            return self.max_score
        else:
            min_score, cursor = 1, 1
            while cursor < len(prog_list):
                transition_bars = prog_list[cursor - 1].progression[-1] + prog_list[cursor].progression[0]
                score = self.transition_score[tuple(transition_bars)]
                if score < min_score:
                    min_score = score
                cursor += 1
            return min_score

    def combinations(self, ingredients_lists):
        if type(ingredients_lists[0][0]) is not list:
            ingredients_lists[0] = [[prog] for prog in ingredients_lists[0]]
        if len(ingredients_lists) == 1:
            return ingredients_lists[0]
        if len(ingredients_lists[1]) == 0:
            return ingredients_lists[0]
        else:
            recur_memo = []
            for comb in ingredients_lists[0]:
                for item in ingredients_lists[1]:
                    recur_memo.append(comb + [item])
            return self.combinations([recur_memo]+ ingredients_lists[2:])

    def concatenate(self):
        available_templates = []

        ingredients_length = set(k for i in self.concat_rule.values() for j in i for k in j)
        ingredients = {length: [] for length in ingredients_length}
        for template in self.templates:
            if len(template)//8 in ingredients_length:
                ingredients[len(template)//8].append(template)
        for aim_length in self.concat_rule:
            for rule in self.concat_rule[aim_length]:
                print(rule)
                for combination in self.combinations([ingredients[length] for length in rule]):
                    score = self.compute_transition(combination)
                    if score >= self.threshold:
                        available_templates.append((score, [prog.progression_class['duplicate-id']
                                                            for prog in combination]))

        return available_templates


if __name__ == '__main__':
    my_concatenater = Concatenate(templates=read_progressions('representative.pcls'),
                                  transition_score=pickle.load(open(STATIC_DIR + 'transition_score.mdch', 'rb')))
    all = my_concatenater.concatenate()
