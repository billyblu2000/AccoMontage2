class PostProcessor:
    def __init__(self, progression_list, progression_lib):
        self.progression_list = progression_list
        self.progression_lib = progression_lib
        print(self.progression_lib[0])

    def get(self):
        return self.progression_list
    