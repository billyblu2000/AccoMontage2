from typing import List
from chords.Chord import Chord
from chords.ChordProgression import ChordProgression, read_progressions, print_progression_list


class Concatenate:
    def __init__(self, aim_length: [4, 8, 12, 16, 24, 32], templates: List[ChordProgression], transition_score: dict):
        self.templates = templates
        self.threshold = 0  # 每个接合允许的最低分数
        self.aim_length = aim_length
        self.transition_score = transition_score
        self.max_score = 1  # 对于不拼接的 打满分

    # def select_candidates(self):
    #     templates_len4 = []
    #     templates_len8 = []
    #     templates_len12 = []
    #     templates_len16 = []
    #     templates_len24 = []
    #     templates_len32 = []
    #     for template in self.templates:
    #         if len(template) == 4:
    #             templates_len4.append(template)
    #         if len(template) == 8:
    #             templates_len8.append(template)
    #         if len(template) == 12:
    #             templates_len12.append(template)
    #         if len(template) == 16:
    #             templates_len16.append(template)
    #         if len(template) == 24:
    #             templates_len24.append(template)
    #         if len(template) == 32:
    #             templates_len32.append(template)
    #

    def concatenate(self):
        available_templates = []

        templates_len4 = []
        templates_len8 = []
        templates_len12 = []
        templates_len16 = []
        templates_len24 = []
        templates_len32 = []
        for template in self.templates:
            if len(template) == 4:
                templates_len4.append(template)
            if len(template) == 8:
                templates_len8.append(template)
            if len(template) == 12:
                templates_len12.append(template)
            if len(template) == 16:
                templates_len16.append(template)
            if len(template) == 24:
                templates_len24.append(template)
            if len(template) == 32:
                templates_len32.append(template)


        if self.aim_length == 4:
            available_templates = templates_len4

        if self.aim_length == 8:
            candidates44 = []
            for i in templates_len4:
                for j in templates_len4:
                    if self.transition_score(i, j) > self.threshold:
                        candidates44.append((self.transition_score(i, j), i.progression + j.progression))

            for i in templates_len8:
                available_templates.append((self.max_score, i.progression))
            available_templates += candidates44

        if self.aim_length == 12:
            candidates444 = []
            for i in templates_len4:
                for j in templates_len4:
                    for k in  templates_len4:
                        score = min(self.transition_score(i, j), self.transition_score(j, k))
                    if score > self.threshold:
                        candidates444.append((score, i.progression + j.progression + k.progression))
            available_templates += candidates444

            candidates48 = []
            for i in templates_len4:
                for j in templates_len8:
                    if self.transition_score(i, j) > self.threshold:
                        candidates48.append((self.transition_score(i, j), i.progression + j.progression))
            available_templates += candidates48

            candidates84 = []
            for i in templates_len8:
                for j in templates_len4:
                    if self.transition_score(i, j) > self.threshold:
                        candidates84.append((self.transition_score(i, j), i.progression + j.progression))
            available_templates += candidates84

            for i in templates_len12:
                available_templates.append((self.max_score, i.progression))

        if self.aim_length == 16:
            candidates88 = []
            for i in templates_len8:
                for j in templates_len8:
                    if self.transition_score(i, j) > self.threshold:
                        candidates88.append((self.transition_score(i, j), i.progression + j.progression))

            for i in templates_len16:
                available_templates.append((self.max_score, i.progression))
            available_templates += candidates88

        if self.aim_length == 24:
            candidates888 = []
            for i in templates_len8:
                for j in templates_len8:
                    for k in templates_len8:
                        score = min(self.transition_score(i, j), self.transition_score(j, k))
                    if score > self.threshold:
                        candidates888.append((score, i.progression + j.progression + k.progression))
            available_templates += candidates888

            candidates816 = []
            for i in templates_len8:
                for j in templates_len16:
                    if self.transition_score(i, j) > self.threshold:
                        candidates816.append((self.transition_score(i, j), i.progression + j.progression))
            available_templates += candidates816

            candidates168 = []
            for i in templates_len16:
                for j in templates_len8:
                    if self.transition_score(i, j) > self.threshold:
                        candidates168.append((self.transition_score(i, j), i.progression + j.progression))
            available_templates += candidates168

            for i in templates_len24:
                available_templates.append((self.max_score, i.progression))

        if self.aim_length == 32:
            candidates1616 = []
            for i in templates_len16:
                for j in templates_len16:
                    if self.transition_score(i, j) > self.threshold:
                        candidates1616.append((self.transition_score(i, j), i.progression + j.progression))
            available_templates += candidates1616

            for i in templates_len32:
                available_templates.append((self.max_score, i.progression))


        return available_templates

