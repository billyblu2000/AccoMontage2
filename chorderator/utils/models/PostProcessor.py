import random


class PostProcessor:
    def __init__(self, progression_list, progression_lib):
        self.progression_list = progression_list
        self.progression_lib = self.__create_dup_progression_list(progression_lib)
        self.progression_lib_filtered = self.__evaluate_reliability(self.progression_lib)

    def get(self):
        final_out = []
        for i in range(len(self.progression_lib_filtered)):
            if len(self.progression_lib_filtered[i]) == 0:
                final_out.append(max(self.progression_lib[i], key=lambda x: x.reliability))
            else:
                final_out.append(random.choice(self.progression_lib_filtered[i]))
        return final_out

    @staticmethod
    def __evaluate_reliability(progression_lib, threshold=0.8):
        new_list = []
        for lst in progression_lib:
            new_sub_list = []
            for progression in lst:
                if progression.reliability >= threshold:
                    new_sub_list.append(progression)
            new_list.append(new_sub_list)
        return new_list

    def __create_dup_progression_list(self, progression_lib):
        new_list = []
        for progression in self.progression_list:
            dup_id = progression.progression_class['duplicate-id']
            new_list.append(progression_lib[dup_id])
        return new_list
