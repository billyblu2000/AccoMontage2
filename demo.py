import chorderator as cdt
import json

if __name__ == '__main__':

    demo_name = 'hpps65'
    input_melody_path = 'MIDI demos/inputs/' + demo_name + '/melody.mid'

    cdt.set_melody(input_melody_path)
    cdt.set_meta(tonic=cdt.Key.G)
    cdt.set_segmentation('A8A8B8B8')
    cdt.set_texture_prefilter((4, 4))
    cdt.set_note_shift(0)
    cdt.set_output_style(cdt.Style.POP_COMPLEX)
    cdt.generate_save(demo_name)