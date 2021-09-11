import os
import pickle

from pretty_midi import PrettyMIDI

from chords.Chord import Chord, print_chord_list
from chords.ChordProgression import ChordProgression, print_progression_list
from utils import utils


def get_class_from_path_and_name(root, file):
    progression_class = {
        'name': 'unknown',
        'tonic': 'unknown',
        'type': 'unknown',  # positions, e.g., 'verse', 'chorus', ...
        'pattern': 'unknown',  # e.g., 'I-vi-IV-V', ...
        'cycle': 'unknown',  # 'no-cycle', 'short', 'mid', 'long', ...?
        'progression-style': 'unknown',  # 'pop', 'edm', 'dark', ...
        'chord-style': 'unknown',  # 'classy', 'emotional', 'standard'
        'performing-style': 'unknown',
        'rhythm': 'unknown',  # 'fast-back-and-force', 'fast-same-time', 'slow'
        'epic-endings': 'unknown',  # 'True', 'False'
        'melodic': 'unknown'
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
            if 'Heaven' in file:
                progression_class['performing-style'] = 'arpeggio-heaven'
            elif 'Back_And_Forth' in file:
                progression_class['performing-style'] = 'arpeggio-back_and_force'
            elif 'Rolling' in file:
                progression_class['performing-style'] = 'arpeggio-rolling'
            elif 'Triplets' in file:
                progression_class['performing-style'] = 'arpeggio-triplets'
            else:
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
        elif 'Chord Breakdown' in root:
            if 'Cluster' in file:
                progression_class['chord-style'] = 'cluster'
            elif 'First Inversion' in file:
                progression_class['chord-style'] = 'first-inversion'
            elif 'Second Inversion' in file:
                progression_class['chord-style'] = 'second-inversion'
            elif 'Root_Note' in file:
                progression_class['chord-style'] = 'root-note'
            elif 'Power Chord' in file:
                progression_class['chord-style'] = 'power-chord'
            elif 'Full Octave' in file:
                progression_class['chord-style'] = 'full-octave'
            elif 'Power Octave' in file:
                progression_class['chord-style'] = 'power-octave'
            elif 'Seventh' in file:
                progression_class['chord-style'] = 'seventh'
            elif 'Sus2' in file:
                progression_class['chord-style'] = 'sus2'
            elif 'Sus4' in file:
                progression_class['chord-style'] = 'sus4'
    progression_class['name'] = file
    root_list = root.split('/')
    for item in root_list:
        if 'Major' in item:
            progression_class['tonic'] = item.split('-')[0].strip().split(' ')[0].strip() \
                                         + '-' \
                                         + item.split('-')[1].strip().split(' ')[0].strip()
            break
    else:
        raise Exception
    return progression_class


def note_time_to_pos(time):
    return int(round(time / 0.25, 0))


def analyze_progression_pattern(notes, merge=False):
    # count notes at each pos
    all_starts = [note.start for note in notes]
    all_pos = [note_time_to_pos(start) for start in all_starts]
    count_pos = {}
    for pos in all_pos:
        if pos not in count_pos:
            count_pos[pos] = 1
        else:
            count_pos[pos] += 1

    # decide bound x, s.t. a pos is a chord pos if it have notes >= x
    chord_bound = two_means_clustering(count_pos.values())

    # find all chord pos
    chord_pos = set()
    for pos in all_pos:
        if count_pos[pos] >= chord_bound:
            chord_pos.add(pos)
    chord_pos = sorted(list(chord_pos))

    if merge:

        # find all notes at a specific chord pos
        pos_note = {i: [] for i in chord_pos}
        for note in notes:
            pos = note_time_to_pos(note.start)
            if pos in chord_pos:
                pos_note[pos].append(note.pitch)

        # merge chord pos if two adjacent chords is actually the same chord
        merged_chord_pos = [chord_pos[0]]
        for i in range(len(chord_pos) - 1):
            if compare_chords(pos_note[chord_pos[i]], pos_note[chord_pos[i + 1]]):
                continue
            else:
                merged_chord_pos.append(chord_pos[i + 1])

        chord_pos = merged_chord_pos

    return chord_pos


def analyze_name(file, root):
    name_list = file.split('_')
    for part in name_list:
        if '-' in part:
            if 'bpm' in part:
                part = part.split(' - ')[0]
            if '(' in part:
                chord_part = part.split('(')[0]
                pattern_part = part.split('(')[1]
                pattern_part = pattern_part.split(')')[0]
                if '-' not in chord_part:
                    root_list = root.split('/')
                    for dir in root_list:
                        if '(' in dir:
                            part = dir.split('(')[0].strip()
                            break
                    else:
                        return False
                else:
                    part = chord_part
            if part[-1] == ')':
                part = part.rstrip(')')
            final_pattern = part.split('-')
            break
    else:
        raise Exception

    striped = []
    for i in final_pattern:
        striped.append(i.strip())
    return striped


def compare_chords(chord_list1, chord_list2):
    for pitch2 in chord_list2:
        for pitch1 in chord_list1:
            if (pitch2 - pitch1) % 12 == 0:
                break
        else:
            return False
    return True


def two_means_clustering(all_appears):
    stop = 0.1

    def distance(pos1, pos2):
        return abs(pos1 - pos2)

    centroid1 = 0
    centroid2 = max(all_appears)
    cls1 = []
    cls2 = []
    while True:
        for pos in all_appears:
            if distance(pos, centroid1) < distance(pos, centroid2):
                cls1.append(pos)
            else:
                cls2.append(pos)

        new_centroid1 = sum(cls1) / len(cls1) if len(cls1) != 0 else centroid1
        new_centroid2 = sum(cls2) / len(cls2) if len(cls2) != 0 else centroid2
        if distance(new_centroid1, centroid1) <= stop and distance(new_centroid2, centroid2) <= stop:
            break
        else:
            centroid1 = new_centroid1
            centroid2 = new_centroid2
            cls1 = []
            cls2 = []
    return min(cls2)


def assign_chord(chord_pos, chord_list):
    if len(chord_list) == 1:
        return False
    if len(chord_pos) == len(chord_list):
        return {chord_pos[i]: chord_list[i] for i in range(len(chord_pos))}
    elif len(chord_pos) % len(chord_list) == 0:
        length = chord_pos[1] - chord_pos[0]
        if length <= 4:
            return False
        for i in range(len(chord_pos) - 1):
            if chord_pos[i + 1] - chord_pos[i] != length:
                break
        else:
            return {chord_pos[i]: chord_list[i % len(chord_list)] for i in range(len(chord_pos))}
        return False
    else:
        return False


def analyze_mode(final_pattern, param):
    maj_tonic = param.split('-')[0]
    min_tonic = param.split('-')[1]
    if maj_tonic in final_pattern:
        return 'M'
    else:
        if min_tonic in param:
            return 'm'
        else:
            return 'M'


def construct_progression(assign, progression_class, metre):
    assert metre == '4/4'
    name = progression_class['name']
    shifted_assign = {}
    for item in assign.items():
        shifted_assign[item[0] - shift_dict[name][0]] = item[1]
    progression_list = []
    end_time = shift_dict[name][1]
    if end_time % 16 != 0:
        end_time = (end_time // 16 + 1) * 16
    pos_pool = sorted(list(shifted_assign.keys()))
    chord_pool = [shifted_assign[i] for i in pos_pool]
    if pos_pool[0] != 0:
        return False
    cursor = 0
    bar_list = []
    for i in range(end_time):
        if cursor + 1 != len(pos_pool):
            if i >= pos_pool[cursor + 1]:
                cursor += 1
        bar_list.append(Chord(name=chord_pool[cursor]))
        if len(bar_list) == 8:
            progression_list.append(bar_list)
            bar_list = []
    return progression_list


def analyze_metre(assign):
    return '4/4'


if __name__ == '__main__':
    try:
        file = open('temp', 'rb')
    except:
        raise Exception('Please run process_niko_save_source_base.py first!')
    shift_dict = pickle.load(file)
    file.close()
    count = 0
    all_progressions = []
    # count_mode = {'M':0,'m':0}
    data_root_dir = "/Users/billyyi/dataset/Niko/Niko's Ultimate MIDI Pack/"
    for root, dirs, files in os.walk(data_root_dir):
        if '2 - Best Chords' in root \
                or ('3 - Rest Of Pack' in root and 'Basslines' not in root):
            for file in files:
                if file[0] != '.':

                    progression_class = get_class_from_path_and_name(root, file)
                    chord_pos = analyze_progression_pattern(PrettyMIDI(root + '/' + file).instruments[0].notes)

                    final_pattern = analyze_name(file, root)
                    if not final_pattern:
                        count += 1
                        print('\033[1;31m' + 'Analyze name failed: ' + file + ' \033[0m')
                        continue

                    assign = assign_chord(chord_pos, final_pattern)
                    if not assign:
                        chord_pos = analyze_progression_pattern(PrettyMIDI(root + '/' + file).instruments[0].notes,
                                                                merge=True)
                        assign = assign_chord(chord_pos, final_pattern)
                        if not assign:
                            count += 1
                            print('\033[1;31m' + 'Assigning chord failed: ' + file + ' \033[0m')
                            continue

                    mode = analyze_mode(final_pattern, progression_class['tonic'])
                    # count_mode[mode] += 1

                    metre = analyze_metre(assign)
                    progression_list = construct_progression(assign, progression_class, metre)
                    if not progression_list:
                        count += 1
                        print('\033[1;31m' + 'Constructing progression failed: ' + file + ' \033[0m')
                        continue

                    print('\033[1;32m' + 'Success: ' + file + ' \033[0m')

                    progression = ChordProgression(source=progression_class['name'],
                                                   tonic=progression_class['tonic'].split('-')[0]
                                                   if mode == 'M' else progression_class['tonic'].split('-')[1],
                                                   type=None,
                                                   metre=metre,
                                                   mode=mode,
                                                   saved_in_source_base=True)
                    progression.progression = progression_list

                    progression.progression_class['pattern'] = progression_class['pattern']
                    progression.progression_class['cycle'] = utils.calculate_density(progression)
                    progression.progression_class['progression-style'] = progression_class['progression-style']
                    progression.progression_class['chord-style'] = progression_class['chord-style']
                    progression.progression_class['performing-style'] = progression_class['performing-style']
                    progression.progression_class['rhythm'] = progression_class['rhythm']
                    progression.progression_class['epic-endings'] = progression_class['epic-endings']
                    progression.progression_class['melodic'] = progression_class['melodic']

                    all_progressions.append(progression)
    print_progression_list(all_progressions)
    # file = open('new_progressions.pcls', 'wb')
    # pickle.dump(all_progressions, file)
    # file.close()
    print(count)
