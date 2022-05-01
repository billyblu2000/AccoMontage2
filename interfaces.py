import os

from accomontage.AccoMontage_inference import accomontage
import chorderator as cdt
import pretty_midi


def generate_chord_and_accompaniment(input_name,
                                     segmentation,
                                     tonic,
                                     input_root='',
                                     mode=cdt.Mode.MAJOR,
                                     meter=cdt.Meter.FOUR_FOUR,
                                     chord_output_style=cdt.Style.POP_STANDARD,
                                     texture_spotlight=None,
                                     texture_prefilter=(4, 1),
                                     output_root='',
                                     output_name='',
                                     with_chord_generation_log=False,
                                     generation_formats=None,
                                     data_cache={}):
    if texture_spotlight is None:
        texture_spotlight = []
    if generation_formats is None:
        generation_formats = ['mid']

    cache_name, cache = [
                            'chord_gen_dict',
                            'chord_gen_lib',
                            'texture_gen_state_dict',
                            'texture_gen_phrase_data',
                            'texture_gen_edge_weights',
                            'texture_gen_four_beat_song_index',
                        ], {}

    for name in cache_name:
        if name in data_cache:
            cache[name] = data_cache[name]
        else:
            cache[name] = None

    phrases = []
    lengths = []
    current = 0
    while segmentation[current] != '\n':
        if segmentation[current].isalpha():
            j = 1
            while not (segmentation[current + j].isalpha() or segmentation[current + j] == '\n'):
                j += 1
            phrases.append(segmentation[current])
            lengths.append(int(segmentation[current + 1: current + j]))
            current += j
    phrases = [sum(lengths[:i]) + 1 for i in range(len(phrases))]

    core = cdt.get_chorderator()
    if input_root != '':
        core.set_melody(input_root + '/' + input_name)
    else:
        core.set_melody(input_name)
    core.set_phrase(phrases)
    core.set_meta(tonic=tonic, mode=mode, meter=meter)
    core.set_output_style(chord_output_style)
    core.set_cache(lib=cache['chord_gen_lib'], dict=cache['chord_gen_dict'])
    if output_root != '':
        try:
            os.makedirs(output_root)
        except:
            pass
        core.generate_save(output_name='chord_gen',
                           base_dir=output_root,
                           with_log=with_chord_generation_log,
                           formats=generation_formats)
    else:
        core.generate_save(output_name='chord_gen',
                           with_log=with_chord_generation_log,
                           formats=generation_formats)
    if output_root != '':
        midi = pretty_midi.PrettyMIDI(output_root + '/chord_gen/chord_gen.mid')
    else:
        midi = pretty_midi.PrettyMIDI('chord_gen/chord_gen.mid')
    new_midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    original_tempo = midi.get_tempo_changes()[1][0]
    for ins in midi.instruments:
        new_ins = pretty_midi.Instrument(0)
        for note in ins.notes:
            new_ins.notes.append(pretty_midi.Note(start=note.start * original_tempo / 120,
                                                  end=note.end * original_tempo / 120,
                                                  pitch=note.pitch,
                                                  velocity=note.velocity))
        new_midi.instruments.append(new_ins)
    if output_root != '':
        new_midi.write(output_root + '/chord_gen/chord_gen_120.mid')
    else:
        new_midi.write('chord_gen/chord_gen_120.mid')
    if output_root != '':
        accomontage(song_name='chord_gen_120.mid',
                    song_root=output_root + '/' + 'chord_gen',
                    segmentation=segmentation,
                    output_name=output_name +'_120.mid',
                    output_root=output_root,
                    spotlight=texture_spotlight,
                    prefilter=texture_prefilter)
    else:
        accomontage(song_name='chord_gen.mid',
                    song_root='chord_gen',
                    segmentation=segmentation,
                    output_name=output_name + '_120.mid',
                    output_root=output_root,
                    spotlight=texture_spotlight,
                    prefilter=texture_prefilter)
    if output_root != '':
        midi = pretty_midi.PrettyMIDI(output_root + '/' + output_name+'_120.mid')
    else:
        midi = pretty_midi.PrettyMIDI(output_name+'_120.mid')
    new_midi = pretty_midi.PrettyMIDI(initial_tempo=original_tempo)
    for ins in midi.instruments:
        new_ins = pretty_midi.Instrument(0)
        for note in ins.notes:
            new_ins.notes.append(pretty_midi.Note(start=note.start * 120 / original_tempo,
                                                  end=note.end * 120 / original_tempo,
                                                  pitch=note.pitch,
                                                  velocity=note.velocity))
        new_midi.instruments.append(new_ins)
    if output_root != '':
        new_midi.write(output_root + '/' + output_name)
    else:
        new_midi.write(output_name)
    if output_root != '':
        os.remove(output_root + '/chord_gen/chord_gen_120.mid')
        os.remove(output_root + '/' + output_name+'_120.mid')
    else:
        os.remove('chord_gen/chord_gen_120.mid')
        os.remove(output_name+'_120.mid')
