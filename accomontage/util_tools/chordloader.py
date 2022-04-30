chord_index = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]  # only # instead of b
chord_Mm_check = [[[0, 4, 7], ""], [[0, 3, 7], "m"]]
chord_tri_check = [[[0, 4, 7], ""], [[0, 3, 7], "m"], [[0, 4, 8], "aug"], [[0, 3, 6], "dim"]]
chord_seven_check = \
    [[[0, 4, 7], ""], [[0, 3, 7], "m"], [[0, 4, 8], "aug"], [[0, 3, 6], "dim"],
     [[0, 4, 7, 10], "7"], [[0, 4, 7, 11], "M7"], [[0, 3, 7, 10], "m7"], [[0, 3, 7, 11], "mM7", ],
     [[0, 3, 6, 9], "dim7"], [[0, 3, 6, 10], "m7b5"], [[0, 4, 8, 11], "aug7"]]


class Chord_Loader:
    def __init__(self, recogLevel="Mm"):
        self.recogLevel = recogLevel
        if recogLevel == "Mm":
            self.chord_check = chord_Mm_check[:]
        if recogLevel == "Tri":
            self.chord_check = chord_tri_check[:]
        if recogLevel == "Seven":
            self.chord_check = chord_seven_check[:]

    def chord_alu(self, x, scalar=1):
        if x == len(self.chord_check) * len(chord_index):
            return x
        y = (x + scalar) % 12 + (x // 12) * 12
        return y

    def isChordEqual(self, x, y):
        return len(set(x) - set(y))

    def index2name(self, x):
        check_p = x // 12
        index_p = x % 12
        total = len(self.chord_check) * len(chord_index)
        if x == total:
            return "NC"
        if x > total or x < 0:
            return "NC"
        return chord_index[index_p] + self.chord_check[check_p][1]

    def name2index(self, name):
        if name is None:
            return len(self.chord_check) * len(chord_index)
        for i in range(len(self.chord_check)):
            for j in range(len(chord_index)):
                chord_name = chord_index[j] + self.chord_check[i][1]
                if name == chord_name:
                    return i * 12 + j
                if name == "NC":
                    return len(self.chord_check) * len(chord_index)
        return len(self.chord_check) * len(chord_index)

    def name2note(self, name, stage=0):
        if name == "NC":
            return None
        obe_index = -1
        obe_check = -1  # the obeservation of the name
        for i in chord_index:
            for j in self.chord_check:
                std_chord_name = i + j[1]
                if std_chord_name == name:
                    obe_index = i
                    obe_check = j
                    break
        if obe_index == -1 and obe_check == -1:
            # print(name)
            return None
        else:
            re = obe_check[0][:]
            chord_num = chord_index.index(obe_index)
            for i in range(len(re)):
                re[i] = re[i] + chord_num + stage * 12
            return re

    def note2name(self, notes):
        re = None
        equalnum = 0.0
        for i in range(len(notes)):
            temp_notes = notes[:]
            for j in range(len(temp_notes)):
                temp_notes[j] = (temp_notes[j] - notes[i]) % 12
            for k in self.chord_check:
                temp_equal = len(k[0]) - self.isChordEqual(k[0], temp_notes)
                if temp_equal > equalnum:
                    re = chord_index[notes[i] % 12] + k[1]
                    equalnum = temp_equal
        return re
