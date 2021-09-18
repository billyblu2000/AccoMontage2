class PostProcessor:
    def __init__(self, progression_list, progression_lib):
        self.progression_list = progression_list
        self.progression_lib = self.create_dup_progression_list(progression_lib)
        self.evaluate_reliability()
        print(self.progression_lib[0])

    def get(self):
        return self.progression_list

    def evaluate_reliability(self, threshold=0.8):
        new_list = []
        for lst in self.progression_lib:
            new_sub_list = []
            for progression in lst:
                if progression.reliability >= threshold:
                    new_sub_list.append(progression)
            new_list.append(new_sub_list)
        self.progression_lib = new_list

    def create_dup_progression_list(self, progression_lib):
        new_list = []
        for progression in self.progression_list:
            dup_id = progression.progression_class['duplicate-id']
            new_list.append(progression_lib[dup_id])
        return new_list