import os
import pickle
from typing import List

from pretty_midi import PrettyMIDI, Note


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
    for note in notes:
        if note.start < start_time:
            start_time = note.start
    if start_time != 0:
        new_notes = []
        for note in notes:
            new_notes.append(Note(start=note.start - start_time,
                                  end=note.end - start_time,
                                  velocity=note.velocity,
                                  pitch=note.pitch))
        notes = new_notes

    # change note format
    all_formatted_notes = []
    for note in notes:
        start = note_time_to_pos(note.start)
        end = note_time_to_pos(note.end)
        pitch = change_key_to_C(note.pitch, tonic)
        formatted_notes = [start, end, pitch, note.velocity]
        all_formatted_notes.append(formatted_notes)
    return all_formatted_notes


def create_source_base(names: List[str], midis: List[PrettyMIDI], tonics):
    assert len(names) == len(midis)
    source_base_dict = dict()
    for i in range(len(names)):
        source_base_dict[names[i]] = midi_to_source_base(midis[i], tonics[i])
    file = open('source_base.pnt', 'wb')
    pickle.dump(source_base_dict, file)
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
                    progression_class = {
                        'name': 'unknown',
                        'type': 'unknown',  # positions, e.g., 'verse', 'chorus', ...
                        'pattern': 'unknown',  # e.g., 'I-vi-IV-V', ...
                        'cycle': 'unknown',  # 'no-cycle', 'short', 'mid', 'long', ...?
                        'progression-style': 'unknown',  # 'pop', 'edm', 'dark', ...
                        'chord-style': 'unknown',  # 'classy', 'emotional', 'standard'
                        'performing-style': 'unknown',
                        'rhythm': 'unknown',  # 'fast-back-and-force', 'fast-same-time', 'slow'
                        'epic-endings': 'unknown',  # 'True', 'False'
                    }
                    if '2 - Best Chords' in root:
                        if 'Dark_HipHop_Trap' in root:
                            progression_class['progression-style'] = 'dark'
                        elif 'EDM' in root:
                            progression_class['progression-style'] = 'edm'
                        elif 'Emotional' in root:
                            progression_class['progression-style'] = 'emotional'
                        elif 'Pop' in root:
                            progression_class['progression-style'] = 'pop'
                        elif 'R&B_Neosoul' in root:
                            progression_class['progression-style'] = 'r&b'
                        if 'Classy_7th_9th' in root:
                            progression_class['chord-style'] = 'classy'
                        elif 'Emotional' in root:
                            progression_class['chord-style'] = 'emotional'
                        elif 'Standard' in root:
                            progression_class['chord-style'] = 'standard'
                    elif '3 - Rest Of Pack' in root:
                        root_list = root.split('/')
                        for item in root_list:
                            if '(' in item:
                                pattern = item
                                break
                        else:
                            raise Exception
                        pattern = pattern.split('(')[1].rstrip(')')
                        progression_class['pattern'] = pattern
                        if 'Arps' in root:
                            progression_class['performing-style'] = 'arpeggio'
                        elif 'Epic Endings' in root:
                            progression_class['epic-endings'] = 'True'
                        elif 'Back & Forth' in root:
                            progression_class['rhythm'] = 'fast-back-and-force'
                        elif 'Same Time' in root:
                            progression_class['rhythm'] = 'fast-same-time'
                        elif 'Slow Chord Rhythm' in root:
                            progression_class['rhythm'] = 'slow'
                        elif 'Melodies' in root:
                            progression_class['melodic'] = 'True'
                    progression_class['name'] = file
                    root_list = root.split('/')
                    for item in root_list:
                        if 'Major' in item:
                            tonic = item.split(' ')[0]
                            break
                    else:
                        raise Exception
                    data_item.append(file)
                    data_item.append(PrettyMIDI(root + '/' + file))
                    data_item.append(tonic)
                    data_item.append(progression_class)
                    all.append(data_item)
    all_names = [i[0] for i in all]
    all_midis = [i[1] for i in all]
    all_tonics = [i[2] for i in all]
    create_source_base(all_names, all_midis, all_tonics)
    # file = open('source_base.pnt','rb')
    # pickle.load(file)