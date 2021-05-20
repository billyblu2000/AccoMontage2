from utils.constants import *
from utils.dictionary import str_to_root, chord_type_to_pitch_relation, root_to_pitch_low
from utils.utils import listen_pitches


class Chord:

    # TODO finish chord class
    def __init__(self, name=None):
        self.root = None
        self.type = None
        self.inversion = None
        self.add = None
        self.sus = None
        if name is not None:
            self.analyze_name(name)

    def to_midi_pitch(self) -> list:
        midi_pitch = []
        root_pitch = root_to_pitch_low[str_to_root[self.root]]
        midi_pitch.append(root_pitch)
        for i in chord_type_to_pitch_relation[self.type]:
            midi_pitch.append(root_pitch + i)
        return midi_pitch

    # TODO
    def analyze_name(self, name):
        try:
            if len(name) == 1:
                self.root = name[0]
                name = name[1:]
            elif name[1] == "#" or name[1] == "b":
                self.root = name[:2]
                name = name[2:]
            else:
                self.root = name[0]
                name = name[1:]
            if name == "":
                self.type = MAJ_TRIAD
            if name == "m":
                self.type = MIN_TRIAD
        except:
            raise Warning("Cannot recognize chord name: {}".format(name))

    # TODO
    def __str__(self):
        str_ = self.root
        if self.type == MIN_TRIAD:
            str_ += "m"
        return "Chord: " + str_


if __name__ == '__main__':
    chord = Chord("Am")
    print(chord)
    listen_pitches(chord.to_midi_pitch(), time=5, instrument=VOCAL)
