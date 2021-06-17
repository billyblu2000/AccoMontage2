from typing import List, Any

from pretty_midi import PrettyMIDI, Instrument, Note

from chords.Chord import Chord
from utils.ProcessDataUtils import type_dict
from utils.dictionary import str_to_root, root_to_str
from utils.string import STATIC_DIR
from utils.utils import listen
from utils.constants import *


class ChordProgression:

    def __init__(self, type=None, tonic=None, metre=None, mode=None, source=None):
        self.meta = {"source": source, "type": type, "tonic": tonic, "metre": metre, "mode": mode}
        self.progression = []
        try:
            self.type = type_dict[type]
        except:
            self.type = "unknown"
        self.appeared_time = 1
        self.appeared_in_other_songs = 0
        self.reliability = -1
        self.progression_class = "unknown"

    @staticmethod
    def render_to_chord(order, tonality="C", mode="M") -> Chord:
        chord = Chord()
        if order not in [1, 2, 3, 4, 5, 6, 7]:
            raise ValueError
        distance = 0
        if mode == "M":
            if order == 1:
                distance = 0
            if order == 2:
                distance = 2
            if order == 3:
                distance = 4
            if order == 4:
                distance = 5
            if order == 5:
                distance = 7
            if order == 6:
                distance = 9
            if order == 7:
                distance = 11
            if order in [1, 4, 5]:
                chord.type = MAJ_TRIAD
            elif order in [2, 3, 6]:
                chord.type = MIN_TRIAD
            else:
                chord.type = DIM_TRIAD
        if mode == "m":
            if order == 1:
                distance = 0
            if order == 2:
                distance = 2
            if order == 3:
                distance = 3
            if order == 4:
                distance = 5
            if order == 5:
                distance = 7
            if order == 6:
                distance = 8
            if order == 7:
                distance = 10
            if order in [1, 4, 5]:
                chord.type = MIN_TRIAD
            elif order in [2]:
                chord.type = DIM_TRIAD
            elif order in [3, 6, 7]:
                chord.type = MAJ_TRIAD
            else:
                chord.type = AUG_TRIAD
        if str_to_root[tonality] + distance >= 12:
            distance -= 12
        chord.root = root_to_str[str_to_root[tonality] + distance]
        return chord

    def to_midi(self, tonic="C", mode="M", tempo=120, instrument=PIANO):
        if not self.progression:
            Warning("Progression not assigned!")
            return None
        midi = PrettyMIDI()
        unit_length = 30 / tempo
        ins = Instrument(instrument)
        current_pos = 0
        for i in self.progression:
            memo = -1
            length = 0
            for j in i:
                if j == memo:
                    length += unit_length
                else:
                    if memo != -1:
                        chord = self.render_to_chord(order=memo, tonality=tonic, mode=mode)
                        for pitch in chord.to_midi_pitch():
                            note = Note(pitch=pitch, velocity=80, start=current_pos, end=current_pos + length)
                            ins.notes.append(note)
                    current_pos += length
                    length = unit_length
                    memo = j
            chord = self.render_to_chord(order=memo, tonality=tonic, mode=mode)
            for pitch in chord.to_midi_pitch():
                note = Note(pitch=pitch, velocity=80, start=current_pos, end=current_pos + length)
                ins.notes.append(note)
            current_pos += length
        midi.instruments.append(ins)
        return midi

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
        for i in self.progression:
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
        return str_ + "\n"

    @staticmethod
    def __print_accept_none(value):
        return str(value) if value is not None else 'None'


def read_progressions(progression_file='progressions.txt'):
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
        if "|" in line:
            line_split = line.split("|")
            for segment in line_split:
                if segment.strip() == "" or segment.strip() == "\n":
                    continue
                bar_chord = []
                memo = -1
                for char in segment:
                    if char == " ":
                        continue
                    if char.isdigit():
                        if type(memo) is str:
                            bar_chord.append(float(memo + char))
                            memo = float(memo + char)
                        else:
                            bar_chord.append(int(char))
                            memo = int(char)
                    if char == "-":
                        bar_chord.append(memo)
                    if char == ".":
                        bar_chord = bar_chord[:-1]
                        memo = str(memo) + "."
                progression.progression.append(bar_chord)
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
    cp = ChordProgression(type="", metre="", mode="", tonic="", source="")
    cp.progression = [[1, 1, 1, 1, 4, 4, 4, 4], [1, 1, 1, 1, 4, 4, 4, 4], [1, 1, 1, 1, 4, 4, 4, 4],
                      [1, 1, 1, 1, 4, 4, 4, 4], ]
    print(cp)
    listen(cp.to_midi(tempo=70, tonic="A", mode="M", instrument=SHAKUHACHI))
