import time

import pretty_midi

STORE_PATH = 'static/midi/'


def construct_midi_seg(session, session_id):
    def construct(midi_path, sep, channel_name, delete_melo):
        all_seg = []
        midi = pretty_midi.PrettyMIDI(midi_path)
        for i in range(1, len(sep)):
            phrase_start = sep[i - 1]
            phrase_end = sep[i]
            midi_seg = pretty_midi.PrettyMIDI()
            if delete_melo:
                ins_seg = pretty_midi.Instrument(0)
                for note in midi.instruments[1].notes:
                    if phrase_start <= note.start < phrase_end:
                        note.start -= phrase_start
                        note.end -= phrase_start
                        ins_seg.notes.append(note)
                midi_seg.instruments.append(ins_seg)
            else:
                for ins in midi.instruments:
                    ins_seg = pretty_midi.Instrument(0)
                    for note in ins.notes:
                        if phrase_start <= note.start < phrase_end:
                            note.start -= phrase_start
                            note.end -= phrase_start
                            ins_seg.notes.append(note)
                    midi_seg.instruments.append(ins_seg)
            all_seg.append(midi_seg)
        current_time = str(time.time())
        count = 0
        names = []
        for seg in all_seg:
            name = session_id + '_' + current_time + '_{}_'.format(channel_name) + str(count) + '.mid'
            names.append(name)
            seg.write(STORE_PATH + name)
            count += 1
        return names

    m = pretty_midi.PrettyMIDI(session_id + '/textured_chord_gen.mid')
    tempo = m.get_tempo_changes()[1][0]
    bar_duration = 60 / tempo * 4
    lengths = [int(session.segmentation[2 * i + 1]) for i in range(len(session.segmentation) // 2)]
    phrase_time_sep = [0]
    current = 0
    for length in lengths:
        phrase_time_sep.append((current + length) * bar_duration)
        current += length
    all_names = {'melody': construct(session_id + '/melody.mid', phrase_time_sep, 'melody', False),
                 'chord_WM': construct(session_id + '/chord_gen.mid', phrase_time_sep, 'chord_WM', True),
                 'chord': construct(session_id + '/chord_gen.mid', phrase_time_sep, 'chord', False),
                 'acc_WM': construct(session_id + '/textured_chord_gen.mid', phrase_time_sep, 'acc_WM', True),
                 'acc': construct(session_id + '/textured_chord_gen.mid', phrase_time_sep, 'acc', False)}
    all_names = [{'melody': all_names['melody'][i],
                  'chord_WM': all_names['chord_WM'][i],
                  'chord': all_names['chord'][i],
                  'acc_WM': all_names['acc_WM'][i],
                  'acc': all_names['acc'][i]} for i in range(len(all_names['melody']))]
    return all_names
