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

# input_dir = 'chorderator/utils/stats'
# output_dir = 'output'
#
# for file in os.listdir(input_dir):
#     if '.mid' in file:
#         cdt.set_melody(input_dir + '/'+ file)
#         phrase_length = file[:-4].split('_')[2:]
#         phrase_length = [int(i) for i in phrase_length]
#         cont = False
#         if len(phrase_length) == 0:
#             cont = True
#         for i in phrase_length:
#             if i not in [4, 8, 12, 16]:
#                 cont = True
#                 break
#         if cont:
#             continue
#         phrase, count = [], 1
#         for l in phrase_length:
#             phrase.append(count)
#             count += l
#         cdt.set_phrase(phrase)
#         cdt.set_meta(tonic=cdt.Key.C, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)
#         cdt.set_output_style(cdt.Style.POP_STANDARD)
#         try:
#             cdt.generate_save(file[:-4], with_log=True, base_dir=output_dir)
#         except:
#             continue

# output_dir = 'output'
# for path,dir_list,file_list in os.walk(output_dir)  :
#     for file_name in file_list:
#         if '.mid' in file_name:
#             midi = PrettyMIDI(os.path.join(path, file_name))
#             listen(midi, path=output_dir, out='/' + str(time.time()) + '.wav')