import pretty_midi as pyd
import numpy as np


from .chordloader import Chord_Loader


def expand_chord(chord, shift, relative=False):
    # chord = np.copy(chord)
    root = (chord[0] + shift) % 12
    chroma = np.roll(chord[1: 13], shift)
    bass = (chord[13] + shift) % 12
    root_onehot = np.zeros(12)
    root_onehot[int(root)] = 1
    bass_onehot = np.zeros(12)
    bass_onehot[int(bass)] = 1
    if not relative:
        pass
    #     chroma = np.roll(chroma, int(root))
    # print(chroma)
    # print('----------')
    return np.concatenate([root_onehot, chroma, bass_onehot])


def melody_data2matrix(melody_track, melody_downbeats):
    HOLD_PITCH = 128
    REST_PITCH = 129
    melody_downbeats = list(melody_downbeats)
    melody_downbeats.append(melody_downbeats[-1] + (melody_downbeats[-1] - melody_downbeats[-2]))
    melodySequence = []
    anchor = 0
    note = melody_track.notes[anchor]
    start = note.start
    new_note = True
    for i in range(len(melody_downbeats) - 1):
        s_curr = round(melody_downbeats[i] * 4) / 4
        s_next = round(melody_downbeats[i + 1] * 4) / 4
        delta = (s_next - s_curr) / 16
        for i in range(16):
            while note.end <= (s_curr + i * delta) and anchor < len(melody_track.notes) - 1:
                anchor += 1
                note = melody_track.notes[anchor]
                start = note.start
                new_note = True
            if s_curr + i * delta < start - 60 / 120 / 16:
                melodySequence.append(REST_PITCH)
            else:
                if not new_note:
                    melodySequence.append(HOLD_PITCH)
                else:
                    melodySequence.append(note.pitch)
                    new_note = False
    ROLL_SIZE = 130
    melodyMatrix = np.zeros((len(melodySequence), ROLL_SIZE))
    for idx, note in enumerate(melodySequence):
        melodyMatrix[idx, note] = 1
    return melodyMatrix


def melody_matrix2data(melody_matrix, tempo=120, start_time=0.0, get_list=False):
    ROLL_SIZE = 130
    HOLD_PITCH = 128
    REST_PITCH = 129
    melodyMatrix = melody_matrix[:, :ROLL_SIZE]
    melodySequence = [np.argmax(melodyMatrix[i]) for i in range(melodyMatrix.shape[0])]

    melody_notes = []
    minStep = 60 / tempo / 4
    onset_or_rest = [i for i in range(len(melodySequence)) if not melodySequence[i] == HOLD_PITCH]
    onset_or_rest.append(len(melodySequence))
    for idx, onset in enumerate(onset_or_rest[:-1]):
        if melodySequence[onset] == REST_PITCH:
            continue
        else:
            pitch = melodySequence[onset]
            start = onset * minStep
            end = onset_or_rest[idx + 1] * minStep
            noteRecon = pyd.Note(velocity=100, pitch=pitch, start=start_time + start, end=start_time + end)
            melody_notes.append(noteRecon)
    if get_list:
        return melody_notes
    else:
        melody = pyd.Instrument(program=pyd.instrument_name_to_program('Acoustic Grand Piano'))
        melody.notes = melody_notes
        return melody


def chord_data2matrix(chord_track, downbeats, resolution='beat', chord_expand=True):
    """applicable to triple chords and seventh chords"""
    if resolution == 'beat':
        num_anchords = 4
    elif resolution == 'quater':
        num_anchords = 16
    chromas = {
        #           1     2     3     4  5     6     7
        'maj': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
        'min': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
        'aug': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        'dim': [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        '7': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        'maj7': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        'min7': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        'minmaj7': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        'dim7': [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        'hdim7': [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
    }
    distr2quality = {'(4, 3)': 'maj/0',
                     '(3, 5)': 'maj/1',
                     '(5, 4)': 'maj/2',

                     '(3, 4)': 'min/0',
                     '(4, 5)': 'min/1',
                     '(5, 3)': 'min/2',

                     '(4, 4)': 'aug/0',

                     '(3, 3)': 'dim/0',
                     '(3, 6)': 'dim/1',
                     '(6, 3)': 'dim/2',

                     '(4, 3, 3)': '7/0',
                     '(3, 3, 2)': '7/1',
                     '(3, 2, 4)': '7/2',
                     '(2, 4, 3)': '7/3',

                     '(4, 3, 4)': 'maj7/0',
                     '(3, 4, 1)': 'maj7/1',
                     '(4, 1, 4)': 'maj7/2',
                     '(1, 4, 3)': 'maj7/3',

                     '(3, 4, 3)': 'min7/0',
                     '(4, 3, 2)': 'min7/1',
                     '(3, 2, 3)': 'min7/2',
                     '(2, 3, 4)': 'min7/3',

                     '(3, 4, 4)': 'minmaj7/0',
                     '(4, 4, 1)': 'minmaj7/1',
                     '(4, 1, 3)': 'minmaj7/2',
                     '(1, 3, 4)': 'minmaj7/3',

                     '(3, 3, 3)': 'dim7/0',

                     '(3, 3, 4)': 'hdim7/0',
                     '(3, 4, 2)': 'hdim7/1',
                     '(4, 2, 3)': 'hdim7/2',
                     '(2, 3, 3)': 'hdim7/3',
                     }
    NC = [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]
    last_time = 0
    chord_set = []
    chord_time = [0.0, 0.0]
    chordsRecord = []
    for note in chord_track.notes:
        if len(chord_set) == 0:
            chord_set.append(note.pitch)
            chord_time[0] = note.start
            chord_time[1] = note.end
        else:
            if note.start == chord_time[0] and note.end == chord_time[1]:
                chord_set.append(note.pitch)
            else:
                if last_time < chord_time[0]:
                    chordsRecord.append({"start": last_time, "end": chord_time[0], "chord": NC})
                chord_set.sort()
                assert (len(chord_set) == 3 or len(chord_set) == 4)
                if len(chord_set) == 3:
                    quality = distr2quality[str(((chord_set[1] - chord_set[0]), (chord_set[2] - chord_set[1])))]
                elif len(chord_set) == 4:
                    quality = distr2quality[str(((chord_set[1] - chord_set[0]), (chord_set[2] - chord_set[1]),
                                                 (chord_set[3] - chord_set[2])))]
                root = chord_set[-int(quality.split('/')[-1])] % 12
                chroma = chromas[quality.split('/')[0]]
                chroma = chroma[-root:] + chroma[:-root]
                bass = (chord_set[0] % 12 - root) % 12

                # concatenate
                chordsRecord.append({"start": chord_time[0], "end": chord_time[1], "chord": [root] + chroma + [bass]})
                last_time = chord_time[1]
                chord_set = []
                chord_set.append(note.pitch)
                chord_time[0] = note.start
                chord_time[1] = note.end
    if len(chord_set) > 0:
        if last_time < chord_time[0]:
            chordsRecord.append({"start": last_time, "end": chord_time[0], "chord": NC})
        chord_set.sort()
        assert (len(chord_set) == 3 or len(chord_set) == 4)
        if len(chord_set) == 3:
            quality = distr2quality[str(((chord_set[1] - chord_set[0]), (chord_set[2] - chord_set[1])))]
        elif len(chord_set) == 4:
            quality = distr2quality[
                str(((chord_set[1] - chord_set[0]), (chord_set[2] - chord_set[1]), (chord_set[3] - chord_set[2])))]
        root = chord_set[-int(quality.split('/')[-1])] % 12
        chroma = chromas[quality.split('/')[0]]
        chroma = chroma[-root:] + chroma[:-root]
        bass = (chord_set[0] % 12 - root) % 12
        chordsRecord.append({"start": chord_time[0], "end": chord_time[1], "chord": [root] + chroma + [bass]})
        last_time = chord_time[1]
    ChordTable = []
    anchor = 0
    chord = chordsRecord[anchor]
    start = chord['start']
    downbeats = list(downbeats)
    downbeats.append(downbeats[-1] + (downbeats[-1] - downbeats[-2]))
    for i in range(len(downbeats) - 1):
        s_curr = round(downbeats[i] * 4) / 4
        s_next = round(downbeats[i + 1] * 4) / 4
        delta = (s_next - s_curr) / num_anchords
        for i in range(num_anchords):  # one-beat resolution
            while chord['end'] <= (s_curr + i * delta) and anchor < len(chordsRecord) - 1:
                anchor += 1
                chord = chordsRecord[anchor]
                start = chord['start']
            if s_curr + i * delta < start:
                if chord_expand:
                    ChordTable.append(expand_chord(chord=NC, shift=0))
                else:
                    ChordTable.append(NC)
            else:
                if chord_expand:
                    ChordTable.append(expand_chord(chord=chord['chord'], shift=0))
                else:
                    ChordTable.append(chord['chord'])
    return np.array(ChordTable)


def chord_matrix2data(chordMatrix, tempo=120, start_time=0.0, get_list=False):
    CHORD_SIZE = 12
    cl = Chord_Loader("Seven")
    if chordMatrix.shape[-1] == CHORD_SIZE:
        pass
    elif chordMatrix.shape[-1] == 14:
        if len(chordMatrix.shape) == 2:
            chordMatrix = chordMatrix[:, 1: -1]
        elif len(chordMatrix.shape) == 3:
            chordMatrix = chordMatrix[:, :, 1: -1]
    elif chordMatrix.shape[-1] == 36:
        if len(chordMatrix.shape) == 2:
            chordMatrix = chordMatrix[:, 12: -12]
        elif len(chordMatrix.shape) == 3:
            chordMatrix = chordMatrix[:, :, 12: -12]
    chordSequence = []
    for i in range(chordMatrix.shape[0]):
        chordset = [idx for idx in range(CHORD_SIZE) if chordMatrix[i][idx] == 1]
        chordSequence.append(cl.note2name(chordset))
    minStep = 60 / tempo / 4  # 16th quantization
    chord_notes = []
    onset_or_rest = [0]
    onset_or_rest_ = [i for i in range(1, len(chordSequence)) if chordSequence[i] != chordSequence[i - 1]]
    onset_or_rest = onset_or_rest + onset_or_rest_
    onset_or_rest.append(len(chordSequence))
    for idx, onset in enumerate(onset_or_rest[:-1]):
        if chordSequence[onset] == 'NC':
            continue
        else:
            chordset = cl.name2note(chordSequence[onset])
            if chordset == None:
                continue
            start = onset * minStep
            end = onset_or_rest[idx + 1] * minStep
            for note in chordset:
                noteRecon = pyd.Note(velocity=100, pitch=note + 4 * 12, start=start_time + start, end=start_time + end)
                chord_notes.append(noteRecon)
    if get_list:
        return chord_notes
    else:
        chord = pyd.Instrument(program=pyd.instrument_name_to_program('Acoustic Grand Piano'))
        chord.notes = chord_notes
        return chord


def accompany_data2matrix(accompany_track, downbeats):
    time_stamp_sixteenth_reso = []
    delta_set = []
    downbeats = list(downbeats)
    downbeats.append(downbeats[-1] + (downbeats[-1] - downbeats[-2]))
    for i in range(len(downbeats) - 1):
        s_curr = round(downbeats[i] * 16) / 16
        s_next = round(downbeats[i + 1] * 16) / 16
        delta = (s_next - s_curr) / 16
        for i in range(16):
            time_stamp_sixteenth_reso.append(s_curr + delta * i)
            delta_set.append(delta)
    time_stamp_sixteenth_reso = np.array(time_stamp_sixteenth_reso)

    pr_matrix = np.zeros((time_stamp_sixteenth_reso.shape[0], 128))
    for note in accompany_track.notes:
        onset = note.start
        t = np.argmin(np.abs(time_stamp_sixteenth_reso - onset))
        p = note.pitch
        duration = int(round((note.end - onset) / delta_set[t]))
        pr_matrix[t, p] = duration
    return pr_matrix


def accompany_matrix2data(pr_matrix, tempo=120, start_time=0.0, get_list=False):
    alpha = 0.25 * 60 / tempo
    notes = []
    for t in range(pr_matrix.shape[0]):
        for p in range(128):
            if pr_matrix[t, p] >= 1:
                s = alpha * t + start_time
                e = alpha * (t + pr_matrix[t, p]) + start_time
                notes.append(pyd.Note(100, int(p), s, e))
    if get_list:
        return notes
    else:
        acc = pyd.Instrument(program=pyd.instrument_name_to_program('Acoustic Grand Piano'))
        acc.notes = notes
        return acc


if __name__ == '__main__':
    midi = pyd.PrettyMIDI('C:/Users/lenovo/Desktop/accomontage code/ECNU_leadsheet.mid')
    melody = midi.instruments[0]
    chord = midi.instruments[1]
    downbeats = midi.get_downbeats()
    melody_matrix = melody_data2matrix(melody, downbeats)
    melody_recon = melody_matrix2data(melody_matrix, 120)
    chordTable = chord_data2matrix(chord, downbeats, 'quater')

    """chordTable_onebeat_res = np.zeros((chordTable.shape[0]*4, chordTable.shape[1]))
    for i in range(chordTable.shape[0]):
        chordTable_onebeat_res[i*4: i*4+4, :] = chordTable[i]
    chord_recon = chord_matrix2data(chordTable_onebeat_res)"""
    # print(chordTable.shape)
    chord_recon = chord_matrix2data(chordTable)
    midi.instruments[0] = melody_recon
    midi.instruments[1] = chord_recon
    midi.write('C:/Users/lenovo/Desktop/accomontage code/test_recon.mid')

    """   midi = pyd.PrettyMIDI('C:/Users/lenovo/Desktop/masaiqu.mid')
    melody = midi.instruments[0]
    acc = midi.instruments[1]
    downbeats = midi.get_downbeats()
    melody_matrix = melody_data2matrix(melody, downbeats)
    melody_recon = melody_matrix2data(melody_matrix, 120)

    pr_matrix = accompany_data2matrix(acc, downbeats)
    acc_recon = accompany_matrix2data(pr_matrix, 120)
    midi.instruments[0] = melody_recon
    midi.instruments[1] = acc_recon
    midi.write('C:/Users/lenovo/Desktop/masaiqu_recon.mid')"""
