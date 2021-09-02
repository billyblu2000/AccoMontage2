import pickle
from typing import List

from pretty_midi import PrettyMIDI, Instrument, Note

from chords.Chord import Chord
from utils.process_raw.ProcessDataUtils import type_dict
from utils.structured import str_to_root, root_to_str, major_map, major_map_backward
from utils.string import STATIC_DIR, RESOURCE_DIR
from utils.utils import compute_distance, compute_destination, Logging
from utils.constants import *


class ChordProgression:

    def __init__(self, type=None, tonic=None, metre=None, mode=None, source=None):
        self.meta = {"source": source, "type": type, "tonic": tonic, "metre": metre, "mode": mode}
        self._progression = []
        try:
            self.type = type_dict[type]
        except:
            self.type = "unknown"
        self.appeared_time = 1
        self.appeared_in_other_songs = 0
        self.reliability = -1
        self.progression_class = "unknown"

    # chords are stored as Chord Class
    # switch to root note and output the progression in a easy-read way
    @property
    def progression(self):
        prog = []
        for bar_chords in self._progression:
            bar_roots = []
            for chord in bar_chords:
                if chord.root == -1:
                    bar_roots.append(0)
                else:
                    root = chord.root
                    bar_roots.append(compute_distance(tonic=self.meta['tonic'], this=root, mode=self.meta['mode']))
            prog.append(bar_roots)
        return prog

    @progression.setter
    def progression(self, new):
        if type(new[0][0]) is not int:
            self._progression = new
        # not recommended to assign numbers to _progression
        else:
            prog = []
            for bar_roots in new:
                bar_chords = []
                for order in bar_roots:
                    if not self.meta['tonic']:
                        raise Exception('cannot convert numbers to chords before tonic assigned')
                    root = compute_destination(tonic=self.meta['tonic'], order=order, mode=self.meta['mode'])
                    if self.meta['mode'] == 'M':
                        if order == 1 or order == 4 or order == 5:
                            attr = [MAJ_TRIAD, -1, -1, -1]
                        elif order == 2 or order == 3 or order == 6:
                            attr = [MIN_TRIAD, -1, -1, -1]
                        elif order == 7:
                            attr = [DIM_TRIAD, -1, -1, -1]
                        else:
                            attr = [-1, -1, -1, -1]
                    elif self.meta['mode'] == 'm':
                        if order == 1 or order == 4 or order == 5:
                            attr = [MIN_TRIAD, -1, -1, -1]
                        elif order == 3 or order == 6 or order == 7:
                            attr = [MAJ_TRIAD, -1, -1, -1]
                        elif order == 2:
                            attr = [DIM_TRIAD, -1, -1, -1]
                        else:
                            attr = [-1, -1, -1, -1]
                    else:
                        attr = [-1, -1, -1, -1]
                    chord = Chord(root=root, attr=attr)
                    bar_chords.append(chord)
                prog.append(bar_chords)
            self._progression = prog

    # all progression getters

    def get(self, only_degree=False, flattened=False, only_root=False):
        if only_root:  # element is a number
            if flattened:
                return self.get_chord_progression_only_root_flattened()
            else:
                return self.get_chord_progression_only_root()
        elif only_degree:  # element is a Chord class, but Chord.root is a number
            if flattened:
                return self.get_chord_progression_only_degree_flattened()
            else:
                return self.get_chord_progression_only_degree()
        else:
            if flattened:
                return self.get_chord_progression_flattened()
            else:
                return self.get_chord_progression()

    # differences between progression.getter: this method returns the exact chord, not number (order)
    def get_chord_progression(self):
        return self._progression

    def get_chord_progression_only_degree(self):
        prog = []
        for bar_chords in self._progression:
            bar_roots = []
            for chord in bar_chords:
                if chord.root != -1:
                    root = chord.root
                    number = compute_distance(tonic=self.meta['tonic'], this=root, mode=self.meta['mode'])
                    new_chord = Chord(root=number, attr=[chord.type, chord.inversion, chord.sus, chord.add])
                else:
                    new_chord = Chord(root=-1, attr=[chord.type, chord.inversion, chord.sus, chord.add])
                bar_roots.append(new_chord)
            prog.append(bar_roots)
        return prog

    def get_chord_progression_only_root(self):
        return self.progression

    def get_chord_progression_flattened(self):
        return self.__flat_progression(self.get_chord_progression())

    def get_chord_progression_only_degree_flattened(self):
        return self.__flat_progression(self.get_chord_progression_only_degree())

    def get_chord_progression_only_root_flattened(self):
        return self.__flat_progression(self.progression)

    @staticmethod
    def __flat_progression(before):
        after = []
        for bar_prog in before:
            after += bar_prog
        return after

    def to_midi(self, tempo=120, instrument=PIANO, tonic=None):
        if not self.progression:
            Warning("Progression not assigned!")
            return None
        if not tonic:
            tonic = self.meta['tonic']
        midi = PrettyMIDI()
        unit_length = 30 / tempo
        ins = Instrument(instrument)
        current_pos = 0
        for i in self.get_chord_progression():
            memo = -1
            length = 0
            for j in i:
                if j == memo:
                    length += unit_length
                else:
                    if memo != -1:
                        for pitch in memo.to_midi_pitch(tonic=self.__key_changer(self.meta['tonic'], memo.root, tonic)):
                            note = Note(pitch=pitch, velocity=80, start=current_pos, end=current_pos + length)
                            ins.notes.append(note)
                    current_pos += length
                    length = unit_length
                    memo = j
            for pitch in memo.to_midi_pitch(tonic=self.__key_changer(self.meta['tonic'], memo.root, tonic)):
                note = Note(pitch=pitch, velocity=80, start=current_pos, end=current_pos + length)
                ins.notes.append(note)
            current_pos += length
        midi.instruments.append(ins)
        return midi

    def __key_changer(self, original_tonic: str, root: str, new_tonic: str):
        if root == -1:
            return None
        order = compute_distance(original_tonic, new_tonic, mode=self.meta['mode'])
        return compute_destination(tonic=root, order=order, mode=self.meta['mode'])

    # setters

    def set_mode(self, mode):
        self.meta["mode"] = mode

    def set_metre(self, metre):
        self.meta["metre"] = metre

    def set_tonic(self, tonic):
        self.meta["tonic"] = tonic

    def set_source(self, source):
        self.meta["source"] = source

    def set_type(self, type):
        try:
            self.type = type_dict[type]
            self.meta["type"] = type
        except:
            self.type = None
            self.meta['type'] = None

    def set_appeared_time(self, time):
        self.appeared_time = time

    def set_appeared_in_other_songs(self, time):
        self.appeared_in_other_songs = time

    def set_reliability(self, reliability):
        self.reliability = reliability

    def set_progression_class(self, progression_class):
        self.progression_class = progression_class

    def __iter__(self):
        if self.progression is None:
            Warning("Progression not assigned!")
            return None
        for i in self.get_chord_progression():
            for j in i:
                yield j

    def __len__(self):
        count = 0
        for i in self:
            count += 1
        return count

    def __str__(self):
        str_ = "Chord Progression\n"
        str_ += "-Source: " + self.__print_accept_none(self.meta["source"]) + "\n"
        str_ += "-Source Type: " + self.__print_accept_none(self.meta["type"]) + "\n"
        str_ += "-Source Tonic: " + self.__print_accept_none(self.meta["tonic"]) + "\n"
        str_ += "-Source Metre: " + self.__print_accept_none(self.meta["metre"]) + "\n"
        str_ += "-Source Mode: " + self.__print_accept_none(self.meta["mode"]) + " (M for Major and m for minor)" + "\n"
        str_ += "-Appeared Times: " + self.__print_accept_none(self.appeared_time) + "\n"
        str_ += "-Appeared In Other Songs: " + self.__print_accept_none(self.appeared_in_other_songs) + "\n"
        str_ += "-Reliability: " + self.__print_accept_none(self.reliability) + "\n"
        str_ += "-Progression Class: " + self.__print_accept_none(self.progression_class) + "\n"
        str_ += "Numbered: " + "\n"
        str_ += "| "
        count = 0
        for i in self.progression:
            if count % 8 == 0 and count != 0:
                str_ += "\n| "
            memo = -1
            for j in i:
                if j == memo:
                    str_ += "-"
                else:
                    str_ += str(j)
                    memo = j
            str_ += " | "
            count += 1
        str_ += "\nChord: \n| "
        for i in self._progression:
            if count % 8 == 0 and count != 0:
                str_ += "\n| "
            memo = -1
            for j in i:
                if str(j) == memo:
                    str_ += "-"
                else:
                    str_ += str(j)
                    memo = str(j)
            str_ += " | "
            count += 1
        return str_ + "\n"

    @staticmethod
    def __print_accept_none(value):
        return str(value) if value is not None else 'None'


def read_progressions(progression_file='progressions_with_type.pk'):
    Logging.info('start read progressions from {f}'.format(f=progression_file))
    if progression_file[-1] == 't':
        file = open(STATIC_DIR + progression_file, "r")
        progression_list = []
        progression = ChordProgression()
        for line in file.readlines():
            if line == "\n":
                progression_list.append(progression)
                continue
            if line == "Chord Progression\n":
                progression = ChordProgression()
                continue
            if "-Source:" in line:
                progression.set_source(line.split(":")[1].strip())
                continue
            if "-Source Type:" in line:
                progression.set_type(line.split(":")[1].strip())
                continue
            if "-Source Tonic:" in line:
                progression.set_tonic(line.split(":")[1].strip())
                continue
            if "-Source Metre:" in line:
                progression.set_metre(line.split(":")[1].strip())
                continue
            if "-Source Mode:" in line:
                progression.set_mode(line[14])
                continue
            if "-Appeared Times:" in line:
                progression.set_appeared_time(int(line.split(":")[1].strip()))
            if "-Appeared In Other Songs:" in line:
                progression.set_appeared_in_other_songs(int(line.split(":")[1].strip()))
            if "-Reliability:" in line:
                progression.set_reliability(int(line.split(":")[1].strip()))
            if "-Progression Class:" in line:
                progression.set_progression_class(line.split(":")[1].strip())

            # read from chord
            # if "|" in line and line[2].isdigit():
            #     line_split = line.split("|")
            #     for segment in line_split:
            #         if segment.strip() == "" or segment.strip() == "\n":
            #             continue
            #         bar_chord = []
            #         memo = -1
            #         segment = segment[1:-1]
            #         for char in segment:
            #             if char.isdigit():
            #                 if type(memo) is str:
            #                     bar_chord.append(float(memo + char))
            #                     memo = float(memo + char)
            #                 else:
            #                     bar_chord.append(int(char))
            #                     memo = int(char)
            #             if char == "-":
            #                 bar_chord.append(memo)
            #             if char == ".":
            #                 bar_chord = bar_chord[:-1]
            #                 memo = str(memo) + "."
            #         progression.progression.append(bar_chord)
            if "|" in line and line != '| \n' and line != '|\n' and not line[2].isdigit():
                line_split = line.split("|")
                for segment in line_split:
                    if segment.strip() == "" or segment.strip() == "\n":
                        continue
                    bar_chord = []
                    memo = -1
                    segment = segment[1:-1]
                    segment_split = segment.split('-')
                    for chord_str in segment_split:
                        if chord_str == '':
                            if memo == '???':
                                my_chord = Chord(root=-1, attr=[-1, -1, -1, -1])
                            elif memo[2] == '?':
                                if memo[1] == ' ':
                                    my_chord = Chord(root=memo[0], attr=[-1, -1, -1, -1])
                                else:
                                    my_chord = Chord(root=memo[0:2], attr=[-1, -1, -1, -1])
                            else:
                                if memo[1] == ' ':
                                    my_chord = Chord(root=memo[0], attr=[int(memo[2]), -1, -1, -1])
                                else:
                                    my_chord = Chord(root=memo[0:2], attr=[int(memo[2]), -1, -1, -1])
                        elif chord_str == '???':
                            my_chord = Chord(root=-1, attr=[-1, -1, -1, -1])
                            memo = chord_str
                        elif chord_str[2] == '?':
                            if chord_str[1] == ' ':
                                my_chord = Chord(root=chord_str[0], attr=[-1, -1, -1, -1])
                            else:
                                my_chord = Chord(root=chord_str[0:2], attr=[-1, -1, -1, -1])
                            memo = chord_str
                        else:
                            if chord_str[1] == ' ':
                                my_chord = Chord(root=chord_str[0], attr=[int(chord_str[2]), -1, -1, -1])
                            else:
                                my_chord = Chord(root=chord_str[0:2], attr=[int(chord_str[2]), -1, -1, -1])
                            memo = chord_str
                        bar_chord.append(my_chord)
                    progression.progression = progression._progression + [bar_chord]
    elif progression_file[-1] == 'k':
        file = open(STATIC_DIR + progression_file, "r")
        progression_list = pickle.load(open(STATIC_DIR + 'progressions_with_type.pk', 'rb'))
    else:
        Logging.error('cannot recognize progression_file "{n}"'.format(n=progression_file))
        return None
    Logging.info('read progressions done')
    return progression_list


# Abandoned!
def query_progression(progression_list, source=None, type=None, tonic=None, mode=None, metre=None, times=None,
                      other_times=None, reliability=None):
    if source:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.meta["source"] == source:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if type:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.meta["type"] == type or prgression.type == type:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if tonic:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.meta["tonic"] == tonic:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if mode:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.meta["mode"] == mode:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if metre:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.meta["metre"] == metre:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if times:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.appeared_time == times:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if other_times:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.appeared_in_other_songs == other_times:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    if reliability:
        new_progression_list = []
        for prgression in progression_list:
            if prgression.reliability == reliability:
                new_progression_list.append(prgression)
        progression_list = new_progression_list[:]
    return progression_list


def print_progression_list(progression_list: List[ChordProgression], limit=None):
    limit = len(progression_list) if limit is None else limit
    count = 0
    for progression in progression_list:
        print(progression)
        count += 1
        if count == limit:
            break
    print("Total: ", len(progression_list), "\n")


if __name__ == '__main__':
    cp = ChordProgression(type="", metre="", mode="M", tonic="D", source="")
    cp.progression = [[1, 1, 1, 1, 4, 4, 4, 4], [1, 1, 1, 1, 4, 4, 4, 4], [1, 1, 1, 1, 4, 4, 4, 4],
                      [1, 1, 1, 1, 4, 4, 4, 4], ]

    print(cp)
    # listen(cp.to_midi(tempo=70, tonic="A", mode="M", instrument=SHAKUHACHI))
