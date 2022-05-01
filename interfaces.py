import os

from accomontage.AccoMontage_inference import accomontage
import chorderator as cdt


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

    if input_root != '':
        cdt.set_melody(input_root + '/' + input_name)
    else:
        cdt.set_melody(input_name)
    cdt.set_phrase(phrases)
    cdt.set_meta(tonic=tonic, mode=mode, meter=meter)
    cdt.set_output_style(chord_output_style)
    if output_root != '':
        try:
            os.makedirs(output_root)
        except:
            pass
        cdt.generate_save(output_name='chord_gen',
                          base_dir=output_root,
                          with_log=with_chord_generation_log,
                          formats=generation_formats)
    else:
        cdt.generate_save(output_name='chord_gen',
                          with_log=with_chord_generation_log,
                          formats=generation_formats)
    if output_root != '':
        accomontage(song_name='chord_gen.mid',
                    song_root=output_root + '/' + 'chord_gen',
                    segmentation=segmentation,
                    output_name=output_name,
                    output_root=output_root,
                    spotlight=texture_spotlight,
                    prefilter=texture_prefilter)
    else:
        accomontage(song_name='chord_gen.mid',
                    song_root='chord_gen',
                    segmentation=segmentation,
                    output_name=output_name,
                    output_root=output_root,
                    spotlight=texture_spotlight,
                    prefilter=texture_prefilter)
