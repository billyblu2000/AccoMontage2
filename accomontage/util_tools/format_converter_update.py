import pretty_midi as pyd
import numpy as np
import copy


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


def chord_data2matrix(chord_track, downbeats, resolution='beat', chord_expand=True, tolerence=0.125):
    """applicable to triple chords and seventh chords"""
    if resolution == 'beat':
        num_anchords = 4
    elif resolution == 'quater':
        num_anchords = 16

    NC = [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]
    last_time = 0
    chord_set = []
    chord_time = [[0.0], [0.0]]
    chordsRecord = []
    for note in chord_track.notes:
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
                if last_time < np.mean(chord_time[0]):
                    chordsRecord.append({"start": last_time, "end": np.mean(chord_time[0]), "chord": NC})
                chord_set.sort()
                chroma = copy.copy(NC)
                for idx in chord_set:
                    chroma[idx % 12 + 1] = 1
                chroma[0] = chord_set[0] % 12
                chroma[-1] = 0

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
        chroma[0] = chord_set[0] % 12
        chroma[-1] = 0
        chordsRecord.append({"start": np.mean(chord_time[0]), "end": np.mean(chord_time[1]), "chord": chroma})
        last_time = np.mean(chord_time[1])
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
    # cl = Chord_Loader("Seven")
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
        chordSequence.append(''.join([str(int(j)) for j in chordMatrix[i]]))
    minStep = 60 / tempo / 4  # 16th quantization
    chord_notes = []
    onset_or_rest = [0]
    onset_or_rest_ = [i for i in range(1, len(chordSequence)) if chordSequence[i] != chordSequence[i - 1]]
    onset_or_rest = onset_or_rest + onset_or_rest_
    onset_or_rest.append(len(chordSequence))
    for idx, onset in enumerate(onset_or_rest[:-1]):
        # if chordSequence[onset] == '000000000000':
        #    continue
        # else:
        chordset = [int(i) for i in chordSequence[onset]]
        # if chordset == None:
        #    continue
        start = onset * minStep
        end = onset_or_rest[idx + 1] * minStep
        for note, value in enumerate(chordset):
            if value == 1:
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
    midi = pyd.PrettyMIDI('./demo/demo lead sheets/ECNU University Song.mid')
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
    midi.write('C:/Users/zhaoj/Desktop/test_recon.mid')

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
