from typing import List


class Concatenate:
    # all available concat rules
    concat_rule = {
        4: [[4]],
        8: [[4, 4], [8]],
        12: [[4, 4, 4], [4, 8], [8, 4]],
        16: [[8, 8], [16]],
        24: [[8, 8, 8], [16, 8], [8, 16]],
        32: [[16, 16]]
    }

    def __init__(self, templates, transition_score: dict):
        self.templates = templates
        self.threshold = 0.875  # 每个接合允许的最低分数
        self.transition_score = transition_score
        self.max_score = 1  # 对于不拼接的 打满分

    # given a list of progressions, compute the minimum transition score
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

    # pick 1 elements from n lists respectively, compute all combinations
    def combinations(self, ingredients_lists):
        try:
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
                return self.combinations([recur_memo] + ingredients_lists[2:])
        except:
            return []

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
                all_ingredients = [ingredients[length] for length in rule]
                for combination in self.combinations(all_ingredients):
                    score = self.compute_transition(combination)
                    if len(all_ingredients) == 2 or len(all_ingredients) == 1:
                        if score >= self.threshold:
                            available_templates.append((score, [prog.progression_class['duplicate-id']
                                                                for prog in combination]))
                    elif len(all_ingredients) == 3:
                        if score >= self.threshold * 1.07:
                            available_templates.append((score, [prog.progression_class['duplicate-id']
                                                                for prog in combination]))

        return available_templates


if __name__ == '__main__':
    # templates = read_progressions('representative.pcls')
    # new_templates = []
    # for t in templates:
    #     if 'mod/2' not in t.meta['source'] and 'modx2' not in t.meta['source']:
    #         new_templates.append(t)
    # templates = new_templates
    #
    # major_templates = []
    # minor_templates = []
    # for template in templates:
    #     if template.meta['mode'] == 'M' or template.meta['mode'] == 'maj':
    #         major_templates.append(template)
    #     else:
    #         minor_templates.append(template)
    # print(len(major_templates), len(minor_templates))
    #
    # my_concatenater = Concatenate(templates=major_templates,
    #                               transition_score=pickle.load(open(STATIC_DIR + 'transition_score.mdch', 'rb')))
    # all = my_concatenater.concatenate()
    # file = open('new_major_score.mdch', 'wb')
    # pickle.dump(all, file)
    # file.close()
    #
    # my_concatenater = Concatenate(templates=minor_templates,
    #                               transition_score=pickle.load(open(STATIC_DIR + 'transition_score.mdch', 'rb')))
    # all = my_concatenater.concatenate()
    # file = open('new_minor_score.mdch', 'wb')
    # pickle.dump(all, file)
    # file.close()
    pass

