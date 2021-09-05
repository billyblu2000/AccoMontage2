import os

from pretty_midi import PrettyMIDI


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


def analyze_name(file):
    name_list = file.split('_')
    # print(name_list)
    for part in name_list:
        if '-' in part:
            if 'bpm' in part:
                part = part.split(' - ')[0]
            if '(' in part:
                chord_part = part.split('(')[0]
                pattern_part = part.split('(')[1]
                pattern_part = pattern_part.split(')')[0]
                if '-' not in chord_part:
                    part = pattern_part
                else:
                    part = chord_part
            # print(part)
            final_pattern = part.split('-')
            # print(final_pattern)
            if len(final_pattern) <= 2:
                print(file)
            break
    else:
        raise Exception
    return final_pattern


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


if __name__ == '__main__':
    # notes = PrettyMIDI("/Users/billyyi/dataset/Niko/Niko's Ultimate MIDI Pack/B Major - G# Minor/3 - Rest Of "
    #                    "Pack/G#m-D#m-E (vi-iii-IV)/Epic Endings/Niko_Kotoulas_Epic_Ending_1_G#m-D#m-E ("
    #                    "vi-iii-IV).mid").instruments[0].notes
    # print(analyze_progression_pattern(notes))
    count = 0
    data_root_dir = "/Users/billyyi/dataset/Niko/Niko's Ultimate MIDI Pack/"
    for root, dirs, files in os.walk(data_root_dir):
        if '2 - Best Chords' in root \
                or ('3 - Rest Of Pack' in root and 'Basslines' not in root):
            for file in files:
                if file[0] != '.':
                    chord_pos = analyze_progression_pattern(PrettyMIDI(root + '/' + file).instruments[0].notes)
                    final_pattern = analyze_name(file)
                    if len(final_pattern) != len(chord_pos):
                        # print(chord_pos, final_pattern)
                        # print(root)
                        chord_pos = analyze_progression_pattern(PrettyMIDI(root + '/' + file).instruments[0].notes,
                                                                merge=True)
                        if len(final_pattern) != len(chord_pos):
                            count += 1
                        else:
                            print(root + '/' + file)
                            print(chord_pos, final_pattern)
                    else:
                        print(root + '/' + file)
                        print(chord_pos, final_pattern)

    print(count)
