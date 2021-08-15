from utils.constants import *
from utils.structured import str_to_root, chord_type_to_pitch_relation, root_to_pitch_low
from utils.utils import listen_pitches


class Chord:

    # TODO finish chord class
    def __init__(self, root = None, attr=None):
        self.root = -1
        self.type = -1
        self.inversion = -1
        self.add = -1
        self.sus = -1
        if root:
            self.root = root
        if attr:
            self.type, self.inversion, self.sus, self.add = attr[0], attr[1], attr[2], attr[3]

    def to_midi_pitch(self) -> list:
        midi_pitch = []
        root_pitch = root_to_pitch_low[str_to_root[self.root]]
        pitch_relation = [0] + chord_type_to_pitch_relation[self.type]
        if self.sus != -1:
            if self.sus == SUS2:
                pitch_relation[1] = 2
            elif self.sus == SUS4:
                pitch_relation[1] = 5
        if self.add != -1:
            if self.add == ADD6:
                pitch_relation.append(9)
            elif self.add == ADD9:
                pitch_relation.append(14)
            elif self.add == ADD69:
                pitch_relation.append(9)
                pitch_relation.append(14)
            elif self.add == ADD11:
                pitch_relation.append(17)
            elif self.add == ADD13:
                pitch_relation.append(21)
            elif self.add == ADD911:
                pitch_relation.append(14)
                pitch_relation.append(17)
            elif self.add == ADD1113:
                pitch_relation.append(17)
                pitch_relation.append(21)
            elif self.add == ADD91113:
                pitch_relation.append(14)
                pitch_relation.append(17)
                pitch_relation.append(21)
        if self.inversion != -1:
            if self.inversion == T6 and len(pitch_relation) == 3:
                pitch_relation = pitch_relation[1:] + [pitch_relation[0] + 12]
            elif self.inversion == T64 and len(pitch_relation) == 3:
                pitch_relation = pitch_relation[2:] + [pitch_relation[0] + 12, pitch_relation[1] + 12]
            elif self.inversion == S65 and len(pitch_relation) == 4:
                pitch_relation = pitch_relation[1:] + [pitch_relation[0] + 12]
            elif self.inversion == S43 and len(pitch_relation) == 4:
                pitch_relation = pitch_relation[2:] + [pitch_relation[0] + 12, pitch_relation[1] + 12]
            elif self.inversion == S2 and len(pitch_relation) == 4:
                pitch_relation = pitch_relation[3:] + [pitch_relation[0] + 12, pitch_relation[1] + 12,
                                                       pitch_relation[2] + 12]
        for i in pitch_relation:
            midi_pitch.append(root_pitch + i)
        return midi_pitch

    def __eq__(self,other):
        if not isinstance(other, Chord):
            return False
        if self.root == other.root \
                and self.type == other.type \
                and self.add == other.add \
                and self.inversion == other.inversion:
            return True
        else:
            return False

    # TODO
    def __str__(self):
        if self.root == -1:
            return '???'

        str_ = self.root
        if len(str_) == 1:
            str_ += ' '
        if self.type != -1:
            str_ += str(self.type)
        else:
            str_ += '?'

        return str_


if __name__ == '__main__':
    chord = Chord('C', [MAJ_TRIAD, S43, -1, ADD9])
    print(chord.to_midi_pitch())
    # listen_pitches(chord.to_midi_pitch(), time=5, instrument=VOCAL)
