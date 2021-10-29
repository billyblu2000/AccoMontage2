import random

from pretty_midi import Instrument

from chords.ChordProgression import print_progression_list
from utils.excp import handle_exception
from utils.utils import midi_shift


class PostProcessor:
    def __init__(self, progression_list, progression_lib, lib, meta, output_chord_style, output_progression_style):
        print_progression_list(progression_list)
        self.progression_list = [p for l in progression_list for p in l]
        self.midi_lib = lib
        self.meta = meta
        self.progression_lib = self.__create_dup_progression_list(progression_lib)
        self.progression_lib_filtered = self.__evaluate_reliability(self.progression_lib)
        self.progression_lib_filtered = self.__filter_style(self.progression_lib_filtered,
                                                            output_chord_style,
                                                            output_progression_style)
        self.midi = self.__construct_midi()

    def get(self):
        return self.midi

    @staticmethod
    def __evaluate_reliability(progression_lib, threshold=0.8):
        new_list = []
        for lst in progression_lib:
            new_sub_list = []
            for progression in lst:
                if progression.reliability >= threshold:
                    new_sub_list.append(progression)
            if len(new_sub_list) == 0:
                handle_exception(0)
            new_list.append(new_sub_list)
        return new_list

    def __create_dup_progression_list(self, progression_lib):
        new_list = []
        for progression in self.progression_list:
            dup_id = progression.progression_class['duplicate-id']
            new_list.append(progression_lib[dup_id])
        return new_list

    def __filter_style(self, progression_lib_filtered, chord_style, prog_style):
        new_list = []
        for lst in progression_lib_filtered:
            new_sub_list = []
            for progression in lst:
                if progression.progression_class['chord-style'] == chord_style \
                        and progression.progression_class['progression-style'] == prog_style:
                    new_sub_list.append(progression)
            if len(new_sub_list) == 0:
                handle_exception(0)
            new_list.append(new_sub_list)
        return new_list

    def __construct_midi(self):
        final_progression_list = []
        for i in range(len(self.progression_lib_filtered)):
            if len(self.progression_lib_filtered[i]) == 0:
                final_progression_list.append(max(self.progression_lib[i], key=lambda x: x.reliability))
            else:
                final_progression_list.append(random.choice(self.progression_lib_filtered[i]))
        ins = Instrument(program=0)
        note_list = []
        shift_count = 0
        for progression in final_progression_list:
            temp_midi = progression.to_midi(lib=self.midi_lib)
            temp_midi = midi_shift(temp_midi, shift=shift_count, tempo=120)
            note_list += temp_midi.instruments[0].notes
            shift_count += len(progression) * 2
        ins.notes += note_list
        return ins

