import chorderator as cdt

if __name__ == '__main__':

    demo_name = 'reelsd-g7'
    input_melody_path = 'MIDI demos/inputs/' + demo_name + '/melody.mid'

    cdt.set_melody(input_melody_path)
    cdt.set_meta(tonic=cdt.Key.A)
    cdt.set_segmentation('A8A8B8B8A8B8B8')
    cdt.set_texture_prefilter((4, 1))
    cdt.set_note_shift(0)
    cdt.set_output_style(cdt.Style.POP_STANDARD)
    cdt.generate_save(demo_name)
