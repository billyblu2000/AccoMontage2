import time

import pretty_midi

STORE_PATH = 'static/pianoroll/midi/'


def construct_midi_seg(path, phrase, session_id):
    all_seg = []
    midi = pretty_midi.PrettyMIDI(path)
    tempo = midi.get_tempo_changes()[1][0]
    bar_duration = 60 / tempo * 4
    lengths = [int(phrase[2*i+1]) for i in range(len(phrase)//2)]
    phrase_time_sep = [0]
    current = 0
    for length in lengths:
        phrase_time_sep.append((current + length) * bar_duration)
        current += length
    for i in range(1, len(phrase_time_sep)):
        phrase_start = phrase_time_sep[i-1]
        phrase_end = phrase_time_sep[i]
        midi_seg = pretty_midi.PrettyMIDI()
        for ins in midi.instruments:
            ins_seg = pretty_midi.Instrument(0)
            for note in ins.notes:
                if phrase_start <= note.start < phrase_end:
                    ins_seg.notes.append(note)
            midi_seg.instruments.append(ins_seg)
        all_seg.append(midi_seg)
    current_time = str(time.time())
    count = 0
    all_names = []
    for seg in all_seg:
        name = session_id + '_' + current_time + '_' + str(count) + '.mid'
        all_names.append(name)
        seg.write(STORE_PATH + name)
        count += 1
    return all_names
