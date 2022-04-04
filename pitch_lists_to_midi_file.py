from pretty_midi import PrettyMIDI, Instrument, Note


def pitch_lists_to_midi_file(pitch_lists, midi_path):
    midi = PrettyMIDI()
    ins = Instrument(0)
    cursor = 0
    unit_length = 0.125
    for pitch_list in pitch_lists:
        for pitch in pitch_list:
            if pitch != 0:
                ins.notes.append(Note(start=cursor, end=cursor + unit_length, pitch=pitch, velocity=60))
            cursor += unit_length
    midi.instruments.append(ins)
    midi.write(midi_path)


if __name__ == '__main__':
    pitch_lists = [[67, 67, 0, 0, 64, 64, 0, 0],
                   [67, 67, 0, 0, 64, 64, 0, 0]]
    pitch_lists_to_midi_file(pitch_lists=pitch_lists, midi_path='converted.mid')
