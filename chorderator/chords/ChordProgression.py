import copy
import json
import pickle
import os
from typing import List

from pretty_midi import PrettyMIDI, Instrument, Note

from .Chord import Chord
from ..utils.string import STATIC_DIR
from ..utils.utils import compute_distance, compute_destination, Logging, pickle_read
from ..utils.constants import *
from ..utils.structured import str_to_root
from ..settings import static_storage


class ChordProgression:

    def __init__(self, type=None, tonic=None, metre=None, mode=None, source=None, saved_in_source_base=False):
        self.meta = {"source": source, "type": type, "tonic": tonic, "metre": metre, "mode": mode}
        self._progression = []
        self.progression_class = {
            'type': 'unknown',  # positions, e.g., 'verse', 'chorus', ...
            'pattern': 'unknown',  # e.g., 'I-vi-IV-V', ...
            'cycle': 'unknown',  # number
            'progression-style': 'unknown',  # 'pop', 'edm', 'dark', ...
            'chord-style': 'unknown',  # 'classy', 'emotional', 'standard'
            'performing-style': 'unknown',  # 'arpeggio'
            'rhythm': 'unknown',  # 'fast-back-and-force', 'fast-same-time', 'slow'
            'epic-endings': 'unknown',  # 'True', 'False'
            'melodic': 'unknown',  # 'True', 'False'
            'folder-id': 'unknown',
            'duplicate-id': 'unknown',
            'new_label': 'unknown'
        }
        try:
            self.progression_class['type'] = type_dict[type]
        except:
            pass
        self.appeared_time = 1
        self.appeared_in_other_songs = 0
        self.reliability = -1
        self.saved_in_source_base = saved_in_source_base
        self.style = {
            'color': -1,
            'density': -1,
            'thickness': -1
        }
        self.cache = {'2d-root': None}

    # chords are stored as Chord Class
    # switch to root note and output the progression in a easy-read way
    @property
    def progression(self):
        if not self.cache['2d-root']:
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
            self.cache['2d-root'] = prog
            return prog
        else:
            return self.cache['2d-root']

    @progression.setter
    def progression(self, new):
        self.cache['2d-root'] = None
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

    @property
    def type(self):
        return self.progression_class['type']

    @property
    def id(self):
        return self.progression_class['duplicate-id']

    @type.setter
    def type(self, new_type):
        self.progression_class['type'] = new_type

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

    def to_midi(self, tempo=120, instrument=PIANO, tonic=None, lib=None):
        if not self.progression:
            Logging.error("Progression not assigned!")
            return None
        if not tonic:
            tonic = self.meta['tonic']
        midi = PrettyMIDI()
        unit_length = 30 / tempo
        ins = Instrument(instrument)
        if not self.saved_in_source_base:
            current_pos = 0
            for i in self.get_chord_progression():
                memo = -1
                length = 0
                for j in i:
                    if j == memo:
                        length += unit_length
                    else:
                        if memo != -1:
                            for pitch in memo.to_midi_pitch(
                                    tonic=self.__key_changer(self.meta['tonic'], memo.root, tonic)):
                                note = Note(pitch=pitch, velocity=80, start=current_pos, end=current_pos + length)
                                ins.notes.append(note)
                        current_pos += length
                        length = unit_length
                        memo = j
                for pitch in memo.to_midi_pitch(tonic=self.__key_changer(self.meta['tonic'], memo.root, tonic)):
                    note = Note(pitch=pitch, velocity=80, start=current_pos, end=current_pos + length)
                    ins.notes.append(note)
                current_pos += length

        else:
            if lib is None:
                lib = pickle_read('lib')
            try:
                all_notes = lib[self.meta['source']]
            except:
                Logging.error('Progression with source name {n} '
                              'cannot be find in library! '
                              'Call set_in_lib(in_lib=False) to generate MIDI '
                              'by progression list itself'.format(n=self.meta['source']))
                return False
            for note in all_notes:
                ins.notes.append(Note(start=note[0] * unit_length,
                                      end=note[1] * unit_length,
                                      pitch=note[2] + str_to_root[tonic],
                                      velocity=note[3]))

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
        self.progression_class = dict(json.loads(progression_class.replace('\'', '"')))

    def set_in_lib(self, in_lib):
        self.saved_in_source_base = True if in_lib else False

    def set_cache(self):
        self.cache = {
            '2d-root': None
        }

    def set_style(self, color=-1, density=-1, thickness=-1):
        self.style = {
            'color': color,
            'density': density,
            'thickness': thickness,
        }

    def __iter__(self):
        if self.progression is None:
            Logging.error("Progression not assigned!")
            return None
        for i in self.get_chord_progression():
            for j in i:
                yield j

    def __len__(self):
        count = 0
        for i in self:
            count += 1
        return count

    def __contains__(self, item):
        if type(item) is str:
            if item.isdigit():
                item = int(item)
            else:
                Logging.error("'Item in ChordProgression': item type cannot be recognized!")
                return False
        if type(item) is int or type(item) is float or type(item) is Chord:
            item = [item]
        if type(item) is list:
            if len(item) > len(self.get(flattened=True)):
                return False
            if type(item[0]) is Chord and type(item[0].root) is str:
                ori_prog = self.get(flattened=True)
            elif type(item[0]) is Chord and (type(item[0].root) is int or type(item[0].root) is float):
                ori_prog = self.get(flattened=True, only_degree=True)
            elif type(item[0]) is int or type(item[0]) is float:
                ori_prog = self.get(flattened=True, only_root=True)
            else:
                Logging.error("'item in ChordProgression': item type cannot be recognized!")
                return False
            all_slices = [ori_prog[i:i + len(item)] for i in range(len(ori_prog) - len(item) + 1)]
            for slice in all_slices:
                if slice == item:
                    return True
            else:
                return False

    def __getitem__(self, item):
        raise SyntaxError('Syntax "ChordProgression[key]" should not be used because the type of the return is '
                          'ambiguous.')

    def __setitem__(self, key, value):
        pass

    def __add__(self, other):
        pass

    def __eq__(self, other):
        if self.meta['type'] != other.meta['type']:
            return False
        if self.meta['mode'] != other.meta['mode']:
            return False
        if self.get(flattened=True, only_degree=True) != other.get(flattened=True, only_degree=True):
            return False
        return True

    def __ne__(self, other):
        pass

    def __bool__(self):
        pass

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


def read_progressions(progression_file='progressions.pcls', span=False):
    class RenameUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            renamed_module = module
            if module == "chords.Chord":
                renamed_module = "chorderator.chords.Chord"
            if module == "chords.ChordProgression":
                renamed_module = "chorderator.chords.ChordProgression"

            return super(RenameUnpickler, self).find_class(renamed_module, name)

    def renamed_load(file_obj):
        try:
            return RenameUnpickler(file_obj).load()
        except:
            return pickle.load(file_obj)

    def span_progression(progression):

        def flatten(before):
            after = []
            for bar_prog in before:
                after += bar_prog
            return after

        def restore(before, bar_length=8):
            after = []
            if len(before) % bar_length != 0:
                raise Exception("Can't span progression: length {l} cannot be restored with bar length {b}"
                                .format(l=len(before), b=bar_length))
            for i in range(len(before) // bar_length):
                after.append(before[i:i + bar_length])
            return after

        def mul(chord_list, scale=2):
            flattened = flatten(chord_list)
            new_chord_list = []
            for chord in flattened:
                for i in range(scale):
                    new_chord_list.append(copy.deepcopy(chord))
            return restore(new_chord_list, bar_length=len(chord_list[0]))

        def div(chord_list, scale=2):
            flattened = flatten(chord_list)
            if len(flattened) % scale != 0:
                raise Exception("Can't span progression: length {l} cannot be divide by scale {s}"
                                .format(l=len(flattened), s=scale))
            new_chord_list = []
            for i in range(len(flattened) // scale):
                new_chord_list.append(copy.deepcopy(flattened[i * scale]))
            return restore(new_chord_list, bar_length=len(chord_list[0]))

        if progression.reliability <= 0.5:
            return [progression]
        if len(progression) // 8 == 4 or len(progression) // 8 == 8:
            p_mul2 = copy.deepcopy(progression)
            p_mul2.progression = mul(p_mul2.get())
            p_mul2.meta['source'] = p_mul2.meta['source'] + 'modx2'
            p_mul2.progression_class['cycle'] *= 2 if type(p_mul2.progression_class['cycle']) is int else 1

            p_div2 = copy.deepcopy(progression)
            p_div2.progression = div(p_div2.get())
            p_div2.meta['source'] = p_div2.meta['source'] + 'mod/2'
            p_div2.progression_class['cycle'] *= 2 if type(p_div2.progression_class['cycle']) is int else 1
            return [progression, p_mul2, p_div2]
        else:
            return [progression]

    Logging.info('start read progressions from {f}'.format(f=progression_file))
    try:
        file = open(static_storage[progression_file], "rb")
        progression_list = renamed_load(file)
        file.close()
    except:
        all_file_names = []
        for file in os.listdir(STATIC_DIR):
            if static_storage[progression_file].split('/')[-1] in file:
                all_file_names.append(file)
        if len(all_file_names) == 0:
            Logging.error('cannot recognize progression_file "{n}"'.format(n=progression_file))
            return None
        progression_list = {}
        for name in all_file_names:
            file = open(STATIC_DIR + name, "rb")
            progression_list.update(renamed_load(file))
            file.close()

    if span:
        if type(progression_list) is list:
            new_progression_list = []
            for prog in progression_list:
                new_progression_list += span_progression(prog)
            progression_list = new_progression_list
        elif type(progression_list) is dict:
            for item in progression_list.items():
                new_progression_list = []
                for prog in item[1]:
                    new_progression_list += span_progression(prog)
                progression_list[item[0]] = new_progression_list
        else:
            pass
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
    for progression_concate in progression_list:
        for progression in progression_concate:
            print(progression)
        count += 1
        if count == limit:
            break
    print("Total: " + str(len(progression_list)) + "\n")


type_dict = {
    "fadein": FADEIN,
    "intro": INTRO,
    "intro-a": INTRO,
    "intro-b": INTRO,
    "pre-verse": PREVERSE,
    "preverse": PREVERSE,
    "verse": VERSE,
    "pre-chorus": PRECHORUS,
    "prechorus": PRECHORUS,
    "chorus": CHORUS,
    "refrain": CHORUS,
    "bridge": BRIDGE,
    "trans": TRANS,
    "transition": TRANS,
    "interlude": INTERLUDE,
    "instrumental": INSTRUMENTAL,
    "solo": SOLO,
    "outro": OUTRO,
    "coda": OUTRO,
    "ending": OUTRO,
    "fadeout": FADEOUT,
}

if __name__ == '__main__':
    cp = ChordProgression(type="", metre="", mode="M", tonic="D", source="")
    cp.progression = [[1, 1, 1, 1, 4, 4, 4, 4], [1, 1, 1, 1, 4, 4, 4, 4], [1, 1, 1, 1, 4, 4, 4, 4],
                      [1, 1, 1, 1, 4, 4, 4, 4], ]

    print(cp)
    # listen(cp.to_midi(tempo=70, tonic="A", mode="M", instrument=SHAKUHACHI))
