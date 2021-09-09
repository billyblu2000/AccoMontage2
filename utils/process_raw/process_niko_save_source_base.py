import os
import pickle
from typing import List

from pretty_midi import PrettyMIDI, Note

from utils.process_raw.process_niko_save_prog_class import get_class_from_path_and_name


def note_time_to_pos(time):
    return int(round(time / 0.25, 0))


def change_key_to_C(pitch, tonic):
    tonic_list = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    pitch -= tonic_list.index(tonic)
    return pitch


def midi_to_source_base(midi: PrettyMIDI, tonic):
    notes = midi.instruments[0].notes

    # ensure that the first note starts at time 0
    start_time = 1000
    ori_start = 1000
    end_time = 0
    for note in notes:
        if note.start < start_time:
            start_time = note.start
            ori_start = note_time_to_pos(note.start)
    new_notes = []
    for note in notes:
        new_notes.append(Note(start=note.start - start_time,
                               end=note.end - start_time,
                               velocity=note.velocity,
                               pitch=note.pitch))
    notes = new_notes

    # change note format
    all_formatted_notes = []
    max_end = 0
    for note in notes:
        start = note_time_to_pos(note.start)
        end = note_time_to_pos(note.end)
        if end > max_end:
            max_end = end
        pitch = change_key_to_C(note.pitch, tonic)
        formatted_notes = [start, end, pitch, note.velocity]
        all_formatted_notes.append(formatted_notes)
    return all_formatted_notes, ori_start, max_end


def create_source_base(names: List[str], midis: List[PrettyMIDI], tonics):
    assert len(names) == len(midis)
    source_base_dict = dict()
    temp_dict = dict()
    for i in range(len(names)):
        source_base = midi_to_source_base(midis[i], tonics[i])
        source_base_dict[names[i]] = source_base[0]
        temp_dict[names[i]] = [source_base[1], source_base[2]]
    # file = open('source_base.pnt', 'wb')
    # pickle.dump(source_base_dict, file)
    # file.close()
    file = open('temp', 'wb')
    pickle.dump(temp_dict, file)
    file.close()


if __name__ == '__main__':
    data_root_dir = "/Users/billyyi/dataset/Niko/Niko's Ultimate MIDI Pack/"
    all = []
    for root, dirs, files in os.walk(data_root_dir):
        if '2 - Best Chords' in root \
                or ('3 - Rest Of Pack' in root and 'Basslines' not in root):
            for file in files:
                if file[0] != '.':
                    data_item = []
                    progression_class = get_class_from_path_and_name(root, file)
                    data_item.append(file)
                    data_item.append(PrettyMIDI(root + '/' + file))
                    data_item.append(progression_class['tonic'])
                    data_item.append(progression_class)
                    all.append(data_item)
    all_names = [i[0] for i in all]
    all_midis = [i[1] for i in all]
    all_tonics = [i[2] for i in all]
    create_source_base(all_names, all_midis, all_tonics)
    # file = open('source_base.pnt','rb')
    # pickle.load(file)
