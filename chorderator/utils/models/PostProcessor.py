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
        new_notes = []
        for note in self.midi.notes:
            if note.duration != 0:
                new_notes.append(note)
        self.midi.notes = new_notes
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
            temp_midi = progression.to_midi(lib=self.midi_lib, tempo=self.meta['tempo'])
            temp_midi = midi_shift(temp_midi, shift=shift_count, tempo=self.meta['tempo'])
            note_list += temp_midi.instruments[0].notes
            shift_count += len(progression) * 2
        note_list = self.__smooth_notes(note_list)
        ins.notes += note_list
        return ins

    def __smooth_notes(self, note_list):

        velocity_dynamics = (30, 90)
        pitch_dynamic = (29, 74)

        def map_velocity(velocity):
            return int((velocity_dynamics[1] - velocity_dynamics[0]) * (velocity / 128) + velocity_dynamics[0])

        def is_note_list_in_pitch_dynamic(notes_index):
            try:
                avg = sum([note_list[idx].pitch for idx in notes_index]) / len(notes_index)
                min_pitch = min([note_list[idx] for idx in notes_index], key=lambda x:x.pitch).pitch
                max_pitch = max([note_list[idx] for idx in notes_index], key=lambda x: x.pitch).pitch
                if avg < (pitch_dynamic[1] - pitch_dynamic[0]) / 10 + pitch_dynamic[0] or min_pitch < pitch_dynamic[0]:
                    return -1
                if avg > pitch_dynamic[1] - (pitch_dynamic[1] - pitch_dynamic[0]) / 10 or max_pitch > pitch_dynamic[1]:
                    return 1
                return 0
            except:
                return 0

        for note in note_list:
            note.velocity = map_velocity(note.velocity)

        four_bars_length = self.meta['unit'] * 64
        max_end = max(note_list, key = lambda x:x.end).end
        cursor = 0
        while cursor <= max_end:
            section_notes_index = []
            for i in range(len(note_list)):
                if cursor <= note_list[i].start < cursor + four_bars_length:
                    section_notes_index.append(i)
            compare_result = is_note_list_in_pitch_dynamic(section_notes_index)
            if compare_result == 1:
                for idx in section_notes_index:
                    note_list[idx].pitch -= 12
            elif compare_result == -1:
                for idx in section_notes_index:
                    note_list[idx].pitch += 12
            cursor += four_bars_length
        return note_list
