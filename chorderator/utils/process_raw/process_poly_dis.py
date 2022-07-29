import copy

import numpy as np
import pretty_midi

import chorderator as cdt


def note_mat2pr(note_mat):
    max_cell = max(note_mat, key=lambda x: x[1])[1]
    pr = np.zeros((max_cell * 2, 128), dtype=int)
    for note in note_mat:
        pr[note[0] * 2, note[2]] = note[1] * 2 - note[0] * 2
    return pr


def note_mat2chroma(note_mat, roots):
    roots = [chord.root for chord in roots]
    eighth_note_length = 0.25
    ins = pretty_midi.Instrument(0)
    for note in note_mat:
        ins.notes.append(pretty_midi.Note(start=note[0] * eighth_note_length, end=note[1] * eighth_note_length,
                                          pitch=note[2], velocity=note[3]))
    midi = pretty_midi.PrettyMIDI()
    midi.instruments.append(ins)
    downbeats = midi.get_downbeats()
    return chord_data2matrix_new(ins, downbeats, roots, 'quater')


def chord_data2matrix_new(chord_track, downbeats, roots, resolution='beat', tolerence=0.125):
    """applicable to triple chords and seventh chords"""
    if resolution == 'beat':
        num_anchords = 4
    elif resolution == 'quater':
        num_anchords = 16

    list_of_roots = []
    table_of_root = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'Fb': 4, 'E#': 5, 'F': 5, "F#": 6, \
                     'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11, 'Cb': 11, 'B#': 0}
    # print(roots)
    for root in roots:
        chord_num = table_of_root[root]
        list_of_roots.append(chord_num)
        list_of_roots.append(chord_num)
    # print(len(list_of_roots))

    NC = [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]
    last_time = 0
    chord_set = []
    chord_time = [[0.0], [0.0]]
    chordsRecord = []

    sorted_chord_track_notes = sorted(chord_track.notes, key=lambda x: x.start)
    for note in sorted_chord_track_notes:
        if note.end - note.start <= 0.1:
            note.end += downbeats[-1] - downbeats[-2]

        if len(chord_set) == 0:
            chord_set.append(note.pitch)
            chord_time[0] = [note.start]
            chord_time[1] = [note.end]
        else:
            if (abs(note.start - np.mean(chord_time[0])) < tolerence) and (
                    abs(note.end - np.mean(chord_time[1])) < tolerence):
                chord_set.append(note.pitch)
                chord_time[0].append(note.start)
                chord_time[1].append(note.end)
            else:
                if last_time < np.mean(chord_time[0]):  # where did we update last_time?
                    chordsRecord.append({"start": last_time, "end": np.mean(chord_time[0]), "chord": NC})
                chord_set.sort()
                chroma = copy.copy(NC)
                for idx in chord_set:
                    chroma[idx % 12 + 1] = 1
                chroma[0] = 0  # use our label
                chroma[-1] = chord_set[0] % 12

                # concatenate
                chordsRecord.append({"start": np.mean(chord_time[0]), "end": np.mean(chord_time[1]), "chord": chroma})
                last_time = np.mean(chord_time[1])
                chord_set = []
                chord_set.append(note.pitch)
                chord_time[0] = [note.start]
                chord_time[1] = [note.end]
    if len(chord_set) > 0:
        if last_time < np.mean(chord_time[0]):
            chordsRecord.append({"start": last_time, "end": np.mean(chord_time[0]), "chord": NC})
        # chord_set.sort()
        chroma = copy.copy(NC)
        for idx in chord_set:
            chroma[idx % 12 + 1] = 1
        chroma[0] = 0  # use our label
        chroma[-1] = chord_set[0] % 12
        chordsRecord.append({"start": np.mean(chord_time[0]), "end": np.mean(chord_time[1]), "chord": chroma})
        last_time = np.mean(chord_time[1])
    ChordTable = []
    anchor = 0
    chord = chordsRecord[anchor]
    start = chord['start']
    downbeats = list(downbeats)
    downbeats.append(downbeats[-1] + (downbeats[-1] - downbeats[-2]))
    # print(downbeats)
    for i in range(len(downbeats) - 1):
        s_curr = round(downbeats[i] * 4) / 4
        s_next = round(downbeats[i + 1] * 4) / 4
        delta = (s_next - s_curr) / num_anchords
        for j in range(num_anchords):  # one-beat resolution
            while chord['end'] <= (s_curr + j * delta) and anchor < len(chordsRecord) - 1:
                anchor += 1
                chord = chordsRecord[anchor]
                start = chord['start']
            if s_curr + j * delta < start:
                ChordTable.append(NC)
            else:
                fourteen_dim_chroma = copy.copy(chord['chord'])
                fourteen_dim_chroma[0] = list_of_roots[16 * i + j]
                fourteen_dim_chroma[-1] = (fourteen_dim_chroma[-1] - list_of_roots[16 * i + j]) % 12
                ChordTable.append(fourteen_dim_chroma)
    return np.array(ChordTable, dtype=int)


def should_filter(prog):
    if prog.progression_class['performing-style'] == 'arpeggio' \
            or prog.progression_class['rhythm'] in ['fast-back-and-force', 'fast-same-time', 'slow'] \
            or prog.progression_class['epic-endings'] == 'True' or prog.progression_class['epic-endings'] is True \
            or prog.progression_class['melodic'] == 'True' or prog.progression_class['melodic'] is True:
        return True
    else:
        return False


def to_original_pitch(note_mat, original, mode):
    root_str_2_num = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'Fb': 4, 'E#': 5, 'F': 5, "F#": 6,
                      'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11, 'Cb': 11, 'B#': 0}
    if mode == 'M' or mode == 'maj':
        gap = root_str_2_num[original]
    elif mode == 'm' or mode == 'min':
        gap = root_str_2_num[original] - 9
    else:
        raise Exception
    if gap >= 7:
        gap -= 12
    if gap <= -6:
        gap += 12
    for note in note_mat:
        note[2] += gap
    return note_mat


if __name__ == '__main__':

    # data = cdt.load_data()
    # l = data['lib']
    # d = data['dict']
    # all_pr, all_c = [], []
    # total, filtered = 0, 0
    # for dup_list in list(d.values()):
    #     for prog in dup_list:
    #         if not should_filter(prog):
    #             try:
    #                 source = to_original_pitch(l[prog.meta['source']], prog.meta['tonic'], prog.meta['mode'])
    #                 # print(source)
    #                 pr = note_mat2pr(source)
    #                 # print(all_pr)
    #                 c = note_mat2chroma(source, prog.get(flattened=True))
    #                 # print(all_c)
    #                 all_pr.append(pr)
    #                 all_c.append(c)
    #                 filtered += 1
    #                 print(filtered)
    #             except Exception as e:
    #                 print(e)
    #         total += 1
    # print(total, filtered)
    # np.savez('poly-dis-niko.npz', pr=all_pr, c=all_c)

    data = np.load('poly-dis-niko.npz', allow_pickle=True)
    pr = data['pr']
    c = data['c']
    print(pr[0])
    print(c[0])
    pass
