import random

from pretty_midi import Instrument

from ...chords.ChordProgression import print_progression_list, read_progressions
from ...utils.excp import handle_exception
from ...utils.utils import midi_shift


class PostProcessor:

    filter_by_new_label = True

    def __init__(self, progression_list, progression_lib, lib, meta, output_chord_style, output_progression_style, output_style):
        if type(progression_list[0][0]) == int:
            progression_list = [[progression_lib[i][0] for i in sub_list] for sub_list in progression_list]
        print_progression_list(progression_list)
        self.progression_list = [p for l in progression_list for p in l]
        self.midi_lib = lib
        self.meta = meta
        self.original_progression_lib = progression_lib
        self.progression_lib = self.__create_dup_progression_list(self.original_progression_lib)
        self.progression_lib_filtered = self.__evaluate_reliability(self.progression_lib)
        self.progression_lib_filtered = self.__filter_style(self.progression_lib_filtered,
                                                            output_chord_style,
                                                            output_progression_style,
                                                            output_style)
        self.midi, self.log = self.__construct_midi()

    def get(self):
        new_notes = []
        for note in self.midi.notes:
            if note.duration != 0:
                new_notes.append(note)
        self.midi.notes = new_notes
        return self.midi, self.log

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

    def __filter_style(self, progression_lib_filtered, chord_style, prog_style, output_style):
        new_list = []
        count = 0
        for lst in progression_lib_filtered:
            new_sub_list = []
            for progression in lst:
                if self.filter_by_new_label:
                    if type(output_style) == str:
                        if progression.progression_class['new_label'] == output_style:
                            new_sub_list.append(progression)
                    elif type(output_style) == list and len(output_style) == len(progression_lib_filtered):
                        if progression.progression_class['new_label'] == output_style[count]:
                            new_sub_list.append(progression)
                    else:
                        handle_exception(351)
                else:
                    if progression.progression_class['chord-style'] == chord_style \
                            and progression.progression_class['progression-style'] == prog_style:
                        new_sub_list.append(progression)
            if len(new_sub_list) == 0:
                handle_exception(0)
            new_list.append(new_sub_list)
            count += 1
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
        log = []
        for progression in final_progression_list:
            log.append(self.__info(progression))
            temp_midi = progression.to_midi(lib=self.midi_lib, tempo=self.meta['tempo'], tonic=self.meta['tonic'])
            temp_midi = midi_shift(temp_midi, shift=shift_count, tempo=self.meta['tempo'])
            note_list += temp_midi.instruments[0].notes
            shift_count += len(progression) * 2
        note_list = self.__smooth_notes(note_list)
        ins.notes += note_list
        return ins, log

    def __smooth_notes(self, note_list):

        velocity_dynamics = (30, 90)
        pitch_dynamic = (29, 74)

        def map_velocity(velocity):
            return int((velocity_dynamics[1] - velocity_dynamics[0]) * (velocity / 128) + velocity_dynamics[0])

        def is_note_list_in_pitch_dynamic(notes_index):
            try:
                avg = sum([note_list[idx].pitch for idx in notes_index]) / len(notes_index)
                min_pitch = min([note_list[idx] for idx in notes_index], key=lambda x: x.pitch).pitch
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
        max_end = max(note_list, key=lambda x: x.end).end
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

    def __info(self, progression):
        info = {
            'score': 1,
            'chord_style': progression.progression_class['chord-style'],
            'progression_style': progression.progression_class['progression-style'],
            'duplicate_id': progression.progression_class['duplicate-id'],
            'style': progression.progression_class['new_label'],
            'cycle': progression.progression_class['cycle'],
            'pattern': progression.progression_class['pattern'],
            'position': progression.meta['type'],
            'rhythm': progression.progression_class['rhythm'],
            'progression': None,
            'other_possible_styles': self.__search_other_styles(progression)
        }
        progression_list = progression.get(flattened=False, only_root=False, only_degree=False)
        progression_list_str = []
        for bar in progression_list:
            memo = None
            bar_str = []
            for chord in bar:
                if memo:
                    if chord == memo:
                        continue
                bar_str.append(str(chord))
                memo = chord
            progression_list_str.append(bar_str)
        info['progression'] = progression_list_str
        return info

    def __search_other_styles(self, progression):
        all_others = self.original_progression_lib[progression.progression_class['duplicate-id']]
        my_set = set()
        for prog in all_others:
            my_set.add(prog.progression_class['new_label'])
        return list(my_set)
