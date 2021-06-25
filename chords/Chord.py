from utils.constants import *
from utils.dictionary import str_to_root, chord_type_to_pitch_relation, root_to_pitch_low
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

    # TODO
    def __str__(self):
        str_ = self.root
        if self.type == MAJ_TRIAD:
            str_ += ''
        elif self.type == MIN_TRIAD:
            str_ += 'm'
        elif self.type == AUG_TRIAD:
            str_ += 'aug'
        elif self.type == DIM_TRIAD:
            str_ += 'dim'
        elif self.type == MAJ_SEVENTH:
            str_ += 'maj7'
        elif self.type == MIN_SEVENTH:
            str_ += 'm7'
        elif self.type == DOM_SEVENTH:
            str_ += '7'
        elif self.type == HALF_DIM_SEVENTH:
            str_ += 'm7-5'
        elif self.type == FULLY_DIM_SEVENTH:
            str_ += 'dim7'

        return "Chord: " + str_


if __name__ == '__main__':
    chord = Chord('C', [DOM_SEVENTH, S65, -1, -1])
    print(chord.to_midi_pitch())
    # listen_pitches(chord.to_midi_pitch(), time=5, instrument=VOCAL)
