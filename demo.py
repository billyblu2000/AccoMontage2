from interfaces import generate_chord_and_accompaniment, cdt

generate_chord_and_accompaniment(input_name='E_86_8-8.mid',
                                 segmentation='A8A8\n',
                                 tonic=cdt.Key.E,
                                 input_root='MIDI demos/inputs',
                                 # mode=cdt.Mode.MAJOR,
                                 # meter=cdt.Meter.FOUR_FOUR,
                                 # chord_output_style=cdt.Style.POP_STANDARD,
                                 # texture_spotlight=[],
                                 # texture_prefilter=(4, 1),
                                 output_root='final_output',
                                 output_name='test.mid',
                                 # data_cache={
                                 #     'chord_gen_dict': None,
                                 #     'chord_gen_lib': None,
                                 #     'texture_gen_state_dict': None,
                                 #     'texture_gen_phrase_data': None,
                                 #     'texture_gen_edge_weights': None,
                                 #     'texture_gen_four_beat_song_index': None, }
                                 )
