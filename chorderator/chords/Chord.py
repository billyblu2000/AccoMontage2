from ..utils.constants import *
from ..utils.structured import str_to_root, chord_type_to_pitch_relation, root_to_pitch_low


class Chord:

    # TODO finish chord class
    def __init__(self, root=None, attr=None):

        self.root = -1
        self.type = -1

        # abandoned
        self.inversion = -1
        self.add = -1
        self.sus = -1

        self.model = {
            'color':-1,
            'density':-1,
            'thickness':-1
        }

        self.pitches = []

        if root:
            self.root = root
        if attr:
            self.type, self.inversion, self.sus, self.add = attr[0], attr[1], attr[2], attr[3]

    def to_midi_pitch(self, tonic=None) -> list:
        if self.pitches:
            return self.pitches

        midi_pitch = []
        if tonic:
            root_pitch = root_to_pitch_low[str_to_root[tonic]]
        else:
            if self.root != -1:
                root_pitch = root_to_pitch_low[str_to_root[self.root]]
            else:
                return []
        if self.type != -1:
            pitch_relation = [0] + chord_type_to_pitch_relation[self.type]
        else:
            pitch_relation = [0]
        for i in pitch_relation:
            midi_pitch.append(root_pitch + i)
        return midi_pitch

    def __eq__(self, other):
        if not isinstance(other, Chord):
            return False
        if self.root == other.root and self.type == other.type:
            return True
        else:
            return False

    def set_root(self, root):
        self.root = root

    def set_type(self, type):
        self.type = type

    def _calculate_pitches_from_model(self):
        self.pitches = []

    def _calculate_model_from_pitches(self):
        self.model = {
            'color': -1,
            'density': -1,
            'thickness': -1
        }

    def _calculate_model_from_type(self):
        self.model = {
            'color': -1,
            'density': -1,
            'thickness': -1
        }

    def set_pitches(self, pitches):
        self.pitches = pitches

    def set_model(self, color=-1, density=-1, thickness=-1):
        self.model = {
            'color': color,
            'density': density,
            'thickness': thickness
        }

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


def print_chord_list(chord_list):
    string = '['
    for i in chord_list:
        string += '['
        for j in i:
            string += str(j) + ', '
        string = string[:-2] + ']\n'
    string = string[:-1] + ']'
    print(string)


if __name__ == '__main__':
    chord = Chord('C', [MAJ_TRIAD, S43, -1, ADD9])
    print(chord.to_midi_pitch())
    # listen_pitches(chord.to_midi_pitch(), time=5, instrument=VOCAL)
