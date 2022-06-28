import chorderator as cdt
import json

if __name__ == '__main__':

    demo_name = '113'

    # with open('MIDI demos/inputs/' + demo_name + '/meta.json', 'r') as f:
    #     data = json.load(f)
    #
    # print(data)


    input_melody_path = 'MIDI demos/inputs/' + demo_name + '/melody.mid'

    cdt.set_melody(input_melody_path)
    cdt.set_meta(tonic=cdt.Key.B)
    cdt.set_segmentation('A8A8C8')
    cdt.set_texture_prefilter((4, 4))
    cdt.set_note_shift(0)
    cdt.set_output_style(cdt.Style.POP_STANDARD)
    cdt.generate_save(demo_name)
    # cdt.generate_save(demo_name, task='texture', cut_in_arg='')
