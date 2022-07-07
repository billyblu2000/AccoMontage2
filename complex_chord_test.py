import pretty_midi

import chorderator as cdt

if __name__ == '__main__':

    input_melody_path = 'complex_chord_test/test2.mid'  # 改我们的和弦

    cdt.set_melody(input_melody_path)
    cdt.set_meta(tonic=cdt.Key.C)
    cdt.set_segmentation('A8')
    cdt.set_texture_prefilter((1, 1))
    cdt.set_note_shift(0)
    cdt.set_output_style(cdt.Style.POP_STANDARD)
    cdt.generate_save('complex_chord_test', task='texture', cut_in_arg=input_melody_path, log=False)
    # m = pretty_midi.PrettyMIDI('complex_chord_test/test2.mid')
    # for note in m.instruments[-1].notes:
    #     print(note)